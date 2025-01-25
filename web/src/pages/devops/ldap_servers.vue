<script setup lang="ts">
import {computed, type Ref, ref} from 'vue'
import {useClipboard} from '@vueuse/core'
import type {
  reqLdapClone,
  reqLdapSe,
  resLdapAll,
  resLdapAttr,
  resLdapClass,
  resLdapDir,
  resLdapDirInfo,
  resLdapSeObj
} from '@/api/itf_ldapServers'
import {ArrowDown, Back, CirclePlus, Delete, Minus, Plus, List, Reading} from '@element-plus/icons-vue'
import {ElTreeV2, genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile, UploadFiles, UploadFile, UploadUserFile } from 'element-plus'
import type {TreeData, TreeKey, TreeNode, TreeNodeData} from 'element-plus/es/components/tree-v2/src/types'
import {global_window, window_right} from '@/api/def_feedback'
import {getServer} from '@/api/def_servers'
import {deepClone} from '@/utils/myvar'
import {sleep} from '@/utils/sleep'
import zihao from '@/assets/zihao.jpg'
import bumen from '@/assets/svg/bumen.svg'
import yuangong from '@/assets/svg/yuangong.svg'
import wendang from '@/assets/svg/wendang.svg'
import dingjiyu from '@/assets/svg/dingjiyu.svg'

