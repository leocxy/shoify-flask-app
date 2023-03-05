#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : discount.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 21/12/22 10:11 AM
"""
from os import environ
from sgqlc.operation import Operation
from datetime import datetime
from simplejson import dumps
from pytz import UTC
# custom modules
from app import db, TIMEZONE
from app.models.shopify import DiscountCode
from app.utils.base import BasicHelper
from app.schemas.shopify import shopify as shopify_schema


class DiscountHelper(BasicHelper):
    def __init__(self, store_id: int, log_name: str = 'discount_helper', fn_id: str = None):
        super(DiscountHelper, self).__init__(store_id, log_name)
        fn_id = fn_id if fn_id is not None else 'SHOPIFY_FUNCTION_EXAMPLE_ID'
        self._function_id = environ.get(fn_id, None)
        if self._function_id is None:
            raise Exception('Can`t get the function ID from config: {}'.format(fn_id))
        # much match the `input.graphql`
        self._ns = 'test-function'
        self._key = 'test-config'
        # Product: 1 << 0
        # Order: 1 << 1
        # Shipping: 1 << 2
        self._code_stamp = 1 << 1
        # DiscountAutomaticNode, DiscountCodeNode
        # gid://shopify/DiscountAutomaticNode/

    @property
    def function_id(self):
        return self._function_id

    @staticmethod
    def get_schema():
        return dict(
            type=dict(type='string', required=True, allowed=['code', 'auto']),
            code=dict(type='string', required=False, maxlength=32, dependencies=dict(type=['code'])),
            title=dict(type='string', required=False, maxlength=64, dependencies=dict(type=['auto'])),
            method=dict(type='string', required=True, allowed=['percentage', 'fixed']),
            value=dict(type='number', min=0.01, required=True)
        )

    @classmethod
    def _format_json_data(cls, record: DiscountCode):
        rs = dict(
            method='fixed' if record.method == 0 else 'percentage',
            value=DiscountCode.convert_value(record.value, True),
            # hardcode for demo
            threshold=5,
        )
        return dumps(rs)

    @classmethod
    def _get_code_type(cls, val: str):
        return 1 if val == 'auto' else 0

    def edit(self, code_id: int, internal: bool = False):
        cond = dict(store_id=self.store.id, code_id=code_id)
        record = DiscountCode.query.filter_by(**cond).first()
        if not record:
            # double check on shopify?
            return False, 'DiscountNode[{}] does not exists!'.format(code_id)
        return True, record.to_dict() if not internal else record

    def create(self, data: dict):
        current_time = datetime.now(TIMEZONE)
        code_type = self._get_code_type(data['type'])
        record = DiscountCode.create(
            store_id=self.store.id,
            code_stamp=self._code_stamp,
            code_type=code_type,
            code_name=data['title'] if code_type == 1 else data['code'],
            method=1 if data['method'] == 'percentage' else 0,
            value=DiscountCode.convert_value(data['value']),
            start_time=current_time,
        )
        json_str = self._format_json_data(record)
        if code_type == 1:
            return self._create_auto_code(record, json_str)
        return self._create_code(record, json_str)

    def update(self, code_id: int, data: dict):
        rs, record = self.edit(code_id, True)
        if not rs:
            return rs, record
        record.value = DiscountCode.convert_value(data['value'])
        record.method = 1 if data['method'] == 'percentage' else 0
        json_str = self._format_json_data(record)
        if record.code_type == 1:
            record.code_name = data['title']
            return self._update_auto_code(record, json_str)
        record.code_name = data['code']
        return self._update_code(record, json_str)

    def delete(self, code_id: int):
        rs, record = self.edit(code_id, True)
        if not rs:
            return rs, record
        if record.code_type == 1:
            return self._delete_auto_code(record)
        return self._delete_code(record)

    def _create_auto_code(self, record: DiscountCode, json_str: str):
        op = Operation(shopify_schema.mutation_type, 'CreateAutoCode')
        mutation = op.discount_automatic_app_create(
            automatic_app_discount=dict(
                title=record.code_name,
                function_id=self.function_id,
                starts_at=record.start_time.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S"),
                metafields=[dict(
                    namespace=self._ns,
                    key=self._key,
                    type='json',
                    value=json_str,
                )]
            )
        )
        mutation.user_errors()
        mutation.automatic_app_discount.discount_id()
        res = self.gql.fetch_data(op)['discountAutomaticAppCreate']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('AutomaticCodeCreateError: %s', msg)
            return False, res['userErrors']
        self.logger.debug('AutomaticCodeCreate: %s', dumps(res))
        record.code_id = res['automaticAppDiscount']['discountId'].split('/')[-1]
        db.session.commit()
        return True, record.to_dict()

    def _update_auto_code(self, record: DiscountCode, json_str: str):
        op = Operation(shopify_schema.mutation_type, 'UpdateAutoCode')
        code_id = 'gid://shopify/DiscountAutomaticNode/{}'.format(record.code_id)
        mutation = op.discount_automatic_app_update(
            id=code_id,
            automatic_app_discount=dict(
                title=record.code_name,
                starts_at=record.start_time.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S"),
            )
        )
        mutation.user_errors()
        res = self.gql.fetch_data(op)['discountAutomaticAppUpdate']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('AutomaticCodeUpdateError: %s', msg)
            return False, res['userErrors']
        # update meta
        rs, msg = self.update_meta(
            owner_id=code_id,
            value=json_str,
            namespace=self._ns,
            key=self._key,
            value_type='json'
        )
        if not rs:
            return rs, msg
        db.session.commit()
        return True, record.to_dict()

    def _delete_auto_code(self, record: DiscountCode):
        op = Operation(shopify_schema.mutation_type, 'DeleteCode')
        mutation = op.discount_automatic_delete(id='gid://shopify/DiscountAutomaticNode/{}'.format(record.code_id))
        mutation.user_errors()
        res = self.gql.fetch_data(op)['discountAutomaticDelete']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('AutomaticCodeDeleteError: %s', msg)
            return False, res['userErrors']
        db.session.delete(record)
        db.session.commit()
        return True, None

    def _create_code(self, record: DiscountCode, json_str: str):
        op = Operation(shopify_schema.mutation_type, 'CreateCode')
        mutation = op.discount_code_app_create(
            code_app_discount=dict(
                title=record.code_name,
                code=record.code_name,
                function_id=self.function_id,
                starts_at=record.start_time.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S"),
                metafields=[dict(
                    namespace=self._ns,
                    key=self._key,
                    type='json',
                    value=json_str
                )]
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
        db.session.commit()
        return True, record.to_dict()

    def _update_code(self, record: DiscountCode, json_str: str):
        op = Operation(shopify_schema.mutation_type, 'UpdateCode')
        code_id = "gid://shopify/DiscountCodeNode/{}".format(record.code_id)
        mutation = op.discount_code_app_update(
            id=code_id,
            code_app_discount=dict(
                title=record.code_name,
                code=record.code_name,
                starts_at=record.start_time.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S"),
            )
        )
        mutation.user_errors()
        mutation.code_app_discount.discount_id()
        res = self.gql.fetch_data(op)['discountCodeAppUpdate']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('CodeUpdateError: %s', msg)
            return False, res['userErrors']
        # Update the meta
        rs, msg = self.update_meta(
            owner_id=code_id,
            namespace=self._ns,
            key=self._key,
            value_type='json',
            value=json_str
        )
        if not rs:
            return rs, msg
        db.session.commit()
        return True, record.to_dict()

    def _delete_code(self, record: DiscountCode):
        op = Operation(shopify_schema.mutation_type, 'DeleteCode')
        mutation = op.discount_code_delete(id='gid://shopify/DiscountCodeNode/{}'.format(record.code_id))
        mutation.user_errors()
        res = self.gql.fetch_data(op)['discountCodeDelete']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('DiscountCodeDeleteError: %s', msg)
            return False, res['userErrors']
        db.session.delete(record)
        db.session.commit()
        return True, None


__all__ = DiscountHelper
