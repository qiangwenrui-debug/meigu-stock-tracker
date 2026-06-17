# AI 供应链股票追踪 · 自动更新网站

这套文件部署到 GitHub 后，会变成一个**公开网址**，并由 GitHub 自己的服务器在每个交易日**自动刷新两次**（盘前 / 盘后），无需你手动操作。

包含文件：
- `index.html` —— 页面本身（初始为快照，部署后会被自动覆盖更新）
- `generate.py` —— 抓取行情并重新生成 `index.html` 的脚本
- `requirements.txt` —— 脚本依赖（yfinance）
- `.github/workflows/update.yml` —— 定时运行脚本的 GitHub Actions 工作流

---

## 部署步骤（一次性，约 5 分钟）

### 1. 注册并新建仓库
- 没有账号就先到 https://github.com 注册（免费）。
- 右上角 “+” → **New repository**。
- 名字随便起，例如 `ai-stock-tracker`；可见性选 **Public**（公开，Pages 免费版需要公开）。
- 点 **Create repository**。

### 2. 上传这些文件
- 在仓库页点 **Add file → Upload files**。
- 把本文件夹里的 `index.html`、`generate.py`、`requirements.txt` 以及 `.github` 整个文件夹一起拖进去（拖文件夹会保留子目录结构）。
- 如果拖文件夹不成功，就手动建工作流：点 **Add file → Create new file**，文件名一栏输入 `.github/workflows/update.yml`，把 `update.yml` 的内容粘进去保存。
- 下方 **Commit changes** 提交。

### 3. 打开 Pages（拿到网址）
- 仓库 **Settings → Pages**。
- Source 选 **Deploy from a branch**，分支选 **main**，目录选 **/ (root)**，点 **Save**。
- 等一两分钟，这页顶部会出现你的公开网址，形如：
  `https://你的用户名.github.io/ai-stock-tracker/`

### 4. 给工作流写入权限（关键）
- 仓库 **Settings → Actions → General**。
- 拉到底 **Workflow permissions**，选 **Read and write permissions**，保存。
- （否则自动更新时无法把新文件提交回仓库。）

### 5. 先手动跑一次测试
- 仓库 **Actions** 标签 → 若提示启用 workflow 就点启用。
- 左侧选 **Update tracker** → 右侧 **Run workflow** → 确认运行。
- 跑完（绿勾）后刷新你的网址，数据就更新成最新的了。

完成！之后它会在每个交易日自动更新两次。

---

## 自动刷新时间
工作流用 UTC 时间，换算成北京时间约为：
- **北京时间 21:00**（美股盘前）
- **次日 05:00**（美股收盘后）

## 修改观察列表
打开 `generate.py`，在最上方 `TICKERS` 里增删股票即可（按 `{"t": 代码, "n": 名称, "note": 备注}` 格式），提交后下次运行生效。

## 小提示
- GitHub Actions 的定时任务在高峰期可能延迟几分钟，属正常。
- 数据来自 Yahoo Finance（yfinance），偶尔某只取不到会显示 “—”，下次运行通常恢复。
- 仅供参考，不构成投资建议。
