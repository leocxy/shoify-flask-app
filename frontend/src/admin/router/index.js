import Vue from 'vue'
import VueRouter from "vue-router"

Vue.use(VueRouter);

const routes = [
    {
        path: '/ext/gift-with-purchase/create',
        name: 'gwp',
        component: () => import('../views/promotion/GiftWithPurchase')
    },
    {
        path: '/ext/gift-with-purchase/:code_id',
        name: 'gwp.edit',
        component: () => import('../views/promotion/GiftWithPurchase'),
        props: true
    },
    {
        path: '/ext/discount_code/create',
        name: 'discount',
        component: () => import('../views/Discount')
    },
    {
        path: '/ext/discount_code/:code_id',
        name: 'discount.edit',
        component: () => import('../views/Discount'),
        props: true
    },
    {
        path: '/promotion/bundles',
        name: 'bundles',
        component: () => import('../views/promotion/bundles/Index')
    },
    {
        path: '/promotion/bundles/create',
        name: 'bundles.create',
        component: () => import('../views/promotion/bundles/Create')
    },
    {
        path: '/promotion/bundles/:id',
        name: 'bundles.edit',
        component: () => import('../views/promotion/bundles/Create'),
        props: true
    },
    {path: '*', component: () => import('../views/Index')}
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition
        }
        return to.hash ? {selector: to.hash} : {x: 0, y: 0}
    },
    routes
});

export default router
