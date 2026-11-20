# 知序 · 企业知识助手前端

Vue 3 + Vite + JavaScript，无 UI 组件库，使用原生 CSS 和 Fetch。

需要 Node.js 22.12+（推荐 Node.js 24 LTS）及 npm。

```powershell
cd web
npm install
npm run dev
```

打开终端打印的本地地址（默认 http://127.0.0.1:5173）。在项目根目录另开终端启动后端：

```powershell
.\kb_env\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

默认 `/api/*` 经 Vite 转发到后端，代理会移除 `/api` 前缀。后端需自行配置好 MySQL、模型和向量库。没有后端时，页面可打开并展示明确的连接错误，不使用假业务数据。

## 页面

- `#dashboard`：工作台、实际文档统计、最近上传、快捷提问。
- `#chat`：多轮智能对话 / 单轮知识库检索；最近 20 个会话保存在当前浏览器。
- `#knowledge`：上传、状态筛选、审核入库、待审核/失败文件删除、批量结果反馈。
- `#business`：员工分页管理、考勤、请假和通讯录查询及编辑。
- `#settings`：测试并保存当前浏览器的 API 基础地址。

## 配置与验证

可把 `.env.example` 复制为 `.env.local`，修改 `API_PROXY_TARGET` 后重启 Vite。`VITE_*` 是公开前端配置，不能放密钥。浏览器已保存的接口设置优先于环境变量。

```powershell
npm test
npm run build
npm run preview
```

`preview` 只用于本地验收。生产部署时托管 `dist/`，并在 Web 服务器配置 `/api` 反向代理到 FastAPI，移除 `/api` 前缀。Vite 的开发代理不会被打包进 `dist`。

学习说明位于项目根目录 `local_notes/前端页面介绍与修改指南.md`（本地笔记按仓库规则不提交）。从 `src/App.vue` 了解页面切换，从 `src/api/client.js` 了解联调，从 `src/style.css` 调整外观。

## 当前边界

后端尚未提供鉴权、流式回答、对话历史接口、已入库文档的安全删除/预览/下载接口；前端不会绕过审核使用旧版服务器路径接口。正式上线前需由后端实现身份与权限校验。
