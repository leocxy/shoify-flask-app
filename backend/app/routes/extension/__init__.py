#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : __init__.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 3/03/23 10:53 AM
"""


def register_sub_routes(app):
    from .index import ext_bp, ext_common_bp
    app.register_blueprint(ext_bp)
    app.register_blueprint(ext_common_bp)
    from .example import admin_bp
    app.register_blueprint(admin_bp)
    from .gwp import gwp_bp
    app.register_blueprint(gwp_bp)
    from .bundles import bundles_bp
    app.register_blueprint(bundles_bp)


__all__ = register_sub_routes
