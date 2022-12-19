#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask Application Routes
"""


def register_routes(app):
    from .shopify import basic_bp, docs_bp
    app.register_blueprint(basic_bp)
    app.register_blueprint(docs_bp)
    from .admin import admin_bp, ext_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(ext_bp)
    # from .webhook import webhook_bp
    # app.register_blueprint(webhook_bp)


__all__ = register_routes
