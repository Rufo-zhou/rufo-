# Architecture

这个项目包含两个单文件 Python 工作流：海报提示词工作流和剧本转视频提示词工作流。核心目标是把创意输入转换成可用于图像或视频生成模型的结构化提示词资产。

## 海报工作流数据流

```text
ProjectInput
  -> CharacterUnderstandingAgent
  -> ThemeParsingAgent
  -> NarrativeCompositionAgent
  -> PromptEngineeringAgent
  -> QualityAssuranceAgent
  -> ImageRenderer placeholder
  -> JSON files + render_instruction.txt + poster_prompt_package.md + production_brief.md
```

## 视频工作流数据流

```text
ProjectInput
  -> ScriptStructureAgent
  -> CharacterProfileAgent
  -> StoryboardPromptAgent
  -> VideoPackageAgent
  -> QualityAssuranceAgent
  -> JSON files + storyboard_prompts.md + character_three_view_prompts.md
  -> production_brief.md + model_prompt_queue.md + shot_prompt_queue.csv
```

## 核心模块

| 模块 | 职责 |
| --- | --- |
| `ProjectInput` | 保存输入、输出目录、语言、质量模式、目标模型和风格设置 |
| `LLMClient` | 在默认 fallback 模式和 OpenAI API 模式之间切换 |
| `BaseAgent` | 提供 Agent 结果包装的基础结构 |
| `CharacterUnderstandingAgent` | 生成人物气质、肖像保留约束和海报角色 |
| `ThemeParsingAgent` | 拆解主题、情绪、符号和叙事弧线 |
| `NarrativeCompositionAgent` | 规划海报构图、视觉层级和剪影内部世界 |
| `PromptEngineeringAgent` | 生成最终提示词、负面词和推荐参数 |
| `QualityAssuranceAgent` | 检查提示词是否包含关键约束 |
| `PosterAgentOrchestrator` | 串联所有 Agent 并保存输出 |
| `ImageRenderer` | 当前是占位渲染器，负责写入 `render_instruction.txt` |
| `ScriptStructureAgent` | 拆解剧本场次、地点、时间、类型和情绪 |
| `CharacterProfileAgent` | 识别角色并生成三视图提示词 |
| `StoryboardPromptAgent` | 为每个场次生成建立镜头、动作镜头、情绪镜头 |
| `VideoPackageAgent` | 汇总视频模型提示词包、风格规则和交付顺序 |
| `QualityAssuranceAgent` | 检查场次、角色、三视图、模型配置、连续性和安全风险 |

## 设计原则

- 默认无第三方依赖，降低运行门槛。
- OpenAI API 是可选增强，不影响离线 fallback 流程。
- 每一步都保存 JSON，方便调试和复用中间结果。
- 输入图片只读取文件元信息和路径，不在默认模式上传图片。
- 渲染器保持占位，便于后续接入真实图片或视频生成服务。
- 海报工作流会根据主题自动推导场景、符号、情绪和色彩，而不是绑定单一示例主题。
- 海报工作流支持风格预设、目标图像模型、质量模式和多变体提示词。
- 视频工作流支持 `fast`、`balanced`、`high` 三档质量模式，方便在速度和质量之间取舍。
- 视频工作流支持 Sora、Runway、Kling、Pika、Luma 等目标模型提示词偏好。
- 视频工作流支持创作风格配置，并输出 Markdown / CSV 两种模型排队格式。

## 后续扩展方向

- 将单文件脚本拆分为 `src/` 包结构。
- 增加单元测试和 fixture。
- 为不同主题增加可配置模板。
- 接入真实图片生成 API。
- 提供正式命令行入口，例如 `python -m poster_agents`。
