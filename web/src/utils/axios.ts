import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

// const router = useRouter()
let loading:any = null
// create an axios instance
const service = axios.create({
    baseURL: '', // api 的 base_url
    timeout: 30000, // request timeout
    withCredentials: true // 需要登录权限的要带cookie
})
// request interceptor
service.interceptors.request.use(config => {
    // 加载进度条
    loading = ElLoading.service({
        lock: true,
        text: '拼命加载中...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
    })
    // 修正method
    if (config.method) {
        config.method = config.method.toLocaleLowerCase()
    }
    // // 请求添加token
    // if (userStore.token) {
    //     config.headers['Authorization'] = getToken()
    // }
    return config
}, error => {
    // 关闭进度条
    loading.close()
    return Promise.reject(error)
})

// response interceptor
service.interceptors.response.use(
    response => {
        // 关闭进度条
        loading.close()
        const res = response.data
        // console.log(res)
        if (!res.code) {
            return res
        } else {
            return Promise.resolve(res)
        }
    },
    error => {
        // 关闭进度条
        loading.close()

        let msg = error.message
        // console.log('axios:msg: ', msg)
        // const regex = /<pre>(.*?)<\/pre>/ig
        // const result = regex.exec(msg)
        if (msg === 'Network Error') {
            msg = '网络错误,请检查网络连接'
        }
        if (msg.indexOf('timeout') >= 0) {
            msg = '请求超时,请重新操作'
        }
        ElMessage({
            message: msg || '系统异常',
            type: 'error'
        })
        return Promise.reject(error)
    }
)

export default service
export {
    service
}
