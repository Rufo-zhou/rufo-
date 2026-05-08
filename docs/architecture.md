# Architecture

这个项目是一个单文件 Python 原型，核心目标是把“人物肖像 + 创意主题”转换成可用于图像生成模型的结构化叙事海报提示词。

## 数据流

```text
ProjectInput
  -> CharacterUnderstandingAgent
  -> ThemeParsingAgent
  -> NarrativeCompositionAgent
  -> PromptEngineeringAgent
  -> QualityAssuranceAgent
  -> ImageRenderer placeholder
  -> JSON files + render_instruction.txt
```

## 核心模块

| 模块 | 职责 |
| --- | --- |
| `ProjectInput` | 保存输入图片路径、主题、输出目录和语言设置 |
| `LLMClient` | 在默认 fallback 模式和 OpenAI API 模式之间切换 |
| `BaseAgent` | 提供 Agent 结果包装的基础结构 |
| `CharacterUnderstandingAgent` | 生成人物气质、肖像保留约束和海报角色 |
| `ThemeParsingAgent` | 拆解主题、情绪、符号和叙事弧线 |
| `NarrativeCompositionAgent` | 规划海报构图、视觉层级和剪影内部世界 |
| `PromptEngineeringAgent` | 生成最终提示词、负面词和推荐参数 |
| `QualityAssuranceAgent` | 检查提示词是否包含关键约束 |
| `PosterAgentOrchestrator` | 串联所有 Agent 并保存输出 |
| `ImageRenderer` | 当前是占位渲染器，负责写入 `render_instruction.txt` |

## 设计原则

- 默认无第三方依赖，降低运行门槛。
- OpenAI API 是可选增强，不影响离线 fallback 流程。
- 每一步都保存 JSON，方便调试和复用中间结果。
- 输入图片只读取文件元信息和路径，不在默认模式上传图片。
- 渲染器保持占位，便于后续接入真实图片生成服务。

## 后续扩展方向

- 将单文件脚本拆分为 `src/` 包结构。
- 增加单元测试和 fixture。
- 为不同主题增加可配置模板。
- 接入真实图片生成 API。
- 提供正式命令行入口，例如 `python -m poster_agents`。
