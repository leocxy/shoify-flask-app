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
from app.utils.base import check_jwt, refresh_jwt_token as jsonify, form_validate, paginate_response
from app.utils.bundles import BundleHelper
from app.models.bundles import Bundle

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


@bundles_bp.route('', methods=['GET', 'POST'], endpoint='actions')
@check_jwt
def default_actions():
    if request.method == 'GET':
        query = Bundle.query.filter_by(store_id=g.store_id)
        count = int(request.args.get('count', 0))
        # Query
        if val := request.args.get('query'):
            query = query.filter(
                (Bundle.title.like('%{}%'.format(val))) | \
                (Bundle.product_title.like('%{}%'.format(val))) | \
                (Bundle.sku.like('%{}%'.format(val)))
            )
        if count == 1:
            return jsonify(data=query.count())
        paginate = query.order_by(Bundle.id.desc()).paginate(error_out=False)
        return paginate_response(paginate)
    else:
        data = request.get_json(silent=True)
        rs, res = form_validate(data, BundleHelper.get_schema())
        if not rs:
            return res
        obj = BundleHelper(g.store_id)
        rs, msg, data = obj.create_or_update_record(**data)
        if not rs:
            return jsonify(400, msg, data)
        return jsonify(data=data)


@bundles_bp.route('/<int:record_id>', methods=['GET', 'PUT', 'DELETE'], endpoint='record_curd')
@check_jwt
def record_curd(record_id):
    if request.method == 'GET':
        record = Bundle.query.filter_by(store_id=g.store_id, id=record_id).first()
        if not record:
            return jsonify(400, 'Record not found')
        rs = True
        msg = None
        data = record.get_all()
    elif request.method == 'DELETE':
        obj = BundleHelper(g.store_id)
        rs, msg, data = obj.delete_record(record_id)
    else:
        data = request.get_json(silent=True)
        rs, res = form_validate(data, BundleHelper.get_schema())
        if not rs:
            return res
        obj = BundleHelper(g.store_id)
        rs, msg, data = obj.create_or_update_record(*data, record_id=record_id)
    if not rs:
        return jsonify(400, msg, data)
    return jsonify(data=data)


__all__ = bundles_bp
