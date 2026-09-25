# 第一个 GitHub 项目的维护方式

仓库名采用 `micromove`。先以私有仓库开发，团队确认公开范围及许可证后再公开。个人负责的插件代码与团队现有网页保持独立。

推荐每天完成一小块可验证的改动再提交，例如 `feat: add reminder snooze`、`fix: prevent duplicate reminders`、`docs: explain installation`。不要把实际未完成的功能写进提交说明。

首次同步说明：这次通过已登录的浏览器上传。远端提交历史与本机最初的两个提交不同；终端 GitHub 登录尚未配置。配置 Git 登录后，应先将远端仓库 clone 到一个新目录并作为后续工作副本，保留原目录作为备份。不要直接对当前本机 main 强制推送，以免覆盖远端历史。下面日常流程适用于新的 clone。

日常流程：

```bash
git status
git switch -c feat/your-feature
# 修改与测试
python3 -m unittest discover -s tests -v
git add <这次修改的文件>
git commit -m "feat: describe the working change"
git push -u origin feat/your-feature
```

在 GitHub 创建 Pull Request，写明问题、变化和测试。合并后回 main，再开始下一项。仓库里的 Actions 会在远端提交后运行测试；本地通过不代表远端已经通过。

建议下一批 Issues：

- 完成 Codex hooks 真实主机验收并记录版本。
- 取得团队部署 URL，约定跟练深链接。
- 比较 Claude Code 的提醒显示和安装体验。
- 决定是否加入独立调度器以支持空闲时准点提醒。
- 做双按钮交互并完成 3–5 人试用。

项目展示时重点讲清楚：用户问题、为什么选 Codex、哪些限制迫使你调整架构、实际测试覆盖了什么。不要把技术预览包装为完整上架产品。
