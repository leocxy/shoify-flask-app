'use strict';
module.exports = {
    base: '/docs/',
    title: 'Pocket Square',
    description: 'Shopify App Scaffold',
    head: [
        ['link', {rel: 'icon', href: '/assets/img/icon.svg'}]
    ],
    host: '0.0.0.0',
    port: '9000',
    dest: 'dist/front',
    themeConfig: {
        logo: '/assets/img/icon.svg',
        nav: [
            {text: 'Home', link: '/'},
            {text: 'Guide', link: '/guide'},
            {text: 'Install', link: '/setup'},
        ],
        sidebar: [
            '/',
            '/guide',
            ['/setup', 'Install'],
        ]
    },
    configureWebpack: (config) => {
        // Image
        config.resolve.alias['@picture'] = `${config.resolve.alias['@source']}/.vuepress/public/assets/img`;
    }
};
