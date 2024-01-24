## Important

This repository has been deprecated. It has been migrated to [flask-shopify-utils](https://github.com/leocxy/flask-shopify-utils)

### Instruction

This repository created by Leo Chen <leo.cxy88@gmail.com>.

Backend is using [Flask](https://www.palletsprojects.com/p/flask/). 
Frontend is using [VueJS](https://vuejs.org/).
Shopify Function is using [Rust](https://www.rust-lang.org/)

### Structure

├── README.md
├── backend 
│ ├── README.md
│ ├── app
│ ├── migrations
│ ├── requirements.txt
│ ├── tests
│ ├── tmp
│ ├── uwsgi.ini
│ ├── uwsgi.ini.heroku
│ ├── uwsgi.ini.local
│ ├── uwsgi.ini.sample
│ └── wsgi.py
├── extensions
│ ├── README.md
│ ├── ps-bundle-sales
│ └── ps-gwp
├── frontend
│ ├── README.md
│ ├── babel.config.js
│ ├── config
│ ├── dist
│ ├── src
│ ├── vue.config.js
│ └── yarn-error.log
├── package.json
├── shopify.app.toml
└── yarn.lock 

`root/backend` for the backend files
`root/extensions` for shopify extensions folder
`root/frontend` for Admin UI/Docs

### Testing & Development Shopify extensions

```shell
yarn ext:server --reset
```

### Environment

- OS: MacOX / Centos
- Python: ^3.8
- VueJS: ^2.6.10

---

### Install to Shopify

https://your-domain.com/install?shop=your-store.myshopify.com

---