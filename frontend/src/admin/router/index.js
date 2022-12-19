import Vue from 'vue'
import VueRouter from "vue-router"

Vue.use(VueRouter);

const routes = [
    {
        path: '/ext/discount_code/:record_id',
        name: 'discount.edit',
        component: () => import('@/views/Discount'),
        props: true
    },
    {path: '/ext/discount_code/create', name: 'discount', component: () => import('@/views/Discount')},
    {path: '*', component: () => import('@/views/Index')}
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
