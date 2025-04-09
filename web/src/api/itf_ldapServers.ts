// 后端返回的所有ldap服务器
export interface resLdapSeObj {
    [key: string]: resLdapSe;
}

// 后端返回的单个ldap服务器
interface resLdapSe {
    "server_name": string,
    "server_addr": string,
    "server_base": string,
    "server_auth_dn": string,
    "server_auth_passwd": string,
}

// 请求新增单个ldap服务器
export interface reqLdapSe {
    "server_name": string,
    "server_addr": string,
    "server_base": string,
    "server_auth_dn": string,
    "server_auth_passwd": string,
}

// 后端返回的单个ldap服务器的所有数据
export interface resLdapAll {
    "obj_tree": resLdapDir[],
    "obj_info": resLdapDirInfo
    "class": resLdapClass,
    "attrs": resLdapAttr,
    "dn_base": string,
}

// 后端返回的单个ldap服务器的所有条目信息
export interface resLdapDir {
    dn: string,
    entry: string,
    objectClass: Array<string>,
    children: resLdapDir[]
    // attrs: {
    //     [key: string]: Array<string>|string,
    // },
}

export interface resLdapDirInfo {
    [key:string]: {
        objectClass: Array<string>,
        attrs: {
            [key: string]: Array<string>|string,
        },
    }
}

// 后端返回的单个ldap服务器的所有模板信息
export interface resLdapClass {
    [key: string]: {
        tem_name_fri: string,
        tem_desc: string,
        tem_oid: string,
        kind: string,
        tem_may_list: Array<string>,
        tem_must_list: Array<string>,
        tem_name_list: Array<string>,
        tem_sup_list: Array<string>,
    }
}

// 后端返回的单个ldap服务器的所有属性信息
export interface resLdapAttr {
    [key: string]: {
        attr_name_fri: string,
        attr_desc: string,
        attr_isSingle: boolean,
        attr_name_list: Array<string>,
        attr_oid: string,
        attr_syntax: string, // 字段类型, 但是难以理解的代码串
        attr_type: string, // 字段类型, 是可以理解的中文注释
    }
}

// 克隆当前选定dn时用到的临时列表
export interface reqLdapClone {
    dn: string,
    dn_v: string,
    attrs: {
        [key: string]: Array<string>|string
    }
}