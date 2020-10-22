#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project: app-scaffold
@File: webhook.py
@Author: Leo Chen <leo.cxy88@gmail.com>
@Date: 2020-10-22 16:56
"""
mutation = """
mutation {
  webhookSubscriptionCreate(topic: %s, webhookSubscription: {callbackUrl: "%s", format: JSON}) {
    userErrors {
      message
    }
  }
}
"""

query = """
query {
    webhookSubscriptions(first: 10) {
        edges {
            node {
                topic
                callbackUrl
                format
                id
                includeFields
            }
        }
        pageInfo {
            hasNextPage
        }
    }
}
"""

delete = """
mutation {
  webhookSubscriptionDelete(id: "%s") {
    userErrors {
      message
    }
  }
}
"""

__all__ = (mutation, query, delete)
