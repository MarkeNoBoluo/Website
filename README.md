# Personal Blog

基于 Flask 的个人博客系统，运行于 Raspberry Pi 4B，支持文章管理与艾森豪威尔矩阵任务管理。

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | Flask 3.1.3 |
| WSGI 服务器 | Gunicorn 21.2.0 |
| 数据库 | SQLite + SQLAlchemy |
| 密码加密 | Flask-Bcrypt |
| Markdown 渲染 | mistune + Pygments |
| 中文转拼音 | pypinyin |

## 功能模块

### 1. 博客模块 (`app/blog/`)

公开的博客文章展示系统。

**路由：**
- `GET /blog/` - 文章列表页（仅显示已发布文章）
- `GET /blog/<slug>` - 文章详情页

**功能：**
- Markdown 文章渲染，支持代码语法高亮（Monokai 风格）
- 自动从内容提取摘要
- 文章缓存（`@lru_cache`）

**数据模型：**
```python
Article:
  - id, title, content, slug, status (draft/published)
  - created_at, updated_at
```

---

### 2. 任务管理模块 (`app/todo/`)

艾森豪威尔矩阵私人任务管理工具，需登录访问。

**路由：**
- `GET /todo/` - 矩阵视图，按四象限分组展示任务
- `GET/POST /todo/add` - 新增任务
- `GET/POST /todo/<id>/edit` - 编辑任务
- `POST /todo/<id>/delete` - 删除任务
- `POST /todo/<id>/toggle` - 切换完成状态
- `POST /todo/<id>/move` - 移动到其他象限
- `POST /todo/<id>/reorder` - 更新优先级

**艾森豪威尔矩阵：**
```
        | 紧急           | 不紧急
--------|----------------|----------------
 重要   | Q1: 立即处理    | Q2: 计划安排
--------|----------------|----------------
 不重要 | Q3: 委托他人    | Q4: 删除
```

**数据模型：**
```python
Todo:
  - id, user_id, title, description
  - quadrant (1-4), priority (1-5, 1为最高)
  - due_date, completed
  - created_at, updated_at
```

---

### 3. 认证模块 (`app/auth/`)

基于 Session 的用户认证系统。

**路由：**
- `GET/POST /auth/login` - 用户登录
- `GET/POST /auth/logout` - 用户登出

**功能：**
- Bcrypt 密码哈希
- Session 存储（浏览器关闭后失效）
- `@login_required` 装饰器保护路由

**数据模型：**
```python
User:
  - id, username, password_hash
  - created_at, updated_at
```

---

### 4. 管理后台 (`app/admin/`)

文章管理与系统运维。

**路由：**
- `GET /admin/articles` - 文章列表（分页、搜索、筛选、排序）
- `GET/POST /admin/articles/new` - 创建文章
- `GET/POST /admin/articles/import` - 批量导入 Markdown 文件
- `GET/POST /admin/articles/<id>/edit` - 编辑文章
- `POST /admin/articles/<id>/delete` - 删除文章
- `POST /admin/articles/<id>/publish` - 发布文章
- `POST /admin/articles/<id>/unpublish` - 下线文章
- `POST /admin/articles/<id>/toggle-status` - 切换发布状态
- `POST /admin/preview` - Markdown 实时预览

**Slug 生成：**
- 中文标题转换为拼音
- 格式：`YYYY-MM-DD-pinyin-title`
- 自动检测并处理重复 slug

---

### 5. 核心功能

**Markdown 渲染 (`app/markdown.py`)：**
- mistune 解析 + Pygments 语法高亮
- Monokai 深色主题
- 自动检测代码语言

**CSRF 防护 (`app/utils.py`)：**
- `@csrf_protected` 装饰器保护 POST 请求
- Session 存储 token
- 模板中使用 `{{ csrf_token }}`

**健康检查：**
- `GET /health` - 返回服务状态 JSON
- `GET /db-test` - 数据库连接与 WAL 模式检测
- `GET /config-test` - 配置信息（不含敏感数据）

---

## 项目结构

```
app/
├── __init__.py          # create_app() 应用工厂
├── config.py            # 配置类（含验证）
├── extensions.py        # Flask 扩展实例
├── models.py            # 数据模型
├── utils.py             # 工具函数（CSRF、健康检查）
├── markdown.py          # Markdown 渲染
├── blog/                # 博客蓝图
│   ├── routes.py        # 路由
│   └── utils.py        # 文章获取与缓存
├── todo/                # 任务管理蓝图
│   ├── routes.py       # 路由
│   └── utils.py        # 验证、权限检查
├── auth/                # 认证蓝图
│   ├── routes.py       # 登录/登出
│   └── utils.py        # 密码哈希、@login_required
└── admin/               # 管理后台蓝图
    ├── routes.py       # 文章管理路由
    └── utils.py        # Slug 生成

posts/                   # Markdown 文章（已弃用，改用数据库）
static/                   # 静态资源
tests/                    # 测试文件
```

---

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 SECRET_KEY 等配置

# 初始化数据库
python init_db.py

# 创建管理员账户
python init_db.py --create-admin --username admin --password <password>

# 开发模式运行
flask --app app run --debug

# 生产环境运行
gunicorn -c gunicorn.conf.py
```

---

## 部署架构

```
外部用户 → Cloudflare Tunnel → Nginx (localhost:8080) → Gunicorn (Unix socket) → Flask App
```

详细部署说明见 [AGENTS.md](./AGENTS.md)。
