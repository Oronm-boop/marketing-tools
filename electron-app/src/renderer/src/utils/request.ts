import axios from 'axios';

const defaultApiBaseURL = import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8088/api';
const apiBaseURL = import.meta.env.VITE_API_BASE_URL || defaultApiBaseURL;

const request = axios.create({
    baseURL: apiBaseURL,
    timeout: 300000
});

// 添加请求拦截器
request.interceptors.request.use(function (config) {
    return config;
}, function (error) {
    return Promise.reject(error);
});


// 添加响应拦截器
request.interceptors.response.use(function (response) {
    return response.data;
}, function (error) {
    const detail = error?.response?.data?.detail;
    const message = typeof detail === 'string' ? detail : error?.message || '请求失败';
    return Promise.reject(new Error(message));
});

export default request;
