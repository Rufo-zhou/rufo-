# Multi-Agent Narrative Poster Automation System

[![Python CI](https://github.com/Rufo-zhou/rufo-/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Rufo-zhou/rufo-/actions/workflows/python-ci.yml)

一个可直接运行的多智能体叙事海报生成辅助工具。它接收一张人物肖像和一个创意主题，自动完成角色理解、主题拆解、叙事构图、图像生成提示词整理和质量检查，帮助创作者把“想法”整理成可用于 SDXL、Midjourney、DALL-E、ComfyUI 等图像模型的高质量海报提示词。

## 这个工具用来做什么

这个项目适合用来做：

- 叙事型人物海报的创意策划
- 肖像照片到海报提示词的结构化转换
- 校园剧院、音乐、舞台、电影感、双重曝光等主题的视觉方案生成
- AI 绘图前的 prompt 工程、负面词整理和 QA 检查
- 多智能体创作流程的 Python 原型参考

它不会直接生成图片。默认模式会生成一组 JSON 分析结果和 `render_instruction.txt`，你可以把最终提示词复制到自己使用的图像生成工具中继续出图。

## 功能特点

- 无第三方依赖即可运行
- 支持 `.jpg`、`.jpeg`、`.png`、`.webp` 输入
- 会检查图片扩展名、文件大小和真实图片文件头
- 内置 5 个创作 Agent：
  - Character Understanding：人物约束与气质分析
  - Theme Parsing：主题、场景、情绪、符号拆解
  - Narrative Composition：叙事构图规划
  - Prompt Engineering：最终提示词与负面词生成
  - Quality Assurance：提示词质量检查
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
```

更多参数、OpenAI API 模式和输出说明请看 [docs/usage.md](docs/usage.md)。

## 文档导航

| 分类 | 文档 |
| --- | --- |
| 文档总览 | [docs/README.md](docs/README.md) |
| 使用说明 | [docs/usage.md](docs/usage.md) |
| 架构说明 | [docs/architecture.md](docs/architecture.md) |
| 开发流程 | [docs/development.md](docs/development.md) |
| 安全与隐私 | [docs/security.md](docs/security.md) |
| 路线图 | [docs/roadmap.md](docs/roadmap.md) |

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
│   ├── roadmap.md
│   ├── security.md
│   └── usage.md
├── multi_agent_poster_system.py
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
