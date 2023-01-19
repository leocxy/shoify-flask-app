#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: admin.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-12-14 11:28
"""
from flask import Blueprint, g, url_for
from os import environ
# Custom Modules
from app.models.shopify import Store
from app.utils.base import check_jwt, refresh_jwt_token as jsonify

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('test_jwt')
@check_jwt
def test():
    """ This is a test admin's api """
    return jsonify()


@admin_bp.route('/check/<action>', methods=['GET'], endpoint='check_action')
@check_jwt
def check_actions(action):
    """ Check API Scopes update to date or not """
    if action not in ['status', 'reinstall']:
        return jsonify()
    store = Store.query.filter_by(id=g.store_id).first()
    if action == 'status':
        current_scopes = store.scopes.lower().split(',')
        scopes = environ.get('SCOPES', '').lower().split(',')
        removes = [v for v in current_scopes if v not in scopes]
        adds = [v for v in scopes if v not in current_scopes]
        return jsonify(data=dict(
            removes=removes,
            adds=adds,
            change=len(removes) != 0 or len(adds) != 0
        ))
    else:
        url = url_for('shopify.install', shop=store.key, _external=True, _scheme='https')
        return jsonify(data=url)


__all__ = [admin_bp]
