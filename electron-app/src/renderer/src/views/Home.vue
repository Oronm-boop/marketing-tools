<template>
    <div>
        <h1>首页</h1>
        <button @click="btn">按钮</button>
        {{ userStore.token }}
        <button @click="login">登录</button>
        <el-button type="success" plain>Success</el-button>
    </div>
</template>

<script setup lang="ts">
// import { useStore } from '../store'
// const store = useStore();
// console.log( store.counter )
import { useUserStore } from '@store/useUserStore'
let userStore = useUserStore();
console.log( userStore.token  );

const btn = ()=>{
    userStore.token = 'fhdkhfdisfhdisfds';
}

// import { useStore } from '../store'
// const store = useStore();
// console.log( store.user.userName );

import { loginByJson } from '@api/login'

const login = async ()=>{
    let res = await loginByJson({
        password:'123',
        username:'2443',
        key:'123',
        captcha:'21332'
    })
    console.log( res );
}

</script>
