#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Project : app-scaffold
# @File    : webhooks.py
# @Author  : Leo Chen<leo.cxy88@gmail.com>
# @Date    : 3/11/21 2:16 pm
"""
from flask import Blueprint, url_for, g
from click import argument
from sgqlc.operation import Operation
from prettytable import PrettyTable
from json import dumps
# Custom Modules
# app.schemas.shopify should generate by `flask generate_schema`
from app.schemas.shopify import shopify as shopify_schema
from app.utils.base import init_gql
from app.models.shopify import Store

webhook_bp = Blueprint('worker_bp', __name__, cli_group='webhook')


def check_store(id):
    """ Query Store by ID """
    record = Store.query.filter_by(id=id).first()
    if not record:
        raise Exception('Store ID[{}] does not exists!'.format(id))
    g.store_id = record.id
    return record


@webhook_bp.cli.command('list')
@argument('store_id')
def webhook_list(store_id):
    """ List all registered webhooks """
    check_store(store_id)
    table = PrettyTable(field_names=['WebhookID', 'Topic', 'CallbackUrl'])
    cursor = None
    with init_gql() as api:
        while True:
            op = Operation(shopify_schema.query_type)
            sub = op.webhook_subscriptions(first=20, after=cursor)
            sub.edges.cursor()
            sub.page_info.has_next_page()
            sub.edges.node.id()
            sub.edges.node.endpoint().__as__(shopify_schema.WebhookHttpEndpoint).callback_url()
            sub.edges.node.topic()
            res = api.fetch_data(op)['webhookSubscriptions']
            for node in res['edges']:
                node = node['node']
                table.add_row([node['id'], node['topic'], node['endpoint']['callbackUrl']])
            if res['pageInfo']['hasNextPage']:
                cursor = res['edges'][-1]['cursor']
            else:
                break
        print(table)


@webhook_bp.cli.command('revoke')
@argument('store_id')
def webhook_revoke(store_id):
    """ Revoke registered webhooks """
    check_store(store_id)
    table = PrettyTable(field_names=['WebhookID', 'Topic', 'Revoke', 'Message'])
    webhooks = {}
    cursor = None
    with init_gql() as api:
        while True:
            op = Operation(shopify_schema.query_type)
            query = op.webhook_subscriptions(first=20, after=cursor)
            query.edges.cursor()
            query.edges.node.id()
            query.edges.node.topic()
            query.page_info.has_next_page()
            res = api.fetch_data(op)['webhookSubscriptions']
            for node in res['edges']:
                node = node['node']
                alias = 'ID{}'.format(node['id'].split('/')[-1])
                webhooks[alias] = dict(id=node['id'], topic=node['topic'])
            if res['pageInfo']['hasNextPage']:
                cursor = res['edges'][-1]['cursor']
            else:
                break
        if len(webhooks.keys()) == 0:
            return print(f'StoreID[{store_id}] does not registered any webhooks')
        op = Operation(shopify_schema.mutation_type, 'RevokeWebhooks')
        for alias in webhooks:
            mutation = op.webhook_subscription_delete(id=webhooks[alias]['id'], __alias__=alias)
            mutation.user_errors()
        res = api.fetch_data(op)
        for alias in webhooks:
            if alias not in res or len(res[alias]['userErrors']) != 0:
                msg = 'Unknown'
                if alias in res:
                    msg = dumps(res[alias]['userErrors'])
                table.add_row([webhooks[alias]['id'], webhooks[alias]['topic'], False, msg])
            else:
                table.add_row([webhooks[alias]['id'], webhooks[alias]['topic'], True, 'Revoked'])
        print(table)


@webhook_bp.cli.command('init')
@argument('store_id')
def webhook_register(store_id):
    """ Register webhooks """
    check_store(store_id)
    topics = dict()
    topics['APP_UNINSTALLED'] = url_for('shopify.shop_redact', _scheme='https', _external=True)
    topics['ORDERS_CREATE'] = url_for('webhook.endpoint', target='orders', action='created', _scheme='https',
                                      _external=True)
    table = PrettyTable(field_names=['Topic', 'CallbackUrl', 'Message'])
    with init_gql() as api:
        op = Operation(shopify_schema.mutation_type, 'RegisterWebhooks')
        for topic in topics:
            mutation = op.webhook_subscription_create(topic=topic, webhook_subscription=dict(
                callback_url=topics[topic]
            ), __alias__=topic)
            mutation.user_errors()
    res = api.fetch_data(op)
    for topic in topics:
        if topic not in res or len(res[topic]['userErrors']) != 0:
            msg = 'Unknown'
            if topic in res:
                msg = dumps(res[topic]['userErrors'])
            table.add_row([topic, topics[topic], msg])
        else:
            table.add_row([topic, topics[topic], 'Success'])
    print(table)
