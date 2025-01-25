import { ElMessage, type MessageParams } from 'element-plus'
import { ElLoading, ElNotification  } from 'element-plus'


// 全局顶部提醒信息
export function global_window(type:'success' | 'warning' | 'info' | 'error', msg:any) {
    // type取值: 'primary' | 'success' | 'warning' | 'danger' | 'info'
    ElMessage({
        // 提示的消息
        message: msg,
        // 停留的时长(毫秒), 0未不自动消失
        duration: 7000,
        // 是否显示关闭按钮
        showClose: true,
        type: type,
    })
}

// 全局右侧弹出框
export function window_right(type:'success' | 'warning' | 'info' | 'error', msg:any) {
    ElNotification({
        title: type,
        message: msg,
        type: type,
        offset: 100,
    })
}


// 全屏阻塞动画开启
export function loading_open(loadTimeout:number|null=null) {
    const loadingInstance = ElLoading.service({
        // 全屏
        fullscreen: true
    })
    // 超时
    if (loadTimeout) {
        setTimeout(() => {
            loadingInstance.close()
            global_window('error', '后端似乎无响应')
        }, loadTimeout)
    }

}

// 全屏阻塞动画关闭
export function loading_close(err:any) {
    const loadingInstance = ElLoading.service({
        fullscreen: true
    })
    loadingInstance.close()
}
