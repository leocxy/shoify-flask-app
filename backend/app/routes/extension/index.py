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
from app.utils.base import check_hmac, create_jwt_token, refresh_jwt_token as jsonify, check_jwt

ext_bp = Blueprint(
    'extension', 'extension_discount', url_prefix='/ext',
    static_folder=path.join(path.dirname(ROOT_PATH), 'frontend/dist'),
    template_folder=path.join(path.dirname(ROOT_PATH), 'frontend/dist'),
)

ext_common_bp = Blueprint(
    'ext_common', __name__,
    url_prefix='/admin/common',
)


def static_html():
    """ Return the same Static file """
    return render_template(
        'admin/index.html',
        apiKey=environ.get('SHOPIFY_API_KEY'),
        # App bridge 2+
        host=request.args.get('host', None),
        # App bridge 1+
        shop=g.store_key,
        jwtToken=create_jwt_token()
    )


@ext_bp.get('/<app_path>/create', endpoint='create')
@check_hmac
def dynamic_app_create(app_path):
    return static_html()


@ext_bp.get('/<app_path>/<int:record_id>', endpoint='edit')
@check_hmac
def dynamic_app_edit(app_path, record_id):
    return static_html()


@ext_common_bp.get('/generate_code', endpoint='generate_code')
@check_jwt
def dynamic_app_generate_code():
    """ Generate a unique code """
    return jsonify(data=Faker().password(12, False, True, True, False))
