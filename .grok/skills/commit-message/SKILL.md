---
name: commit-message
description: >-
  Write a git commit message as a Chinese line, an English line, then a blank
  line, using a Conventional Commits prefix. Use whenever creating a git
  commit message.
when-to-use: git commit, 提交说明, commit message
---

# 提交说明

只在写 `git commit` 说明时使用。说明只记这次改了什么，不要把本技能的格式规则写进说明。

中文一行，紧接英文一行，然后空一行。不要在中英文之间再插空行。没有必要就不要正文。

```
docs: 增加提交说明技能
docs: add a commit message skill
```

多段正文时，每一段同样是中文一行、英文一行、再空一行。

使用 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 前缀。中英文两行用同一个前缀。标题用祈使句，一次提交只做一件事。

| 前缀 | 何时用 |
|---|---|
| feat | 新功能 |
| fix | 修复 |
| docs | 只改文档 |
| refactor | 改结构，不改行为 |
| test | 测试 |
| chore | 仓库杂务、约定、配置 |

仓库自身的文档和约定用 `docs` 或 `chore`。不写本机路径、用户名和令牌。
