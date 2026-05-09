# Examples

这里放可直接用于 smoke test 和演示的输入文件。

## sample_script.txt

`sample_script.txt` 是一个短剧本示例，包含：

- 片名
- 人物表
- 三个场次
- 角色台词
- 旁白

运行：

```bash
python3 script_to_video_prompt_workflow.py \
  --script examples/sample_script.txt \
  --target-model sora \
  --quality-mode high \
  --creative-style cinematic \
  --aspect-ratio 9:16 \
  --out outputs/video
```

输出重点查看：

- `outputs/video/production_brief.md`
- `outputs/video/model_prompt_queue.md`
- `outputs/video/shot_prompt_queue.csv`
- `outputs/video/storyboard_prompts.md`
- `outputs/video/character_three_view_prompts.md`