// 后端返回的所有ldap服务器, 是个对象
  let data_res_servers:Ref<resLdapSeObj> = ref({})
  // 后端返回的单个ldap服务器的所有条目树状图
  let data_res_serverdirTree:Ref<resLdapDir[]> = ref([])
  // 后端返回的单个ldao服务器的所有条目信息
  let data_res_serverdirInfo:Ref<resLdapDirInfo> = ref({})
  // 后端返回的单个ldap服务器的所有模板信息
  let data_res_serverclass:Ref<resLdapClass> = ref({})
  // 后端返回的单个ldap服务器的所有属性信息
  let data_res_serverattrs:Ref<resLdapAttr> = ref({})
  // 后端返回的单个ldap服务器的起始dn
  let data_res_serverbase:Ref<string> = ref("")
  // 目录树的ref回调
  let tree_ldapdir = ref<InstanceType<typeof ElTreeV2>>()
  // 当前选中的单个ldap服务器的单个条目的信息(用来更新)
  let data_req_dir_update:Ref<{[key: string]: Array<string>|string}> = ref({})
  // 当前选中的单个ldap服务器的单个条目的objectClass(用来更新)
  let data_req_dir_objectClass_update:Ref<Array<string>> = ref([])
  // 树状图的高度
  let height_tree:number = window.innerHeight - 60 - 300;
  // 新增一个ldap服务器的临时数据
  let data_req_server_add:Ref<reqLdapSe> = ref({
    "server_name": "",
    "server_addr": "",
    "server_base": "",
    "server_auth_dn": "",
    "server_auth_passwd": "",
  })
  // 更新一个ldap服务器的临时数据
  let data_req_server_update:Ref<reqLdapSe> = ref({
    "server_name": "",
    "server_addr": "",
    "server_base": "",
    "server_auth_dn": "",
    "server_auth_passwd": "",
  })
  // 新增一个ldap条目的属性临时信息
  let data_req_dir_add:Ref<{[key: string]: Array<string>|string}> = ref({})
  // 新增一个ldap条目的ObjectClass临时信息
  let data_req_dir_objectClass_add:Ref<Array<string>> = ref(['top'])
  // 当前新增的dn的可选属性列表
  let create_dir_attrs_may:Ref<Array<string>> = ref([])
  // 当前新增的dn的必选属性列表
  let create_dir_attrs_must:Ref<Array<string>> = ref([])
  // 克隆当前dn的临时数据
  let data_req_dir_clone:Ref<reqLdapClone[]> = ref([])
  // 当前获取的ldif文本内容
  let data_res_dir_export:Ref<string> = ref("")
  const { text, copy, copied, isSupported } = useClipboard()

  // 当前选择的ldap服务器
  let select_server:Ref<string> = ref("")
  // 当前请求成功的ldap服务器
  let request_server:Ref<string> = ref("")
  // 当前展开的ldap服务器详细信息
  let select_server_collapse:Ref<string> = ref("")
  // 当前目录树多选的条目
  let select_tree_checkbox:Ref<Array<string>> = ref([])
  // 目录树的搜索框值
  let input_search_dir:Ref<string> = ref("")
  // 当前选中的单个ldap服务器的单个条目的信息
  let select_dir_info:Ref<{[key: string]: Array<string>|string}> = ref({})
  // 克隆当前dn时的参考数据
  let select_dir_clone:Ref<{[key: string]: Array<string>|string}> = ref({})
  // 当前选中的dn
  let select_dir_dn:Ref<string> = ref("")
  // 当前选中的dn的objectClass
  let select_dir_objectClass:Ref<Array<string>> = ref([])
  // 当前选中的dn的可选属性列表
  let select_dir_attrs_may:Ref<Array<string>> = ref([])
  // 当前选中的dn的比选属性列表
  let select_dir_attrs_must:Ref<Array<string>> = ref([])
  // 更新时用以搜索模板类下拉框的输入值
  let input_search_class:Ref<string> = ref("")
  // 更新时用以搜索属性下拉框的输入值
  let input_search_attrs:Ref<string> = ref("")
  // 创建单个条目时用以搜索模板类下拉框的输入值
  let input_search_class_add:Ref<string> = ref("")
  // 创建单个条目时用以搜索属性下拉框的输入值
  let input_search_attrs_add:Ref<string> = ref("")
  // 当前目录树搜索框的提示词
  let input_search_dir_txt:Ref<string> = ref("搜索关键字")
  // 新建单个dn时, dn的input框输入值
  let input_dn_add:Ref<string> = ref("")
  // 新建单个dn时, 锁死的后缀
  let input_dn_add_append:Ref<string> = ref("")
  // 克隆dn时, 锁死的前缀, 也就是命名属性
  let input_dn_clone_prepend:Ref<string> = ref("")
  // 克隆dn时, 锁死的后缀
  let input_dn_clone_append:Ref<string> = ref("")
  // 当前的命名属性
  let select_dn_mingming:Ref<string> = ref("")
  // 重命名dn时, 指定的命名属性值
  let input_dn_rename:Ref<string> = ref("")
  // 移动dn时, 指定的目录
  let select_ou_mv:Ref<string> = ref("")
  // 移动dn时, 指定的目录的命名属性
  let select_ou_mv_mingming:Ref<string> = ref("")
  // 用户输入的要上传的ldif内容
  let input_dn_upload:Ref<string> = ref("")

  // 加载所有ldap服务器的状态
  let load_servers_get:Ref<boolean> = ref(false)
  // 新增ldap服务器时的弹框状态
  let status_win_servers_add:Ref<boolean> = ref(false)
  // 当前选中服务器的详细信息
  let status_win_server_info:Ref<boolean> = ref(false)
  // 上半区ldap服务器的编辑状态
  let status_change_server:Ref<boolean> = ref(false)
  // 询问确认删除ldap服务器的弹框状态
  let status_ask_servers_delete:Ref<boolean> = ref(false)
  // 获取一个ldap服务器所有条目是否成功的状态
  let status_req_get_dir:Ref<boolean> = ref(true)
  // 单个条目是否正在被更改, 创建, 或删除
  let status_change_dir:Ref<boolean> = ref(false)
  // 目录树是否允许多选
  let status_tree_checkbox:Ref<boolean> = ref(false)
  // // 创建单个条目的状态
  // let status_change_dir:Ref<boolean> = ref(false)
  // 新增单个条目的弹窗状态
  let status_win_create_dir:Ref<boolean> = ref(false)
  // 批量新增多个条目的弹窗状态
  let status_win_create_dirs:Ref<boolean> = ref(false)
  // 删除当前选中的单个dn的弹窗状态
  let status_win_delete_dir_one:Ref<boolean> = ref(false)
  // 删除当前选中的多个dn的弹窗状态
  let status_win_delete_dir_more:Ref<boolean> = ref(false)
  // 克隆多个同级条目的弹框
  let status_win_clone_dir:Ref<boolean> = ref(false)
  // 重命名单个条目的弹框
  let status_win_rename_dir:Ref<boolean> = ref(false)
  // 移动单个条目的弹框
  let status_win_move_dir:Ref<boolean> = ref(false)
  // 移动条目时是否删除原条目
  let status_dir_delold:Ref<boolean> = ref(false)
  // 导出窗口的状态
  let status_win_export_dir:Ref<boolean> = ref(false)
  // 是否一并导出子条目
  let status_dir_export_tree:Ref<boolean> = ref(true)
  // 导出结果的右侧弹框
  let status_win_export_res:Ref<boolean> = ref(false)
  // 导入ldif的弹框
  let status_win_load_dir:Ref<boolean> = ref(false)
  // 导入的按钮的状态
  let status_btn_load:Ref<boolean> = ref(false)
  // 是否强制覆盖导入
  let status_load_force:Ref<boolean> = ref(false)
  // 帮助页面的状态
  let status_win_help:Ref<boolean> = ref(false)


  def_servers_get()

  // 打开帮助页面的前置动作
  function def_help_before() {

    status_win_help.value = true
  }

  // 还原更新一个ldap服务器数据的操作
  function def_init_server_update() {
    // data_req_server_update.value = {...data_res_servers.value[request_server.value]}
    data_req_server_update.value = deepClone(data_res_servers.value[select_server.value])
    // console.log("当前选定的服务器信息: ", data_req_server_update.value)
  }

  // 点击克隆按钮的前期准备工作
  function def_dir_clone_init() {
    // 先让按钮转圈
    status_change_dir.value = true
    // 提取克隆用的参考值
    select_dir_clone.value = deepClone(select_dir_info.value)
    // 提取前后缀
    input_dn_clone_prepend.value = select_dir_dn.value.split('=')[0]
    input_dn_clone_append.value = select_dir_dn.value.split(',').slice(1).join(',')
    // 获取修正后的属性信息
    let dn_attrs_new = def_dir_clone_format()
    // 向列表内装填一行初始数据, 以当前选中的dn的数据为基准
    data_req_dir_clone.value= [{
      attrs: dn_attrs_new,
      dn: "",
      // 这里之前是放了dn的命名属性的值, 但是考虑后改为空值
      dn_v: "",
    }]
    // 置空更新用的搜索框
    input_search_attrs.value = ""
    // 最后打开窗口
    status_win_clone_dir.value = true
    status_change_dir.value = false
  }
  // 在克隆窗口新增一行数据
  function def_dir_clone_addline() {
    // 获取修正后的属性信息
    let dn_attrs_new = def_dir_clone_format()
    // 向列表内追加一行初始数据, 以当前选中的dn的数据为基准
    data_req_dir_clone.value.push({
      attrs: dn_attrs_new,
      dn: "",
      dn_v: "",
    })
  }

  // 克隆时修整已有属性列表已经对应值的函数
  function def_dir_clone_format() {
    // 提取当前选中dn的命名属性的值
    let dn_value = select_dir_dn.value.split(',')[0].split('=')[1]
    // 将命名属性中与原dn中值一样的值置空
    let dn_attrs = deepClone(select_dir_info.value) as { [p: string]: string | string[] }
    for ( let k in dn_attrs) {
      // 找到属性
      if (k==input_dn_clone_prepend.value) {
        if (Array.isArray(dn_attrs[k])) {
          for (let [index, kk] of dn_attrs[k].entries()) {
            // 改变相等的值
            if (kk == dn_value) {
              dn_attrs[k][index] = ""
            }
          }
        } else {
          // 单值直接改变
          dn_attrs[k] = ""
        }
      }
    }
    return dn_attrs
  }

  // 重命名一个dn时做的准备工作
  function def_serverdir_rename_before() {
    // 置空
    input_dn_rename.value = ""
    // 开启弹框
    status_win_rename_dir.value = true
  }

  // 移动或复制一个dn是做的准备工作
  function def_serverdir_move_before() {
    // 给个默认值
    input_dn_rename.value = select_dir_dn.value.split(",")[0].split("=")[1]
    // 开启弹框
    status_win_move_dir.value = true
  }

  // 选择的ldap服务器发生变化时的动作
  function def_server_changed() {
    console.log("更换了ldap服务器")
    // 临时装填update的数据
    def_init_server_update()
  }
  // 取消更改ldap服务器时的动作
  function def_server_update_cancel() {
    status_change_server.value = false
    // 覆盖回初始的数据
    def_init_server_update()
  }

  // 查询所有的ldap服务器
  async function def_servers_get() {
    load_servers_get.value = true
    try {
      let data_res_tmp = await getServer('/api/devops/ldapserver/conn/getall', {ok: "ok"})
      data_res_servers.value = data_res_tmp  as resLdapSeObj
      // console.log("请求完成一次ldapserver", data_res_servers.value)
    } catch (e) {

    }
    load_servers_get.value = false
  }
  // 新增一个ldap服务器
  async function def_servers_add() {
    load_servers_get.value = true
    try {
      await getServer('/api/devops/ldapserver/conn/add', data_req_server_add.value)
      // 新增成功就再刷新一次数据
      data_res_servers.value = await getServer('/api/devops/ldapserver/conn/getall', {ok: "ok"})  as resLdapSeObj
      // 关闭新增框
      status_win_servers_add.value = false
      global_window("success", "新增 '"+data_req_server_add.value.server_name+"' 成功")
    } catch (e) {
    }
    load_servers_get.value = false
  }
  // 更新一个ldap服务器
  async function def_servers_update() {
    load_servers_get.value = true
    try {
      await getServer('/api/devops/ldapserver/conn/update', data_req_server_update.value)
      // 更新成功就再刷新一次数据
      data_res_servers.value = await getServer('/api/devops/ldapserver/conn/getall', {ok: "ok"})  as resLdapSeObj
      // 取消更新状态
      def_server_update_cancel()
      global_window("success", "更新 '"+select_server.value+"' 成功")
    } catch (e) {
    }
    load_servers_get.value = false
  }
  // 删除一个ldap服务器
  async function def_servers_delete() {
    load_servers_get.value = true
    try {
      await getServer('/api/devops/ldapserver/conn/delete', {"server_name": select_server.value})
      // 更新成功就再刷新一次数据
      data_res_servers.value = await getServer('/api/devops/ldapserver/conn/getall', {ok: "ok"})  as resLdapSeObj
      // 关闭弹窗
      status_ask_servers_delete.value = false
      // 取消选中状态
      select_server.value = ''
      global_window("success", "删除 '"+select_server.value+"' 成功")
    } catch (e) {
    }
    load_servers_get.value = false
  }

  // 向后端请求单个ldap服务器的数据
  async function def_serverdata_api() {
    let data_res_tmp = await getServer('/api/devops/ldapserver/obj/getall', {server_name: select_server.value}) as resLdapAll
    request_server.value = select_server.value
    data_res_serverdirTree.value = data_res_tmp.obj_tree
    data_res_serverdirInfo.value = data_res_tmp.obj_info
    data_res_serverclass.value = data_res_tmp.class
    data_res_serverattrs.value = data_res_tmp.attrs
    data_res_serverbase.value = data_res_tmp.dn_base
  }

  // 查询ldap服务器的所有信息
  async function def_serverdata_get() {
    load_servers_get.value = true
    try {
      // let data_res_tmp = await getServer('/api/devops/ldapserver/obj/getall', {server_name: select_server.value}) as resLdapAll
      // request_server.value = select_server.value
      // data_res_serverdir.value = data_res_tmp.obj
      // data_res_serverclass.value = data_res_tmp.class
      // data_res_serverattrs.value = data_res_tmp.attrs
      // data_res_serverbase.value = data_res_tmp.dn_base
      await def_serverdata_api()
      // console.log("请求完成一次ldapserver", data_res_servers.value)
      global_window("success", "成功获取 '"+request_server.value+"' 的数据")
      // 置空当前选择的dn
      select_dir_dn.value = ""
      select_dn_mingming.value = ""
      status_req_get_dir.value = true
    } catch (e) {
      select_dir_dn.value = ""
      status_req_get_dir.value = false
    }
    load_servers_get.value = false
  }
  
  // 更新一条dn
  async function def_serverdir_update() {
    load_servers_get.value = true
    status_change_dir.value = true
    // 组合数据
    let data_update = {
      server_name: request_server.value,
      dn: select_dir_dn.value,
      objectClass: data_req_dir_objectClass_update.value,
      attrs: data_req_dir_update.value,
    }
    // 检查
    def_check_dir_update()
    // 执行更新
    try {
      await getServer('/api/devops/ldapserver/obj/update', data_update)
      global_window("success", "成功更新 '"+select_dir_dn.value+"' ")
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }

    try {
      // 再获取一次当前服务器数据
      await def_serverdata_api()
      // let data_res_tmp = await getServer('/api/devops/ldapserver/obj/getall', {server_name: request_server.value}) as resLdapAll
      // data_res_serverdir.value = data_res_tmp.obj
      // data_res_serverclass.value = data_res_tmp.class
      // data_res_serverattrs.value = data_res_tmp.attrs
      // data_res_serverbase.value = data_res_tmp.dn_base
      // console.log("请求完成一次ldapserver", data_res_servers.value)
      // global_window("success", "成功更新 '"+select_dir_dn.value+"' ")
      // 置空当前选择的dn
      // select_dir_dn.value = ""
      // 再触发一次选择新建的dn
      // def_dir_click_tmp(select_dir_dn.value)
      // tree_ldapdir.value?.setCheckedKeys([select_dir_dn.value])
      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }
    load_servers_get.value = false
    status_change_dir.value = false
    // 再触发一次选择新建的dn, 在try内会导致过早触发导致点击不到数据
    await sleep(2000)
    def_dir_click_tmp(select_dir_dn.value)
  }

  // 新增一条dn
  async function def_serverdir_add() {
    load_servers_get.value = true
    status_change_dir.value = true
    // 新dn
    let dn_new = input_dn_add.value + input_dn_add_append.value
    // 拼装数据
    let data_add = {
      server_name: request_server.value,
      objectClass: data_req_dir_objectClass_add.value,
      dirs: [
          {dn: dn_new, attrs: data_req_dir_add.value}
      ]
    }
    // 检查
    def_check_dir_add()
    // 请求新增
    try {
      console.log("新增的dn: ", dn_new, data_add)
      await getServer('/api/devops/ldapserver/obj/add', data_add)
      global_window("success", "成功新增dn '"+dn_new+"' ")
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }
    try {
      // 获取一次当前服务器数据
      await def_serverdata_api()
      // let data_res_tmp = await getServer('/api/devops/ldapserver/obj/getall', {server_name: request_server.value}) as resLdapAll
      // data_res_serverdir.value = data_res_tmp.obj
      // data_res_serverclass.value = data_res_tmp.class
      // data_res_serverattrs.value = data_res_tmp.attrs
      // data_res_serverbase.value = data_res_tmp.dn_base
      // console.log("请求完成一次ldapserver", data_res_servers.value)
      // global_window("success", "成功更新 '"+select_dir_dn.value+"' ")
      // 置空当前选择的dn
      // select_dir_dn.value = ""
      // 再触发一次选择当前的dn
      // def_dir_click_tmp(dn_new)
      // tree_ldapdir.value?.setCheckedKeys([dn_new])
      // tree_ldapdir.value?.setCurrentKey(dn_new)
      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }

    load_servers_get.value = false
    status_change_dir.value = false
    // 再触发一次选择新建的dn, 在try内会导致过早触发导致点击不到数据
    def_dir_click_tmp(dn_new)
  }

  // 克隆多条dn
  async function def_serverdir_clone() {
    load_servers_get.value = true
    status_change_dir.value = true

    // 拼凑新条目的dn
    data_req_dir_clone.value.forEach((value, index, array) => {
      value.dn = `${input_dn_clone_prepend.value}=${value.dn_v},${input_dn_clone_append.value}`
    });

    // 拼装数据
    let data_add = {
      server_name: request_server.value,
      objectClass: select_dir_objectClass.value,
      dirs: data_req_dir_clone.value
    }
    // await sleep(3000)
    // 检查
    def_check_dir_clone()
    // return
    // 请求新增
    try {
      // console.log("新增的dn: ", dn_new, data_add)
      await getServer('/api/devops/ldapserver/obj/add', data_add)
      global_window("success", "成功新增 "+data_req_dir_clone.value.length+" 条dn")
      status_win_clone_dir.value = false
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }
    try {
      // 获取一次当前服务器数据
      await def_serverdata_api()

      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }

    load_servers_get.value = false
    status_change_dir.value = false
  }

  // 删除多条dn
  async function def_serverdir_delete(list_dn:Array<string>) {
    load_servers_get.value = true
    status_change_dir.value = true
    
    // 组合数据
    let data_delete = {
      server_name: request_server.value,
      list_dn: list_dn,
    }
    // 检查
    def_check_dir_delete(list_dn)
    // 执行删除
    try {
      await getServer('/api/devops/ldapserver/obj/delete', data_delete)
      global_window("success", "删除成功")
      status_win_delete_dir_one.value = false
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }

    try {
      // 再获取一次当前服务器数据
      await def_serverdata_api()
      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }
    load_servers_get.value = false
    status_change_dir.value = false
    // 如果之前被选中的dn在被删除的dn列表中, 则清空编辑区, 否则重新选取
    if (list_dn.includes(select_dir_dn.value)) {
      select_dir_dn.value = ""
    } else {
      def_dir_click_tmp(select_dir_dn.value)
    }
  }

  // 重命名dn
  async function def_serverdir_rename() {
    load_servers_get.value = true
    status_change_dir.value = true

    // 拼凑新条目的命名属性
    let relative_dn = input_dn_clone_prepend.value+"="+input_dn_rename.value
    let dn_new = relative_dn+","+input_dn_clone_append.value

    // 拼装数据
    let data_add = {
      server_name: request_server.value,
      dn: select_dir_dn.value,
      relative_dn: relative_dn,
      superior: input_dn_clone_append.value,
      delete_old_dn: true
    }
    // await sleep(3000)
    // 检查
    def_check_dir_rename()
    // return
    // 请求新增
    try {
      // console.log("新增的dn: ", dn_new, data_add)
      await getServer('/api/devops/ldapserver/obj/move', data_add)
      global_window("success", "成功更名为 "+relative_dn+","+input_dn_clone_append.value)
      status_win_rename_dir.value = false
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }
    try {
      // 获取一次当前服务器数据
      await def_serverdata_api()
      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }
    // 再触发一次选择新的dn
    def_dir_click_tmp(dn_new)

    load_servers_get.value = false
    status_change_dir.value = false
  }

  // 移动或复制dn
  async function def_serverdir_move(copy:boolean=true) {
    load_servers_get.value = true
    status_change_dir.value = true

    // 拼凑新条目的命名属性
    let relative_dn = input_dn_clone_prepend.value+"="+input_dn_rename.value
    // 拼凑新的dn
    let new_dn = relative_dn+","+input_dn_clone_append.value

    // 拼装数据
    let data_add = {
      server_name: request_server.value,
      dn: select_dir_dn.value,
      relative_dn: relative_dn,
      superior: select_ou_mv.value,
      delete_old_dn: status_dir_delold.value
    }
    // await sleep(3000)
    // 检查
    def_check_dir_move()
    // return
    // 请求新增
    try {
      // console.log("新增的dn: ", dn_new, data_add)
      await getServer('/api/devops/ldapserver/obj/move', data_add)
      global_window("success", "成功新建 "+new_dn)
      status_win_move_dir.value = false
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }
    try {
      // 获取一次当前服务器数据
      await def_serverdata_api()
      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }
    // 再触发一次选择新的dn
    def_dir_click_tmp(new_dn)

    load_servers_get.value = false
    status_change_dir.value = false
  }

  // 导入dn
  async function def_serverdir_load() {
    load_servers_get.value = true
    status_change_dir.value = true
    status_btn_load.value = true

    // 拼装数据
    let data_add = {
      server_name: request_server.value,
      ldif: input_dn_upload.value,
      force: status_load_force.value,
    }
    // await sleep(3000)
    // 检查
    // def_check_dir_move()
    // return
    // 请求新增
    try {
      // console.log("新增的dn: ", dn_new, data_add)
      await getServer('/api/devops/ldapserver/obj/upload', data_add)
      global_window("success", "成功导入 ")
      // status_win_load_dir.value = false
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      status_btn_load.value = false
      return
    }
    try {
      // 获取一次当前服务器数据
      await def_serverdata_api()
      status_req_get_dir.value = true
    } catch (e) {
      status_req_get_dir.value = false
    }
    // 再触发一次选择新的dn
    // def_dir_click_tmp(new_dn)
    status_btn_load.value = false
    load_servers_get.value = false
    status_change_dir.value = false
  }

  // 导出dn
  async function def_serverdir_export() {
    load_servers_get.value = true
    status_change_dir.value = true

    // 拼装数据
    let data_export = {
      server_name: request_server.value,
      dn: select_dir_dn.value,
      export_tree: status_dir_export_tree.value
    }

    // 请求新增
    try {
      // console.log("新增的dn: ", dn_new, data_add)
      let tmp_export = await getServer('/api/devops/ldapserver/obj/export', data_export)
      data_res_dir_export.value = tmp_export as string
      status_win_export_dir.value = false
      status_win_export_res.value = true
    } catch (e) {
      load_servers_get.value = false
      status_change_dir.value = false
      return
    }

    load_servers_get.value = false
    status_change_dir.value = false
  }

  // 移动或复制dn前的检查
  function def_check_dir_move() {
    let el = ""
    // 选定的目标目录不能是当前的目录
    if (select_ou_mv.value==input_dn_clone_prepend.value) {
      el = "不能选定当前的父条目"
    }
    // 必须选择一个目录
    if (!select_ou_mv.value) {
      el = "你还没选择要迁移到的父条目"
    }

    if (el) {
      global_window("error", el)
      load_servers_get.value = false
      status_change_dir.value = false
      throw new Error(el)
    }
  }

  // 重命名前的数据校验
  function def_check_dir_rename() {
    let el = ""
    // 命名属性的新值不能为空
    if (!input_dn_rename.value) {
      el = "命名属性的值不能为空"
    }

    if (el) {
      global_window("error", el)
      load_servers_get.value = false
      status_change_dir.value = false
      throw new Error(el)
    }
  }

  // 更新dn前的数据校验
  function def_check_dir_update() {
    let el = ""
    // 检查objectClass中是否至少含有一个结构化对象类
    let n_class = 0
    for (let i of data_req_dir_objectClass_update.value) {
      if (data_res_serverclass.value[i].kind=='STRUCTURAL') {
        n_class += 1
      }
    }
    if (n_class==0) {
      el = "至少选择一个结构化对象类"
    }
    // 有报错就终止
    if (el) {
      global_window("error", el)
      load_servers_get.value = false
      status_change_dir.value = false
      throw new Error(el)
    }
  }
  // 新增一条dn前的数据校验
  function def_check_dir_add() {
    let el = ""
    // 检查objectClass中是否至少含有一个结构化对象类
    let n_class = 0
    for (let i of data_req_dir_objectClass_add.value) {
      if (data_res_serverclass.value[i].kind=='STRUCTURAL') {
        n_class += 1
      }
    }
    if (n_class==0) {
      el = "至少选择一个结构化对象类"
    }
    // 检查dn
    if (!input_dn_add.value) {
      el = "未输入有效的dn"
    }
    // 有报错就终止
    if (el) {
      global_window("error", el)
      load_servers_get.value = false
      status_change_dir.value = false
      throw new Error(el)
    }
  }
  // 删除一条dn前的数据校验
  function def_check_dir_delete(list_dn:Array<string>) {
    let el = ""
    // 数量不能为0
    if (list_dn.length==0) {
      el = "至少选中一个dn再删除"
    }
    // dn不能为空
    for (let dn of list_dn) {
      if (!dn) {
        el = "删除列表中有dn为空"
        break
      }
    }
    // 有报错就终止
    if (el) {
      global_window("error", el)
      load_servers_get.value = false
      status_change_dir.value = false
      throw new Error(el)
    }
  }
  // 克隆dn前的数据校验
  function def_check_dir_clone() {
    let el = ""
    // 对列表循环
    for (let k of data_req_dir_clone.value) {
      // dn的输入值不能为空
      if (!k.dn_v) {
        el = "有dn的命名属性为空"
        break
      }
      // 循环属性值
      for (let [attr, attr_info] of Object.entries(k.attrs)) {
        // 对单值的命名属性的值做校验
        if (attr==k.dn_v && !Array.isArray(attr_info)) {
          if (attr_info != k.dn_v) {
            el = `${k.dn} 中的单值命名属性 ${attr} 的值于dn中的值 ${k.dn_v} 不一致`
          }
        }
      }
    }
    // 有报错就终止
    if (el) {
      global_window("error", el)
      load_servers_get.value = false
      status_change_dir.value = false
      throw new Error(el)
    }
  }

  // 对树节点进行筛选的值改变时调用的方法
  function def_search_dir_changed(query: string) {
    return tree_ldapdir.value!.filter(query)
  }

  // 对树节点进行筛选时执行的方法
  function tree_filterMethod(query: string, node: TreeNodeData) {
    return node.entry!.includes(query)
  }

  // 主页面点击目录树中其中一个条目时触发的动作
  function def_dir_click(data: TreeNodeData, node: TreeNode, e: MouseEvent) {
    // console.log("tree传入了: ", node)
    def_dir_click_action(node.key.toString())
  }
  // 移动一个dn时选取目的条目时的点击动作
  function def_dir_click_move(data: TreeNodeData, node: TreeNode, e: MouseEvent) {
    select_ou_mv.value = node.key.toString()
    if (select_ou_mv.value==data_res_serverbase.value) {
      select_ou_mv_mingming.value = deepClone(data_res_serverbase.value)
    } else {
      select_ou_mv_mingming.value = select_ou_mv.value.split(',')[0]
    }

  }
  // 更改编辑区和操作区的数据
  function def_dir_click_action(dn: string) {
    console.log("点击dn: ", dn)
    // console.log("node: ", node)
    if (Object.keys(data_res_serverdirInfo.value).includes(dn)) {
      let tmp_attrs = data_res_serverdirInfo.value[dn].attrs
      let tmp_class = data_res_serverdirInfo.value[dn].objectClass
      // 更新当前属性的值的信息
      select_dir_info.value = deepClone(tmp_attrs)
      data_req_dir_update.value = deepClone(tmp_attrs)
      // 更新当前条目的模板类列表
      select_dir_objectClass.value = deepClone(tmp_class)
      data_req_dir_objectClass_update.value = deepClone(tmp_class)
      // console.log("data_req_dir_objectClass_update: ",data_req_dir_objectClass_update.value)
      // 更新选中条目的dn
      select_dir_dn.value = dn
      // 提取前后缀
      input_dn_clone_prepend.value = dn.split('=')[0]
      input_dn_clone_append.value = dn.split(',').slice(1).join(',')
      // 命名属性, 用来确定高亮当前选中
      if (select_dir_dn.value==data_res_serverbase.value) {
        select_dn_mingming.value = deepClone(data_res_serverbase.value)
      } else {
        select_dn_mingming.value = select_dir_dn.value.split(',')[0]
      }
      // select_dn_mingming.value = dn.split(',')[0]
      // 更新当前条目可选的属性和必选的属性
      def_dir_update_attrs(tmp_class)
    } else {
      select_dir_dn.value = ""
      console.log("当前数据中没有焦点: ", dn)
    }

  }

  // 多选目录树的值发生变化时 (也就是更改了中间的编辑区)
  function def_dir_changed_checkbox(data: TreeNodeData, info: { checkedKeys: TreeKey[],checkedNodes: TreeData, halfCheckedKeys: TreeKey[], halfCheckedNodes: TreeData,}) {
    // console.log("选中的值发生了变化data: ", data)
    // console.log("选中的值发生了变化data: ", info)
    select_tree_checkbox.value = info.checkedKeys as Array<string>
  }
  // const cpd_isChange_dir = computed(() => console.log(
  //     select_dir_info.value == data_req_dir_update.value
  //     && select_dir_objectClass.value == data_req_dir_objectClass_update.value
  // ))
  let cpd_isChange_dir = computed(() => {
      // console.log("触发计算: ", JSON.stringify(select_dir_info.value) === JSON.stringify(data_req_dir_update.value))
    // console.log("触发计算: ", select_dir_info.value === data_req_dir_update.value)
      return JSON.stringify(select_dir_info.value) === JSON.stringify(data_req_dir_update.value) &&
        JSON.stringify(select_dir_objectClass.value) === JSON.stringify(data_req_dir_objectClass_update.value)
    //     return select_dir_info.value === data_req_dir_update.value
    //     && select_dir_objectClass.value === data_req_dir_objectClass_update.value
    }
  )
  // 选中的条目的指定列表属性新增一个值
  function def_dir_addline(attr_name:string) {
    if (Array.isArray(data_req_dir_update.value[attr_name])) {
      data_req_dir_update.value[attr_name].push("");
    }
  }
  // 新增一个条目时, 条目的指定列表属性新增一个值
  function def_dir_addline_add(attr_name:string) {
    if (Array.isArray(data_req_dir_add.value[attr_name])) {
      data_req_dir_add.value[attr_name].push("");
    }
  }
  // 选中的条目的指定列表属性删除一个值
  function def_dir_delline(attr_name:string, index:number) {
    if (Array.isArray(data_req_dir_update.value[attr_name])) {
      console.log(attr_name, "删除值", index)
      data_req_dir_update.value[attr_name].splice(index, 1);
    }
  }
  // 新增一个条目时, 条目的指定列表属性删除一个值
  function def_dir_delline_add(attr_name:string, index:number) {
    if (Array.isArray(data_req_dir_add.value[attr_name])) {
      console.log(attr_name, "删除值", index)
      data_req_dir_add.value[attr_name].splice(index, 1);
    }
  }
  // 选中的条目新增一个指定模板类
  function def_dir_addclass(command: string) {
    status_change_dir.value = true
    console.log("更新条目时新增模板类: ", command)
    data_req_dir_objectClass_update.value.push(command)

    // 更新当前条目可选的属性和必选的属性
    def_dir_update_attrs(data_req_dir_objectClass_update.value)

    // 如果当前的属性里面没有刚新增的模板的必选属性, 就新增
    let list_tmp_add = []
    for (let i of select_dir_attrs_must.value) {
      if (!Object.keys(data_req_dir_update.value).includes(i)) {
        def_dir_addattr(i)
        list_tmp_add.push(i)
      }
    }
    if (list_tmp_add.length>0) {
      global_window("warning", "为你自动添加了新的必选属性: "+list_tmp_add)
    }
    status_change_dir.value = false
  }
  // 新增的单个条目新增一个指定模板类
  function def_dir_addclass_add(command: string) {
    status_change_dir.value = true
    console.log("创建条目时新增模板类: ", command)
    data_req_dir_objectClass_add.value.push(command)

    // 更新当前条目可选的属性和必选的属性
    def_dir_update_attrs_add(data_req_dir_objectClass_add.value)

    // 如果当前的属性里面没有刚新增的模板的必选属性, 就新增
    let list_tmp_add = []
    for (let i of create_dir_attrs_must.value) {
      if (!Object.keys(data_req_dir_add.value).includes(i)) {
        def_dir_addattr_add(i)
        list_tmp_add.push(i)
      }
    }
    if (list_tmp_add.length>0) {
      global_window("warning", "为你自动添加了新的必选属性: "+list_tmp_add)
    }
    status_change_dir.value = false
  }
  // 选中的条目删除一个指定模板类
  function def_dir_delclass(class_index:number) {
    // 删除指定下标的class模板
    data_req_dir_objectClass_update.value.splice(class_index,1)

    // 更新当前条目可选的属性和必选的属性
    def_dir_update_attrs(data_req_dir_objectClass_update.value)
    // console.log("删除class后的may: ", select_dir_attrs_may.value)
    // 删除当前条目详细信息里不在可选属性列表的属性
    let list_tmp_del = []
    for (let k in data_req_dir_update.value) {
      if (!select_dir_attrs_may.value.includes(k)) {
        delete data_req_dir_update.value[k]
        list_tmp_del.push(k)
      }
    }
    if (list_tmp_del.length>0) {
      global_window("warning", "为你自动删除该objectClass独有的属性: "+list_tmp_del)
    }
  }
  // 新增条目时删除一个指定模板类
  function def_dir_delclass_add(class_index:number) {
    // 删除指定下标的class模板
    data_req_dir_objectClass_add.value.splice(class_index,1)

    // 更新当前条目可选的属性和必选的属性
    def_dir_update_attrs_add(data_req_dir_objectClass_add.value)
    // console.log("删除class后的may: ", select_dir_attrs_may.value)
    // 删除当前条目详细信息里不在可选属性列表的属性
    let list_tmp_del = []
    for (let k in data_req_dir_add.value) {
      if (!create_dir_attrs_may.value.includes(k)) {
        delete data_req_dir_add.value[k]
        list_tmp_del.push(k)
      }
    }
    if (list_tmp_del.length>0) {
      global_window("warning", "为你自动删除该objectClass独有的属性: "+list_tmp_del)
    }
  }


  // 筛选可选模板类的计算函数(更新现有条目)
  const filter_show_class = computed(() =>
      Object.keys(data_res_serverclass.value).filter(
          (data) =>
              !input_search_class.value || data.toLowerCase().includes(input_search_class.value.toLowerCase())
          // console.log(select_date_work.value, data.date_work)
      )
  )
  // 筛选可选模板类的计算函数(创建单个条目)
  const filter_show_class_add = computed(() =>
      Object.keys(data_res_serverclass.value).filter(
          (data) =>
              !input_search_class_add.value || data.toLowerCase().includes(input_search_class_add.value.toLowerCase())
          // console.log(select_date_work.value, data.date_work)
      )
  )
  // 选中的条目新增一个指定属性
  function def_dir_addattr(command: string) {
    status_change_dir.value = true
    console.log("更新条目时新增属性: ", command)
    // console.log("当前所有属性: ", data_res_serverattrs.value)
    if (data_res_serverattrs.value[command].attr_isSingle) {
      // 如果为是, 则说明该属性不允许多值
      data_req_dir_update.value[command] = ''
    } else {
      // 否, 则赋予列表
      data_req_dir_update.value[command] = ['']
    }
    status_change_dir.value = false
  }
  // 新增一个条目时新增一个指定属性
  function def_dir_addattr_add(command: string) {
    status_change_dir.value = true
    console.log("创建条目时新增属性: ", command)
    // console.log("当前所有属性: ", data_res_serverattrs.value)
    if (data_res_serverattrs.value[command].attr_isSingle) {
      // 如果为是, 则说明该属性不允许多值
      data_req_dir_add.value[command] = ''
    } else {
      // 否, 则赋予列表
      data_req_dir_add.value[command] = ['']
    }
    status_change_dir.value = false
  }
  // 克隆一个条目时新增一个指定属性
  function def_dir_addattr_clone(command: string) {
    status_change_dir.value = true
    console.log("创建条目时新增属性: ", command)
    // console.log("当前所有属性: ", data_res_serverattrs.value)
    let v
    if (data_res_serverattrs.value[command].attr_isSingle) {
      // 如果为是, 则说明该属性不允许多值
      v = ''
    } else {
      // 否, 则赋予列表
      v = ['']
    }
    // 为所有行新增值, 为了显示列中的input框
    for (let [i, k] of data_req_dir_clone.value.entries()) {
      data_req_dir_clone.value[i].attrs[command] = v
    }
    // 为模板新增, 为了显示新的列
    select_dir_clone.value[command] = v
    status_change_dir.value = false
  }

  // 筛选更新时可选属性的计算函数
  const filter_show_attrs = computed(() =>
      select_dir_attrs_may.value.filter(
          (data) =>
              !input_search_attrs.value || data.toLowerCase().includes(input_search_attrs.value.toLowerCase())
          // console.log(select_date_work.value, data.date_work)
      )
  )
  // 筛选新增单个条目时可选属性的计算函数
  const filter_show_attrs_add = computed(() =>
      create_dir_attrs_may.value.filter(
          (data) =>
              !input_search_attrs_add.value || data.toLowerCase().includes(input_search_attrs_add.value.toLowerCase())
          // console.log(select_date_work.value, data.date_work)
      )
  )
  // 选中的条目删除一个指定属性
  function def_dir_delattr(attr_name:string) {
    status_change_dir.value = true
    // if (Array.isArray(data_req_dir_update.value[attr_name])) {
    //   console.log(select_dir_dn.value, "删除属性", attr_name)
    //   delete data_req_dir_update.value[attr_name];
    // }
    if (select_dir_attrs_must.value.includes(attr_name)) {
      global_window("error", "不允许删除必要属性")
    } else {
      delete data_req_dir_update.value[attr_name];
    }
    status_change_dir.value = false
  }
  // 新增一个条目时删除一个指定属性
  function def_dir_delattr_add(attr_name:string) {
    status_change_dir.value = true
    // if (Array.isArray(data_req_dir_update.value[attr_name])) {
    //   console.log(select_dir_dn.value, "删除属性", attr_name)
    //   delete data_req_dir_update.value[attr_name];
    // }
    if (create_dir_attrs_must.value.includes(attr_name)) {
      global_window("error", "不允许删除必要属性")
    } else {
      delete data_req_dir_add.value[attr_name];
    }
    status_change_dir.value = false
  }
  // 克隆一个条目时删除一个指定属性
  function def_dir_delattr_clone(attr_name:string) {
    status_change_dir.value = true
    // if (Array.isArray(data_req_dir_update.value[attr_name])) {
    //   console.log(select_dir_dn.value, "删除属性", attr_name)
    //   delete data_req_dir_update.value[attr_name];
    // }
    if (select_dir_attrs_must.value.includes(attr_name)) {
      global_window("error", "不允许删除必要属性")
    } else {
      // 为所有行删除属性, 为了显示列中的input框
      for (let [i, k] of data_req_dir_clone.value.entries()) {
        delete data_req_dir_clone.value[i].attrs[attr_name]
      }
      // 将模板的列删除, 为了不显示这个列
      delete select_dir_clone.value[attr_name]
    }
    status_change_dir.value = false
  }
  // 取消更改一个条目, 还原数据
  function def_dir_change_cancel() {
    status_change_dir.value = true
    data_req_dir_update.value = deepClone(select_dir_info.value)
    data_req_dir_objectClass_update.value = deepClone(select_dir_objectClass.value)
    status_change_dir.value = false
  }

  // 更新可选字段列表和必选字段列表(更新现有条目)
  function def_dir_update_attrs(list_class:Array<string>) {
    status_change_dir.value = true
    // 重置当前条目可选的属性
    select_dir_attrs_may.value = []
    for (let i of list_class) {
      // console.log("tem_may_list: ", data_res_serverclass.value[i])
      select_dir_attrs_may.value = [...new Set(select_dir_attrs_may.value.concat(data_res_serverclass.value[i].tem_may_list))]
    }
    // 重置当前条目必选的属性
    select_dir_attrs_must.value = []
    for (let i of list_class) {
      select_dir_attrs_must.value = [...new Set(select_dir_attrs_must.value.concat(data_res_serverclass.value[i].tem_must_list))]
    }
    // 去掉objectClass属性
    select_dir_attrs_must.value = select_dir_attrs_must.value.filter(item => item !== 'objectClass')
    select_dir_attrs_may.value = select_dir_attrs_may.value.filter(item => item !== 'objectClass')
    status_change_dir.value = false
  }
  // 更细可选字段列表和必选字段列表(创建新条目)
  function def_dir_update_attrs_add(list_class:Array<string>) {
    status_change_dir.value = true
    // 重置当前条目可选的属性
    create_dir_attrs_may.value = []
    for (let i of list_class) {
      // console.log("tem_may_list: ", data_res_serverclass.value[i])
      create_dir_attrs_may.value = [...new Set(create_dir_attrs_may.value.concat(data_res_serverclass.value[i].tem_may_list))]
    }
    // 重置当前条目必选的属性
    create_dir_attrs_must.value = []
    for (let i of list_class) {
      create_dir_attrs_must.value = [...new Set(create_dir_attrs_must.value.concat(data_res_serverclass.value[i].tem_must_list))]
    }
    // 去掉objectClass属性
    create_dir_attrs_must.value = create_dir_attrs_must.value.filter(item => item !== 'objectClass')
    create_dir_attrs_may.value = create_dir_attrs_may.value.filter(item => item !== 'objectClass')
    status_change_dir.value = false
  }

  // 开启目录树多选
  function def_tree_on() {
    // 清空筛选, 只有在已筛选时才置空, 不然会直接展开所有节点
    if (input_search_dir.value) {
      input_search_dir.value = ""
      def_search_dir_changed(input_search_dir.value)
    }
    // 清空已选列表
    select_tree_checkbox.value = []
    tree_ldapdir.value!.setCheckedKeys([])
    // 打开
    status_tree_checkbox.value = true
    input_search_dir_txt.value = "多选时禁止搜索"
  }
  // 关闭目录树多选
  function def_tree_off() {
    // 清空已选列表
    select_tree_checkbox.value = []
    tree_ldapdir.value!.setCheckedKeys([])
    input_search_dir_txt.value = "搜索关键字"
    // 打开
    status_tree_checkbox.value = false
  }
  // 点击新增一个条目时触发的动作
  function def_dir_add_before() {
    // 先确定dn的后缀和前缀
    input_dn_add_append.value = ',' + data_res_serverbase.value
    // 激活弹窗
    status_win_create_dir.value = true
  }
  // 目录树的各属性映射
  const props_ldapdir = {
    value: 'dn',
    label: 'entry',
    children: 'children',
    objectClass: 'objectClass',
  }

  // 手动触发点击目录树的某节点
  function def_dir_click_tmp(dn:string) {
    // console.log("tree当前引用的数据: ", dn, data_res_serverdirTree.value)
    // let dir_data = tree_ldapdir.value?.getNode(dn)
    console.log("即将切换至焦点: ", dn)
    // if (dir_data) {
    //   def_dir_click_action(dn)
    //   console.log("已手动切换焦点: ", dir_data?.key)
    // }
    def_dir_click_action(dn)
    console.log("已手动切换焦点: ", dn)
  }

  // 测试触发点击某指定节点
  function def_test_click() {
    // tree_ldapdir?.setCurrentKey('ou=daoqi,dc=teyvat,dc=com')
    let dir_data = tree_ldapdir.value?.getNode('ou=daoqi,dc=teyvat,dc=com')
    if (dir_data) {
      def_dir_click_action('ou=daoqi,dc=teyvat,dc=com')
      console.log("手动切换焦点: ", dir_data?.key)
    }
  }

  // 复制导出的ldif
  function def_dir_export_copy() {
    // console.log(isSupported)
    copy(data_res_dir_export.value)

    if (copied) {
      window_right("success", "已复制到剪切板")
    } else {
      window_right("error", "复制失败")
    }

  }
  // 下载导出的ldif
  function def_dir_export_down() {
    load_servers_get.value = true
    status_change_dir.value = true

    // 创建一个 Blob 对象，指定类型为文本文件
    let blob = new Blob([data_res_dir_export.value], { type: 'text/plain' });
    // 创建一个临时的 <a> 标签
    let link = document.createElement('a');
    // 创建 Blob URL
    let url = URL.createObjectURL(blob);
    let date_tmp = def_get_date()
    // 设置下载文件名
    link.download = `${request_server.value}-${date_tmp}.ldif`;
    // 设置 href 属性为 Blob URL
    link.href = url;
    // 触发点击事件，开始下载
    link.click();
    // 释放 Blob URL
    URL.revokeObjectURL(url);

    load_servers_get.value = false
    status_change_dir.value = false
  }

  // 获取当前时间
  function def_get_date() {
    let today = new Date();
    // 获取年份 (取后四位)
    let year = today.getFullYear().toString().slice(-4);
    // 获取月份 (注意月份是从0开始的，所以需要加1)
    let month = (today.getMonth() + 1).toString().padStart(2, '0');
    // 获取日期
    let day = today.getDate().toString().padStart(2, '0');
    // 获取小时
    let hours = today.getHours().toString().padStart(2, '0');
    // 获取分钟
    let minutes = today.getMinutes().toString().padStart(2, '0');
    // 获取秒钟
    let seconds = today.getSeconds().toString().padStart(2, '0');
    // 拼接成需要的格式
    return year + month + day + hours + minutes + seconds
  }

  // 上传的ldif文件的反调
  const upload_ldif = ref<UploadInstance>()
  // 上传的ldif文件列表
  let fileList_ldif:Ref<UploadUserFile[]> = ref([])
  // 上传ldif文件时如果超过数量限制了
  const handleExceed: UploadProps['onExceed'] = (files) => {
    upload_ldif.value!.clearFiles()
    const file = files[0] as UploadRawFile
    file.uid = genFileId()
    upload_ldif.value!.handleStart(file)
  }

  // 文件如果状态改变了
  async function def_upload_change(uploadFile: UploadFile, uploadFiles: UploadFiles) {
    status_btn_load.value = true
    console.log(typeof uploadFile.raw, uploadFile, fileList_ldif.value)

    const reader = new FileReader();

    reader.onload = (e) => {
      // 读取成功，e.target.result 是文件的文本内容
      input_dn_upload.value = e.target!.result as string
      console.log("文件内容读取成功");
      status_btn_load.value = false
    };

    reader.onerror = (e) => {
      console.error("文件读取错误:", e);
      status_btn_load.value = false
    };

    // 读取文件内容为文本
    reader.readAsText(uploadFile.raw!);

    // console.log("文件内容读取结束");

  }

  // table表头的样式
  let style_table_header = {
    "background-color": "#f5f5f5",
    "color": "#5a5a5a",
    "padding-top": "2px",
    "padding-bottom": "2px",
    "border-right": "1px solid #dbdbdb",
    // "border-right-color": "#dbdbdb",
    "--el-table-border-color": "white"
  }
  // table普通列的样式
  let style_table_cell = {
    // "border-bottom": "none",
    "border-right": "none",
    "border-bottom-color": "#f5f5f5",
    "--el-table-border-color": "white",
  }
  // table整体外边框的样式
  let style_table = {
    "--el-table-border-color": "white",
  }

  // input转圈图标
  const svg = `
    <path class="path" d="
      M 30 15
      L 28 17
      M 25.61 25.61
      A 15 15, 0, 0, 1, 15 30
      A 15 15, 0, 1, 1, 27.99 7.5
      L 15 15
    " style="stroke-width: 4px; fill: rgba(0, 0, 0, 0)"/>
  `

