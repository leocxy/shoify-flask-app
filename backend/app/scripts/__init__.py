#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: __init__.py.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-22 16:55
"""


def register_scripts(app):
    from .shopify import shopify_bp
    app.register_blueprint(shopify_bp)
    # add webhook CLI if you need
    # from .webhook import webhook_bp
    # app.register_blueprint(webhook_bp)


__all__ = register_scripts
