# 工程约定

这些规矩与具体电脑无关。用户名、家目录、解释器路径和版本一律在当前电脑上现查，不要沿用其他会话或另一台电脑里出现过的路径。

## 工程放在哪里

- Python 工程放在 Windows 用户配置文件下的 `workspace_p` 目录。先查出当前 Windows 用户的配置文件路径，再使用其下的 `workspace_p`。
- 从 WSL 协助时，不要把工程源码写进 WSL 的家目录。WSL 里用挂载路径访问上面那个 Windows 目录。
- 目录不存在就创建。不要猜盘符或用户名。

## 在哪里执行

- 创建工程、安装依赖、运行、测试和提交，使用 Windows 的 Python 和 Git。
- 先确认 Windows 上对应的可执行文件能运行，并记下实际版本。有多个 Python 时，向用户确认用哪一个，不要自行选定。
- WSL 里的 `python` 和 `git` 只用于 WSL 自己的文件。调用 Windows 程序时使用 Windows 可执行文件，或通过 `powershell.exe` 调用。
- 路径在 WSL 与 Windows 之间转换时使用 `wslpath`，不要手写盘符。

## GitHub

- 代码用 Git 推送到 GitHub。已配置 GitHub MCP 时，用它做仓库、Issue 和 Pull Request 操作。
- 令牌、`auth.json`、`mcp_credentials.json` 和 `.env` 只留在本机，不写入仓库，也不写进会提交的文档。
- 另一台电脑需要自己的令牌和 MCP 配置。不要复制或提交本机令牌文件。

## 交接

- 用户要接着做已有任务时，若存在 `HANDOFF.md`，先读它。文件不存在就当没有未完成任务。
- 任务过程只写在 `HANDOFF.md`。不要把讨论细节写进本文件或技能。

## 会话里的旧事实

- 对话、导出记录和 memory 里出现的主机名、用户名、绝对路径、软件版本，只对记录它们的那台电脑有效。
- 在一台新电脑上开始工作前，重新检测 Windows 用户配置文件、`workspace_p`、Python 和 Git。检测结果写在本机的 `machine.local.md`，该文件不提交。