</script>

<template>
  <div style="height: 100%">
    <!-- ldap服务器自身操作区 -->
    <el-card v-loading="load_servers_get" style="margin-bottom: 20px">
      <!-- ldap服务器操作区 -->
      <div style="display: flex; justify-content: space-between">
        <div>
          <el-button type="primary" plain @click="def_servers_get()">刷新</el-button>
          <el-select class="select_server" filterable @change="def_server_changed" v-model="select_server" placeholder="选择LDAP服务器">
            <el-option v-for="k of Object.keys(data_res_servers)" :key="k" :label="k" :value="k" />
          </el-select>
          <el-button v-if="select_server" type="primary" @click="def_serverdata_get()">发起连接</el-button>
          <el-button type="success" @click="status_win_servers_add=true">新增</el-button>
          <el-button v-if="select_server" type="danger" @click="status_ask_servers_delete=true">删除</el-button>

        </div>
        <div>
          <el-button type="info" v-if="select_server" @click="status_win_server_info=true">详细信息</el-button>
        </div>
      </div>
      <!-- 当前选中服务器的详细信息 -->
      <el-dialog v-model="status_win_server_info" width="600px">
        <template #header>
          <el-text size="large" type="info" style="margin-right: 20px;">{{select_server}} 的详细信息</el-text>
        </template>
        <div  class="div_show_server">
          <div style="margin-bottom: 10px">
            <el-button size="small" type="warning" @click="status_change_server=true" v-if="!status_change_server">修改</el-button>
            <el-button size="small" type="warning" plain @click="def_server_update_cancel()" v-if="status_change_server">取消修改</el-button>
            <el-button size="small" type="success" plain @click="def_servers_update()" v-if="status_change_server">提交更新</el-button>
          </div>
          <el-form label-width="auto">
            <el-form-item label="显示名" >
              <el-input v-model="data_req_server_update.server_name" disabled/>
            </el-form-item>
            <el-form-item label="LDAP服务器地址">
              <el-input v-model="data_req_server_update.server_addr" :disabled="!status_change_server"/>
            </el-form-item>
            <el-form-item label="起始域">
              <el-input v-model="data_req_server_update.server_base" :disabled="!status_change_server"/>
            </el-form-item>
            <el-form-item label="登录用dn">
              <el-input style="" v-model="data_req_server_update.server_auth_dn" :disabled="!status_change_server"/>
            </el-form-item>
            <el-form-item label="登录密码">
              <el-input style="" v-model="data_req_server_update.server_auth_passwd" show-password autocomplete="new-password" :disabled="!status_change_server"/>
            </el-form-item>
          </el-form>
        </div>
      </el-dialog>
      <!-- 新增ldap服务器的弹窗 -->
      <el-dialog width="600px" center v-model="status_win_servers_add">
        <div v-loading="load_servers_get">
          <el-form v-model="data_req_server_add" label-width="auto">
            <el-form-item label="显示名">
              <el-input show-word-limit maxlength="30" v-model="data_req_server_add.server_name"/>
            </el-form-item>
            <el-form-item label="LDAP服务器地址">
              <el-input show-word-limit maxlength="200" v-model="data_req_server_add.server_addr"/>
            </el-form-item>
            <el-form-item label="起始域">
              <el-input show-word-limit maxlength="200" v-model="data_req_server_add.server_base"/>
            </el-form-item>
            <el-form-item label="登录用dn">
              <el-input show-word-limit maxlength="200" v-model="data_req_server_add.server_auth_dn"/>
            </el-form-item>
            <el-form-item label="登录密码">
              <el-input show-word-limit maxlength="200" v-model="data_req_server_add.server_auth_passwd" show-password autocomplete="new-password"/>
            </el-form-item>
          </el-form>
        </div>
        <template #footer>
          <el-button :loading="load_servers_get" type="success" @click="def_servers_add()">新增</el-button>
          <el-button :loading="load_servers_get" @click="status_win_servers_add=false">取消</el-button>
        </template>
      </el-dialog>
      <!-- 确认删除一个ldap服务器的确认弹框 -->
      <el-dialog v-model="status_ask_servers_delete" width="400px" center title="警告">
        <div>
          <el-text>确认删除LDAP连接: '</el-text>
          <el-text type="danger">{{select_server}}</el-text>
          <el-text>' 吗?'</el-text>
        </div>
        <template #footer>
          <el-button :loading="load_servers_get" type="danger" @click="def_servers_delete()">删除</el-button>
          <el-button :loading="load_servers_get" @click="status_ask_servers_delete=false">取消</el-button>
        </template>
      </el-dialog>
      <!--<el-icon color="#409EFF" @click=""><Plus /></el-icon>-->
      <!--<el-icon color=#F56C6C><Minus /></el-icon>-->
      <!--<el-icon color="#F56C6C"><Delete /></el-icon>-->

    </el-card>
    <!--{{select_tree_checkbox}}-->
    <!-- 选定的ldap服务器数据展示区 -->
    <!--{{data_req_dir_add}}-->
    <el-card style="height: calc(100vh - 60px - 130px)">

      <!-- 数据获取失败时的展示 -->
      <div v-if="!status_req_get_dir" class="zihao_error">
        <el-empty :image="zihao" description="获取失败了呢 ~"/>
      </div>
      <!-- 数据获取为空时的展示 -->
      <div v-if="status_req_get_dir && data_res_serverdirTree.length==0 && Object.keys(data_res_serverclass).length>0" class="zihao_error">
        <el-empty :image="zihao" description="返回为空呢 ~"/>
      </div>

      <el-row :gutter="20" style="height: 100%;" v-if="status_req_get_dir && request_server && data_res_serverdirTree.length>0">
        <!-- 左侧目录树 -->
        <el-col :span="6" style="display: flex; justify-content: space-between;">
          <div  style="width: 100%;height: calc(100vh - 60px - 180px);position: relative;">
            <div style="position: absolute; top: 0;right: 0;">
              <el-link @click="def_help_before()"><el-text type="primary">文档<el-icon><List /></el-icon></el-text></el-link>
            </div>

            <h3 class="h3_right">{{request_server}} </h3>
            <!-- 目录树操作区 -->
            <div style="display: flex; align-items: self-start">
              <el-button v-if="!status_tree_checkbox" size="small" type="info" @click="def_tree_on()">开启多选</el-button>
              <el-button v-else plain size="small" type="info" @click="def_tree_off()">关闭多选</el-button>
              <el-button :disabled="select_tree_checkbox.length==0" size="small" type="danger" @click="status_win_delete_dir_more=true">删除</el-button>
              <el-button size="small" type="success" @click="def_dir_add_before()">新增</el-button>
              <el-button size="small" type="primary" @click="status_win_load_dir=true">导入</el-button>
            </div>
            <!-- 搜索框, 多选时不允许开启, 因为即使筛选了也仅仅是隐藏已选选项, 不会从已选列表中删除被筛选掉的选项 -->
            <el-input
                :disabled="status_tree_checkbox"
                v-model="input_search_dir"
                style="width: 200px;margin-bottom: 10px;margin-top: 10px"
                :placeholder="input_search_dir_txt"
                @input="def_search_dir_changed"
                size="small"
            />
            <!-- 目录树 -->
            <el-tree-v2
                ref="tree_ldapdir"
                :data="data_res_serverdirTree"
                :props="props_ldapdir"
                :filter-method="tree_filterMethod"
                :check-on-click-node="false"
                :expand-on-click-node="false"
                @node-click="def_dir_click"
                :show-checkbox="status_tree_checkbox"
                @check="def_dir_changed_checkbox"
                :height="height_tree"
                :current-node-key="select_dir_dn"
                :check-strictly="true"
                :default-expanded-keys="[data_res_serverbase]"
            >
              <template #default="{ node }">
                <!-- 人员图标 -->
                <el-image v-if="node.data.objectClass.includes('inetOrgPerson')" :src="yuangong" style="width: 12px;height: 12px;margin-right: 2px"/>
                <!-- 目录图标 -->
                <el-image v-else-if="node.data.objectClass.includes('organizationalUnit')" :src="bumen" style="width: 12px;height: 12px;margin-right: 2px"/>
                <!-- 顶级域图标 -->
                <el-image v-else-if="node.data.objectClass.includes('dcObject')" :src="dingjiyu" style="width: 12px;height: 12px;margin-right: 2px"/>
                <!-- 无法识别的图标 -->
                <el-image v-else :src="wendang" style="width: 12px;height: 12px;margin-right: 2px"/>
                <el-text>{{node.label}}</el-text>
                <el-text type="primary" v-if="select_dn_mingming==node.label">&nbsp;&nbsp;&nbsp;&nbsp;<el-icon><Back /></el-icon></el-text>
              </template>
            </el-tree-v2>
            <!--{{select_tree_checkbox}}-->
          </div>
          <!-- 第一栏的分割线 -->
          <el-divider v-if="request_server && data_res_serverdirTree.length>0" direction="vertical" style="height: 100%;"/>
          <!-- 创建单个条目的弹窗 -->
          <el-dialog v-model="status_win_create_dir" center width="80%">
            <template #header>
              <el-text size="large">创建单个条目</el-text>
            </template>
            <!--{{data_req_dir_add}}-->
            <el-row :gutter="20" style="height: 100%;">
              <el-col :span="15">
                <div style="display: flex;flex-direction: column;align-items: center;">

                  <el-form label-width="auto">
                    <!-- dn的输入框 -->
                    <el-form-item label="dn" label-width="auto" style="">
                      <template #label>
                        <el-text type="danger">*&nbsp;</el-text>
                        <el-text>dn</el-text>
                      </template>
                      <el-input v-model="input_dn_add">
                        <template #append>{{input_dn_add_append}}</template>
                      </el-input>
                    </el-form-item>
                    <!-- 属性选择框 -->
                    <el-popover trigger="click" width="300px" style="min-width: 10px;max-width: 300px">
                      <template #reference>
                        <el-button type="primary" size="small" style="margin-bottom: 20px" :loading="status_change_dir">
                          新增属性 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </el-button>
                      </template>
                      <!--<el-select v-model="data_req_dir_objectClass_update" filterable multiple clearable>-->
                      <!--  <el-option v-for="k of Object.keys(data_res_serverclass)" :label="k" :value="k"/>-->
                      <!--</el-select>-->
                      <el-table :data="filter_show_attrs_add" height="300px" fit size="small" empty-text="请先选择有效的模板">
                        <el-table-column fixed width="240px">
                          <template #header>
                            <el-input v-model="input_search_attrs_add" size="small" placeholder="搜索..." />
                          </template>
                          <template #default="scope">
                            <el-button
                                :disabled="Object.keys(data_req_dir_add).includes(scope.row)" style="width: 100%"
                                plain text @click="def_dir_addattr_add(scope.row)" size="small" type="primary"
                            >
                              {{scope.row}}
                            </el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-popover>
                    <!-- 普通属性的输入框, 如果是命名属性, 则不展示 -->
                    <el-form-item v-for="(v, k) in data_req_dir_add" :label="k">
                      <template #label>
                        <el-text type="danger" v-if="create_dir_attrs_must.includes(k.toString())">*&nbsp;</el-text>
                        <el-text>{{k}}</el-text>
                        <el-button size="small" type="danger" plain text :icon="Delete" @click="def_dir_delattr_add(k.toString())" style="width: 20px"></el-button>
                      </template>
                      <div class="div_item_input">
                        <!-- 单值时的输入框, 不允许编辑命名属性 -->
                        <el-input
                            v-if="typeof data_req_dir_add[k] == 'string'" v-model="data_req_dir_add[k]" style="max-width: 400px;min-width: 250px"
                        />
                        <!-- 多值时的输入框, 不允许编辑命名属性 -->
                        <div v-if="Array.isArray(data_req_dir_add[k])" class="div_form_item" >
                          <div v-for="(vv, i) of v" class="div_item_input">
                            <el-input v-model="data_req_dir_add[k][i]" style="max-width: 400px;min-width: 250px"/>
                            <el-button type="danger" plain text :icon="Minus" @click="def_dir_delline_add(k.toString(),i)" style="width: 20px"></el-button>
                          </div>
                        </div>
                        <el-button v-if="Array.isArray(data_req_dir_add[k])" type="primary" plain text :icon="Plus" @click="def_dir_addline_add(k.toString())" style="width: 20px"/>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>
              </el-col>
              <el-col :span="1">
                <div style="height: 100%;width: 3px;background-color: #8c939d"/>
              </el-col>
              <el-col :span="8">
                <div style="display: flex;flex-direction: column;align-items: flex-start;">
                  <div style="display: flex; gap: 10px; align-items: center;">
                    <h3 class="h3_right">objectClass</h3>
                    <!-- 模板选择框 -->
                    <el-popover trigger="click" width="300px" style="min-width: 10px;max-width: 300px">
                      <template #reference>
                        <el-button type="primary" plain text :icon="Plus" style="width: 20px"></el-button>
                        <!--<el-button type="primary" size="small" style="margin-bottom: 10px" :loading="status_change_dir">-->
                        <!--  新增模板 <el-icon class="el-icon&#45;&#45;right"><arrow-down /></el-icon>-->
                        <!--</el-button>-->
                      </template>
                      <!--<el-select v-model="data_req_dir_objectClass_update" filterable multiple clearable>-->
                      <!--  <el-option v-for="k of Object.keys(data_res_serverclass)" :label="k" :value="k"/>-->
                      <!--</el-select>-->
                      <el-table :data="filter_show_class_add" height="300px" fit size="small">
                        <el-table-column fixed width="240px">
                          <template #header>
                            <el-input v-model="input_search_class_add" size="small" placeholder="搜索..." />
                          </template>
                          <template #default="scope">
                            <el-button
                                :disabled="data_req_dir_objectClass_add.includes(scope.row)" style="width: 100%"
                                plain text @click="def_dir_addclass_add(scope.row)" size="small" type="primary"
                            >
                              {{scope.row}}
                            </el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-popover>
                  </div>

                  <!-- 已选模板列表 -->
                  <div style="margin-bottom: 10px">
                    <el-tag
                        v-for="(k, i) of data_req_dir_objectClass_add" style="margin: 5px"
                        :key="k" :closable="k!=='top'" @close="def_dir_delclass_add(i)"
                        :type="['primary','success','danger','warning'][Math.floor(Math.random() * 4)]"
                    >
                      {{k}}
                    </el-tag>
                  </div>
                  <h3 class="h3_right">创建</h3>
                  <div>
                    <el-button @click="status_win_create_dir=false" :loading="status_change_dir">取消</el-button>
                    <el-button type="success" :loading="status_change_dir" @click="def_serverdir_add();status_win_create_dir=false">仅创建</el-button>
                    <el-button type="success" :loading="status_change_dir" @click="def_serverdir_add()">创建并继续</el-button>
                  </div>

                </div>
              </el-col>
            </el-row>
          </el-dialog>

          <!-- 删除多个条目的提示弹框 -->
          <el-dialog v-model="status_win_delete_dir_more" center title="警告">
            <div style="display: flex; justify-content: center; flex-direction: column; margin-bottom: 20px">
              <el-text>确认删除以下dn吗</el-text>
              <div v-for="dn of select_tree_checkbox" style="display: flex; justify-content: center;">
                <el-text type="danger">{{dn}}</el-text>
              </div>
              <div style="display: flex; justify-content: center; margin-top: 20px">
                <el-text size="small" type="info">*将一并删除其所有子条目*</el-text>
              </div>
            </div>
            <template #footer>
              <div class="">
                <el-button @click="status_win_delete_dir_more = false">取消</el-button>
                <el-button type="danger" @click="def_serverdir_delete(select_tree_checkbox);status_win_delete_dir_more=false" :loading="status_change_dir">删除</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 导入ldif数据 -->
          <el-dialog v-model="status_win_load_dir" center title="导入LDIF">
            <!-- 上传文件的窗口 -->
            <el-upload
                ref="upload_ldif"
                v-model:file-list="fileList_ldif"
                :limit="1"
                :on-exceed="handleExceed"
                :on-change="def_upload_change"
                :auto-upload="false"
            >
              <el-button size="small" type="primary" :loading="status_btn_load">从文件导入</el-button>
            </el-upload>
            <h3 class="h3_right">输入LDIF格式数据, 仅支持新增</h3>

            <!-- 文本输入框 -->
            <el-text size="small" type="info">* 导入数据最终以输入框内容为主 *</el-text>
            <el-input
                type="textarea" v-model="input_dn_upload" :autosize="{ minRows: 18, maxRows: 18 }"
                v-loading="status_btn_load"
            />
            <!--<el-card v-loading="status_btn_load">-->
            <!--  -->
            <!--</el-card>-->

            <div style="display: flex;justify-content: center; align-items: center; margin-top: 20px; gap: 20px">
              <el-text>重复时是否覆盖: </el-text>
              <el-radio-group v-model="status_load_force" size="small">
                <el-radio-button label="是" :value="true" />
                <el-radio-button label="否" :value="false" />
              </el-radio-group>
            </div>
            <template #footer>

              <div class="">
                <el-button @click="status_win_load_dir = false">取消</el-button>
                <el-button type="success" @click="def_serverdir_load" :loading="status_btn_load">导入</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 文档页面 -->
          <el-dialog v-model="status_win_help" center title="文档">
            <div style="display: flex; justify-content: center; flex-direction: column; margin-bottom: 20px">
              <el-text>正在施工...</el-text>
            </div>
            <template #footer>
              <div class="">
                <el-button @click="status_win_help = false">关闭</el-button>
              </div>
            </template>
          </el-dialog>

        </el-col>

        <!-- 中间编辑区 -->
        <el-col :span="12" style="display: flex; justify-content: space-between; ">
          <!--{{select_dir_dn}}-->
          <!--{{data_req_dir_update}}-->
          <div v-if="select_dir_dn" style="width: 100%; height: calc(100vh - 90px - 180px); overflow: auto">
            <!-- 属性选择框 -->
            <el-popover trigger="click" width="300px" style="min-width: 10px;max-width: 300px" >
              <template #reference>
                  <el-button type="primary" size="small" style="margin-bottom: 20px" :loading="status_change_dir" :disabled="select_dir_dn==data_res_serverbase">
                    新增属性 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
              </template>
              <!--<el-select v-model="data_req_dir_objectClass_update" filterable multiple clearable>-->
              <!--  <el-option v-for="k of Object.keys(data_res_serverclass)" :label="k" :value="k"/>-->
              <!--</el-select>-->
              <el-table :data="filter_show_attrs" height="300px" fit size="small">
                <el-table-column fixed width="240px">
                  <template #header>
                    <el-input v-model="input_search_attrs" size="small" placeholder="搜索..." />
                  </template>
                  <template #default="scope">
                    <el-button
                        :disabled="Object.keys(data_req_dir_update).includes(scope.row)" style="width: 100%"
                        plain text @click="def_dir_addattr(scope.row)" size="small" type="primary"
                    >
                      {{scope.row}}
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-popover>
            <el-form label-width="auto" :disabled="select_dir_dn==data_res_serverbase">
              <el-form-item v-for="(v, k) in data_req_dir_update" :label="k">
                <template #label>
                  <el-text type="danger" v-if="select_dir_attrs_must.includes(k.toString())">*&nbsp;</el-text>
                  <el-text>{{k}}</el-text>
                  <el-button size="small" type="danger" plain text :icon="Delete" @click="def_dir_delattr(k.toString())" style="width: 20px"></el-button>
                </template>
                <div class="div_item_input">
                  <!-- 单值时的输入框, 不允许编辑命名属性 -->
                  <el-input
                      v-if="typeof data_req_dir_update[k] == 'string'" v-model="data_req_dir_update[k]" style="max-width: 400px;min-width: 250px"
                      :disabled="select_dir_dn.split('=')[0]==k && select_dir_dn.split(',')[0].split('=')[1] == data_req_dir_update[k]"
                  />
                  <!-- 多值时的输入框, 不允许编辑命名属性 -->
                  <div v-if="Array.isArray(data_req_dir_update[k])" class="div_form_item" >
                    <div v-for="(vv, i) of v" class="div_item_input">
                      <el-input
                          v-model="data_req_dir_update[k][i]" style="max-width: 400px;min-width: 250px"
                          :disabled="select_dir_dn.split('=')[0] == k && select_dir_dn.split(',')[0].split('=')[1] == data_req_dir_update[k][i]"
                      />
                      <el-button
                          :disabled="select_dir_dn.split('=')[0] == k && select_dir_dn.split(',')[0].split('=')[1] == data_req_dir_update[k][i]"
                          type="danger" plain text :icon="Minus" @click="def_dir_delline(k.toString(),i)" style="width: 20px"
                      />
                    </div>
                  </div>

                  <el-button v-if="Array.isArray(data_req_dir_update[k])" type="primary" plain text :icon="Plus" @click="def_dir_addline(k.toString())" style="width: 20px"/>
                </div>

              </el-form-item>
            </el-form>
            <!--<el-text>编辑区尾部</el-text>-->
            <!--{{data_req_dir_objectClass_update}} <br>-->
            <!--{{select_dir_objectClass}}<br>-->
            <!--{{data_req_dir_update}}<br>-->
            <!--{{select_dir_info}}<br>-->
          </div>

          <el-divider v-if="select_dir_dn" direction="vertical" style="height: 100%"/>
        </el-col>

        <!-- 右侧选项区 -->
        <el-col :span="6">
          <div v-if="select_dir_dn" style="height: calc(100vh - 60px - 180px); overflow: auto">
            <h3 class="h3_right">dn</h3>
            <el-text size="large">{{select_dir_dn}}</el-text>

            <div style="display: flex; gap: 2px; align-items: center;">
              <h3 class="h3_right">objectClass</h3>
              <!-- 模板选择框 -->
              <el-popover trigger="click" width="300px" style="min-width: 10px;max-width: 300px">
                <template #reference>
                  <el-button type="primary" plain text :icon="Plus" style="width: 20px" :disabled="select_dir_dn==data_res_serverbase"/>
                </template>
                <!--<el-select v-model="data_req_dir_objectClass_update" filterable multiple clearable>-->
                <!--  <el-option v-for="k of Object.keys(data_res_serverclass)" :label="k" :value="k"/>-->
                <!--</el-select>-->
                <el-table :data="filter_show_class" height="300px" fit size="small">
                  <el-table-column fixed width="240px">
                    <template #header>
                      <el-input v-model="input_search_class" size="small" placeholder="搜索..." />
                    </template>
                    <template #default="scope">
                      <el-button
                          :disabled="data_req_dir_objectClass_update.includes(scope.row)" style="width: 100%"
                          plain text @click="def_dir_addclass(scope.row)" size="small" type="primary"
                      >
                        {{scope.row}}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-popover>
            </div>

            <div style="">
              <!-- :type="['primary','success','danger','warning'][Math.floor(Math.random() * 4)]" -->
              <el-tag
                  v-for="(k, i) of data_req_dir_objectClass_update" style="margin: 5px"
                  :key="k" :closable="select_dir_dn!=data_res_serverbase" @close="def_dir_delclass(i)" type="primary"
              >
                {{k}}
              </el-tag>

            </div>
            <h3 class="h3_right">更新</h3>
            <el-button
                size="small" :disabled="cpd_isChange_dir || select_dir_dn==data_res_serverbase"
                type="warning" plain @click="def_dir_change_cancel()" :loading="status_change_dir"
            >取消更改</el-button>
            <el-button
                size="small" :disabled="cpd_isChange_dir || select_dir_dn==data_res_serverbase"
                type="warning" :loading="status_change_dir" @click="def_serverdir_update()"
            >提交</el-button>
            <!--<el-button @click="tree_ldapdir?.setCurrentKey('ou=daoqi,dc=teyvat,dc=com')">点击稻妻</el-button>-->
            <!--<el-button @click="def_test_click()">点击稻妻</el-button>-->
            <h3 class="h3_right">新增</h3>
            <el-button
                size="small" type="success" @click="def_serverdir_rename_before()" :loading="status_change_dir"
                :disabled="select_dir_dn==data_res_serverbase"
            >重命名</el-button>
            <el-button
                size="small" type="success" @click="def_serverdir_move_before()" :loading="status_change_dir"
                :disabled="select_dir_dn==data_res_serverbase"
            >移动</el-button>
            <el-button
                size="small" type="success" @click="def_dir_clone_init()" :loading="status_change_dir"
                :disabled="select_dir_dn==data_res_serverbase"
            >同级克隆</el-button>
            <!--<el-container :disabled="select_dir_dn==data_res_serverbase">-->
            <!--  -->
            <!--</el-container>-->

            <h3 class="h3_right">删除</h3>
            <el-button
                size="small" type="danger" @click="status_win_delete_dir_one=true" :loading="status_change_dir"
                :disabled="select_dir_dn==data_res_serverbase"
            >删除</el-button>
            <h3 class="h3_right">导出</h3>
            <el-button size="small" type="info" @click="status_win_export_dir=true" :loading="status_change_dir">导出为ldif</el-button>
          </div>

          <!-- 克隆当前选中dn的弹框 -->
          <el-dialog v-model="status_win_clone_dir" center :title="'克隆: '+select_dir_dn" width="90%">
            <!-- objectClass展示区 -->
            <div style="display: flex;flex-direction: column; justify-content: left; margin-bottom: 20px">
              <div style="display: flex; align-items: center; margin-bottom: 10px">
                <h3 class="h3_right">objectClass: </h3>
                <el-tag size="small" v-for="(k, i) of select_dir_objectClass" style="margin: 5px" :key="k" type="primary">{{k}}</el-tag>
              </div>
              <h3 class="h3_right">当前命名属性: {{input_dn_clone_prepend}}</h3>
              <!-- 属性选择框 -->
              <el-popover trigger="click" width="300px" style="min-width: 10px;max-width: 300px">
                <template #reference>
                  <el-button type="primary" size="small" style="width: 100px;margin-bottom: 10px;margin-top: 10px" :loading="status_change_dir">
                    新增属性 <el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                </template>
                <!--<el-select v-model="data_req_dir_objectClass_update" filterable multiple clearable>-->
                <!--  <el-option v-for="k of Object.keys(data_res_serverclass)" :label="k" :value="k"/>-->
                <!--</el-select>-->
                <el-table :data="filter_show_attrs" height="300px" fit size="small">
                  <el-table-column fixed width="240px">
                    <template #header>
                      <el-input v-model="input_search_attrs" size="small" placeholder="搜索..." />
                    </template>
                    <template #default="scope">
                      <el-button
                          :disabled="Object.keys(select_dir_clone).includes(scope.row)" style="width: 100%"
                          plain text @click="def_dir_addattr_clone(scope.row)" size="small" type="primary"
                      >
                        {{scope.row}}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-popover>
              <el-table :data="data_req_dir_clone" :style="style_table" :header-cell-style="style_table_header" :cell-style="style_table_cell" border>
                <!-- dn列 -->
                <el-table-column prop="dn_v" label="dn命名属性值" fixed width="180px">
                  <template #default="scope" >
                    <el-tooltip
                        placement="top-start"
                        :content="input_dn_clone_prepend+'={'+(data_req_dir_clone[scope.$index].dn_v||'')+'},'+input_dn_clone_append"
                    >
                      <el-input size="small" v-model="data_req_dir_clone[scope.$index].dn_v" style="width: 150px"/>
                    </el-tooltip>
                    <!--<el-input size="small" v-model="data_req_dir_clone[scope.$index].dn" style="width: 150px">-->
                    <!--  <template #prepend>{{select_dir_dn.split('=')[0]}}=</template>-->
                    <!--  <template #append>,{{select_dir_dn.split(',').slice(1).join(',')}}</template>-->
                    <!--</el-input>-->
                  </template>
                </el-table-column>
                <!-- 其他属性的列, 动态加载 -->
                <el-table-column v-for="(v, k) in select_dir_clone" :prop="k" :label="k" min-width="200px">
                  <template #header>
                    <el-text type="danger" v-if="select_dir_attrs_must.includes(k.toString())">*&nbsp;</el-text>
                    <el-text>{{k}}</el-text>
                    <el-button size="small" type="danger" plain text :icon="Delete" @click="def_dir_delattr_clone(k.toString())" style="width: 20px"></el-button>
                  </template>
                  <template #default="scope">
                    <!--{{data_req_dir_clone[scope.$index][k]}}-->
                    <div class="div_item_input">
                      <!-- 单值时的输入框, 不允许编辑命名属性 -->
                      <el-input
                          size="small" v-if="data_res_serverattrs[k].attr_isSingle" v-model="scope.row.attrs[k]"
                      />
                      <!-- 多值时的输入框, 不允许编辑命名属性 -->
                      <div v-if="!data_res_serverattrs[k].attr_isSingle" class="div_form_item" >
                        <!--{{data_req_dir_clone[scope.$index].attrs}}-->
                        <!--{{scope.row.attrs}}{{k}}-->
                        <div v-for="(vv, i) of scope.row.attrs[k]" class="div_item_input_inline">
                          <!-- :disabled="select_dir_dn.split('=')[0] == k && scope.row.dn == scope.row.attrs[k][i]" -->
                          <el-input
                              size="small" v-model="scope.row.attrs[k][i]"
                          />
                          <!-- :disabled="select_dir_dn.split('=')[0] == k && scope.row.dn == scope.row.attrs[k][i]" -->
                          <el-button
                              type="danger" size="small" plain text :icon="Minus" @click="scope.row.attrs[k].splice(i,1)" style="width: 10px"
                          />
                        </div>
                      </div>
                      <el-button v-if="!data_res_serverattrs[k].attr_isSingle" size="small" type="primary" plain text :icon="Plus" @click="scope.row.attrs[k].push('')" style="width: 10px"/>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
              <el-button style="width: 100%;margin-top: 20px" @click="def_dir_clone_addline()" :icon="CirclePlus" text type="primary">新增一行</el-button>
              <!--{{data_req_dir_clone}}<br>-->
              <!--{{select_dir_info}}<br>-->
              <!--{{select_dir_clone}}<br>-->
            </div>
            <template #footer>
              <div class="">
                <el-button @click="status_win_clone_dir = false">取消</el-button>
                <el-button type="success" @click="def_serverdir_clone()" :loading="status_change_dir">新增</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 确认删除当前选中dn的弹框 -->
          <el-dialog v-model="status_win_delete_dir_one" center title="警告">
            <div style="display: flex;flex-direction: column; margin-bottom: 20px">
              <div style="display: flex; justify-content: center; margin-bottom: 20px">
                <el-text>确认删除dn: '</el-text>
                <el-text type="danger">{{select_dir_dn}}</el-text>
                <el-text>' 吗</el-text>
              </div>
              <div style="display: flex; justify-content: center; ">
                <el-text size="small" type="info">*将一并删除其所有子条目*</el-text>
              </div>
            </div>
            <template #footer>
              <div class="">
                <el-button @click="status_win_delete_dir_one = false">取消</el-button>
                <el-button type="danger" @click="def_serverdir_delete([select_dir_dn])" :loading="status_change_dir">删除</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 重命名的弹框 -->
          <el-dialog v-model="status_win_rename_dir" center title="重命名dn">
            <div style="display: flex; flex-direction: column; justify-content: center; margin-bottom: 20px; gap: 5px">
              <el-text size="small">原dn: {{select_dir_dn}}</el-text>
              <el-input v-model="input_dn_rename">
                <template #prepend>{{input_dn_clone_prepend}}=</template>
                <template #append>,{{input_dn_clone_append}}</template>
              </el-input>
            </div>
            <template #footer>
              <div class="">
                <el-button @click="status_win_rename_dir = false">取消</el-button>
                <el-button type="warning" @click="def_serverdir_rename()" :loading="status_change_dir">重命名</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 移动或复制的弹框 -->
          <el-dialog v-model="status_win_move_dir" center title="选取新dn的父条目">
            <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; gap: 5px;">
              <!--<el-text>选取新dn的父条目</el-text>-->
                <div class="div_biankuang" style="width: 500px;">
                  <el-tree-v2
                      :data="data_res_serverdirTree"
                      :props="props_ldapdir"
                      @node-click="def_dir_click_move"
                      @check="def_dir_changed_checkbox"
                      :height="200"
                      :current-node-key="select_dir_dn"
                      :default-expanded-keys="[data_res_serverbase]"
                      :expand-on-click-node="false"
                  >
                    <template #default="{ node }">
                      <el-text>{{node.label}}</el-text>
                      <el-text type="primary" v-if="select_ou_mv_mingming==node.label">&nbsp;&nbsp;&nbsp;&nbsp;<el-icon><Back /></el-icon></el-text>
                    </template>
                  </el-tree-v2>
                </div>
                <div style="display: flex; flex-direction: column;">
                  <div style="display: flex; align-items: center; flex-wrap: wrap">
                    <!--<el-text>命名属性: </el-text>-->
                    <h3 class="h3_right" style="margin-right: 20px">命名属性:</h3>
                    <el-text type="info">{{input_dn_clone_prepend}}=</el-text>
                    <el-tooltip
                        placement="top-start"
                        :content="input_dn_clone_prepend+'={'+(input_dn_rename||'')+'},'+select_ou_mv"
                    >
                      <el-input v-model="input_dn_rename" style="width: 200px"/>
                    </el-tooltip>
                  </div>
                  <div style="display: flex; align-items: center">
                    <!--<el-text>是否删除旧条目: </el-text>-->
                    <h3 class="h3_right" style="margin-right: 20px">是否删除旧条目:</h3>
                    <el-radio-group v-model="status_dir_delold" size="small">
                      <el-radio-button label="否" :value="false" />
                      <el-radio-button label="是" :value="true" />
                    </el-radio-group>
                  </div>
                </div>

            </div>

            <template #footer>
              <div class="">
                <el-button @click="status_win_move_dir = false">取消</el-button>
                <el-button type="warning" @click="def_serverdir_move()" :loading="status_change_dir">移动</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 导出为ldif格式文本的弹框 -->
          <el-dialog v-model="status_win_export_dir" center title="导出为LDIF">
            <div style="display: flex; flex-direction: column; justify-content: center;align-items: center;
             margin-bottom: 20px; gap: 5px">
              <div>
                <el-text>即将导出dn:&nbsp;&nbsp;</el-text>
                <el-text type="success">{{select_dir_dn}}</el-text>
              </div>
              <div style="display: flex; align-items: center">
                <!--<el-text>是否删除旧条目: </el-text>-->
                <h3 class="h3_right" style="margin-right: 20px">是否一并导出子条目:</h3>
                <el-radio-group v-model="status_dir_export_tree" size="small">
                  <el-radio-button label="否" :value="false" />
                  <el-radio-button label="是" :value="true" />
                </el-radio-group>
              </div>
            </div>
            <template #footer>
              <div class="">
                <el-button @click="status_win_export_dir = false">取消</el-button>
                <el-button type="warning" @click="def_serverdir_export()" :loading="status_change_dir">导出</el-button>
              </div>
            </template>
          </el-dialog>

          <!-- 显示导出ldif结果的弹框 -->
          <el-drawer
              v-model="status_win_export_res"
              title="导出为LDIF"
              direction="rtl"
              size="60%"
          >
            <el-text><pre>{{data_res_dir_export}}</pre></el-text>
            <template #footer>
              <div style="flex: auto">
                <el-button type="primary" @click="def_dir_export_copy()" v-if="isSupported">复制</el-button>
                <el-button type="success" @click="def_dir_export_down()" :loading="status_change_dir">下载</el-button>
              </div>
            </template>
          </el-drawer>
          <!--{{data_req_dir_objectClass_update}}-->
        </el-col>
      </el-row>
    </el-card>

  </div>
</template>

<style scoped>
  .zihao_error {
    height: calc(100vh - 60px - 180px);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .div_show_server {
    margin-top: 20px;
  }
  .select_server {
    width: 300px;
    margin-left: 20px;
    margin-right: 20px;
  }
  .div_form_item {
    display: flex;
    flex-direction: column;
    gap: 5px;
    /*align-items: center;*/
  }
  .div_item_input {
    display: flex;
    gap: 2px;
    align-items: flex-end;
  }
  .div_item_input_inline {
    display: flex;
    gap: 2px;
    align-items: center;
  }
  .h3_right {
    margin-bottom: 10px;
    margin-top: 10px;
  }
  .div_biankuang {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
  }

</style>