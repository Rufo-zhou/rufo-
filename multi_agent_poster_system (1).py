"""
Multi-Agent Narrative Poster Automation System

A complete, runnable Python prototype for a multi-agent creative pipeline.

Input:
  - portrait image path
  - creative theme

Output:
  - structured character analysis
  - theme breakdown
  - narrative composition plan
  - final image prompt
  - QA report
  - optional image generation instruction file

Run:
  python multi_agent_poster_system.py --image ./portrait.jpg --theme "校园剧院独唱" --out ./outputs

Optional with OpenAI API:
  export OPENAI_API_KEY="your_key"
  python multi_agent_poster_system.py --image ./portrait.jpg --theme "校园剧院独唱" --out ./outputs --use-openai
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =========================
# Security / Stability Config
# =========================

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_THEME_CHARS = 500
MAX_IMAGE_BYTES = 25 * 1024 * 1024


# =========================
# Data Models
# =========================

@dataclass
class ProjectInput:
    image_path: str
    theme: str
    output_dir: str
    language: str = "zh-CN"


@dataclass
class AgentResult:
    agent_name: str
    output: Dict[str, Any]
    created_at: str


@dataclass
class PosterPipelineResult:
    project: ProjectInput
    character_analysis: AgentResult
    theme_analysis: AgentResult
    composition_plan: AgentResult
    visual_prompt: AgentResult
    qa_report: AgentResult
    final_prompt: str
    negative_prompt: str
    saved_files: List[str]


# =========================
# Utilities
# =========================

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def validate_image_path(image_path: str | Path) -> Path:
    p = Path(image_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")
    if not p.is_file():
        raise ValueError(f"Image path is not a file: {p}")
    if p.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension: {p.suffix}. "
            f"Allowed: {sorted(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    if p.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError(f"Image is too large. Max size: {MAX_IMAGE_BYTES // 1024 // 1024}MB")
    return p


def validate_theme(theme: str) -> str:
    cleaned = " ".join(theme.strip().split())
    if not cleaned:
        raise ValueError("Theme cannot be empty.")
    if len(cleaned) > MAX_THEME_CHARS:
        raise ValueError(f"Theme is too long. Max characters: {MAX_THEME_CHARS}")
    return cleaned


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def compact_multiline(text: str) -> str:
    return "
".join(
        line.strip()
        for line in textwrap.dedent(text).strip().splitlines()
        if line.strip()
    )


# =========================
# Optional LLM Client
# =========================

class LLMClient:
    """Small wrapper. Default mode is deterministic fallback output.

    The project runs without external dependencies.
    If --use-openai is enabled and OPENAI_API_KEY exists, it calls OpenAI.
    """

    def __init__(self, use_openai: bool = False, model: str = "gpt-4o-mini"):
        self.use_openai = use_openai
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")

        if self.use_openai and not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required when --use-openai is enabled.")

    def complete_json(self, system: str, user: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        if not self.use_openai:
            return fallback

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                temperature=0.35,
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ValueError("LLM output must be a JSON object.")
            return parsed
        except Exception as exc:
            # Do not expose API keys or environment variables in logs.
            return {
                "warning": "OpenAI call failed; deterministic fallback returned.",
                "error_type": exc.__class__.__name__,
                "fallback": fallback,
            }


# =========================
# Base Agent
# =========================

class BaseAgent:
    name = "BaseAgent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, context: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def result(self, output: Dict[str, Any]) -> AgentResult:
        return AgentResult(agent_name=self.name, output=output, created_at=now_iso())


# =========================
# Agent 1: Character Understanding
# =========================

class CharacterUnderstandingAgent(BaseAgent):
    name = "CharacterUnderstandingAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        image_path = context["project"].image_path
        fallback = {
            "portrait_source": image_path,
            "identity_constraints": [
                "保留输入肖像的核心五官比例",
                "保留发型轮廓与面部气质",
                "输出为侧脸剪影外轮廓，不直接复刻原图背景",
            ],
            "visual_traits": {
                "age_range": "young adult",
                "expression": "calm, focused, slightly reserved",
                "wardrobe_hint": "formal black suit, white shirt, stage-performance context",
                "temperament": ["克制", "安静", "学院感", "舞台感", "怀旧"],
            },
            "poster_role": "主角侧脸剪影，内部承载叙事世界观",
        }

        system = "你是视觉理解 Agent。只输出 JSON 对象，不输出解释文字。"
        user = (
            "分析人物肖像，用于叙事型海报生成。"
            f"图片路径：{image_path}。"
            "输出人物气质、保留约束、海报角色。"
        )
        output = self.llm.complete_json(system, user, fallback)
        return self.result(output)


# =========================
# Agent 2: Theme Parsing
# =========================

class ThemeParsingAgent(BaseAgent):
    name = "ThemeParsingAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        theme = context["project"].theme
        fallback = {
            "theme": theme,
            "core_pain_point": "普通 AI 海报容易像素材拼贴，缺少主题统一、叙事中心和可读世界观。",
            "core_emotion": ["独唱前的紧张", "青春的孤独", "聚光灯下的神圣感", "校园剧院的怀旧感"],
            "key_scenes": ["校园剧院", "排练厅", "空座观众席", "舞台中央聚光灯", "黑色三角钢琴"],
            "symbols": ["乐谱", "聚光灯", "幕布", "空座位", "剧院拱门", "尘埃光束"],
            "narrative_arc": [
                "少年站在后台阴影中",
                "他走向舞台中央",
                "独唱声穿过空剧院",
                "远处校园建筑在雾中浮现",
            ],
            "avoid": ["廉价奇幻元素", "杂乱拼贴", "过度赛博朋克", "无关生物", "模板化背景"],
        }
        system = "你是主题解析 Agent。只输出 JSON 对象，不输出解释文字。"
        user = f"请将主题拆解为场景、情绪、符号、叙事弧线。主题：{theme}"
        output = self.llm.complete_json(system, user, fallback)
        return self.result(output)


# =========================
# Agent 3: Narrative Composition
# =========================

class NarrativeCompositionAgent(BaseAgent):
    name = "NarrativeCompositionAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        character = context["character_analysis"].output
        theme = context["theme_analysis"].output

        fallback = {
            "layout": {
                "canvas_ratio": "2:3 vertical collectible poster",
                "main_shape": "large left-facing profile silhouette occupying 65% height",
                "negative_space": "warm off-white paper background with large breathing space",
                "visual_hierarchy": [
                    "side profile silhouette",
                    "glowing theater stage inside head silhouette",
                    "solo singer under spotlight",
                    "piano, sheet music, campus architecture as secondary symbols",
                ],
            },
            "inside_silhouette_world": {
                "upper_area": "arched theater windows, golden volumetric light, floating dust",
                "middle_area": "stage, red curtain, solo singer rehearsing",
                "lower_area": "campus theater exterior, stairs, lonely student figure walking in mist",
                "edge_treatment": "watercolor bleeding, dry brush edges, paper grain, subtle double exposure",
            },
            "camera_language": {
                "mood": "quiet, epic, sacred, nostalgic, poetic",
                "lighting": "soft backlight, stage spotlight, warm amber haze",
                "depth": "soft atmospheric perspective, layered mist",
            },
            "composition_rules": [
                "所有元素必须生长在侧脸剪影内部",
                "不要硬拼贴，不要贴图感",
                "场景之间用雾化和水彩晕染过渡",
                "保留大面积留白与高级克制版式",
            ],
        }
        system = "你是电影海报构图 Agent。只输出 JSON 对象，不输出解释文字。"
        user = json.dumps({"character": character, "theme": theme}, ensure_ascii=False)
        output = self.llm.complete_json(system, user, fallback)
        return self.result(output)


# =========================
# Agent 4: Prompt Engineering
# =========================

class PromptEngineeringAgent(BaseAgent):
    name = "PromptEngineeringAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        project = context["project"]
        composition = context["composition_plan"].output
        theme = context["theme_analysis"].output

        final_prompt = compact_multiline(
            f"""
            收藏版史诗叙事海报，基于输入人物肖像生成一个左侧脸剪影外轮廓，剪影内部自然生长出完整世界观。
            主题：{project.theme}。
            构图：竖版 2:3，高级电影海报版式，大面积米白纸张留白；人物侧脸剪影占据画面主体，边缘带飞白、水彩刷痕与纸张颗粒。
            剪影内部：校园剧院排练独唱场景，舞台中央一名穿黑色正装的年轻独唱者站在温暖聚光灯下；空座观众席、黑色三角钢琴、红色厚重幕布、剧院拱门、乐谱纸、后台光束、校园剧院建筑与台阶在雾中若隐若现。
            叙事关系：孤独的主角、舞台、音乐、青春记忆、无人剧院之间形成安静而宏大的精神世界。
            风格：电影海报 + 梦幻水彩插画 + 双重曝光式联想；柔和空气透视，轻雾化过渡，暖金与深褐色调，安静、宏大、神圣、怀旧、诗意、传说感。
            画面要求：不是普通拼贴，而是剪影轮廓填充式叙事合成；所有元素必须强绑定校园剧院独唱主题；不要杂乱，不要模板化背景，不要廉价奇幻素材；高级克制、可收藏、艺术展级质感。
            """
        )

        negative_prompt = compact_multiline(
            """
            low quality, cheap fantasy, messy collage, random objects, unrelated monsters, cyberpunk, over saturated colors,
            bad anatomy, distorted face, extra limbs, text errors, watermark, logo, noisy background, template poster,
            hard cutout, sticker-like elements, generic AI fantasy background, cluttered composition
            """
        )

        output = {
            "model_target": "SDXL / Midjourney / DALL-E / ComfyUI compatible",
            "final_prompt_zh": final_prompt,
            "negative_prompt": negative_prompt,
            "recommended_params": {
                "aspect_ratio": "2:3",
                "style_strength": 0.72,
                "cfg_scale": 6.5,
                "steps": 35,
                "seed_policy": "fix seed for iteration, random seed for exploration",
            },
            "source_composition_plan": composition,
            "theme_keywords": theme.get("symbols", []),
        }
        return self.result(output)


# =========================
# Agent 5: Quality Assurance
# =========================

class QualityAssuranceAgent(BaseAgent):
    name = "QualityAssuranceAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        prompt = context["visual_prompt"].output.get("final_prompt_zh", "")
        checks = {
            "has_profile_silhouette": "侧脸剪影" in prompt,
            "has_theme_scene": "校园剧院" in prompt and "独唱" in prompt,
            "has_narrative_world": "世界观" in prompt or "叙事" in prompt,
            "has_style_constraints": "水彩" in prompt and "电影海报" in prompt,
            "has_anti_collage_constraint": "不是普通拼贴" in prompt or "不要杂乱" in prompt,
        }
        score = sum(1 for value in checks.values() if value) / len(checks)
        output = {
            "checks": checks,
            "score": round(score, 2),
            "status": "pass" if score >= 0.8 else "needs_revision",
            "suggestions": [] if score >= 0.8 else [
                "增强侧脸剪影约束",
                "补充主题关键场景",
                "减少无关元素",
            ],
        }
        return self.result(output)


# =========================
# Optional Renderer Placeholder
# =========================

class ImageRenderer:
    """Renderer placeholder.

    For real production, replace this with:
    - OpenAI Images API
    - ComfyUI API
    - Automatic1111 Stable Diffusion API
    - Replicate / fal.ai / internal image model
    """

    def render(self, prompt: str, negative_prompt: str, output_dir: Path) -> Dict[str, Any]:
        render_instruction_path = output_dir / "render_instruction.txt"
        save_text(
            render_instruction_path,
            f"FINAL PROMPT:
{prompt}

NEGATIVE PROMPT:
{negative_prompt}
",
        )
        return {
            "status": "placeholder_saved",
            "message": "Image rendering is not enabled. Prompt saved for external image model.",
            "file": str(render_instruction_path),
        }


# =========================
# Orchestrator
# =========================

class PosterAgentOrchestrator:
    def __init__(self, llm: LLMClient, renderer: Optional[ImageRenderer] = None):
        self.llm = llm
        self.renderer = renderer or ImageRenderer()
        self.character_agent = CharacterUnderstandingAgent(llm)
        self.theme_agent = ThemeParsingAgent(llm)
        self.composition_agent = NarrativeCompositionAgent(llm)
        self.prompt_agent = PromptEngineeringAgent(llm)
        self.qa_agent = QualityAssuranceAgent(llm)

    def run(self, project: ProjectInput) -> PosterPipelineResult:
        output_dir = ensure_dir(project.output_dir)
        context: Dict[str, Any] = {"project": project}
        saved_files: List[str] = []

        character = self.character_agent.run(context)
        context["character_analysis"] = character
        path = output_dir / "01_character_analysis.json"
        save_json(path, asdict(character))
        saved_files.append(str(path))

        theme = self.theme_agent.run(context)
        context["theme_analysis"] = theme
        path = output_dir / "02_theme_analysis.json"
        save_json(path, asdict(theme))
        saved_files.append(str(path))

        composition = self.composition_agent.run(context)
        context["composition_plan"] = composition
        path = output_dir / "03_composition_plan.json"
        save_json(path, asdict(composition))
        saved_files.append(str(path))

        visual_prompt = self.prompt_agent.run(context)
        context["visual_prompt"] = visual_prompt
        path = output_dir / "04_visual_prompt.json"
        save_json(path, asdict(visual_prompt))
        saved_files.append(str(path))

        qa = self.qa_agent.run(context)
        context["qa_report"] = qa
        path = output_dir / "05_qa_report.json"
        save_json(path, asdict(qa))
        saved_files.append(str(path))

        final_prompt = visual_prompt.output["final_prompt_zh"]
        negative_prompt = visual_prompt.output["negative_prompt"]
        render_info = self.renderer.render(final_prompt, negative_prompt, output_dir)
        path = output_dir / "06_render_info.json"
        save_json(path, render_info)
        saved_files.append(str(path))
        saved_files.append(render_info["file"])

        pipeline_path = output_dir / "pipeline_result.json"
        saved_files.append(str(pipeline_path))

        result = PosterPipelineResult(
            project=project,
            character_analysis=character,
            theme_analysis=theme,
            composition_plan=composition,
            visual_prompt=visual_prompt,
            qa_report=qa,
            final_prompt=final_prompt,
            negative_prompt=negative_prompt,
            saved_files=saved_files,
        )
        save_json(pipeline_path, asdict(result))
        return result


# =========================
# CLI
# =========================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Agent Narrative Poster Automation System")
    parser.add_argument("--image", required=True, help="Path to portrait image: jpg/jpeg/png/webp")
    parser.add_argument("--theme", required=True, help="Creative theme, e.g. 校园剧院独唱")
    parser.add_argument("--out", default="./outputs", help="Output directory")
    parser.add_argument("--use-openai", action="store_true", help="Enable OpenAI JSON generation")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name")
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        image_path = validate_image_path(args.image)
        theme = validate_theme(args.theme)
        output_dir = ensure_dir(args.out)

        project = ProjectInput(
            image_path=str(image_path),
            theme=theme,
            output_dir=str(output_dir),
        )
        llm = LLMClient(use_openai=args.use_openai, model=args.model)
        orchestrator = PosterAgentOrchestrator(llm)
        result = orchestrator.run(project)

        print("
=== Multi-Agent Poster Pipeline Finished ===")
        print(f"QA status: {result.qa_report.output['status']}")
        print(f"QA score: {result.qa_report.output['score']}")
        print("
Saved files:")
        for file in result.saved_files:
            print(f"- {file}")
        print("
Final prompt saved to render_instruction.txt")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
