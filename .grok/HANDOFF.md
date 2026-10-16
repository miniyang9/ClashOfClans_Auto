# 交接

## 已经定了的事

- 仓库 `ClashOfClans_Auto` 是公开的。
- 长期规矩在 `AGENTS.md`。GitHub 相关操作分在四个技能：`github-mcp-setup`、`github-token-permissions`、`git-push-auth`、`commit-message`。
- 包代码放在 `src/clashofclans_auto/`，测试放在 `tests/`。
- 工程不绑定单一 Python 版本。各台电脑的解释器写在本机 `.grok/machine.local.md`。代码保持与 `pyproject.toml` 的 `requires-python`（`>=3.12`）兼容。
- 每台电脑只保留一份检出，放在 Windows 用户的 `workspace_p`。Grok 留在 WSL，用挂载路径打开这一份。

## 现在停在哪

- 环境已经就绪，还没有功能代码。
- `main` 最新提交是 `fb80d51`。

## 下一步

- 等第一个功能任务。
