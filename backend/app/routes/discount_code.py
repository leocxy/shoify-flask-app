#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : discount_code.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 12/01/23 11:01 AM
"""
from flask import Blueprint, g, render_template, request
from os import environ, path
from faker import Faker
# Custom modules
from app import ROOT_PATH
from app.utils.base import check_jwt, refresh_jwt_token as jsonify, check_hmac, create_jwt_token, form_validate
from app.utils.discount import DiscountHelper

admin_bp = Blueprint('admin_code', __name__, url_prefix='/admin/discount_code')

ext_bp = Blueprint(
    'extension', 'extension_discount', url_prefix='/ext/discount_code',
    static_folder=path.join(path.dirname(ROOT_PATH), 'frontend/dist'),
    template_folder=path.join(path.dirname(ROOT_PATH), 'frontend/dist'),
)


def static_html():
    """ Return the same Static file """
    return render_template(
        'admin/index.html',
        apiKey=environ.get('APP_KEY'),
        # App bridge 2+
        host=request.args.get('host', None),
        # App bridge 1+
        shop=g.store_key,
        jwtToken=create_jwt_token()
    )


@ext_bp.get('/create', endpoint='discount_code')
@check_hmac
def discount_code():
    return static_html()


@ext_bp.get('/<int:record_id>', endpoint='edit_discount_code')
@check_hmac
def edit_discount_code(record_id):
    return static_html()


@admin_bp.route('/generate', methods=['GET'], endpoint='generate_unique_code')
@check_jwt
def generate_code():
    code = Faker().password(12, False, True, True, False)
    return jsonify(data=code)


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
