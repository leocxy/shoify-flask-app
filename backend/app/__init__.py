#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NZ Mint App
Create by Pocket Square
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
from pytz import timezone
__version__ = '0.0.1'
__author__ = 'Leo Chen'
__email__ = 'leo.cxy88@gmail.com'
__copyright__ = 'Copyright © Pocketsquare'
# Global Setting
app = None
db = None
ROOT_PATH = path.abspath(path.dirname(path.dirname(__file__)))
TIMEZONE = timezone('Pacific/Auckland')


def init_app():
    global app, db
    app = Flask(__name__)
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
    # from .scripts import register_scripts
    # register_scripts(app)


init_app()
__all__ = (app, db, ROOT_PATH, TIMEZONE)
