export const deepClone = (data: any) => {
    let type = getType(data)
    let obj
    if (type === 'array') {
        obj = [] as any[]
        for (let i = 0, len = data.length; i < len; i++) {
            obj.push(deepClone(data[i]))
        }
    } else if (type === 'object') {
        obj = {} as Record<string, any>
        for (let key in data) {
            obj[key] = deepClone(data[key])
        }
    } else {
        return data
    }
    return obj
}
export const getType = <T>(obj: T) => {
    let toString = Object.prototype.toString
    let map: Record<string, string> = {
        '[object Boolean]': 'boolean',
        '[object Number]': 'number',
        '[object String]': 'string',
        '[object Function]': 'function',
        '[object Array]': 'array',
        '[object Date]': 'date',
        '[object RegExp]': 'regExp',
        '[object Undefined]': 'undefined',
        '[object Null]': 'null',
        '[object Object]': 'object'
    }
    if (obj instanceof Element) {
        return 'element'
    }
    return map[toString.call(obj)]
}