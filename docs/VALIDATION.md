# 验证记录 · 2026-09-25

## 实际完成

- Python unittest：10 / 10 通过。
- 插件 manifest 校验及 skill frontmatter 校验通过。
- Codex CLI 安装成功；编码修复后已重新安装缓存版本 `0.1.0+codex.20260925182559`。
- [GitHub Actions #4](https://github.com/EmmaZhao422/micromove/actions/runs/36173470228)：提交 `6077ec6` 的六组任务全部成功。覆盖 Ubuntu、macOS、Windows × Python 3.10、3.13，每组运行 10 项测试。
- 提醒开关、时间配置、snooze、完成、入口 URL 的 CLI 生命周期通过。
- 16 个并发检查只消费一次到期提醒。
- 畸形事件输入及 Stop 重入返回空 JSON、退出码 0。
- 合法 Stop 子进程首次仅输出 systemMessage，第二次为空；测试对话标记未写入数据库。

## 本次修复

第一轮 CI 发现 Windows 默认字符编码无法输出中文，导致 CLI 和 hook 进程报错。现在标准输入/输出/错误统一使用 UTF-8，测试显式按 UTF-8 解码，并新增 `PYTHONIOENCODING=cp1252` 的回归用例。修复后六组 CI 全部通过。

CI 仍提示 checkout/setup-python 使用旧 Node 声明，目前 GitHub 强制在 Node 24 下运行；属于依赖维护事项，不是本轮测试失败。

## 尚未验证

- 真实 Codex 新任务中信任 hooks 后的自动消息可见性。
- Claude Code 主机加载和 UI 展示。
- Windows / Linux 的实际 Codex 或 Claude 主机集成（CLI 测试通过不等于主机体验通过）。
- 团队跟练网页接入、原生按钮、桌面小组件和空闲定时。

单元测试使用临时目录，不启用用户的真实提醒。主机事件仍是模拟输入，不能替代界面验收。
