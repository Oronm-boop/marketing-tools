export const AppRoutes = [
    {
        path: "/",
        redirect: "/trends"
    },
    {
        path: "/trends",
        name:'热点分析',
        meta: { page: 'trends' },
        component: ()=>import('@views/MarketingSuite.vue')
    },
    {
        path: "/seo",
        name:'SEO关键词',
        meta: { page: 'seo' },
        component: ()=>import('@views/MarketingSuite.vue')
    },
    {
        path: "/copywriting",
        name:'宣传文案工具',
        meta: { page: 'copywriting' },
        component: ()=>import('@views/MarketingSuite.vue')
    },
    {
        path: "/publish",
        name:'发布中心',
        meta: { page: 'publish' },
        component: ()=>import('@views/MarketingSuite.vue')
    },
    {
        path: "/accounts",
        name:'账号管理',
        meta: { page: 'accounts' },
        component: ()=>import('@views/MarketingSuite.vue')
    },
    {
        path: "/accounts/login",
        redirect: "/accounts"
    },
    {
        path: "/history",
        name:'历史记录',
        meta: { page: 'history' },
        component: ()=>import('@views/MarketingSuite.vue')
    }
]
