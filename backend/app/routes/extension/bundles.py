#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : bundles.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 27/04/23 10:44 AM
"""
from flask import Blueprint, g, request
# Custom modules
from app.utils.base import check_jwt, refresh_jwt_token as jsonify, form_validate
from app.utils.bundles import BundleHelper

bundles_bp = Blueprint('admin_bundles', __name__, url_prefix='/admin/bundles')


@bundles_bp.route('/meta_definitions', methods=['GET', 'POST', 'DELETE'], endpoint='meta_definition_actions')
@check_jwt
def meta_definition_actions():
    obj = BundleHelper(g.store_id)
    if request.method == 'GET':
        return jsonify(data=obj.get_meta_definitions())
    elif request.method == 'POST':
        rs, message, data = obj.create_meta_definition()
    else:
        rs, message, data = obj.delete_meta_definition()
    if not rs:
        return jsonify(400, message, data)
    return jsonify(data=data)


__all__ = bundles_bp
