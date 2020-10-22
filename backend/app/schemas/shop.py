#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: shop.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:40
"""
QUERY_DOMAIN = """
{
  shop {
    name
    url
  }
}
"""

__all__ = [QUERY_DOMAIN]
