# Changelog

## 2026-05-09

- Added general theme profiling for the poster workflow so non-theater themes produce relevant scenes, symbols, emotions, and palettes.
- Added poster options: `--style-preset`, `--model-target`, `--quality-mode`, `--aspect-ratio`, and `--variations`.
- Added poster Markdown outputs: `poster_prompt_package.md` and `production_brief.md`.
- Added video `--creative-style` profiles for cinematic, realistic, anime, documentary, commercial, and fantasy outputs.
- Added video handoff outputs: `model_prompt_queue.md` and `shot_prompt_queue.csv`.
- Expanded CI safeguards for poster secret detection and the new output files.

## 2026-05-08

- Added target-model prompt profiles for `general`, `sora`, `runway`, `kling`, `pika`, and `luma`.
- Added `--quality-mode fast|balanced|high` for speed and quality control.
- Added `--aspect-ratio`, `--max-scenes`, and `--max-characters` options.
- Added `production_brief.md` output for handoff and QA review.
- Improved narrator handling: voice-only roles no longer generate character three-view prompts.
- Added prompt quality guide and examples documentation.
