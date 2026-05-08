# Usage Guide

## 环境要求

- Python 3.10 或更高版本
- 默认模式不需要第三方依赖
- OpenAI API 模式需要安装 `openai` Python SDK

## 海报提示词工作流

```bash
git clone https://github.com/Rufo-zhou/rufo-.git
cd rufo-
python3 multi_agent_poster_system.py \
  --image ./portrait.png \
  --theme "校园剧院独唱" \
  --out ./outputs
```

## 参数说明

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `--image` | 是 | 输入人物肖像路径，支持 JPG、JPEG、PNG、WebP |
| `--theme` | 是 | 创意主题，例如 `校园剧院独唱` |
| `--out` | 否 | 输出目录，默认 `./outputs` |
| `--use-openai` | 否 | 开启 OpenAI API 模式 |
| `--model` | 否 | OpenAI 模型名，默认 `gpt-4o-mini` |

## 输出文件

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

其中 `render_instruction.txt` 是最适合复制到图像生成工具里的最终提示词文件。

## 剧本转视频提示词工作流

```bash
python3 script_to_video_prompt_workflow.py \
  --script examples/sample_script.txt \
  --title "雨夜排练" \
  --target-model sora \
  --quality-mode high \
  --aspect-ratio 9:16 \
  --out ./outputs/video
```

运行完成后，输出目录会包含：

```text
outputs/video/
  01_script_analysis.json
  02_character_profiles.json
  03_storyboard_prompts.json
  04_video_prompt_package.json
  05_qa_report.json
  storyboard_prompts.md
  character_three_view_prompts.md
  production_brief.md
  video_workflow_result.json
```

详细说明请看 [video-workflow.md](video-workflow.md)。

## OpenAI API 模式

默认模式不需要网络和 API key。如果你想让 Agent 使用 OpenAI 生成更灵活的 JSON 输出，可以安装 OpenAI Python SDK 并设置环境变量：

```bash
python3 -m pip install openai
export OPENAI_API_KEY="your_key"
python3 multi_agent_poster_system.py \
  --image ./portrait.png \
  --theme "校园剧院独唱" \
  --out ./outputs \
  --use-openai
```

不要把 API key 写进代码、提交到 GitHub 或放进输出目录。

## 常见问题

### 这个工具会直接生成图片吗？

当前版本不会直接生成图片或视频。它会生成结构化分析结果和最终提示词，方便你继续放入 SDXL、Midjourney、DALL-E、ComfyUI、Sora、Runway、Kling、Pika、Luma 等工具。

### 为什么要提供真实图片文件？

脚本会检查图片路径、扩展名、文件大小和文件头签名，用来确保输入是真实图片文件，而不是伪装扩展名的文本或其他文件。

### 可以输入任意主题吗？

可以。主题会被清理空白字符，并限制最大长度，避免过长输入影响输出质量和可读性。
