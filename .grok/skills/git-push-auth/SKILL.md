---
name: git-push-auth
description: >-
  Push over HTTPS when the GitHub API accepts a PAT but git push says invalid
  credentials, and set a repo-local commit identity when Git has none. Use when
  git push authentication fails or git commit complains that user.name or
  user.email is missing.
when-to-use: >-
  git push invalid credentials, could not read Username, 推送认证失败, user.name
---

# Git 推送认证

API 能用这枚令牌、但 `git push` 报 `invalid credentials` 或 `could not read Username` 时，令牌多半有效。Git for Windows 自带的凭据助手会和另加的 `Authorization` 头冲突。不要把令牌写进 remote URL，也不要读取或复述令牌。

推送时关掉凭据助手。用户名用 `x-access-token`，密码用这枚 PAT。`GIT_TERMINAL_PROMPT=0`，避免弹出登录框卡住。

执行 `git` 的进程必须读得到令牌文件。WSL 里的路径在 Windows 的 `git.exe` 中可能时好时坏。读不到时，把令牌拷到该进程看得见的临时文件，推送结束后立刻删除。

这台电脑的 Git 还没有 `user.name` 或 `user.email` 时，只在当前仓库设置提交身份，不要改全局配置。没有把握时向用户确认名字和邮箱。
