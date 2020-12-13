#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask Application Routes
"""


def register_routes(app):
    from .shopify import basic_bp, docs_bp
    app.register_blueprint(basic_bp)
    app.register_blueprint(docs_bp)
    from .admin import admin_bp
    app.register_blueprint(admin_bp)


__all__ = register_routes
