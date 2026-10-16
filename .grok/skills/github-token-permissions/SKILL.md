---
name: github-token-permissions
description: >-
  Add the missing fine-grained PAT permission when a GitHub API call returns
  403. Use when creating a repository fails with "Resource not accessible by
  personal access token", or another GitHub API says the token lacks permission.
when-to-use: >-
  403 Resource not accessible, 创建仓库失败, token permission, 令牌权限不够
---

# GitHub API 权限不足

MCP 安装和初始权限在 `github-mcp-setup`。这里只处理已经持有令牌、但某次 API 返回 403 的情况。不要读取或复述令牌。

## 创建仓库

Contents、Issues、Pull requests 不能创建仓库。`POST /user/repos` 返回 403 `Resource not accessible by personal access token` 时，在同一枚 Fine-grained token 上把 **Repository creation（仓库创建）** 设为 Read and write。

列表里没有这项时，再用 **Administration（管理）** 的写权限。它也能创建仓库，但范围更大。

权限仍在 Repository permissions 表格的 Access 下拉框里，不在 Add permission 弹出的账户权限里。用户把新令牌覆盖进原来的令牌文件，不要发到对话里。创建时不要 `autoInit`，避免和本地已有提交冲突。

## 其他 403

看响应里的 `X-Accepted-GitHub-Permissions`，或文档对应该接口要求的权限名，只补那一项。不要换成 classic token，也不要给整枚令牌开 Administration，除非没有更窄的权限。
