#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: admin.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-12-14 11:28
"""
from flask import Blueprint
# Custom Modules
from app.utils.base import check_jwt, refresh_jwt_token as jsonify

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('test_jwt')
@check_jwt
def test():
    """ This is a test admin's api """
    return jsonify()


__all__ = [admin_bp]
