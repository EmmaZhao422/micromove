# 安装与主机验收

## 本机结果

2026-09-25 已执行 `codex plugin add micromove@personal`，成功安装到 Codex 的 personal 插件缓存。源码位于工作目录 `micromove`。个人市场以 `~/plugins/micromove` 的软链接访问源码；只提交仓库内容，不提交个人市场配置。

当前运行时 `codex-cli 0.155.0-alpha.16.4`，`hooks` 和 `plugins` 功能为 true。这不是所有 Codex 版本的保证。

## 首次试用

1. 在 Codex 插件界面找到 MicroMove，确认启用。
2. 在 hooks 管理界面查看并信任本插件定义。需要执行的命令只有 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/micromove.py" hook`，事件为 SessionStart 和 Stop。Codex 文档说明提供该兼容环境变量。
3. 新建任务，让 Codex “用 MicroMove 演示一次提醒”，再“开启提醒”。
4. 把时间临时设为当前分钟，在该时段内结束一次回复，观察消息；再次结束回复应不重复。
5. 执行“10 分钟后提醒”，到期后产生新事件验证；“暂停提醒”后应保持安静。
6. 恢复 11:00 / 16:00。没有主机事件时不会响铃。

不能用手动脚本输出代替第 4 步的真实界面证据。信任是宿主安全机制，本项目不通过修改信任文件来绕过。

## 在其他电脑

可先 clone 仓库并按 README 运行 CLI。Codex 安装需把本插件加入该电脑的本地插件市场；本版本尚未提供跨机器一键市场安装器。可以在 Codex 请求“使用 plugin-creator 技能把这个本地插件加入个人市场”，保留现有市场条目。不要直接复制作者的绝对路径。

Claude Code 可按其官方本地插件开发流程加载仓库，但当前只有清单与事件配置准备好，尚未通过实际主机验收。

## 开发后更新

Codex 安装的是缓存副本。使用插件创建技能的 cachebuster 更新脚本，然后重新执行 `codex plugin add micromove@personal`，新任务试用。不要只修改源码后就认为已安装副本同步了。

卸载：`codex plugin remove micromove@personal`（以当前 CLI help 为准）。也可以在插件界面卸载。暂停提醒可先运行 CLI `pause`。本机设置保留在 `~/.micromove`，以便重新安装；如需清除，由用户明确决定。
