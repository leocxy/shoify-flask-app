#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : webhooks.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 31/03/22 12:19 PM
"""
from flask import Blueprint
# custom modules
from app.utils.base import check_webhook

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')


@webhook_bp.route('/<target>/<action>', methods=['POST'], endpoint='endpoint')
@check_webhook
def webhook_endpoint(target, action):
    """ Received and process the webhook """
    print(target, action)
    return 'success'


__all__ = webhook_bp
