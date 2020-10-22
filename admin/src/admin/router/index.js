import Vue from 'vue'
import VueRouter from "vue-router"

Vue.use(VueRouter);

const routes = [
    {
        path: '*', component: () => import('@/views/index.vue')
    }
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
