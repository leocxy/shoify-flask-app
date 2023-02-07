#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : gwp.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 3/02/23 12:19 PM
"""
from flask import render_template
from sgqlc.operation import Operation
from simplejson import dumps
# custom modules
from app import db
from app.utils.base import BasicHelper
from app.models.shopify import GiftWithPurchase, GiftWithPurchaseItems
from app.schemas.shopify import shopify as shopify_schema


class GWPHelper(BasicHelper):
    def __init__(self, store_id: int, log_name: str = 'gwp_helper'):
        super(GWPHelper, self).__init__(store_id, log_name)
        # template path
        self.template_path = 'ruby/gwp.rb'
        # make sure this match shopify.ui.extension.toml
        self._ns = 'gwp-test'
        self._key = 'gwp-test'
        self._attr_key = '_gwp_hash_str'

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
            return value
        if reverse:
            return float('{:0.2f}'.format(float(value) * 0.01))
        return int(float(value) * 100)

    def generate_ruby_script(self, data: dict):
        return render_template(self.template_path, **data, attr_key=self._attr_key)

    def get_data(self):
        record = GiftWithPurchase.query.filter_by(store_id=self.store.id).first()
        if not record:
            return []
        data = record.to_dict()
        data['script'] = self.generate_ruby_script(data)
        return data

    def save_data(self, data: dict):
        cond = dict(store_id=self.store.id)
        values = dict(
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
        # Query Shop ID
        op = Operation(shopify_schema.query_type, 'QueryShopID')
        query = op.shop()
        query.id()
        res = self.gql.fetch_data(op)['shop']
        if not res:
            msg = 'Can`t fetch ShopID'
            self.logger.error(msg)
            return False, msg, None
        owner_id = res['id']
        # Update store meta data
        op = Operation(shopify_schema.mutation_type, 'UpdateShopMeta')
        mutation = op.metafields_set(metafields=[dict(
            owner_id=owner_id,
            namespace=self._ns,
            key=self._key,
            type='json',
            value=dumps(dict(attr_key=self._attr_key, **data)),
        )])
        mutation.metafields.id()
        mutation.user_errors()
        res = self.gql.fetch_data(op)['metafieldsSet']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('UpdateShopMeatError: %s', msg)
            return False, 'Update Shop Meta error!', res['userErrors']
        self.logger.debug('MetaID: %s', res['metafields'][0]['id'])
        # gid://shopify/Metafield/xxxxx
        record.mid = res['metafields'][0]['id'].split('/')[-1]
        db.session.commit()
        data = record.to_dict()
        data['script'] = self.generate_ruby_script(data)
        return True, None, data


__all__ = GWPHelper
