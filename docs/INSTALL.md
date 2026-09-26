# 安装与主机验收

## 支持范围

这是技术预览版，安装成功不等于自动提醒已就绪。需要本机 Python 3.10+、支持插件及 hooks 的 Codex，并由使用者信任两个 MicroMove hooks。组织策略禁止 hooks 时，插件不能绕过限制。

| 环境 | 当前证据 |
| --- | --- |
| macOS Codex CLI 0.155.0-alpha.16.4 | 两个 hooks 已授权，真实主机自动提醒可见 |
| Codex 桌面应用 | 需要在新任务执行下方验收；CLI 成功不能代替桌面验收 |
| Windows / Linux | Python 引擎旧版六组 CI 通过；真实宿主集成仍待验证 |
| Claude Code | 兼容清单已有，实际宿主验收待完成 |

## 换一台电脑安装

1. 获取仓库副本。当前 GitHub 仓库是私有的，需作者授予访问权限；也可使用作者提供的源码压缩包。不要复制作者的绝对路径或 Codex 配置。
2. 在终端确认 `python3 --version` 为 3.10 或以上。Windows 当前 hooks 也调用 `python3`，仅能执行 `python` 不代表自动 hooks 可用；这一情况属于未支持的安装，先修正 Python 的 PATH，再验收。不要只因为手动 demo 可用就宣布安装成功。
3. 用 Codex 打开源码目录，请求：“将这个 MicroMove 本地插件加入我的个人插件市场，保留已有条目，安装后引导我审核 hooks。”若有 plugin-creator 技能，可按其标准流程安装。当前尚无面向所有电脑的一键安装器。
4. 只有该电脑的个人市场已注册本插件后，才能执行 `codex plugin add micromove@personal`。确认插件为 enabled。
5. 在 Codex CLI 输入 `/hooks`，分别审核 **SessionStart** 和 **Stop** 中来源为 `micromove@personal` 的命令。应为缓存目录内 `scripts/micromove.py hook`，超时 3 秒。信任后两项都应显示 Active 1；只安装或启用插件不会自动授予信任。
6. 在 Codex 桌面应用中新开任务，再执行下面的安装检查。如果仍未显示，核对应用与 CLI 是否使用相同账户、机器和 Codex 配置；必要时重新打开应用。不要反复手动运行 hook 来伪装成功。

## 每位用户都要完成的安装检查

在新任务发送：

> 用 MicroMove 检查安装，运行 doctor，然后运行 probe。请让真实的回复结束事件触发检查，不要手动执行 hook 或 check。

应当在这次回复结束或下一次会话开始时，看到：

> MicroMove 安装检查通过：已收到 Stop（或 SessionStart）事件。

`doctor` 检查 Python 和状态存储，显示最近一次事件记录；它无法读取或证明宿主的当前信任状态，也无法确认用户看到了消息。`probe` 是一次诊断消息，不会开启提醒或消费已有计划。看到宿主实际显示的消息后，才算自动触发验收通过。

随后发送“开启 MicroMove 提醒”，再发送“1 分钟后提醒”。一分钟后继续对话，观察真实提醒；继续对话应不重复；发送“暂停 MicroMove 提醒”后应保持安静。不要用 `check` 预览，它会消费提醒。

没有主机事件时不会准点响铃。此版本不能作为后台闹钟使用。

## 故障排查

| 现象 | 检查与处理 |
| --- | --- |
| 找不到 Python / 命令退出非零 | 安装 Python 3.10+ 并确认宿主 PATH 可执行 python3 |
| 插件找不到 | 检查该电脑的市场注册和插件 enabled 状态 |
| 配置保存了但没有消息 | `/hooks` 核对两项 Active；再用 probe 验收 |
| probe 一直 pending | 尚未收到有效事件，检查信任、安装缓存及宿主支持 |
| last_hook 有记录但界面没显示 | 记录只证明脚本运行过，继续核对事件时间、缓存路径和当前宿主界面 |
| 到点没有聊天也没响 | 属于事件式设计限制，不是后台定时器 |
| 数据存储报错 | 检查报错中的目录权限和磁盘空间；不要删除数据库来掩盖问题 |

## 更新与卸载

Codex 安装的是缓存副本。开发时按 plugin-creator 的 cachebuster 流程更新版本，再安装并新开任务。更新可能重新要求审核 hooks，重复安装验收，不要修改宿主信任文件或使用跳过信任的开关。

卸载可用插件界面，或当前版本 CLI 的 `codex plugin remove micromove@personal`。先暂停提醒即可停止提醒；卸载保留 `~/.micromove` 的个人设置。

官方依据：[Codex hooks 与信任机制](https://learn.chatgpt.com/docs/hooks)。
