#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : bundles.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 27/04/23 10:52 AM
"""
# custom modules
from app import db
from . import BasicMethod, current_time


class Bundle(db.Model, BasicMethod):
    __tablename__ = 'bundles'
    __table_args__ = (
        db.PrimaryKeyConstraint('id'),
        db.Index('store_shopify_id', 'store_id', 'pid', 'vid')
    )
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    pid = db.Column(db.BigInteger, comment="Shopify Product ID")
    vid = db.Column(db.BigInteger, comment='Shopify Variant ID')
    meta_id = db.Column(db.String(255), comment='Split with comma')
    title = db.Column(db.String(255))
    product_title = db.Column(db.String(255))
    image = db.Column(db.String(1024))
    sku = db.Column(db.String(128), index=True)
    barcode = db.Column(db.String(128), index=True)
    status = db.Column(db.SmallInteger, default=0, comment='0:disable 1:enable')
    message = db.Column(db.String(255))
    total_price = db.Column(db.Integer, comment='Cent')
    total_discount = db.Column(db.Numeric(6, 2, asdecimal=False), comment='percentage')
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)
    items = db.relationship('BundleItem', backref="bundles", lazy='dynamic')

    def to_dict(self):
        return dict(
            id=self.id,
            pid=self.pid,
            vid=self.vid,
            name=self.title,
            product_title=self.product_title,
            image=self.image,
            sku=self.sku,
            barcode=self.barcode,
            status=self.status,
            message=self.message,
            total_price=self.total_price,
            total_discount=float('{:0.2f}'.format(self.total_discount)) if self.total_discount else 0,
            updated_at=self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        )

    def get_all(self):
        children = []
        for item in self.items.limit(1000).all():
            item = item.to_dict()
            del item['id']
            children.append(item)
        return dict(
            record_id=self.id,
            name=self.title,
            status=self.status,
            total_price=self.total_price,
            total_discount=self.total_discount,
            parent=dict(
                pid=self.pid,
                vid=self.vid,
                title=self.product_title,
                image=self.image,
                sku=self.sku,
                barcode=self.barcode,
            ),
            children=children
        )


class BundleItem(db.Model, BasicMethod):
    """ Bundle Product Item """
    __tablename__ = 'bundle_items'
    __table_args__ = (
        db.PrimaryKeyConstraint('id'),
        db.Index('store_parent_id', 'store_id', 'parent_id')
    )
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('bundles.id'))
    pid = db.Column(db.BigInteger, comment="Item's Product ID")
    vid = db.Column(db.BigInteger, comment="Item's Variant ID")
    meta_id = db.Column(db.BigInteger)
    title = db.Column(db.String(255), comment='Variant`s title')
    image = db.Column(db.String(1024))
    sku = db.Column(db.String(128), index=True)
    barcode = db.Column(db.String(128), index=True)
    origin_price = db.Column(db.BigInteger, comment="Origin Price, Cent")
    price = db.Column(db.BigInteger, comment="Cent")
    discount = db.Column(db.Numeric(5, 2), comment='Percentage')
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)

    def to_dict(self):
        return dict(
            id=self.id,
            vid=self.vid,
            pid=self.pid,
            title=self.title,
            image=self.image,
            sku=self.sku,
            barcode=self.barcode,
            price=self.price,
            origin_price=self.origin_price,
            quantity=self.quantity,
            discount=self.discount,
        )
