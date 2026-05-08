# Security Policy

## Supported Versions

当前仓库处于原型阶段，默认只维护 `main` 分支。

## Reporting a Vulnerability

如果你发现安全问题，请通过 GitHub issue 描述问题。请尽量包含：

- 影响范围
- 复现步骤
- 你预期的安全行为
- 实际发生的问题

请不要在 issue 中公开 API key、真实个人照片、隐私数据或可被滥用的敏感细节。

## Current Protections

- 默认运行模式不依赖外部 API。
- 图片输入会检查扩展名、大小和文件头签名。
- `OPENAI_API_KEY` 只从环境变量读取，不会写入输出文件。
- GitHub Actions 使用只读仓库权限。

更完整的安全与隐私说明请看 [docs/security.md](docs/security.md)。
