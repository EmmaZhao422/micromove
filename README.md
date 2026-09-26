# MicroMove · 回个电 🔋

Gentle, local work-break reminders for Codex. 在工作间隙，给自己充一点电。

**v0.1.0 技术预览** · Python 3.10+ · 零第三方依赖 · 默认关闭 · 数据仅保存在本机

探索如何让 AI 编程工具在自然停顿时提供轻量运动提醒。主要目标平台为 Codex；附带 Claude Code 兼容清单，尚未完成 Claude 主机实测。

## 已实现

- 默认 11:00 / 16:00 的事件式提醒，可自定义时间。
- 开启、暂停、稍后提醒、手动预览和完成确认。
- `doctor` 安装诊断与 `probe` 真实事件验收，避免把配置成功误报成提醒就绪。
- 多任务共用状态，避免同一时段重复提醒。
- 配置团队跟练网页入口；不捏造动作库，不生成运动处方。
- Codex 插件 manifest、skill、SessionStart / Stop hooks。

**范围说明：**没有主机事件时不会准点响铃。提醒在计划时间之后 30 分钟内遇到事件时触发；过期不补发。稍后提醒在到期后的下一次事件触发。当前显示的是主机消息和对话选项，尚无原生双按钮或桌面小组件。它不检测真实坐姿、久坐时长或身体活动。

## 一分钟运行

从本仓库根目录运行：

```bash
python3 scripts/micromove.py doctor
python3 scripts/micromove.py demo
python3 scripts/micromove.py enable
python3 scripts/micromove.py configure --times 11:00 16:00
python3 scripts/micromove.py snooze 10
python3 scripts/micromove.py status
python3 scripts/micromove.py pause
```

Windows 手动运行 CLI 可用 `python` 替代 `python3`；自动 hooks 当前要求 `python3` 在宿主 PATH 中可用，完整安装仍需验收。时间采用电脑当前本地时区，变更时区后随系统切换。

`demo` 只预览；`check` 会消费当前到期提醒。`start` 返回跟练链接，`done` 仅在用户主动确认后使用。配置真实团队网址：`configure --url <网址>`，支持 HTTPS 或 localhost HTTP。未配置时不会打开一个假地址。

## 在当前作者电脑上使用 Codex

插件已通过 personal marketplace 安装。新开一个 Codex 任务，使用：

> 用 MicroMove 开启工作间隙提醒。

> 用 MicroMove 演示一次提醒。

> 10 分钟后提醒我。 / 暂停 MicroMove 提醒。

自动触发前需要在 Codex 的 hooks 管理界面检查并信任插件 hooks；安装不等于信任。查看 [安装与验收](docs/INSTALL.md)。当前安装命令是 `codex plugin add micromove@personal`，它依赖已注册的个人市场，**不能在其他电脑上直接照抄并期望成功**。

## 项目结构

```text
.codex-plugin/plugin.json    Codex 插件入口
.claude-plugin/plugin.json   Claude Code 兼容入口（待主机验证）
hooks/hooks.json            自然停顿事件
skills/micromove/SKILL.md    对话操作说明
scripts/micromove.py         本机状态与提醒判断
tests/test_engine.py        行为与并发测试
docs/                       开发规划、安装验收、GitHub 指南
```

运行测试：`python3 -m unittest discover -s tests -v`。

## 文档

- [技术可行性与开发规划](docs/TECHNICAL_PLAN.md)
- [安装和主机验收](docs/INSTALL.md)
- [第一个 GitHub 项目怎么维护](docs/GITHUB_GUIDE.md)
- [测试结果与限制](docs/VALIDATION.md)

## 隐私与授权

只保存开关、计划时间、跟练 URL、稍后时间、去重键、待执行的安装检查，以及最近一次 hook 的事件名、时间和脚本路径，位置为 `~/.micromove/state.sqlite3`。测试可设置 `MICROMOVE_DATA_DIR`。没有遥测、API key、第三方请求或代码/对话采集。插件不会自行开启后台任务。移除插件不会删除个人设置。

本仓库不包含团队原始需求文档、问卷、会议纪要或动作图片。当前未授予开源许可证；公开发布及团队资产的再分发需另行确定。
