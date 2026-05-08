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
  --out ./outputs/video
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

`storyboard_prompts.md` 会为每个场次输出三类镜头：

- establishing：建立空间和气氛
- action：表现动作和剧情推进
- emotion：捕捉人物情绪和关键反应

每条镜头提示词都包含：

- 场次编号
- 地点和时间
- 角色绑定
- 镜头语言
- 灯光风格
- 连续性要求
- 负面词

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
| `--use-openai` | 否 | 开启可选 OpenAI JSON 增强 |
| `--model` | 否 | OpenAI 模型名，默认 `gpt-4o-mini` |

## 安全限制

- 最大脚本文本大小为 512KB。
- 最大脚本文本长度为 60000 字符。
- 只读取 UTF-8 文本文件。
- 会过滤危险控制字符。
- QA 会检测疑似 API key 或 token。
- 默认模式不依赖网络，也不会上传剧本。
