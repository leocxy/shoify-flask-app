#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manager Asset by ShopifyApi
"""
from pyactiveresource.connection import ResourceNotFound


def is_theme_exist(api, **kwargs):
    """ detect the theme exists or not """
    exists = True
    try:
        api.Asset.find('layout/theme.liquid', **kwargs)
    except ResourceNotFound:
        exists = False
    return exists


def get_asset_obj(api, asset_key, **kwargs):
    """ get asset object """
    try:
        asset = api.Asset.find(asset_key, **kwargs)
    except ResourceNotFound:
        asset = api.Asset(prefix_options=kwargs)
        asset.key = asset_key
    return asset


def deploy_to_theme(api, **kwargs):
    """ Deploy assets to theme """
    # Do something here
    # asset = get_asset_obj(api, liquid_path, **kwargs)
    # asset.value = liquid_content
    # asset.save()
    pass


def revert_from_theme(api, **kwargs):
    """ Revert asset from theme """
    # if not is_theme_exist(api, **kwargs):
    #     return
    # try:
    #     asset = api.Asset.find(liquid_path, **kwargs)
    #     asset.destroy()
    # except ResourceNotFound:
    #     pass
    pass
