'use strict';
export default {
    app_url: process.env.VUE_APP_URL,
    rest_api: [
        {name: 'themes', url: '/api/themes'},
        {name: 'available_themes', url: '/api/themes_list'},
    ],
    bridge: {}
}
