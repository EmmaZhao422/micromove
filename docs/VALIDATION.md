# 验证记录 · 2026-09-25

## 实际完成

- 新增安装诊断回归后，本机 Python unittest：11 / 11 通过；下面六组远端 CI 是上一版的 10 项结果，不代表本次改动已通过远端 CI。
- 插件 manifest 校验及 skill frontmatter 校验通过。
- Codex CLI 安装成功；安装诊断修复后已重新安装缓存版本 `0.1.0+codex.20260926015141`。
- [GitHub Actions #4](https://github.com/EmmaZhao422/micromove/actions/runs/36173470228)：提交 `6077ec6` 的六组任务全部成功。覆盖 Ubuntu、macOS、Windows × Python 3.10、3.13，每组运行 10 项测试。
- 提醒开关、时间配置、snooze、完成、入口 URL 的 CLI 生命周期通过。
- 16 个并发检查只消费一次到期提醒。
- 畸形事件输入及 Stop 重入返回空 JSON、退出码 0。
- 合法 Stop 子进程首次仅输出 systemMessage，第二次为空；测试对话标记未写入数据库。

## 本次修复

第一轮 CI 发现 Windows 默认字符编码无法输出中文，导致 CLI 和 hook 进程报错。现在标准输入/输出/错误统一使用 UTF-8，测试显式按 UTF-8 解码，并新增 `PYTHONIOENCODING=cp1252` 的回归用例。修复后六组 CI 全部通过。

CI 仍提示 checkout/setup-python 使用旧 Node 声明，目前 GitHub 强制在 Node 24 下运行；属于依赖维护事项，不是本轮测试失败。

## 尚未验证

- Codex 桌面应用中新任务的自动消息可见性（CLI 实测通过不替代桌面验收）。
- Claude Code 主机加载和 UI 展示。
- Windows / Linux 的实际 Codex 或 Claude 主机集成（CLI 测试通过不等于主机体验通过）。
- 团队跟练网页接入、原生按钮、桌面小组件和空闲定时。

单元测试使用临时目录，不启用用户的真实提醒。主机事件仍是模拟输入，不能替代界面验收。

## 安装失效修复与真实主机证据

用户试用失败的直接原因：SessionStart 和 Stop 均为未信任，Active 0。经用户明确授权，使用正常 /hooks 审核界面分别信任，确认两项 Active 1。随后使用独立临时状态目录启动 Codex CLI，真实会话事件显示了 `Hook · 这段忙完了吗？给自己充一点电，30 秒也可以。`，未手动调用 hook 或 check。

新增 doctor 与 probe：诊断不宣称已获宿主授权；一次检查不消费计划，pause 会取消未执行的检查。新增回归覆盖中文及空格数据路径、诊断不消费提醒、探测只执行一次、暂停取消探测、事件不保留对话字段。

更新缓存后的 probe 实测：真实 SessionStart 显示一次安装检查消息；再次设置 probe，下一轮真实 Stop 也显示安装检查消息。测试使用临时数据目录，没有修改用户原有提醒计划。
