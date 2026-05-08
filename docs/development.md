# Development Guide

## 本地检查

修改 Python 代码后，至少运行：

```bash
python3 -m py_compile multi_agent_poster_system.py
python3 -m py_compile script_to_video_prompt_workflow.py
```

建议再运行一次烟雾测试：

```bash
printf 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=' | base64 -d > ci.png
python3 multi_agent_poster_system.py --image ci.png --theme ci-smoke --out outputs/ci
test -f outputs/ci/pipeline_result.json
python3 script_to_video_prompt_workflow.py --script examples/sample_script.txt --title ci-video --out outputs/video-ci
test -f outputs/video-ci/video_workflow_result.json
python3 script_to_video_prompt_workflow.py --script examples/sample_script.txt --quality-mode high --target-model sora --aspect-ratio 9:16 --out outputs/video-high-ci
test -f outputs/video-high-ci/production_brief.md
```

## CI

GitHub Actions 位于 `.github/workflows/python-ci.yml`，当前会执行：

- Python 编译检查
- 海报工作流最小 PNG 输入 smoke test
- 视频工作流示例剧本 smoke test
- 视频工作流快速模式和高质量模式检查
- 敏感 token、异常扩展名和参数校验检查
- `pipeline_result.json` 和 `video_workflow_result.json` 输出检查

## 目录约定

```text
.
├── .github/                 # GitHub 工作流、Issue 模板、PR 模板
├── docs/                    # 详细文档
├── examples/                # 示例输入
├── multi_agent_poster_system.py
├── script_to_video_prompt_workflow.py
├── README.md                # 项目入口和文档导航
├── CONTRIBUTING.md          # 贡献入口
├── CODE_OF_CONDUCT.md       # 社区行为准则
├── SECURITY.md              # 安全策略入口
└── LICENSE
```

## 提交建议

- 每次提交聚焦一个主题。
- 文档改动、CI 改动、功能改动尽量拆开。
- 不提交 `outputs/`、`.env`、API key、真实肖像或临时测试文件。
- 修改 README 的命令时，同步检查 `docs/usage.md` 和 CI。
- 修改脚本入口文件名时，同步检查 README、文档和工作流。
- 新增工作流时，同步更新示例、docs、README 和 CI。
- 新增 CLI 参数时，同步更新 docs/video-workflow.md 和 CI 覆盖。

## PR 检查清单

- [ ] README 或 docs 已同步更新
- [ ] 本地编译检查已通过
- [ ] 如涉及运行逻辑，已跑 smoke test
- [ ] 没有提交敏感信息或输出目录
- [ ] PR 描述包含修改原因和验证方式
