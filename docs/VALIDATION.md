# 验证记录 · 2026-09-25

本次实际完成：

- Python unittest：9 / 9 通过。
- 插件创建技能的 manifest 校验：通过。
- skill frontmatter 校验：通过。
- Codex CLI 安装：成功，personal / micromove / 0.1.0。
- 提醒开关、时间配置、snooze、完成、入口 URL 的 CLI 生命周期通过。
- 16 个并发检查只消费一次到期提醒。
- 畸形事件输入和 Stop 重入输入返回空 JSON，退出码为 0。

尚未验证：

- 真实 Codex 新任务中信任 hooks 后的自动消息可见性。
- Claude Code 主机加载和 UI 展示。
- Windows / Linux 的实际主机兼容性（已配置 CI 矩阵，不等于已运行）。
- 团队跟练网页接入、原生按钮、桌面小组件和空闲定时。

单元测试使用临时目录，不启用用户的真实提醒。默认仍为关闭。

补充：从真实 hook 子进程输入合法 Stop 事件，首次仅输出 systemMessage，第二次为空；测试标记未写入数据库。仍属于模拟事件，不替代主机 UI 验收。
