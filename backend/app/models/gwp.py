#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : gwp.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 27/04/23 1:41 PM
"""
from app import db
from . import current_time, BasicMethod


class GiftWithPurchase(db.Model, BasicMethod):
    __tablename__ = 'gift_with_purchases'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), index=True)
    code_id = db.Column(db.BigInteger)
    code = db.Column(db.String(255))
    mid = db.Column(db.BigInteger)
    method = db.Column(db.SmallInteger)
    value = db.Column(db.Integer)
    message = db.Column(db.String(255))
    force_remove = db.Column(db.SmallInteger, default=0)
    secret_number = db.Column(db.Integer)
    status = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)
    items = db.relationship('GiftWithPurchaseItems', backref='gift_with_purchases', lazy='dynamic')

    def to_dict(self):
        value = self.value
        if self.method != 1:
            value = float('{:0.2f}'.format(value * 0.01))
        target = self.items.filter_by(target=1).first()
        if target:
            target = target.to_dict()
        pre_requirements = []
        cursor = 0
        sort_by = GiftWithPurchaseItems.id.asc()
        con1 = dict(target=2)
        con2 = GiftWithPurchaseItems.id > cursor
        count = self.items.filter_by(**con1).filter(con2).limit(1).count()
        while count > 0:
            for item in self.items.filter_by(**con1).filter(con2).order_by(sort_by).limit(100).all():
                cursor = item.id
                pre_requirements.append(item.to_dict())
            con2 = GiftWithPurchaseItems.id > cursor
            count = self.items.filter_by(**con1).filter(con2).limit(1).count()
        return dict(
            code=self.code,
            code_id=self.code_id,
            enable=self.status == 1,
            method=self.method,
            value=value,
            message=self.message,
            force_remove=self.force_remove == 1,
            secret_number=self.secret_number,
            target=target,
            pre_requirements=pre_requirements,
        )


class GiftWithPurchaseItems(db.Model, BasicMethod):
    __tablename__ = 'gift_with_purchase_items'
    __table_args__ = (
        db.PrimaryKeyConstraint('id'),
        db.Index('store_parent_id', 'store_id', 'parent_id')
    )
    id = db.Column(db.Integer)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('gift_with_purchases.id'))
    target = db.Column(db.SmallInteger, comment='1: Target, 2: Pre requirements')
    pid = db.Column(db.BigInteger)
    vid = db.Column(db.BigInteger)
    title = db.Column(db.String(255))
    handle = db.Column(db.String(255))
    image = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=current_time)
    updated_at = db.Column(db.DateTime, default=current_time, onupdate=current_time)

    def to_dict(self):
        data = dict(
            pid=self.pid,
            title=self.title,
            handle=self.handle,
            image=self.image
        )
        if self.target == 1:
            data['vid'] = self.vid
        return data
