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
python3 "multi_agent_poster_system (1).py" \
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

## 可选：使用 OpenAI API

默认模式不需要网络和 API key。如果你想让 Agent 使用 OpenAI 生成更灵活的 JSON 输出，可以安装 OpenAI Python SDK 并设置环境变量：

```bash
python3 -m pip install openai
export OPENAI_API_KEY="your_key"
python3 "multi_agent_poster_system (1).py" \
  --image ./portrait.png \
  --theme "校园剧院独唱" \
  --out ./outputs \
  --use-openai
```

不要把 API key 提交到 GitHub。

## 参数说明

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `--image` | 是 | 输入人物肖像路径，支持 JPG、PNG、WebP |
| `--theme` | 是 | 创意主题，例如 `校园剧院独唱` |
| `--out` | 否 | 输出目录，默认 `./outputs` |
| `--use-openai` | 否 | 开启 OpenAI API 模式 |
| `--model` | 否 | OpenAI 模型名，默认 `gpt-4o-mini` |

## 项目结构

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/python-ci.yml
├── multi_agent_poster_system (1).py
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── .gitignore
```

## 安全与隐私

- 输入图片只在本地按路径读取，默认不会上传到任何服务。
- `--use-openai` 开启后，文本上下文会发送给 OpenAI API；当前原型不会把图片二进制上传给 OpenAI。
- 项目会拒绝扩展名伪装的假图片文件。
- 请不要提交真实肖像、API key、输出目录、临时测试图片或 `.env` 文件。

## 贡献

欢迎提交 issue、改进提示词结构、补充测试、优化 Agent 流程或接入真实图像渲染器。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 路线图

- 增加单元测试
- 增加标准 `requirements.txt` 或 `pyproject.toml`
- 将脚本文件名整理为更适合命令行使用的 `multi_agent_poster_system.py`
- 接入真实图片生成 API
- 增加更多主题模板和输出格式

## 许可证

本项目使用 [MIT License](LICENSE) 开源，欢迎学习、复用和二次开发。
