#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask Application Routes
"""
from .shopify import basic_bp


def register_routes(app):
    app.register_blueprint(basic_bp)
