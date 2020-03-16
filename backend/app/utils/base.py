#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GraphQL Client
"""
from sgqlc.endpoint.http import HTTPEndpoint
from urllib.error import HTTPError, URLError
from os import getenv, environ
from time import sleep
from contextlib import contextmanager
# Request validation
from hashlib import sha256
import hmac, json, base64, shopify
from flask import g, jsonify, session, request
from pyactiveresource.connection import ResourceNotFound
# Custom
from app.models.shopify import Store


@contextmanager
def init_api(version=None):
    """ Init Shopify Restful API """
    app = Store.query.filter_by(id=g.store_id).first()
    if not app:
        raise Exception('can not init shopify api, something wrong from database')
    if version is None:
        version = environ.get('API_VERSION')
    api_session = shopify.Session(app.key, version, app.token)
    shopify.ShopifyResource.activate_session(api_session)
    yield shopify, app
    shopify.ShopifyResource.clear_session()


def deploy_to_theme(api, filepath, content, **kwargs):
    """ Deploy asset files to theme """
    try:
        api.Asset.find('layout/theme.liquid', **kwargs)
    except ResourceNotFound:
        return
    # Deploy
    try:
        asset = api.Asset.find(filepath, **kwargs)
    except ResourceNotFound:
        asset = api.Asset(prefix_options=dict(theme_id=kwargs['theme_id']))
        asset.key = filepath
    asset.value = content
    asset.save()


@contextmanager
def init_gql(timeout=5):
    """ Init Shopify GraphQL Client """
    app = Store.query.filter_by(id=g.store_id).first()
    if not app:
        raise Exception('can not init shopify api, something wrong from database')
    base = Base(app.key, app.token, timeout)
    yield base


class Base(object):
    def __init__(self, app_url, token, timeout=15):
        self._app_url = app_url
        self._token = token
        self._header = {'X-Shopify-Access-Token': self.token}
        self.version = getenv('API_VERSION')
        self.timeout = timeout
        if self.version:
            url = 'https://{}/admin/api/{}/graphql.json'.format(self._app_url, self.version)
        else:
            url = 'https://{}/admin/api/graphql.json'.format(self._app_url)
        self._endpoint = HTTPEndpoint(url, self.header, self.timeout)

    @property
    def app_url(self):
        return self._app_url

    @property
    def token(self):
        return self._token

    @property
    def header(self):
        return self._header

    def fetch_data(self, query, attempts=5):
        try:
            res = self._endpoint(query)
            if 'errors' in res.keys():
                if res['errors'][0]['message'] == 'Throttled':
                    sleep(2)
                    if attempts <= 0:
                        raise Exception(res)
                    # Try again
                    attempts -= 1
                    return self.fetch_data(query, attempts)
                # Something wrong
                raise Exception(res)
            else:
                return res['data']
        except (HTTPError, URLError) as err:
            if attempts < 0:
                raise err
            else:
                attempts -= 1
                return self.fetch_data(query, attempts)

    def get_url(self, url):
        return 'https://{}'.format(self.app_url) + url.format(version=self.version)


def check_hmac(params):
    """ Validation Shopify request """
    def hmac_calculate(params):
        def calculate(params):
            def encode_pairs(params):
                for k, v in params.items():
                    if k == 'hmac':
                        continue
                    if k.endswith('[]'):
                        k = k.rstrip('[]')
                        v = json.dumps(list(map(str, v)))
                    # escape delimiters to avoid tampering
                    k = str(k).replace("%", "%25").replace("=", "%3D")
                    v = str(v).replace("%", "%25")
                    yield '{0}={1}'.format(k, v).replace("&", "%26")
            return '&'.join(sorted(encode_pairs(params)))
        return hmac.new(environ.get('APP_SECRET').encode(), calculate(params).encode(), sha256).hexdigest()
    # Wow
    my_hmac = hmac_calculate(params).encode('utf-8')
    get_hmac = params['hmac'].encode('utf-8')
    try:
        return hmac.compare_digest(my_hmac, get_hmac)
    except AttributeError:
        return get_hmac == my_hmac


def check_proxy(fn):
    """ verify proxy request """
    def before(*args, **kwargs):
        # for development mode
        if getenv('FLASK_ENV', 'production') == 'development':
            store = Store.query.first()
            g.store_id = store.id
            return fn(*args, **kwargs)
        params = {}
        signature = ''
        for key in request.args:
            if key != 'signature':
                params[key] = request.args.get(key)
            else:
                signature = request.args.get(key)
        query = ''
        for key in sorted(params):
            query += '{}={}'.format(key, params[key].join(',') if isinstance(params[key], list) else params[key])
        if signature != hmac.new(environ.get('APP_SECRET').encode(), query.encode(), sha256).hexdigest():
            resp = jsonify(status=401, message='proxy validation fail!')
            resp.status_code = 401
            return resp
        # Setup Store
        store = Store.query.filter_by(domain=request.args.get('shop')).first()
        if not store:
            resp = jsonify(status=401, message='proxy validation fail!')
            resp.status_code = 401
            return resp
        g.store_id = store.id
        return fn(*args, **kwargs)
    return before


def check_webhook(fn):
    """ verify webhook request by public app """
    def before(*args, **kwargs):
        data = request.get_data()
        hmac_string = request.headers.get('X-Shopify-Hmac-Sha256')
        digest = hmac.new(environ.get('APP_SECRET').encode('utf-8'), data, sha256).digest()
        computed_hmac = base64.b64encode(digest)
        if not hmac.compare_digest(computed_hmac, hmac_string.encode('utf-8')):
            resp = jsonify(dict(status=400, message="Invalid Session, Please refresh the page"))
            return resp
        return fn(*args, **kwargs)
    return before


def check_session(fn):
    """ Check session """
    def before(*args, **kwargs):
        # for development debug
        if getenv('FLASK_ENV', 'production') == 'development':
            store_id = session.get('store_id', 1)
        else:
            store_id = session.get('store_id')
        if not store_id:
            resp = jsonify(dict(status=400, message="Invalid Session, Please refresh the page"))
            resp.status_code = 400
            return resp
        g.store_id = store_id
        return fn(*args, **kwargs)
    return before
