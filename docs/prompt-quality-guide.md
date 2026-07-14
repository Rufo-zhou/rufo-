# Prompt Quality Guide

这份指南帮助你在速度、稳定性和作品质量之间做选择。

## 快速选择

| 目标 | 推荐参数 |
| --- | --- |
| 海报快速试方向 | `--quality-mode fast --variations 1` |
| 海报高质量出图 | `--quality-mode high --style-preset cinematic --model-target sdxl --variations 5` |
| 海报更像商业主视觉 | `--style-preset commercial --model-target midjourney` |
| 快速看方向 | `--quality-mode fast --target-model general` |
| 默认生产 | `--quality-mode balanced --target-model runway` |
| Seedance 2.0 导演式交付 | `--quality-mode high --target-model seedance` |
| 高质量分镜包 | `--quality-mode high --target-model sora` |
| 竖屏短视频 | `--aspect-ratio 9:16 --quality-mode balanced` |
| 动作感更强 | `--target-model kling --quality-mode high` |
| 空间真实感 | `--target-model luma --quality-mode high` |
| 纪实风视频 | `--creative-style documentary --target-model luma` |

## 质量模式

海报和视频都支持 `fast`、`balanced`、`high`。海报模式主要影响提示词交付完整度和建议变体数量；视频模式主要影响每场生成的镜头数量。

### fast

每场只生成一个关键镜头，适合快速试方向、提案草稿和脚本初筛。

### balanced

每场生成建立、动作、情绪三类镜头，是默认推荐模式。

### high

每场生成建立、动作、细节、情绪、转场五类镜头，适合交付前精修和高质量视频制作。

## 目标模型

### 图像模型

- `general`：通用兼容模式。
- `midjourney`：适合强审美、风格化和快速变体比较。
- `sdxl`：适合明确正负提示词、参数和本地工作流。
- `dalle`：适合完整自然语言描述。
- `comfyui`：适合节点化复用提示词结构。

### 视频模型

- `seedance`：强调导演意图、参考角色分工、动作终点、首尾帧连续性和 textless 交付。
- `sora`：强调连续世界状态、自然运动和长镜头一致性。
- `runway`：提示词更简洁，镜头、主体、灯光需要更明确。
- `kling`：适合动作、肢体、环境互动和强节奏。
- `pika`：适合短视频创意钩子和简单动作。
- `luma`：适合真实空间、镜头路径、景深和灯光连续。
- `general`：通用兼容模式。

## 海报主题写法

- 主题里写清地点、情绪、人物关系和关键物件，例如 `未来城市侦探 雨夜 真相`。
- 如果只写抽象词，输出会更偏概念海报；如果写具体场景，输出会更容易落地。
- 用 `--style-preset` 控制审美方向，用 `--model-target` 控制提示词结构。
- 先用 `fast` 看方向，再用 `high` 生成完整变体包。

## 提升作品质量的剧本写法

- 用 `第1场：外景 地点 时间` 或 `INT. ROOM - NIGHT` 明确场次。
- 用 `角色名：台词` 标记说话人。
- 在每场里写清关键道具、人物动作和情绪变化。
- 不要把角色设定、片名和正文混在同一段里。
- 对需要出镜的旁白角色，明确写出动作和外貌；否则旁白默认作为 voice-only 处理。

## 交付顺序

1. 先生成 `character_three_view_prompts.md` 中的可视角色参考。
2. 锁定角色 identity seed、服装、发型和主色。
3. 再按 `storyboard_prompts.md` 逐场生成视频镜头。
4. 用 `production_brief.md` 检查目标模型、画幅、镜头数和 QA 状态。
5. 最后再进入视频模型或剪辑软件。
