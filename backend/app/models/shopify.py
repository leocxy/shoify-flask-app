#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: shopify.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:39
"""
from app import db
from . import current_time, BasicMethod


class Store(db.Model):
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

    def __repr__(self):
        return '<Store {}>'.format(self.id)


class Theme(db.Model):
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

    def __repr__(self):
        return '<StoreTheme {}>'.format(self.id)


class Webhook(db.Model, BasicMethod):
    """ Shopify Webhook """
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    webhook_id = db.Column(db.BigInteger, comment="Webhook ID")
    target = db.Column(db.String(24), comment='Action Target')
    action = db.Column(db.String(24), comment='Action')
    data = db.Column(db.Text, comment='JSON string')
    remark = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)

    @staticmethod
    def get_status(name):
        names = dict(wait=0, done=1, error=2, ignore=3, unknown=9)
        return names.get(name, 9)
