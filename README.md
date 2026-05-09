# Multi-Agent Creative Prompt Workflows

[![Python CI](https://github.com/Rufo-zhou/rufo-/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Rufo-zhou/rufo-/actions/workflows/python-ci.yml)
[![Website](https://github.com/Rufo-zhou/rufo-/actions/workflows/pages.yml/badge.svg)](https://github.com/Rufo-zhou/rufo-/actions/workflows/pages.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License](https://img.shields.io/badge/license-MIT-black)

一个可直接运行的多智能体创作提示词工具集。当前包含两个工作流：叙事海报提示词生成，以及剧本转 AI 视频分镜提示词生成。它可以帮助创作者把“想法、肖像、剧本”整理成可交给图像模型或视频模型继续生产的结构化提示词。

## 这个工具用来做什么

这个项目适合用来做：

- 叙事型人物海报的创意策划
- 肖像照片到海报提示词的结构化转换
- 校园剧院、音乐、舞台、电影感、双重曝光等主题的视觉方案生成
- 剧本场次识别、角色识别和 AI 视频分镜提示词生成
- 人物三视图 / 角色参考图提示词生成
- AI 绘图前的 prompt 工程、负面词整理和 QA 检查
- 多智能体创作流程的 Python 原型参考

它不会直接生成图片或视频。默认模式会生成一组 JSON 分析结果、Markdown 提示词文件和模型可读的 prompt package，你可以把最终提示词复制到自己使用的图像或视频生成工具中继续出图、出片。

## 项目网站

仓库新增了一个互动展示网站：[site/](site/)。

它把项目包装成一个 AI 创作工作室入口，包含全屏 3D 视觉、剧本转分镜演示、两个工作流介绍和文档导航。发布到 GitHub Pages 后，默认访问地址为：

```text
https://rufo-zhou.github.io/rufo-/
```

本地预览：

```bash
python3 -m http.server 4173 --directory site
```

## 功能特点

- 无第三方依赖即可运行
- 支持 `.jpg`、`.jpeg`、`.png`、`.webp` 输入
- 会检查图片扩展名、文件大小和真实图片文件头
- 海报工作流支持风格预设、目标图像模型、质量模式、画幅和多变体提示词
- 内置 5 个创作 Agent：
  - Character Understanding：人物约束与气质分析
  - Theme Parsing：主题、场景、情绪、符号拆解
  - Narrative Composition：叙事构图规划
  - Prompt Engineering：最终提示词与负面词生成
  - Quality Assurance：提示词质量检查
- 新增剧本转视频工作流：
  - 自动识别剧本场次、地点、时间和角色
  - 生成可用于 Sora、Runway、Kling、Pika、Luma 等 AI 视频模型的分镜提示词
  - 生成角色三视图提示词和人物一致性规则
  - 输出视频提示词总包、分镜 Markdown 和 QA 报告
- 可选 OpenAI API 模式；不配置 API key 时使用确定性 fallback 输出
- GitHub Actions 会自动运行 Python 编译和 smoke test

## 快速开始

准备 Python 3.10 或更高版本。

```bash
git clone https://github.com/Rufo-zhou/rufo-.git
cd rufo-
python3 multi_agent_poster_system.py \
  --image ./portrait.png \
  --theme "校园剧院独唱" \
  --out ./outputs
```

运行完成后，输出目录会包含：

```text
outputs/
  01_character_analysis.json
  02_theme_analysis.json
  03_composition_plan.json
  04_visual_prompt.json
  05_qa_report.json
  06_render_info.json
  pipeline_result.json
  render_instruction.txt
  poster_prompt_package.md
  production_brief.md
```

剧本转视频分镜工作流：

```bash
python3 script_to_video_prompt_workflow.py \
  --script examples/sample_script.txt \
  --title "雨夜排练" \
  --target-model sora \
  --quality-mode high \
  --creative-style cinematic \
  --aspect-ratio 9:16 \
  --out ./outputs/video
```

需要更快出草稿时，把 `--quality-mode high` 换成 `--quality-mode fast`。

更多参数、OpenAI API 模式和输出说明请看 [docs/usage.md](docs/usage.md)、[docs/video-workflow.md](docs/video-workflow.md) 和 [docs/prompt-quality-guide.md](docs/prompt-quality-guide.md)。

## 文档导航

| 分类 | 文档 |
| --- | --- |
| 文档总览 | [docs/README.md](docs/README.md) |
| 使用说明 | [docs/usage.md](docs/usage.md) |
| 海报工作流 | [docs/poster-workflow.md](docs/poster-workflow.md) |
| 视频工作流 | [docs/video-workflow.md](docs/video-workflow.md) |
| 质量指南 | [docs/prompt-quality-guide.md](docs/prompt-quality-guide.md) |
| 架构说明 | [docs/architecture.md](docs/architecture.md) |
| 开发流程 | [docs/development.md](docs/development.md) |
| 安全与隐私 | [docs/security.md](docs/security.md) |
| 路线图 | [docs/roadmap.md](docs/roadmap.md) |
| 变更记录 | [CHANGELOG.md](CHANGELOG.md) |

## 项目结构

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/python-ci.yml
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── development.md
│   ├── poster-workflow.md
│   ├── prompt-quality-guide.md
│   ├── roadmap.md
│   ├── security.md
│   ├── usage.md
│   └── video-workflow.md
├── examples/
│   ├── README.md
│   └── sample_script.txt
├── site/
│   ├── README.md
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── multi_agent_poster_system.py
├── script_to_video_prompt_workflow.py
├── CHANGELOG.md
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── .gitignore
```

## 贡献

欢迎提交 issue、改进提示词结构、补充测试、优化 Agent 流程或接入真实图像渲染器。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [docs/development.md](docs/development.md)。

## 许可证

本项目使用 [MIT License](LICENSE) 开源，欢迎学习、复用和二次开发。
