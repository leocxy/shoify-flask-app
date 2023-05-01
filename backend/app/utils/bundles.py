#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : bundles.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 27/04/23 1:26 PM
"""
from sgqlc.operation import Operation
from simplejson import dumps
# custom modules
from app import db
from app.models.shopify import MetaDefinition
from app.models.bundles import Bundle, BundleItem
from app.utils.base import BasicHelper
from app.schemas.shopify import shopify as shopify_schema


class BundleHelper(BasicHelper):
    def __init__(self, store_id: int = 1, log_name: str = 'bundle_helper'):
        super(BundleHelper, self).__init__(store_id, log_name)
        # @important make sure this namespace and key are matching the extension query
        self._meta_definitions = [dict(
            namespace='ps-bundle',
            key='component_parents',  # Child Item only
            type='json',
            owner_type='PRODUCTVARIANT',
            description='Child item parent definition',
        ), dict(
            namespace='ps-bundle',
            key='component_reference',  # Parent Item only
            type='list.variant_reference',
            owner_type='PRODUCTVARIANT',
            description='Items included in the bundles'
        ), dict(
            namespace='ps-bundle',
            key='component_quantities',  # Parent Item only
            type='list.number_integer',
            owner_type='PRODUCTVARIANT',
            description='Quantity of items included in Bundle'
        ), dict(
            namespace='ps-bundle',
            key='price_adjustment',  # Parent Item only
            type='number_decimal',
            owner_type='PRODUCTVARIANT',
            description='Price Adjustment',  # in total, percentage
        )]

    @classmethod
    def get_schema(cls):
        pass

    def get_meta_definitions(self):
        # Query from internal database
        rs = []
        for val in self._meta_definitions:
            cond = dict(store_id=self.store.id, namespace=val['namespace'], key=val['key'],
                        owner_type=val['owner_type'])
            record = MetaDefinition.query.filter_by(**cond).first()
            if record:
                rs.append(record.to_dict())
            else:
                rs.append(dict(**val, status=0))
        return rs

    def create_meta_definition(self):
        # check if meta definition already exists
        result = []
        for val in self._meta_definitions:
            op = Operation(shopify_schema.query_type, 'QueryMetaDefinition')
            query = op.metafield_definitions(
                first=1,
                namespace=val['namespace'],
                key=val['key'],
                owner_type=val['owner_type']
            )
            query = query.edges.node
            query.id()
            # query.access.admin()
            query.name()
            query.description()
            query.owner_type()
            query.namespace()
            query.key()
            query.type.value_type()
            query.pinned_position()
            query.validations()
            query.use_as_collection_condition()
            query.visible_to_storefront_api()
            res = self.gql.fetch_data(op)['metafieldDefinitions']
            cond = dict(
                store_id=self.store.id,
                namespace=val['namespace'],
                key=val['key'],
                owner_type=val['owner_type']
            )
            if len(res['edges']) != 0:
                # meta definition already exists
                node = res['edges'][0]['node']
                record = MetaDefinition.create_or_update(cond, **cond, **dict(
                    md_id=node['id'].split('/')[-1],
                    # access=node['access']['admin'],
                    name=node['name'],
                    description=node['description'],
                    type=node['type']['valueType'],
                    pin=1 if node['pinnedPosition'] else 0,
                    validations=dumps(node['validations']),
                    collections=1 if node['useAsCollectionCondition'] else 0,
                    store_front=1 if node['visibleToStorefrontApi'] else 0,
                    status=1
                ))
                db.session.commit()
                result.append(record.to_dict())
                continue
            # create meta definition
            op = Operation(shopify_schema.mutation_type, 'MutationMetaDefinition')
            mutation = op.metafield_definition_create(
                definition=dict(
                    owner_type=val['owner_type'],
                    name=val['key'],
                    description=val['description'],
                    namespace=val['namespace'],
                    key=val['key'],
                    type=val['type'],
                    pin=True,
                    # access=dict(admin='MERCHANT_READ')
                )
            )
            mutation.user_errors()
            mutation.created_definition.id()
            res = self.gql.fetch_data(op)['metafieldDefinitionCreate']
            if len(res['userErrors']) != 0:
                msg = dumps(res['userErrors'])
                self.logger.error('Meta Definition create query: {}'.format(op))
                self.logger.error('Meta Definition create error: {}'.format(msg))
                return False, msg, res['userErrors']
            record = MetaDefinition.create_or_update(cond, **cond, **dict(
                md_id=res['createdDefinition']['id'].split('/')[-1],
                # only available on unstable version
                # access='MERCHANT_READ',
                name=val['key'],
                description=val['description'],
                type=val['type'],
                pin=1,
                collections=0,
                store_front=0,
                status=1
            ))
            result.append(record.to_dict())
            db.session.commit()
        return True, None, result

    def delete_meta_definition(self):
        result = []
        for val in self._meta_definitions:
            cond = dict(store_id=self.store.id, namespace=val['namespace'],
                        key=val['key'], owner_type=val['owner_type'])
            record = MetaDefinition.query.filter_by(**cond).first()
            if record and record.md_id and record.status == 1:
                # query before delete
                op = Operation(shopify_schema.query_type, 'QueryMetaDefinition')
                query = op.metafield_definition(
                    id='gid://shopify/MetafieldDefinition/{}'.format(record.md_id)
                )
                query.id()
                res = self.gql.fetch_data(op)['metafieldDefinition']
                if not res:
                    record.md_id = None
                    record.status = record.get_status('wait')
                    db.session.commit()
                    result.append(record.to_dict())
                    continue
                # delete meta definition
                op = Operation(shopify_schema.mutation_type, 'DeleteMetaDefinition')
                mutation = op.metafield_definition_delete(
                    delete_all_associated_metafields=True,
                    id='gid://shopify/MetafieldDefinition/{}'.format(record.md_id),
                )
                mutation.user_errors()
                res = self.gql.fetch_data(op)['metafieldDefinitionDelete']
                if len(res['userErrors']) > 0:
                    msg = dumps(res['userErrors'])
                    self.logger.error('Meta Definition delete query: {}'.format(op))
                    self.logger.error('Meta Definition delete error: {}'.format(msg))
                    return False, msg, res['userErrors']
                record.md_id = None
                record.status = 0
                db.session.commit()
                result.append(record.to_dict())
        return True, None, result

    def create_record(self):
        pass

    def update_record(self):
        pass
