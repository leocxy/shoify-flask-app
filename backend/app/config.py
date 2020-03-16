#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration for Flask
"""
from os import path, getenv
from dotenv import load_dotenv
from app import ROOT_PATH
# Load env variables
load_dotenv(dotenv_path=path.join(ROOT_PATH, '.env'))


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
    # Session
    SESSION_USE_SIGNER = True
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = path.join(ROOT_PATH, 'tmp', 'session')
    # Upload Folder
    UPLOAD_FOLDER = path.join(ROOT_PATH, 'tmp')
