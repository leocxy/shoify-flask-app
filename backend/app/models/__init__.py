#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: __init__.py.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:33
"""
from app import TIMEZONE
from datetime import datetime


def current_time():
    """ Return the current time """
    return datetime.now(TIMEZONE)
