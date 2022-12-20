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
# custom modules
from app.utils.base import BasicHelper
from app.schemas.shopify import shopify as shopify_schema


class DiscountHelper(BasicHelper):
    def __init__(self, store_id: int, log_name: str = 'discount_helper', env_key: str = 'FUNCTION_ORDER_DISCOUNT_ID'):
        super(DiscountHelper, self).__init__(store_id, log_name)
        self._function_id = environ.get(env_key, None)
        if self._function_id is None:
            raise Exception('Can not load function ID from config')
        self._ns = 'test-function'
        self._key = 'test-config'

    @property
    def function_id(self):
        return self._function_id

    def _create_auto_code(self, data: dict):
        current_time = datetime.utcnow()
        op = Operation(shopify_schema.mutation_type, 'CreateAutoCode')
        mutation = op.discount_automatic_app_create(
            automatic_app_discount=dict(
                title=data.get('title'),
                function_id=self.function_id,
                starts_at=current_time.strftime("%Y-%m-%dT%H:%M:%S"),
                metafields=[dict(
                    namespace=self._ns,
                    key=self._key,
                    type='json',
                    value=dumps(dict(type=data['type'], value=data['value']))
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
        # gid://shopify/DiscountAutomaticNode/xxxxx
        return True, res['automaticAppDiscount']['id']

    def _update_auto_code(self, data: dict, code_id: int):
        op = Operation(shopify_schema.mutation_type, 'UpdateAutoCode')
        mutation = op.discount_automatic_app_update(
            id='',
            automatic_app_discount=dict(
                title=data.get('title'),
                function_id=self.function_id,
                metafields=dict(
                    namespace=self._ns,
                    key=self._key,
                    type='json',
                    value=dumps(dict(type=data['type'], value=data['value']))
                )
            )
        )
        mutation.user_errors()
        res = self.gql.fetch_data(op)['discountAutomaticAppUpdate']
        if len(res['userErrors']) > 0:
            msg = dumps(res['userErrors'])
            self.logger.error('AutomaticCodeUpdateError: %s', msg)
            return False, res['userErrors']
        return True, None

    def _delete_auto_code(self):
        pass

    def _create_code(self, data: dict):
        pass

    def _update_code(self, data: dict):
        pass

    def _delete_code(self):
        pass

    def create(self, data: dict):
        return self._create_auto_code(data) if data.get('method') == 'auto' else self._create_code(data)

    def update(self, data: dict):
        pass

    def delete(self):
        pass


__all__ = DiscountHelper
