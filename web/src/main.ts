import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'

const app = createApp(App)

// 修改支持中文
app.use(ElementPlus, {
    locale: zhCn,
})

app.mount('#app')
export { app }

