#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask Application Routes
"""


def register_routes(app):
    from .shopify import basic_bp, docs_bp
    app.register_blueprint(basic_bp)
    app.register_blueprint(docs_bp)
