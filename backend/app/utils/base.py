#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Project: app-sherry-kitchen
@File: base.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-20 09:35
'''
from sgqlc.endpoint.http import HTTPEndpoint
from urllib.error import HTTPError, URLError
from os import getenv, environ, path, getpid, remove
from sys import exc_info
from time import sleep, time
from contextlib import contextmanager
from psutil import pid_exists
from datetime import datetime, timedelta
# Request validation
import hmac
import jwt
from hashlib import sha256
from json import dumps
from base64 import b64encode
import shopify
from flask import g, jsonify, session, request
from pyactiveresource.connection import ResourceNotFound, ClientError
from shopify.base import ShopifyConnection
# Custom
from app import ROOT_PATH, TIMEZONE
from app.models.shopify import Store


def patch_shopify_with_limits():
    func = ShopifyConnection._open

    def patched_open(self, *args, **kwargs):
        while True:
            try:
                return func(self, *args, **kwargs)
            except ClientError as e:
                if e.response.code == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 4))
                    print('Service exceeds Shopify API call limit, '
                          'will retry to send request in %s seconds' % retry_after)
                    sleep(retry_after)
                else:
                    raise e

    ShopifyConnection._open = patched_open


@contextmanager
def init_api(version=None):
    """ Init Shopify Restful API """
    app = Store.query.filter_by(id=g.store_id).first()
    if not app:
        raise Exception('can not init shopify api, something wrong from database')
    if version is None:
        version = environ.get('API_VERSION')
    patch_shopify_with_limits()
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


def check_hmac(fn):
    """ verify hmac """

    def before(*args, **kwargs):
        # for development mode
        if getenv('FLASK_ENV', 'production') == 'development':
            store = Store.query.first()
            g.store_id = store.id
            g.store_key = store.key
            return fn(*args, **kwargs)

        # production mode
        def hmac_calculate(params):
            def calculate(params):
                def encode_pairs(params):
                    for k, v in params.items():
                        if k == 'hmac':
                            continue
                        if k.endswith('[]'):
                            k = k.rstrip('[]')
                            v = dumps(list(map(str, v)))
                        # escape delimiters to avoid tampering
                        k = str(k).replace("%", "%25").replace("=", "%3D")
                        v = str(v).replace("%", "%25")
                        yield '{0}={1}'.format(k, v).replace("&", "%26")

                return '&'.join(sorted(encode_pairs(params)))

            return hmac.new(environ.get('APP_SECRET').encode(), calculate(params).encode(), sha256).hexdigest()

        params = request.args
        my_hmac = hmac_calculate(params).encode('utf-8')
        get_hmac = params['hmac'].encode('utf-8')
        valid = False
        try:
            valid = hmac.compare_digest(my_hmac, get_hmac)
        except AttributeError:
            pass
        if not valid:
            resp = jsonify({'status': 401, 'message': 'Invalid HMAC'})
            resp.status_code = 401
            return resp
        store = Store.query.filter_by(key=params['shop']).first()
        if not store:
            resp = jsonify(dict(status=401, message='Unknow store name'))
            resp.status_code = 401
            return resp
        g.store_id = store.id
        g.store_key = store.key
        return fn(*args, **kwargs)

    return before


def check_callback(fn):
    def before(*args, **kwargs):
        params = request.args
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

        def hmac_calculate(params):
            def calculate(params):
                def encode_pairs(params):
                    for k, v in params.items():
                        if k == 'hmac':
                            continue
                        if k.endswith('[]'):
                            k = k.rstrip('[]')
                            v = dumps(list(map(str, v)))
                        # escape delimiters to avoid tampering
                        k = str(k).replace("%", "%25").replace("=", "%3D")
                        v = str(v).replace("%", "%25")
                        yield '{0}={1}'.format(k, v).replace("&", "%26")

                return '&'.join(sorted(encode_pairs(params)))

            return hmac.new(environ.get('APP_SECRET').encode(), calculate(params).encode(), sha256).hexdigest()

        my_hmac = hmac_calculate(params).encode('utf-8')
        get_hmac = params['hmac'].encode('utf-8')
        valid = False
        try:
            valid = hmac.compare_digest(my_hmac, get_hmac)
        except AttributeError:
            pass
        if not valid:
            resp = jsonify({'status': 401, 'message': 'Invalid HMAC'})
            resp.status_code = 401
            return resp
        return fn(*args, **kwargs)

    return before


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
            resp = jsonify(status=401, message='proxy validation fail!', headers=request.headers.get_all(),
                           params=request.args)
            resp.status_code = 401
            return resp
        # Setup Store
        store = Store.query.filter_by(key=request.args.get('shop')).first()
        if not store:
            resp = jsonify(status=401, message='proxy validation fail!!')
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
        resp = jsonify(dict(status=401, message="Invalid Hmac Header, Please refresh the page"))
        resp.status_code = 401
        if not hmac_string:
            return resp
        digest = hmac.new(environ.get('APP_SECRET').encode('utf-8'), data, sha256).digest()
        computed_hmac = b64encode(digest)
        if not hmac.compare_digest(computed_hmac, hmac_string.encode('utf-8')):
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


def get_now(f='%Y-%m-%d %H:%M:%S'):
    return datetime.now(TIMEZONE).strftime(f)


def create_jwt_token():
    expire_time = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(dict(
        store_id=g.store_id,
        expire_time=int(expire_time.timestamp()),
        exp=expire_time,
    ), environ.get('APP_SECRET'), algorithm='HS256')


def check_jwt(fn):
    """ Check JWT Session Token """

    def before(*args, **kwargs):
        store_id = 1 if getenv(
            'FLASK_ENV', 'production') == 'development' else None
        if store_id:
            store = Store.query.filter_by(id=store_id).first()
            g.store_id = store.id
            g.jwt_expire_time = 0
            return fn(*args, **kwargs)
        # Regular Validation
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify(dict(status=401, message='Invalid Session Token, Please refresh the page'))
        try:
            res = jwt.decode(token[7:], environ.get(
                'APP_SECRET'), algorithms='HS256')
            g.store_id = res['store_id']
            g.jwt_expire_time = res['expire_time']
            return fn(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(dict(status=401, message='Session Token Expire, Please refresh the page'))
        except Exception as e:
            exc_type, exc_obj, exc_tb = exc_info()
            print(exc_type, exc_obj, exc_tb)
            raise e

    return before


def refresh_jwt_token(data: dict):
    """ Refresh JWT Token """
    expire_time = int(datetime.utcnow().timestamp()) + 600
    if g.jwt_expire_time != 0 and expire_time >= g.jwt_expire_time:
        data['jwtToken'] = create_jwt_token()
    return jsonify(data)



@contextmanager
def prevent_concurrency(key='main'):
    flag = path.join(ROOT_PATH, 'tmp', 'worker-{}.flag'.format(key))
    try:
        if path.isfile(flag):
            with open(flag, 'r') as f:
                pid = f.read()
                if pid_exists(int(pid)):
                    raise RuntimeError('%s [%s - %s] is running!' % (get_now(), key, getpid()))
            with open(flag, 'w+') as f:
                f.write(str(getpid()))
        else:
            with open(flag, 'w+') as f:
                f.write(str(getpid()))
        yield
        remove(flag)
    except RuntimeError as e:
        raise e
    except Exception as e:
        exc_type, exc_obj, exc_tb = exc_info()
        print(exc_type, exc_obj, exc_tb)
        raise e

# MultiPass Only
# def generate_token(data):
#     from Crypto.Random import get_random_bytes
#     from Crypto.Cipher import AES
#     from Crypto.Util.Padding import pad
#
#     secret = environ.get('MP_TOKEN')
#     if not secret:
#         raise Exception('MP_TOKEN is none!')
#     hash = sha256(secret.encode()).digest()
#     encrypt_key = hash[:16]
#     signature_key = hash[16:32]
#
#     # Genreate Token
#     data['created_at'] = datetime.utcnow().replace(microsecond=0).isoformat()
#     data = dumps(data)
#     iv = get_random_bytes(AES.block_size)
#     cipher = AES.new(encrypt_key, AES.MODE_CBC, iv=iv)
#     cipher_bytes = iv + cipher.encrypt(pad(data.encode(), AES.block_size))
#     sign_bytes = hmac.new(signature_key, cipher_bytes, sha256).digest()
#     return b64encode(cipher_bytes + sign_bytes).decode('utf-8').replace('+', '-').replace('/', '_')
