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
        common = dict(
            pid=dict(type='integer', required=True),
            vid=dict(type='integer', required=True),
            title=dict(type='string', required=True, maxlength=255),
            image=dict(type='string', required=True, nullable=True),
            sku=dict(type='string', required=True, nullable=True, maxlength=128),
            barcode=dict(type='string', required=True, nullable=True, maxlength=128),
        )
        return dict(
            name=dict(type='string', required=True, maxlength=255),
            status=dict(type='integer', required=True, min=0, max=1),
            total_price=dict(type='integer', required=True, min=0),
            total_discount=dict(type='number', required=True, max=100),
            parent=dict(type='dict', required=True, schema=common),
            children=dict(type='list', required=True, schema=dict(type='dict', schema=dict(
                origin_price=dict(type='integer', required=True, min=0),
                price=dict(type='integer', required=True, min=0),
                discount=dict(type='number', required=True, max=100),
                quantity=dict(type='integer', required=True, min=0),
                **common
            )))
        )

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
        # Check Bundles records
        count = Bundle.query.filter_by(store_id=self.store.id).count()
        if count > 0:
            return False, 'Bundles is not empty', None
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

    def delete_child_meta(self, meta_id):
        op = Operation(shopify_schema.mutation_type, 'DeleteChildMeta')
        mutation = op.metafield_delete(input=dict(id='gid://shopify/Metafield/{}'.format(meta_id)))
        mutation.user_errors()
        res = self.gql.fetch_data(op)['metafieldDelete']
        if len(res['userErrors']) != 0:
            msg = dumps(res['userErrors'])
            self.logger.error('Child Item delete error: {}'.format(msg))
            return False, msg, res['userErrors']
        return True, None, None

    def update_internal_records(self, name: str, status: int, total_price: int, total_discount: float, parent: dict,
                                children: list, record_id: int = None):
        # Create internal records
        cond = dict(store_id=self.store.id, pid=parent['pid'], vid=parent['vid'])
        if record_id:
            cond['id'] = record_id
        record = Bundle.create_or_update(
            cond,
            **cond,
            title=name,
            product_title=parent['title'],
            image=parent['image'],
            sku=parent['sku'],
            barcode=parent['barcode'],
            status=status,
            total_price=total_price,
            total_discount=total_discount
        )
        if not record_id:
            db.session.flush()
            record_id = record.id
        child_ids = []
        for val in children:
            cond = dict(store_id=self.store.id, pid=val['pid'], vid=val['vid'], parent_id=record_id)
            child = BundleItem.create_or_update(
                cond,
                **cond,
                title=val['title'],
                image=val['image'],
                sku=val['sku'],
                barcode=val['barcode'],
                origin_price=val['origin_price'],
                price=val['price'],
                discount=val['discount'],
                quantity=val['quantity'],
            )
            if not child.id:
                db.session.flush()
            child_ids.append(child.id)
        return record, child_ids

    def update_parent_meta(self, parent: dict, children: list, total_discount: float):
        prefix = 'gid://shopify/ProductVariant/{}'
        vid = prefix.format(parent['vid'])
        meta = []
        for val in self._meta_definitions[1:]:
            if val['type'] == 'list.variant_reference':
                value = dumps(list(map(lambda x: prefix.format(x['vid']), children)))
            elif val['type'] == 'list.number_integer':
                value = [int(x['quantity']) for x in children]
            else:
                value = '{:0.2f}'.format(float(100) - total_discount)
            meta.append(dict(
                owner_id=vid,
                namespace=val['namespace'],
                key=val['key'],
                value=value,
            ))
        op = Operation(shopify_schema.mutation_type, 'UpdateParentMeta')
        mutation = op.metafields_set(metafields=meta)
        mutation.user_errors()
        mutation.metafields.id()
        res = self.gql.fetch_data(op)['metafieldsSet']
        if len(res['userErrors']) != 0:
            msg = dumps(res['userErrors'])
            self.logger.error('Parent Item update query: {}'.format(op))
            self.logger.error('Parent Item update error: {}'.format(msg))
            return False, msg, res['userErrors']
        return True, ','.join(list(map(lambda x: x['id'].split('/')[-1], res['metafields']))), None

    def update_child_meta(self, parent: dict, children: list, total_discount: float, record: Bundle, child_ids: list):
        prefix = 'gid://shopify/ProductVariant/{}'
        definition = self._meta_definitions[0]
        value = dumps([dict(
            id=prefix.format(parent['vid']),
            component_reference=dict(
                value=list(map(lambda x: prefix.format(x['vid']), children)),
            ),
            component_quantities=dict(
                value=list(map(lambda x: int(x['quantity']), children)),
            ),
            price_adjustment=dict(value='{:0.2f}'.format(float(100) - total_discount))
        )])
        for val in children:
            op = Operation(shopify_schema.mutation_type, 'UpdateChildMeta')
            mutation = op.metafields_set(metafields=[dict(
                owner_id=prefix.format(val['vid']),
                namespace=definition['namespace'],
                key=definition['key'],
                value=value,
            )])
            mutation.user_errors()
            mutation.metafields.id()
            res = self.gql.fetch_data(op)['metafieldsSet']
            if len(res['userErrors']) != 0:
                msg = dumps(res['userErrors'])
                self.logger.error('Child Item update query: {}'.format(op))
                self.logger.error('Child Item update error: {}'.format(msg))
                return False, msg, res['userErrors']
            item = record.items.filter_by(vid=val['vid']).first()
            item.meta_id = int(res['metafields'][0]['id'].split('/')[-1])
        # delete child variant
        for item in record.items.filter(~BundleItem.id.in_(child_ids)).limit(1000).all():
            if item.meta_id:
                rs, msg, data = self.delete_child_meta(item.meta_id)
                if not rs:
                    return rs, msg, data
            db.session.delete(item)
        return True, None, None

    def create_or_update_record(self, name: str, status: int,
                                total_discount: float, total_price: int, parent: dict, children: list,
                                record_id: int = None):
        # Strict Children number
        if len(children) > 100:
            return False, 'Too many child variants!', None
        # Check Parent
        if record_id is None:
            # Create
            cond = dict(store_id=self.store.id, pid=parent['pid'], vid=parent['vid'])
            record = Bundle.query.filter_by(**cond).first()
        else:
            # Update
            cond = dict(store_id=self.store.id, pid=parent['pid'], vid=parent['vid'])
            record = Bundle.query.filter_by(**cond).filter(Bundle.id != record_id).first()
        # common
        if record:
            return False, 'Parent variant already assign as a child variant!', None
        record = BundleItem.query.filter_by(**cond).first()
        if record:
            return False, 'Parent variant already assign as a child variant!', None
        # Check Children
        for val in children:
            cond = dict(store_id=self.store.id, pid=val['pid'], vid=val['vid'])
            record = Bundle.query.filter_by(**cond).first()
            if record:
                return False, '{} already assign as a parent object'.format(val.title), None
            record = BundleItem.query.filter_by(**cond)
            if not record_id:
                record = record.first()
            else:
                record = record.filter(BundleItem.parent_id != record_id).first()
            if record:
                return False, '{} already assign as a child variant!'.format(val.title), None
        # Create internal records
        record, child_ids = self.update_internal_records(name, status, total_price, total_discount, parent, children)
        # Update variants' meta
        rs, msg, data = self.update_parent_meta(parent, children, total_discount)
        if not rs:
            return rs, msg, data
        record.meta_id = msg
        rs, msg, data = self.update_child_meta(parent, children, total_discount, record, child_ids)
        if not rs:
            return rs, msg, data
        db.session.commit()
        return True, None, record.get_all()

    def delete_record(self, record_id: int):
        record = Bundle.query.filter_by(store_id=self.store.id, id=record_id).first()
        if not record:
            return True, None, None
        # delete child variant's meta
        for item in record.items.limit(1000).all():
            if item.meta_id:
                rs, msg, data = self.delete_child_meta(item.meta_id)
                if not rs:
                    return rs, msg, data
            db.session.delete(item)
        # delete parent variant's meta
        if record.meta_id:
            for meta_id in record.meta_id.split(','):
                rs, msg, data = self.delete_child_meta(meta_id)
                if not rs:
                    return rs, msg, data
        db.session.delete(record)
        db.session.commit()
        return True, None, None

    def refresh_variant_data(self):
        pass
