### Introduction

Here is the backend of the app.

### Environment

- OS: MacOX / Centos
- Python: 3.6.*

---

### Configuration

```shell
# create .env from sample
cd path/to/project/backend
cp .env.sample .env

# modify .env
vim .env
```

---

### Local Development

You should already install virtualenv

```shell
# Access the project
cd /path/to/project/backend

# Create virtual env
virtualenv .venv -p python3.6 --no-site-packages

# Active virtual env
source .venv/bin/active

# Install dependancise
pip install -r requirements.txt

# Run flask 
flask run
```

---

### Generate Shopify GraphQL schema

python -m sgqlc.introspection \
     --exclude-deprecated \
     --exclude-description \
     -H "X-Shopify-Access-Token: ${token}" \
     https://${SHOP}.myshopify.com/admin/api/${VERSION}/graphql \
     shopify_schema.json

---

Update react webhook URL