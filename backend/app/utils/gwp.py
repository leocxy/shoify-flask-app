#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : gwp.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 3/02/23 12:19 PM
"""
from sgqlc.operation import Operation
from simplejson import dumps
from os import environ
from datetime import datetime
# custom modules
from app import db
from app.utils.base import BasicHelper
from app.models.gwp import GiftWithPurchase, GiftWithPurchaseItems
from app.schemas.shopify import shopify as shopify_schema


class GWPHelper(BasicHelper):
    def __init__(self, store_id: int, log_name: str = 'gwp_helper', fn_id: str = None):
        super(GWPHelper, self).__init__(store_id, log_name)
        fn_id = fn_id if fn_id is not None else 'SHOPIFY_GWP_FUNCTION_ID'
        self._function_id = environ.get(fn_id, None)
        if self._function_id is None:
            raise Exception('Can`t get the function ID from config: {}'.format(fn_id))
        # make sure this match shopify.ui.extension.toml
        self._ns = 'gwp-test'
        self._key = 'config'
        self._attr_key = '_gwp_item'

    @property
    def function_id(self):
        return self._function_id

    @classmethod
    def get_schema(cls):
        item = dict(
            pid=dict(type='number', required=True),
            title=dict(type='string', required=True, maxlength=255),
            handle=dict(type='string', required=True, maxlength=255),
            image=dict(type='string', required=True, maxlength=512, nullable=True),
        )
        target = dict(**item, vid=dict(type='number', required=True))
        return dict(
            code_id=dict(type='integer', required=True, nullable=True),
            code=dict(type='string', required=True),
            enable=dict(type='boolean', required=True),
            method=dict(type='number', required=True, allowed=[1, 2]),
            value=dict(type='number', required=True, min=0),
            target=dict(type='dict', required=True, schema=target),
            pre_requirements=dict(type='list', required=True, schema=dict(type='dict', schema=item)),
            message=dict(type='string', required=True, maxlength=255, regex=r'^(?!.*[\'\"]).*$'),
            force_remove=dict(type='boolean', required=True),
            secret_number=dict(type='number', required=True, min=1, max=99999)
        )

    @classmethod
    def format_value(cls, value, method: int, reverse: bool = False):
        if method == 1:
            return int(value)
        if reverse:
            return float('{:0.2f}'.format(float(value) * 0.01))
        return int(float(value) * 100)

    def _format_code_meta(self, record: GiftWithPurchase, data: dict):
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%S'), dict(
            namespace=self._ns,
            key=self._key,
            type='json',
            value=dumps(dict(
                status=record.status == 1,
                method=record.method,
                value=record.value,
                message=record.message,
                secret_number=record.secret_number,
                pid=data['target']['pid'],
                attr_key=self._attr_key,
            ))
        )

    def _format_shop_meta(self, record: GiftWithPurchase, data: dict):
        return dict(
            namespace=self._ns,
            key=self._key,
            value_type='json',
            value=dumps(dict(
                status=record.status == 1,
                method=record.method,
                value=record.value,
                message=record.message,
                secret_number=record.secret_number,
                force_remove=record.force_remove == 1,
                attr_key=self._attr_key,
                target=data['target'],
                pre_requirements=list(map(lambda x: x['pid'], data['pre_requirements'])),
                code=record.code,
            ))
        )

    def _create_code(self, record: GiftWithPurchase, starts_at: str, meta: dict):
        op = Operation(shopify_schema.mutation_type, 'CreateDiscountCode')
        mutation = op.discount_code_app_create(
            code_app_discount=dict(
                title='PS-GWP',
                code=record.code,
                function_id=self.function_id,
                starts_at=starts_at,
                metafields=[meta]
            )
        )
        mutation.user_errors()
        mutation.code_app_discount.discount_id()
        res = self.gql.fetch_data(op)['discountCodeAppCreate']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('CodeCreateError: %s', msg)
            return False, res['userErrors']
        self.logger.debug('CodeCreate: %s', dumps(res))
        record.code_id = res['codeAppDiscount']['discountId'].split('/')[-1]
        return True, None

    def _update_code(self, record: GiftWithPurchase, starts_at: str, meta: dict):
        code_id = 'gid://shopify/DiscountCodeNode/{}'.format(record.code_id)
        op = Operation(shopify_schema.mutation_type, 'UpdateDiscountCode')
        mutation = op.discount_code_app_update(
            id=code_id,
            code_app_discount=dict(
                code=record.code,
                starts_at=starts_at
            )
        )
        mutation.user_errors()
        res = self.gql.fetch_data(op)['discountCodeAppUpdate']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('CodeUpdateError: %s', msg)
            return False, res['userErrors']
        # Update meta
        rs, msg = self.update_meta(
            owner_id=code_id,
            namespace=meta.get('namespace'),
            key=meta.get('key'),
            value_type=meta.get('type'),
            value=meta.get('value')
        )
        if not rs:
            return rs, msg
        return True, None

    def get_data(self):
        record = GiftWithPurchase.query.filter_by(store_id=self.store.id).first()
        if not record:
            return []
        data = record.to_dict()
        return data

    def save_data(self, data: dict):
        cond = dict(store_id=self.store.id)
        values = dict(
            code=data['code'],
            status=1 if data['enable'] else 0,
            method=data['method'],
            value=self.format_value(data['value'], data['method']),
            force_remove=1 if data['force_remove'] else 0,
            secret_number=data['secret_number'],
            message=data['message'],
        )
        record = GiftWithPurchase.create_or_update(cond, **cond, **values)
        if not record.id:
            db.session.flush()
        # target item
        target = data.get('target')
        cond = dict(store_id=self.store.id, parent_id=record.id, target=1)
        GiftWithPurchaseItems.create_or_update(cond, **cond, **target)
        # pre requirements
        ids = []
        for item in data['pre_requirements']:
            cond = dict(store_id=self.store.id, parent_id=record.id, target=2, pid=item['pid'])
            values = dict(title=item['title'], image=item['image'], handle=item['handle'])
            item_record = GiftWithPurchaseItems.create_or_update(cond, **cond, **values)
            db.session.flush()
            ids.append(item_record.id)
        # remove old data
        cond = dict(store_id=self.store.id, parent_id=record.id, target=2)
        record.items.filter_by(**cond).filter(~GiftWithPurchaseItems.id.in_(ids)).delete()
        # Create/Update DiscountNode -> Product discount function
        starts_at, meta = self._format_code_meta(record, data)
        rs, msg = self._update_code(record, starts_at, meta) if record.code_id else \
            self._create_code(record, starts_at, meta)
        if not rs:
            return False, msg, None
        # Create/Update Shopify Meta -> Checkout UI need this
        op = Operation(shopify_schema.query_type, 'QueryShopID')
        query = op.shop()
        query.id()
        res = self.gql.fetch_data(op)['shop']
        if not res:
            msg = 'Can`t fetch ShopID'
            self.logger.error(msg)
            return False, msg, None
        # Update store meta data
        rs, msg = self.update_meta(
            owner_id=res['id'],
            **self._format_shop_meta(record, data),
        )
        # gid://shopify/Metafield/xxxxx
        record.mid = msg
        db.session.commit()
        return True, None, record.to_dict()

    def delete_data(self, code_id: int):
        # Query Shop Meta
        op = Operation(shopify_schema.query_type, 'QueryShopMeta')
        query = op.shop()
        query = query.metafield(namespace=self._ns, key=self._key)
        query.id()
        res = self.gql.fetch_data(op)['shop']
        if res['metafield']:
            # Remove Shopify Meta
            op = Operation(shopify_schema.mutation_type, 'DeleteShopMeta')
            mutation = op.metafield_delete(input=dict(id=res['metafield']['id']))
            mutation.user_errors()
            res = self.gql.fetch_data(op)['metafieldDelete']
            if len(res['userErrors']) > 0:
                msg = 'Delete Shop Meta Error: {}'.format(dumps(res))
                self.logger.error(msg)
                return False, msg, res['userErrors']
        # Delete DiscountNode
        op = Operation(shopify_schema.mutation_type, 'DeleteCode')
        mutation = op.discount_code_delete(id='gid://shopify/DiscountCodeNode/{}'.format(code_id))
        mutation.user_errors()
        res = self.gql.fetch_data(op)['discountCodeDelete']
        if len(res['userErrors']) > 0:
            msg = 'Delete Code Error: {}'.format(dumps(res['userErrors']))
            self.logger.error(msg)
            return False, msg, res['userErrors']
        # Remove internal records
        record = GiftWithPurchase.query.filter_by(store_id=self.store.id, code_id=code_id).first()
        if record:
            record.items.delete()
            db.session.delete(record)
            db.session.commit()
        return True, None, None


__all__ = GWPHelper
