---
name: setup-github-mcp
description: >-
  Install the official GitHub remote MCP and authenticate with a fine-grained
  PAT file. Use when grok mcp list has no github server, grok mcp doctor github
  fails, GitHub MCP reports auth required or auth failed, or the user asks to
  install or fix GitHub MCP.
when-to-use: >-
  github mcp missing, auth failed, auth required, 安装 GitHub MCP, 修复 GitHub 认证
---

# 安装 GitHub MCP

先检查，已经可用就停止。不要重复安装，也不要读取或复述令牌。

```bash
grok mcp list
grok mcp doctor github
```

`doctor` 显示 handshake OK 且能发现工具时，什么都不用做。

## 还没有服务器时

只用官方远程服务 `https://api.githubcopilot.com/mcp/`。不要安装已停更的 `@modelcontextprotocol/server-github`。

```bash
mkdir -p ~/.config/github
chmod 700 ~/.config/github
grok mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "X-MCP-Toolsets: repos,issues,pull_requests,actions"
```

在 `~/.grok/config.toml` 的 `[mcp_servers.github]` 中保留上面的 url 和 header，并设置：

```toml
bearer_token_file = "~/.config/github/grok-mcp-token"
```

不要在配置里写 `Authorization` 头，空的也会阻止正确认证。

## 令牌

请用户在浏览器创建 Fine-grained personal access token：`https://github.com/settings/personal-access-tokens/new`。不要用 Tokens (classic)。classic 只有 `repo` 勾选，没有下面这些权限名。

权限在 **Repository permissions（存储库权限）** 表格里，改每行的 Access。不要在 **Add permission** 弹出的账户权限里找，那边是 Email、Profile、Gists。

| 名称 | 中文界面可能显示 | 设置 |
|---|---|---|
| Contents | 内容 | Read and write |
| Issues | 议题 | Read and write |
| Pull requests | 拉取请求 | Read and write |
| Metadata | 元数据 | Read-only，通常已经勾上 |
| Actions | 操作 | 先不设。需要看 CI 时再改成 Read-only |

Account permissions 和 Organization permissions 留空，除非保存时 GitHub 明确要求。先选好 Repository access，再改这些下拉框。

用户自己把令牌写入文件。助手不代写、不读取、不把令牌放进对话、仓库或 `machine.local.md`。

```bash
umask 077
printf '%s' '令牌' > ~/.config/github/grok-mcp-token
chmod 600 ~/.config/github/grok-mcp-token
```

## 认证失败时

在 `/mcps` 里按 `i` 不会弹出浏览器。GitHub 没有客户端自动注册接口，结果是 `auth failed`。不要再按 `i`。

服务器已在配置里但仍提示需要认证时，只补令牌文件和 `bearer_token_file`，不要再执行一次 `grok mcp add`。

令牌写好后必须退出 Grok 进程再打开。已经连过一次的会话只刷新 `/mcps` 不够，会继续显示需要认证。

重启后再次运行 `grok mcp doctor github`。握手成功并发现工具后，把令牌文件路径（不含令牌内容）记入本机的 `machine.local.md`。
