#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: __init__.py.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:29
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import environ
from os.path import dirname, abspath, join
from pytz import timezone
from logging.config import dictConfig
from dotenv import load_dotenv

__version__ = '0.1.1'
__author__ = 'Leo Chen'
__email__ = 'leo.cxy88@gmail.com'
__copyright__ = 'Copyright © PocketSquare'
# Global Setting
app = None
db = None
logger = None
# /backend
ROOT_PATH = abspath(dirname(dirname(__file__)))
TIMEZONE = timezone('Pacific/Auckland')
# root/.env - shopify ClI
load_dotenv(dotenv_path=join(dirname(ROOT_PATH), '.env'))


def create_app(test_config: dict = None):
    global app, db, logger
    dictConfig({
        'version': 1,
        'root': {'level': 'DEBUG' if environ.get('FLASK_ENV', 'development') == 'development' else 'INFO'}
    })
    app = Flask(__name__)
    logger = app.logger
    # Load Config From Object
    app.config.from_object('app.config.Config')
    # Update Testing Config
    if test_config:
        app.config.update(test_config)

    # Init Database
    db = SQLAlchemy(app)
    Migrate(app, db)

    # Init Routes
    from .routes import register_routes
    register_routes(app)

    # Init Script
    from .scripts import register_scripts
    register_scripts(app)

    if test_config is not None:
        return app, db
    return app


__all__ = (app, db, logger, ROOT_PATH, TIMEZONE, create_app)
