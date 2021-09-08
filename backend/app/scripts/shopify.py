#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : shopify.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 8/09/21 5:37 pm
"""
from flask import Blueprint
from os import remove
from click import option
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.introspection import query, variables
from sgqlc.codegen import get_arg_parse
from json import dump
# Custom Modules
from app.models.shopify import Store
from app.utils.base import get_version

shopify_bp = Blueprint('default', __name__, cli_group=None)


@shopify_bp.cli.command('generate_schema')
@option('-s', 'store_id', default=1, help='Store ID')
@option('-v', 'version', default=None, help='Version: 20xx-01 or 20xx-04 ...')
def generate_schema(store_id, version):
    """ Generate Shopify GraphQL Schema """
    version = get_version(version)
    store = Store.query.filter_by(id=store_id).first()
    if not store:
        raise Exception('Store does not exists!')
    headers = {'X-Shopify-Access-Token': store.token}
    url = 'https://{}/admin/api/{}/graphql'.format(store.key, version)
    endpoint = HTTPEndpoint(url, headers)
    data = endpoint(query, variables(
        include_description=False,
        include_deprecated=False,
    ))
    with open('schema.json', 'w') as f:
        dump(data, f, sort_keys=True, indent=2, default=str)
    ap = get_arg_parse()
    raw_args = ['schema', 'schema.json', './app/schemas/shopify.py']
    args = ap.parse_args(raw_args)
    args.func(args)
    # Remove the file
    remove('schema.json')
    print('Version: {} - Done'.format(version))


__all__ = shopify_bp
