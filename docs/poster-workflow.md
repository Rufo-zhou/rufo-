# Poster Prompt Workflow

这个工作流用于把人物肖像和创意主题整理成可直接交给图像模型的海报提示词资产。它不会直接生成图片，而是输出主提示词、负面词、多个变体方向、制作简报和 QA 报告。

## 适合做什么

- 从人物肖像生成叙事海报提示词
- 根据任意主题自动拆解场景、符号、情绪和色彩
- 为 Midjourney、SDXL、DALL-E、ComfyUI 等图像模型准备提示词
- 快速比较多个海报方向，减少反复手写 prompt 的时间
- 归档可复用的 JSON、Markdown 和最终复制文本

## 快速运行

```bash
python3 multi_agent_poster_system.py \
  --image ./portrait.png \
  --theme "未来城市侦探" \
  --style-preset noir \
  --model-target sdxl \
  --quality-mode high \
  --aspect-ratio 2:3 \
  --variations 5 \
  --out ./outputs/poster
```

需要快速试方向时：

```bash
python3 multi_agent_poster_system.py \
  --image ./portrait.png \
  --theme "校园剧院独唱" \
  --quality-mode fast \
  --variations 1 \
  --out ./outputs/poster-fast
```

## 输出文件

```text
outputs/poster/
  01_character_analysis.json
  02_theme_analysis.json
  03_composition_plan.json
  04_visual_prompt.json
  05_qa_report.json
  06_render_info.json
  render_instruction.txt
  poster_prompt_package.md
  production_brief.md
  pipeline_result.json
```

## 关键输出怎么用

- `render_instruction.txt`：最短路径，直接复制到图像模型。
- `poster_prompt_package.md`：包含主提示词、负面词和多个变体方向。
- `production_brief.md`：包含主题拆解、构图、使用顺序和 QA 检查。
- `pipeline_result.json`：完整机器可读结果，适合后续自动化处理。

## 参数说明

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `--image` | 是 | 输入人物肖像路径，支持 JPG、JPEG、PNG、WebP |
| `--theme` | 是 | 创意主题，例如 `未来城市侦探` |
| `--out` | 否 | 输出目录，默认 `./outputs` |
| `--aspect-ratio` | 否 | 海报画幅，例如 `2:3`、`1:1`、`16:9`、`9:16` |
| `--style-preset` | 否 | 支持 `cinematic`、`editorial`、`watercolor`、`commercial`、`noir`、`anime` |
| `--model-target` | 否 | 支持 `general`、`midjourney`、`sdxl`、`dalle`、`comfyui` |
| `--quality-mode` | 否 | 支持 `fast`、`balanced`、`high` |
| `--variations` | 否 | 输出变体方向数量，范围 1-5 |
| `--use-openai` | 否 | 开启可选 OpenAI JSON 增强 |
| `--model` | 否 | OpenAI 模型名，默认 `gpt-4o-mini` |

## 推荐使用顺序

1. 先用 `fast + variations 1` 快速看主题是否正确。
2. 方向正确后切换到 `balanced` 或 `high`。
3. 根据目标模型选择 `--model-target`。
4. 从 `poster_prompt_package.md` 里比较变体。
5. 选中一个方向后固定 seed，再微调光影、色彩和符号。

## 安全限制

- 会检查图片扩展名、文件大小和真实图片文件头。
- 主题文本会清理控制字符。
- 主题中疑似包含 API key 或 token 时会直接拒绝运行。
- 默认模式不依赖网络，也不会上传图片。
