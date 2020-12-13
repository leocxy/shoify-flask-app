#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration for Flask
"""
from os import path, getenv
from app import ROOT_PATH


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLE = True
    DEVELOPMENT = False
    SECRET_KEY = getenv('SECRET_KEY', 'this-is-flask-secret-key123123123123')
    SERVER_NAME = getenv('SERVER_NAME')
    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(ROOT_PATH, 'app.db') \
        if not getenv('DATABASE_URL') else getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Embedded apps currently rely on 3rd party cookies to authenticate.
    # When the app loads, it sets a cookie in the browser.
    # The app keeps track of the cookie and any other relevant information in a session on its server.
    # The browser sends the cookie to the server with every request.
    # For privacy reasons, browsers are now restricting the use of 3rd party cookies.
    # This means that you can't use cookies to keep track of sessions of embedded apps.
    # Flask Session
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = False
    # Upload Folder
    UPLOAD_FOLDER = path.join(ROOT_PATH, 'tmp')
