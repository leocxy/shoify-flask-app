#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : example.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 3/03/23 10:54 AM
"""
from flask import Blueprint, request, g
# custom modules
from app.utils.base import check_jwt, refresh_jwt_token as jsonify, form_validate
from app.utils.discount import DiscountHelper

admin_bp = Blueprint('admin_code', __name__, url_prefix='/admin/discount_code')


@admin_bp.route('/create', methods=['POST'], endpoint='create_discount_code')
@check_jwt
def create_discount_code():
    data = request.get_json(silent=True)
    rs, resp = form_validate(data, DiscountHelper.get_schema(), True)
    if not rs:
        return resp
    obj = DiscountHelper(g.store_id)
    rs, msg = obj.create(data)
    if not rs:
        return jsonify(400, 'Something wrong', msg)
    return jsonify(data=msg)


@admin_bp.route('/<int:code_id>', methods=['GET', 'PUT', 'DELETE'], endpoint='edit_discount_code')
@check_jwt
def get_discount_code(code_id):
    obj = DiscountHelper(g.store_id)
    # Post -> Update, form validation
    if request.method == 'PUT':
        data = request.get_json(silent=True)
        rs, resp = form_validate(data, DiscountHelper.get_schema(), True)
        if not rs:
            return resp
        rs, msg = obj.update(code_id, data)
    elif request.method == 'GET':
        rs, msg = obj.edit(code_id)
    else:
        rs, msg = obj.delete(code_id)
    if not rs:
        if type(msg) == list:
            return jsonify(400, 'An error occurred', msg)
        return jsonify(400, msg)
    return jsonify(data=msg)
