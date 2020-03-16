### Introduction

This is an _**custom app**_ for `Community Organics`.
Because this is a `Custom App`, so this app will only able to install to one merchant.

Backend is using [Flask](https://www.palletsprojects.com/p/flask/). 
Admin panel is using [VueJS](https://vuejs.org/).

### Environment

- OS: MacOX / Centos
- Python: 3.6.*
- VueJS: ^2.6.10
---

### Install to Shopify

`https://organics.pocketsquare.co.nz/install?shop=your-domain.myshopify.com`

---

### Development & Deployment

Please check the README.md under **admin** and **backend** folder 

---

### Install Recharge App

Replace the CLIENT_ID with Recharge App Client ID

`https://shopifysubscriptions.com/partners/app/CLIENT_ID/install?myshopify_domain=communityorganics`

---

### Deploy to Heroku (If use)

You need to download heroku cli and login before you can go ahead.

```shell
# Access to project
cd path/to/project

# Create App at heroku
heroku apps:create APP-NAME

# Need to build Vue first
heroku buildpacks:add --index 1 heroku/nodejs

# Backend build
heroku buildpacks:add --index 2 heroku/python

# Added Postgresql as database 
heroku addons:add heroku-postgresql:hobby-dev

# Set env config
heroku config:set SERVER_NAME=APP-NAME-URL

# Set other configs -  check .env.sample
heroku config:set XX=YY

# Install database
heroku run upgrade

# Push current master branch to heroku
git push heroku master

# Push other branch to heroku
git push heroku OTHER_BRANCH:master
```
