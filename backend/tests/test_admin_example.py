#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : test_admin_example.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 5/10/21 11:57 am
"""
import sys
from os import path
from pytest import fixture
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta
from unittest import TestCase
from random import choice, randint
from json import dumps

# Custom Modules
sys.path.append(path.abspath(path.dirname(path.dirname(__file__))))
from app import create_app, TIMEZONE


@fixture
def client():
    app, db = create_app({
        'TESTING': True,
        'FLASK_ENV': 'development',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    from app.models.shopify import Store
    with app.test_client() as client:
        with app.app_context():
            db.init_app(app)
            # create table
            db.create_all()
            # inject data
            record = Store(
                key='test.myshopify.com',
                domain='teststore.com',
                scopes='write_customers,write_orders,read_products',
                # You need to grab this from DB if you need to query product
                token='test_token'
            )
            db.session.add(record)
            db.session.commit()
            yield client, db


@fixture
def test():
    test = TestCase()
    test.maxDiff = None
    yield test


def test_admin_example(client, test):
    client = client[0]
    rv = client.get('/admin/test_jwt')
    expect = dict(status=0, message='success', data=[])
    test.assertDictEqual(rv.get_json(), expect)
