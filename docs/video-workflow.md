# Script-to-Video Prompt Workflow

这个工作流用于把剧本文本转换成 AI 视频模型可用的提示词资产。它不会直接生成视频，而是输出分镜、角色三视图和一致性规则，方便继续交给 Sora、Runway、Kling、Pika、Luma、ComfyUI 视频流等工具。

## 适合做什么

- 从剧本识别场次、地点、时间和剧情节拍
- 从台词和角色表识别人物
- 为每个角色生成三视图 / 角色参考图提示词
- 为每个场次生成建立镜头、动作镜头、情绪特写
- 生成全局风格规则、人物一致性规则和负面词
- 输出可归档的 JSON 与 Markdown 提示词包

## 快速运行

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

需要更快得到草稿时：

```bash
python3 script_to_video_prompt_workflow.py \
  --script examples/sample_script.txt \
  --quality-mode fast \
  --out ./outputs/video-fast
```

## 支持的输入

剧本文本支持：

- `.txt`
- `.md`
- `.markdown`
- `.fountain`
- `.screenplay`

建议使用以下格式提升识别效果：

```text
片名：雨夜排练
人物：林舟、阿宁、旁白

第1场：外景 校园剧院门口 夜
雨水打在剧院门口的台阶上。
阿宁：你又想临阵逃走？
林舟：我只是觉得，今晚的舞台太空了。
```

也支持常见英文格式，例如 `INT. ROOM - NIGHT`、`EXT. STREET - DAY`、`SCENE 1`。

## 输出文件

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
  model_prompt_queue.md
  shot_prompt_queue.csv
  video_workflow_result.json
```

## 核心输出

### 角色三视图提示词

`character_three_view_prompts.md` 会为每个识别到的角色输出：

- `character_id`
- 角色名
- 角色定位
- identity seed
- front / side / back 三视图提示词
- 负面词
- 人物一致性注意事项

### 视频分镜提示词

`storyboard_prompts.md` 会按质量模式输出镜头：

- `fast`：每场 1 个关键镜头，适合快速试方向
- `balanced`：每场 3 个镜头，包含建立、动作、情绪
- `high`：每场 5 个镜头，包含建立、动作、细节、情绪、转场

每条镜头提示词都包含：

- 场次编号
- 地点和时间
- 角色绑定
- 镜头语言
- 灯光风格
- 连续性要求
- 负面词
- 目标模型提示词偏好
- 画幅比例

### 生产简报

`production_brief.md` 会汇总：

- 目标模型
- 质量模式
- 画幅比例
- 场次数、角色数和镜头数
- 模型提示建议
- QA 检查清单
- 分镜索引

### 模型排队提示词

`model_prompt_queue.md` 会按 `shot_id` 顺序整理可复制提示词，适合人工逐条放入视频模型。

`shot_prompt_queue.csv` 会把镜头编号、角色、镜头语言、提示词、负面词和制作备注整理成表格，适合导入表格工具或后续自动化流程。

### 视频模型总包

`04_video_prompt_package.json` 适合被其他工具读取或二次处理，里面包含：

- global style bible
- character reference prompts
- shot prompts
- global negative prompt
- handoff order

## 参数说明

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `--script` | 是 | 剧本文本路径 |
| `--title` | 否 | 项目标题，默认使用文件名 |
| `--out` | 否 | 输出目录，默认 `./outputs/video` |
| `--language` | 否 | 输出语言提示，默认 `zh-CN` |
| `--target-model` | 否 | 目标视频模型，支持 `general`、`sora`、`runway`、`kling`、`pika`、`luma` |
| `--quality-mode` | 否 | 输出质量模式，支持 `fast`、`balanced`、`high` |
| `--creative-style` | 否 | 视频风格，支持 `cinematic`、`realistic`、`anime`、`documentary`、`commercial`、`fantasy` |
| `--aspect-ratio` | 否 | 视频画幅，例如 `16:9`、`9:16`、`1:1` |
| `--max-scenes` | 否 | 最多处理场次数，默认 40 |
| `--max-characters` | 否 | 最多识别角色数，默认 12 |
| `--use-openai` | 否 | 开启可选 OpenAI JSON 增强 |
| `--model` | 否 | OpenAI 模型名，默认 `gpt-4o-mini` |

## 目标模型建议

| 目标模型 | 适合场景 |
| --- | --- |
| `general` | 通用视频模型，默认兼容 |
| `sora` | 强调长时连续性、世界状态和自然运动 |
| `runway` | 强调简洁、视觉优先、镜头和灯光明确 |
| `kling` | 强调动作、环境互动和节奏 |
| `pika` | 强调短提示词、强视觉钩子和简单动作 |
| `luma` | 强调真实感、空间深度、镜头路径和灯光连续 |

## 风格建议

| 风格 | 适合场景 |
| --- | --- |
| `cinematic` | 默认电影感叙事、短片、预告片式分镜 |
| `realistic` | 写实真人、生活化剧情、低夸张度项目 |
| `anime` | 动画 key visual、二次元短片、情绪化动作 |
| `documentary` | 纪实感、真实人物故事、自然光影 |
| `commercial` | 广告短片、产品化表达、强钩子短视频 |
| `fantasy` | 奇幻、神话、魔法现实主义世界观 |

## 安全限制

- 最大脚本文本大小为 512KB。
- 最大脚本文本长度为 60000 字符。
- 只读取 UTF-8 文本文件。
- 会过滤危险控制字符。
- QA 会检测疑似 API key 或 token。
- 默认模式不依赖网络，也不会上传剧本。
