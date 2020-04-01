#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, uuid, requests
from flask import request, Blueprint, jsonify, url_for, redirect, session
from os import environ, path
from urllib.parse import urlencode
from time import time
# App Package
from app import db, ROOT_PATH
from app.models.shopify import Store
from app.utils.base import Base, check_hmac, check_webhook

basic_bp = Blueprint(
    'shopify',
    __name__,
    static_url_path='/admin',
    static_folder=path.dirname(ROOT_PATH) + '/admin/dist',
    template_folder=path.dirname(ROOT_PATH) + '/admin/dist',
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


@basic_bp.route('/callback', methods=['GET'])
def callback():
    params = {}
    for arg in request.args:
        params[arg] = request.args.get(arg)
    # Check cookie
    state = request.cookies.get('state')
    if state is None or state != params['state']:
        resp = jsonify({'status': 403, 'message': 'Request origin cannot be verified'})
        resp.status_code = 403
        return resp
    # Timestamp
    one_day = 86400
    if int(request.args.get('timestamp', 0)) < time() - one_day:
        resp = jsonify({'status': 401, 'message': 'The request has expired'})
        resp.status_code = 401
        return resp
    # Hmac valid
    if not check_hmac(params):
        resp = jsonify({'status': 401, 'message': 'Invalid HMAC'})
        resp.status_code = 401
        return resp
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
    from app.schemas.shop import QUERY_DOMAIN
    res = base.fetch_data(QUERY_DOMAIN)['shop']
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
    return redirect('https://{}/admin/apps'.format(params['shop']))


@basic_bp.route('/admin', methods=['GET'])
def admin():
    """ Shopfiy Admin Embedded App """
    params = {}
    for arg in request.args:
        params[arg] = request.args.get(arg)
    # HMAC Check
    if not check_hmac(params):
        resp = jsonify({'status': 401, 'message': 'Invalid HMAC'})
        resp.status_code = 401
        return resp
    # Store Check
    store = Store.query.filter_by(key=params['shop']).first()
    if not store:
        resp = jsonify(dict(status=401, message='Unknow store name'))
        resp.status_code = 401
        return resp
    session['store_id'] = store.id
    # VueJS
    from flask import render_template, make_response
    from jinja2 import TemplateNotFound
    try:
        resp = make_response(render_template('index.html'))
        resp.set_cookie(
            'apiKey',
            environ.get('APP_KEY'),
            secure=True,
            samesite='None',
            domain='.' + environ.get('SERVER_NAME', 'localhost'))
        resp.set_cookie(
            'shop',
            store.key,
            secure=True,
            samesite='None',
            domain='.' + environ.get('SERVER_NAME', 'localhost'))
        return resp
    except TemplateNotFound:
        resp = jsonify({'status': 404, 'message': "Template missing"})
        resp.status_code = 404
        return resp


@basic_bp.route('/', methods=['GET'])
def index():
    """ Handle Request """
    params = request.args
    if len([x for x in params.keys() if x in ['timestamp', 'shop', 'hmac']]) == 3 and len(params) == 3:
        return redirect(url_for('.install', **params))
    if 'session' in params.keys() and len(params) == 5:
        return redirect(url_for('.admin', **params))
    return 'Please contact Pocket Square <dev@pocketsquare.co.nz> for more information about this app.'


@basic_bp.route('/webhook/shop/redact', methods=['POST'], endpoint='redact')
@check_webhook
def redact():
    data = request.get_json()
    record = Store.query.filter_by(key=data.shop_domain).first()
    if record:
        themes = record.themes.all()
        for theme in themes:
            db.session.delete(theme)
        db.session.delete(record)
    db.session.commit()
    return 'success'
