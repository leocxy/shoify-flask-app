### Introduction

This app created by Pocket Square.
It build for <MERCHANT_NAME>.

Backend is using [Flask](https://www.palletsprojects.com/p/flask/). 
Admin panel is using [VueJS](https://vuejs.org/).

### Environment

- OS: MacOX / Centos
- Python: 3
- VueJS: ^2.6.10

---

### Install to Shopify

https://your-domain.com/install?shop=your-store.myshopify.com

---

### Development & Deployment

Please check the README.md under **admin** and **backend** folder 

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
