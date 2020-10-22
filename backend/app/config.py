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
    # Flask Session
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = False
    # Upload Folder
    UPLOAD_FOLDER = path.join(ROOT_PATH, 'tmp')
