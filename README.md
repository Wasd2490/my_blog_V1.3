# 谁暖了冬季 · 个人博客站 V1.3

> glowden · 微光 的个人小站，2026-10-21 首发。

## V1.3 更新（2026-10-21）

- 首页项目卡片每次进首页自动刷新 GitHub 仓库列表，删除的仓库不再残留
- footer 版权改为「仅供学习·著作权归@谁暖了冬季所有」

## V1.2 更新（2026-10-21）

- 空间动态改后端 SQLite 存储，刷新不丢
- 空间动态 4 条/页分页 + 删除按钮
- 空间新增相册 tab，网格浏览所有照片，点击放大
- 修复嵌套模板字符串导致的 JS 语法错误
- 修复图片/视频类型判断错误
- 后端 body 限制提到 20MB
- 修复 blog.html Hero 轮播空元素导致的 JS 报错
- footer 改为「characteristic · 博客 / 仅供学习·著作权归@谁暖了冬季」
- Hero 大标题黑色，右侧个人卡名字统一为「谁暖了冬季」
- 所有页面 title 和导航栏 brand 统一为「characteristic · 博客」

## V1.1 更新（2026-10-21）

- 全文正文文字改为黑色（`--ink:#000`，`--ink-soft:#0a0a0a`），仅保留手写体标题和按钮粉色
- 博客文章列表新增 ↑ 上移 / ↓ 下移排序按钮
- 首页项目板块自动拉取 GitHub API，无需先访问项目页
- 4 张文章预览图本地化到 `assets/`（解决 CSDN 防盗链）
- 项目详情页 404 时显示返回列表按钮
- 修复 blog.html / projects.html 残留 JS 语法错误导致页面崩盘

## V1.0 更新日志（2026-10-21）

## 功能总览

| 页面 | 文件 | 功能 |
|---|---|---|
| 首页 | `index.html` | Hero 动态背景轮播 + 左栏内容区 + 右侧个人卡/分类/归档 |
| 博客 | `blog.html` | MD 上传/富文本粘贴 + 4 篇分页 + Markdown 渲染 + 删除 |
| 项目 | `projects.html` | GitHub API 同步仓库列表 + 文件树 + README 预览 |
| 记录 | `personal.html` | 技能栈 + 成长时间线 + 链接卡片 |
| 空间 | `space.html` | 朋友圈风格日常动态（文字+图片/视频+评论） |

## V1.0 更新日志（2026-10-21）

### 新增
- Hero 全屏动态背景 4 张轮播：樱花 / 银河 / 风铃视频 + 银发精灵图，下滑收缩成小 banner
- CSDN 两栏博客布局，粉色系配色
- 鲨鱼帽小白熊头像（圆形裁切 + 粉色描边）
- 博客写文章功能：支持 `.md` 文件上传 + Markdown 粘贴，marked.js 渲染
- 文章删除、侧栏 categories / archive 动态统计
- 博客列表 4 篇/页分页
- GitHub API 同步 Wasd2490 仓库，文件树浏览 + README 展示
- 项目详情独立页（hash 路由 `#repo/<name>`）
- 空间分享：发文字+图片/视频+评论，localStorage 持久化
- 首页右下角 ⚙ 设置按钮，可选博客板块展示哪篇文章、项目板块展示哪个仓库
- 联系我板块：GitHub / CSDN / 邮箱
- Flask 后端 `app.py` + SQLite `site.db`
- 邮箱注册/登录，GitHub OAuth 登录
- 博客文章、项目仓库评论功能（登录后可发评论）
- ngrok 外网穿透，公网可访问

### 已删除
- 早期粉色二次元桃之夭夭翻版
- 暗色赛博朋克/Matrix 代码雨风格
- 所有编造的假文章假数据
- 旧的「关于」「留言」独立页面

## 使用说明

### 本地运行（带后端）
```
python app.py
```
浏览器打开 http://127.0.0.1:5000

### 外网访问
```
C:\ngrok\ngrok.exe http 5000
```
获取公网链接。

### 发文章
1. 打开 `blog.html`，点右上角「✎ 写文章」
2. 粘贴 Markdown 内容，或上传 `.md` 文件
3. 选分类、填标题，保存
4. 文章自动存浏览器 localStorage，首页最新文章卡片自动更新

### 发空间动态
打开 `space.html`，写文字 + 传照片/视频，点发布。每条动态下面可评论。

### 选首页展示内容
首页右下角点 ⚙ 按钮，下拉选：
- 博客板块展示哪篇文章
- 项目板块展示哪个 GitHub 仓库

### GitHub 项目同步
项目页自动拉取 `https://api.github.com/users/Wasd2490/repos`，点仓库卡片进详情，左侧文件树点文件看内容，默认打开 README。

## 技术栈
- 原生 HTML / CSS / JavaScript（无构建）
- marked.js（Markdown 渲染）
- GitHub REST API
- localStorage（文章/动态/设置持久化）

## 目录结构
```
personal-site/
├── index.html        # 首页
├── blog.html         # 博客
├── projects.html     # GitHub 项目
├── personal.html     # 记录
├── space.html        # 空间分享
├── assets/
│   ├── avatar.png    # 鲨鱼帽小白熊
│   ├── hero-angel.png
│   ├── bg-sakura.mp4
│   ├── bg-galaxy.mp4
│   └── bg-wind-bell.mp4
└── README.md         # 本文件
```

## 联系
- GitHub: https://github.com/Wasd2490
- CSDN: https://blog.csdn.net/wjcjjsjs
- 邮箱: 3287316014@qq.com
