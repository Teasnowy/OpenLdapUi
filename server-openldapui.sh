#!/bin/bash

# 服务启动脚本

# 启动用户, 非root用户请注意日志目录、配置文件权限
cmd_user="root"  
# 工作路径
dir_work="./api"
# 程序名
name_app="OpenLdapUi"
# grep匹配正则表达式
pattern_re="python OpenLdapUi-api.py"
# 启动命令和启动参数
cmd_start="python OpenLdapUi-api.py"
cmd_opt=""
# 你希望你的进程ps到的最起码有几个
cmd_wcl="1"
# 日志路径和日志名
dir_log="./logs"
name_log="openldapui-api"


# 定义日志格式, 需传入一个参数
# 参数1: 日志级别
# 参数2: 要打印的内容
function log() {
    # 日志级别
    case $1 in
        0)
            lv="INFO";;
        1)
            lv="WARNING";;
        3)
            lv="DEBUG";;
        4)
            lv="ERROR";;
        *)
            lv=$1;;
    esac

    ldate=`date +%Y-%m-%d\ %H:%M:%S`
    # 格式: [日期] [级别] 工作目录:用户:进程号:已运行秒数 ## 自定义内容
    echo -e "[${ldate}] [${lv}] ${PWD}:${USER}:$$:${SECONDS} ## $2"
}


# 检查进程存在性
# 需要传入三个参数: 
# 参数1: 进行什么比较, 需输入shell数字条件测试符: eq ne gt lt le ge, 不能带横杠
# 参数2: 期望进程数
# 参数3: 错误提示信息
function ac_monitor() {

    arg_fun_test=$1
    arg_fun_psn=$2
    arg_fun_tips=$3

    if [ -z "${pattern_re}" ];then
        pattern_re="${name_app}"
    fi

    pattern_test="eq ne gt lt le ge"
    n_test=`echo ${pattern_test} | grep -w "${arg_fun_test}" | wc -l`
    if [ ${n_test} -ne 1 ];then
        log 4 "输入的比较参数${arg_fun_test}不对, 只支持: [${pattern_test}]"
        exit 3
    fi
    
    sleep 3

    # n_ps=`ps -ef | grep "${pattern_re}" | grep -w -v -e grep -e "su - ${cmd_user}" -e "^${cmd_user}[[:space:][:digit:]]*$$" | wc -l`
    n_ps=`ps -ef | grep "${pattern_re}" | grep -w -v -e grep -e "su - ${cmd_user}" -e "^${cmd_user} \{1,\}$$" | wc -l`
    # aa=`ps -ef | grep "${pattern_re}" | grep -w -v -e grep -e "su - ${cmd_user}" -e "${cmd_user} \{1,\}$$"`
    # echo "$$"
    # echo "${aa}"
    if [ ${n_ps} -${arg_fun_test} ${arg_fun_psn} ];then
        log 0 "进程数为${n_ps}, 符合期望 ${arg_fun_test} ${arg_fun_psn}"
    else
        log 4 "进程数为${n_ps}, 不符合期望 ${arg_fun_test} ${arg_fun_psn}"
        log 4 "匹配规则: ps -ef | grep \"${pattern_re}\" | grep -w -v -e grep -e \"su - ${cmd_user}\" -e \"${cmd_user} \{1,\}$$\""
        log 4 "${arg_fun_tips}"
        exit 3
    fi
}


# 启动进程的函数
function ac_start() {
    # 进入工作目录
    cd ${dir_work}
    # 检查进程是否已存在, 已存在则退出
    ac_monitor eq 0 "进程已存在, 放弃本次启动"

    # 启动进程, 看看有没有cronolog, 有的话就按日期切割日志
    which cronolog &> /dev/null
    if [ $? -eq 0 ];then
        nohup ${cmd_start} ${cmd_opt} 2>&1 | cronolog ${dir_log}/${name_log}-%Y%m%d.log &
    else
        nohup ${cmd_start} ${cmd_opt} >> ${dir_log}/${name_log}.log 2>&1 &
    fi

    # 等待3秒
    sleep 3
    # 再次检查进程是否已存在
    ac_monitor ge ${cmd_wcl} "启动检测失败 命令: nohup ${cmd_start} ${cmd_opt}"
    log 0 "${name_app}启动成功"
}


# 停止进程的函数
function ac_stop() {
    # 对符合条件的进程执行kill -9
    # ps -ef | grep "${cmd_start}" | grep "${pattern_re}" | grep -w -v -e grep -e "su - ${cmd_user}" -e "$$" | awk '{print $2}' | while read pid;do
    ps -ef | grep "${pattern_re}" | grep -w -v -e grep -e "su - ${cmd_user}" -e "$$" | awk '{print $2}' | while read pid;do
        kill -9 ${pid}
        log 0 "已对进程号${pid}执行kill -9"
    done

    ac_monitor eq 0 "仍有进程存在, 停止失败"
    log 0 "${name_app}停止成功"
}

# 判断用户是否符合要求
if [ "`whoami`" != "${cmd_user}" ];then
    log 4 "您当前的用户${USER}不是指定的用户${cmd_user}\n\t请切换用户后再执行脚本\n\t不建议使用命令: su - ${cmd_user} -c \"/bin/bash `readlink -f ${0}` $*\", 某些情况会误判进程数 "
    exit 7
fi

# 检查有无日志目录且有写权限, 没有则创建
if [ ! -w "${dir_log}" ];then
    # 没有目录则创建目录（使用指定用户）
    mkdir -p ${dir_log}
    if [ ! -w "${dir_log}" ];then
        log 4 "创建日志目录${dir_log}失败, 可能是因为权限问题, 请手动创建后再执行"
        exit 6
    else
        log 0 "使用${cmd_user}用户创建了日志目录${dir_log}"
    fi
fi

case ${1} in
    "start")
        ac_start
        ;;
    "stop")
        ac_stop
        ;;
    "restart")
        ac_stop
        sleep 3
        ac_start
        ;;
    "status")
        ac_monitor ge ${cmd_wcl} "进程不存在"
        log 0 "${name_app}检测到存在的进程"
        ;;
    *)
        log 4 "不能识别的动作: ${1}\n仅支持以下动作: \
            \n\tstart       启动进程, 依靠脚本头部配置的变量组合启动命令并执行\
            \n\tstop        停止进程, 使用kill -9进程PID\
            \n\trestart     重启进程, 先停后起\
            \n\tstatus       检查进程, 进程不存在则返回异常状态码"
        exit 2
        ;;
esac