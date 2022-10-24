#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: __init__.py.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:33
"""
from app import TIMEZONE, db
from datetime import datetime


def current_time():
    """ Return the current time """
    return datetime.now(TIMEZONE)


class BasicMethod(object):
    """ Basic Model carry with frequency methods """

    @classmethod
    def create_or_update(cls, cond: dict, **kwargs):
        record = cls.query.filter_by(**cond).first()
        if not record:
            record = cls()
            db.session.add(record)
        for key in kwargs:
            if hasattr(record, key):
                setattr(record, key, kwargs[key])
        return record

    @classmethod
    def create(cls, **kwargs):
        record = cls()
        db.session.add(record)
        for key in kwargs:
            if hasattr(record, key):
                setattr(record, key, kwargs[key])
        return record

    @staticmethod
    def get_status(name):
        names = dict(wait=0, done=1, error=2, ignore=3, unknown=9)
        return names.get(name, 9)
