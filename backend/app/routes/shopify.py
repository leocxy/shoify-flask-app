#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-sherry-kitchen
@File: shopify.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:40
"""
import re
import requests
import uuid
from os import environ, path
from urllib.parse import urlencode
from flask import request, Blueprint, jsonify, url_for, redirect, render_template, make_response, g
from jinja2 import TemplateNotFound
from sgqlc.operation import Operation
# App Package
from app import db, ROOT_PATH, logger
from app.models.shopify import Store
from app.utils.base import Base, check_webhook, check_hmac, check_callback, create_jwt_token
from app.schemas.shopify import shopify as shopify_schema

basic_bp = Blueprint(
    'shopify',
    'default_shopify',
    static_url_path='',
    static_folder=path.dirname(ROOT_PATH) + '/admin/dist',
    template_folder=path.dirname(ROOT_PATH) + '/admin/dist',
)

docs_bp = Blueprint(
    'app_docs',
    __name__,
    url_prefix='/docs',
    static_url_path='',
    static_folder=path.dirname(ROOT_PATH) + '/admin/dist/front',
    template_folder=path.dirname(ROOT_PATH) + '/admin/dist/front',
)


@basic_bp.route('/install', methods=['GET'])
def install():
    target = request.args.get('shop') or ''
    regx = re.compile(r'^(.*).myshopify.com$')
    if re.match(regx, target) is None:
        resp = jsonify({'status': 500, 'message': 'Missing parameter. ?shop=your-shop.myshopify.com'})
        resp.status_code = 500
        return resp

    # Create Auth Url
    redirect_uri = url_for('.callback', _scheme='https', _external=True)
    state = uuid.uuid4().hex
    query_params = dict(client_id=environ.get('APP_KEY'), scope=environ.get('SCOPES'), redirect_uri=redirect_uri,
                        state=state)
    url = 'https://%s/admin/oauth/authorize?%s' % (target, urlencode(query_params))
    resp = redirect(url)
    resp.set_cookie('state', state)
    return resp


@basic_bp.route('/callback', methods=['GET'], endpoint='callback')
@check_callback
def callback():
    params = request.args
    # Store Token IN Database
    code = params['code']
    query = dict(client_id=environ.get('APP_KEY'), client_secret=environ.get('APP_SECRET'), code=code)
    url = 'https://{}/admin/oauth/access_token'.format(params['shop'])
    res = requests.post(url, json=query)
    data = res.json()
    if res.status_code != 200:
        resp = jsonify(data)
        resp.status_code = 500
        return resp
    # GraphQL Shop Info
    base = Base(params['shop'], data['access_token'])
    op = Operation(shopify_schema.query_type, 'QueryShopDomain')
    query = op.shop()
    query.name()
    query.url()
    res = base.fetch_data(op)['shop']
    domain = res['url'].split('/')[-1]
    # Store To Database
    record = Store.query.filter_by(key=params['shop']).first()
    if record is None:
        record = Store(
            key=params['shop'],
            domain=domain,
            scopes=data['scope'],
            token=data['access_token'],
            extra=''
        )
        db.session.add(record)
    else:
        record.scopes = data['scope']
        record.token = data['access_token']
        record.domain = domain
    db.session.commit()
    # Register GDPR mandatory webhooks
    op = Operation(shopify_schema.mutation_type, 'AddUninstallWebhook')
    mutation = op.webhook_subscription_create(topic='APP_UNINSTALLED', webhook_subscription=dict(
        callback_url=url_for('shopify.shop_redact', _scheme='https', _external=True)
    ))
    mutation.user_errors()
    res = base.fetch_data(op)['webhookSubscriptionCreate']
    if len(res['userErrors']):
        logger.error('Store Redact Mutation Error: %s', res['userErrors'])
    return redirect('https://{}/admin/apps/{}'.format(params['shop'], environ.get('APP_KEY')))


@basic_bp.route('/admin', methods=['GET'], endpoint='admin')
@check_hmac
def admin():
    """ Shopfiy Admin Embedded App - Vue SPA """
    try:
        resp = make_response(render_template(
            'admin/index.html',
            apiKey=environ.get('APP_KEY'),
            # App bridge 2+
            host=request.args.get('host', None),
            # App bridge 1+
            shop=g.store_key,
            jwtToken=create_jwt_token()
        ))
        return resp
    except TemplateNotFound:
        resp = jsonify({'status': 404, 'message': "Template missing"})
        resp.status_code = 404
        return resp


@basic_bp.route('/', methods=['GET'])
def index():
    """ Handle Request """
    params = request.args
    if len([x for x in params.keys() if x in ['timestamp', 'shop', 'hmac', 'host']]) == 4 and len(params) == 4
        return redirect(url_for('shopify.install', **params))
    if 'session' in params.keys() and len(params) >= 5:
        return redirect(url_for('shopify.admin', **params))
    return redirect(url_for('app_docs.index'))


@basic_bp.route('/webhook/shop/redact', methods=['POST'], endpoint='shop_redact')
@check_webhook
def shop_redact():
    """ erase the customer information for that store from your database """
    data = request.get_json()
    record = Store.query.filter_by(key=data['myshopify_domain']).first()
    if record:
        # store record
        db.session.delete(record)
    db.session.commit()
    return 'success'


@basic_bp.route('/webhook/customers/redact', methods=['POST'], endpoint='customer_redact')
@check_webhook
def customer():
    """ If your app has been granted access to the store's customers or orders,
    then you receive a redaction request webhook with the resource IDs that you need to redact or delete.
    In some cases, a customer record contains only the customer's email address. """
    # @todo
    return 'success'


@basic_bp.route('/webhook/customers/data_request', methods=['POST'], endpoint='customer_data_request')
@check_webhook
def customer_data():
    """ If your app has been granted access to customers or orders, then you receive a data request webhook
    with the resource IDs of the data that you need to provide to the store owner.
    It's your responsibility to provide this data to the store owner directly.
    In some cases, a customer record contains only the customer's email address. """
    # @todo
    return 'success'


@docs_bp.route('/', methods=['GET'])
def index():
    """ Docs """
    try:
        return make_response(render_template('index.html'))
    except TemplateNotFound:
        return 'Please contact dev@pocketsquare.co.nz for more information about this page.'
