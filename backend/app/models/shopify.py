#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: shopify.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:39
"""
from simplejson import loads
# custom modules
from app import db
from . import current_time, BasicMethod


class Store(db.Model, BasicMethod):
    """ Shopify list/unlist App """
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), index=True, nullable=False)
    domain = db.Column(db.String(255))
    scopes = db.Column(db.Text, nullable=False)
    token = db.Column(db.String(64), nullable=False)
    extra = db.Column(db.Text, nullable=True)
    themes = db.relationship('Theme', backref='store', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)


class Theme(db.Model, BasicMethod):
    """ Install Theme """
    __tablename__ = 'store_themes'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), index=True)
    theme_id = db.Column(db.BigInteger)
    theme_name = db.Column(db.String(128), nullable=True)
    published = db.Column(db.SmallInteger, default=0)
    version = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)

    def to_dict(self):
        return dict(theme_id=self.theme_id, theme_name=self.theme_name, id=self.id)


class Webhook(db.Model, BasicMethod):
    """ Shopify Webhook """
    __tablename__ = 'webhooks'
    __table_args__ = (
        db.PrimaryKeyConstraint('id'),
        db.Index('store_webhook', 'store_id', 'webhook_id')
    )
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    webhook_id = db.Column(db.BigInteger, comment="Webhook ID")
    target = db.Column(db.String(24), comment='Action Target')
    action = db.Column(db.String(24), comment='Action')
    data = db.Column(db.Text(64000), comment='JSON string -> 64kb medium text for MYSQL/MariaDB')
    remark = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)


class DiscountCode(db.Model, BasicMethod):
    """ Shopify discount code """
    __tablename__ = 'discount_codes'
    __table_args__ = (
        db.PrimaryKeyConstraint('id'),
        db.Index('store_code_id', 'store_id', 'code_id')
    )
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    code_id = db.Column(db.BigInteger)
    code_stamp = db.Column(db.SmallInteger, comment='0: Product, 1: Order, 2: Shipping')
    code_type = db.Column(db.SmallInteger, default=0, comment="0: Manually, 1: Automatic")
    code_name = db.Column(db.String(255))
    method = db.Column(db.SmallInteger, default=1, comment='Percentage: 1, Fixed: 0')
    value = db.Column(db.Integer)
    combination = db.Column(db.SmallInteger, default=0, comment='Calculate by code_stamp')
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    message = db.Column(db.String(255))
    # cart, product, customer eligibility
    extra = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)

    @classmethod
    def convert_value(cls, val, reverse: bool = False):
        if reverse:
            return float('{:0.2f}'.format(float(val) * 0.01))
        return int(float(val) * 100)

    def get_extra(self):
        return {} if self.extra is None else loads(self.extra)

    def to_dict(self):
        return dict(
            id=self.id,
            code_id=self.code_id,
            code_stamp=self.code_stamp,
            code_type=self.code_type,
            code_name=self.code_name,
            method=self.method,
            value=self.convert_value(self.value, True),
            combination=self.combination,
            start_time=self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            end_time=self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            message=self.message,
            extra=self.get_extra(),
        )
