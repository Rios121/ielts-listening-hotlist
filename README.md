# ielts-listening-hotlist

一个 Claude Code skill：把**实时更新的七天热榜听力题库**，自动整理成雅思听力备考速查笔记。

## 能做什么

按 Part 类型，用最贴合考场的总结方式：

- **P1（填空）**：答案词速查 + 滚动词表——直接记住要听出哪些词
- **P2/P3（选择+匹配）**：题干中文翻译 + **信号词**（听到哪个词就选哪个）+ **坑**（陷阱规律）+ 同义替换
- **P4（填空）**：**题干 + 答案词 + 听力原句**逐题精听，对照笔记空格定位，附关键词滚动

文档目录可点击跳转，还能一键导出 Word 方便打印。

## 一键安装

**Windows（PowerShell）**：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
git clone https://github.com/Rios121/ielts-listening-hotlist.git "$env:USERPROFILE\.claude\skills\ielts-listening-hotlist"
```

**macOS / Linux**：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Rios121/ielts-listening-hotlist.git ~/.claude/skills/ielts-listening-hotlist
```

装好后在 Claude Code 里运行 `/reload-skills`（或重启会话）。

## 使用

输入 `/ielts-listening-hotlist`，或直接说「抓一下雅思听力热榜」，Claude 会自动抓取最新七天热榜、整理成文档。

依赖：Python 3（转 Word 需 `pip install python-docx`）+ 联网 + Claude Code。

## 免责声明

本工具只提供代码与文档，**不含任何第三方版权内容**。数据由使用者从自己已获授权的平台即时获取，仅供个人学习。使用者需自行确认符合所在地法律及数据源的服务条款，责任自负。MIT 许可证仅覆盖本仓库代码与文档。
