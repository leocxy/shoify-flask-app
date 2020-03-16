#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Models for flask application
"""
from app import TIMEZONE
from datetime import datetime


def current_time():
    """ Return the current time """
    return datetime.now(TIMEZONE)

