#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-sherry-kitchen
@File: __init__.py.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:29
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path, environ
from pytz import timezone
from logging.config import dictConfig
from dotenv import load_dotenv
from gevent import monkey
__version__ = '0.0.1'
__author__ = 'Leo Chen'
__email__ = 'leo.cxy88@gmail.com'
__copyright__ = 'Copyright © Pocketsquare'
# Global Setting
app = None
db = None
logger = None
ROOT_PATH = path.abspath(path.dirname(path.dirname(__file__)))
TIMEZONE = timezone('Pacific/Auckland')
load_dotenv(dotenv_path=path.join(ROOT_PATH, '.env'))
monkey.patch_all()


def init_app():
    global app, db, logger
    dictConfig({
        'version': 1,
        'root': {'level': 'DEBUG' if environ.get('FLASK_ENV', 'development') == 'development' else 'INFO'}
    })
    app = Flask(__name__)
    logger = app.logger
    # Load Config From Object
    app.config.from_object('app.config.Config')

    # Init Database
    db = SQLAlchemy(app)
    Migrate(app, db)
    # Load Models
    from .models import shopify

    # Init Routes
    from .routes import register_routes
    register_routes(app)

    # Init Script
    from .scripts import register_scripts
    register_scripts(app)


init_app()
__all__ = (app, db, logger, ROOT_PATH, TIMEZONE)
