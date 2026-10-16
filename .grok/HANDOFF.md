# 交接

## 已经定了的事

- 仓库 `ClashOfClans_Auto` 是公开的。
- 长期规矩在 `AGENTS.md`。GitHub 相关操作分在四个技能：`github-mcp-setup`、`github-token-permissions`、`git-push-auth`、`commit-message`。
- 包代码放在 `src/clashofclans_auto/`，测试放在 `tests/`。
- 工程不绑定单一 Python 版本。各台电脑的解释器写在本机 `.grok/machine.local.md`。代码保持与 `pyproject.toml` 的 `requires-python`（`>=3.12`）兼容。
- 每台电脑只保留一份检出，放在 Windows 用户的 `workspace_p`。Grok 留在 WSL，用挂载路径打开这一份。
- 游戏跑在 Windows 官方客户端。核心是程序自己完成家乡里的基础任务：回到家乡，收取已就绪的收集器，认不出就停。AI 辅助和人类行为对比是加分项。
- 第一步只记录人的操作，不自动点击。

## 现在停在哪

- 已确认能截到官方客户端的真实家乡画面。游戏窗口标题以「部落冲突」或「Clash of Clans」开头。
- 只读记录器会把客户区内的按下、拖动采样和松开写入被忽略的 `recordings/`。按下时保存窗口截图。它不点击，也不记录键盘。
- 结束记录用 Ctrl+C，或在该次会话目录里创建 `STOP`。
- `main` 最新提交是 `9e35700`。

## 下一步

- 打开官方客户端后开始一次记录。人在家乡关掉挡路弹窗，并收取已经就绪的收集器。
