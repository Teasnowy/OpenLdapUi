import axios from "axios";
import {global_window} from '@/api/def_feedback'
import {loading_open, loading_close} from '@/api/def_feedback'


// 后端返回的基本数据格式
interface yukikazeAppResult {
    "code": number,
    "ok": 'ok' | 'no',
    "message_err": string,
    "data": {} | [] | string | null,
    "jwt": string,
    "time": string
}


// 根据不同自定义后端状态码进行的操作
function code_next(data:yukikazeAppResult) {
    // if (data["code"]==40001) {
    //     // 40001说明是登录凭据错误, 此时弹回登录页
    //     console.log(data)
    //     router_left.push('/auth/login')
    //
    //     // window.location.href = '/#/auth/login';
    // }
}


function apiserver(path:string, info:any){
    return axios({
        method: 'post',
        url: path,
        data: info,
        headers: {
            // jwt
            'Authorization': 'Bearer ' + localStorage.getItem('yukikaze_user_jwt') || '',
            'X-Username':localStorage.getItem('yukikaze_user_account') || '',
        }
    })
}
// 通用api, 如果后端返回错误可以弹出全局窗口
export async function getServer(path:string, info:any, loading:boolean=false, loadTimeout:number|null=null){
    return new Promise((resolve, reject) => {
        if (loading) {
            loading_open(loadTimeout)
        }
        apiserver(path, info).then((res)=>{
            // 判断返回的header中有没有续签的jwt
            // console.log(res.headers)
            let header_jwt_renew = res.headers['x-jwt-renew']
            if (header_jwt_renew && header_jwt_renew != 'None') {
                console.log("触发续签: ", header_jwt_renew)
                localStorage.setItem('yukikaze_user_jwt', header_jwt_renew)
            }
            // 根据返回数据的信息做相应的动作
            let data = res.data as yukikazeAppResult
            if (data["ok"] == "ok"){
                resolve(data["data"])
            } else {
                // 根据不同的返回状态码进行不同的操作
                code_next(data)
                global_window("error", data["message_err"])
                reject(info)
            }
            if (loading) {
                loading_close(loadTimeout)
            }
        }).catch((error)=>{
            console.log(error)
            let header_jwt_renew = error.response.headers['x-jwt-renew'] || null
            if (header_jwt_renew && header_jwt_renew != 'None') {
                console.log("触发续签: ", header_jwt_renew)
                localStorage.setItem('yukikaze_user_jwt', header_jwt_renew)
            }
            // 优先取返回信息中的错误信息, 如果没有, 就用axios原生的message
            let data: yukikazeAppResult | any; // 使用any类型以防不确定性
            if (error.response && error.response.data) {
                data = error.response.data as yukikazeAppResult;
                // 根据不同的返回状态码进行不同的操作
                code_next(data)
                global_window("error", data.message_err || error)
            } else {
                console.log("无法解析自定义报错, 返回原error: ", error)
                global_window("error", error) // 如果不存在，则使用error对象
            }
            if (loading) {
                loading_close(loadTimeout)
            }
            reject(info)
        })

    })
}


// 根据邮箱发送邮箱验证码的函数
export async function def_sendcode_email(email:string) {
    await getServer('/api/email/send/code', {"email": email})
    global_window("success", '邮箱验证码发送成功')
}

// 根据手机号发送短信验证码的函数
export async function def_sendcode_sms(tel:string) {
    await getServer('/api/sms/send/code', {"tel": tel})
    global_window("success", '短信验证码发送成功')
}

// 根据账号发送邮箱验证码的函数
export async function def_sendcode_email_fromUser(user_account:string) {
    await getServer('/api/fromuser/email/send/code', {"user_account": user_account})
    global_window("success", '邮箱验证码发送成功')
}

// 根据账号发送短信验证码的函数
export async function def_sendcode_sms_fromUser(user_account:string) {
    await getServer('/api/fromuser/sms/send/code', {"user_account": user_account})
    global_window("success", '短信验证码发送成功')
}