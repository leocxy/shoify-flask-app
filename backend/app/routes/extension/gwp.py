#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : gift_with_purchase.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 3/02/23 9:21 AM
"""
from flask import Blueprint, request, g
from os.path import join
# Custom Modules
from app import ROOT_PATH
from app.utils.base import check_jwt, refresh_jwt_token as jsonify, form_validate
from app.utils.gwp import GWPHelper

gwp_bp = Blueprint(
    'admin_gwp', __name__,
    url_prefix='/admin/gift_with_purchase',
    template_folder=join(ROOT_PATH, 'app', 'templates')
)


@gwp_bp.get('', endpoint='get_data')
@check_jwt
def get_gwp_data():
    """ Get All GWP data """
    obj = GWPHelper(g.store_id)
    return jsonify(data=obj.get_data())


@gwp_bp.post('', endpoint='save_data')
@check_jwt
def save_data():
    """ Save GWP data """
    data = request.get_json(silent=True)
    rs, resp = form_validate(data, GWPHelper.get_schema())
    if not rs:
        return resp
    obj = GWPHelper(g.store_id)
    rs, msg, data = obj.save_data(data)
    if not rs:
        return jsonify(400, msg, data)
    return jsonify(data=data)


@gwp_bp.delete('<int:code_id>', endpoint='delete_data')
@check_jwt
def delete_data(code_id):
    """ Delete GWP Data """
    obj = GWPHelper(g.store_id)
    rs, msg, data = obj.delete_data(code_id)
    if not rs:
        return jsonify(400, msg, data)
    return jsonify()


__all__ = gwp_bp
