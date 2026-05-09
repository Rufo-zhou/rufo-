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
  - prompt variations
  - production brief
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
import re
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
MAX_VARIATIONS = 5

CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SECRET_PATTERN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9_]{12,}|github_pat_[A-Za-z0-9_]{12,}|"
    r"xox[baprs]-[A-Za-z0-9-]{12,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,})"
)

SUPPORTED_POSTER_STYLE_PRESETS = {"cinematic", "editorial", "watercolor", "commercial", "noir", "anime"}
SUPPORTED_POSTER_MODEL_TARGETS = {"general", "midjourney", "sdxl", "dalle", "comfyui"}
SUPPORTED_POSTER_QUALITY_MODES = {"fast", "balanced", "high"}

POSTER_STYLE_PRESETS = {
    "cinematic": {
        "label": "cinematic poster",
        "visual_language": "film poster composition, motivated lighting, cinematic depth, premium typography-safe space",
        "texture": "subtle film grain, atmospheric haze, coherent color grading",
    },
    "editorial": {
        "label": "editorial art poster",
        "visual_language": "magazine-grade composition, restrained layout, strong negative space, clear visual hierarchy",
        "texture": "fine paper texture, refined graphic balance, elegant color blocking",
    },
    "watercolor": {
        "label": "dreamlike watercolor poster",
        "visual_language": "soft watercolor edges, layered washes, poetic double exposure, hand-crafted warmth",
        "texture": "paper grain, dry brush edge, translucent pigment transitions",
    },
    "commercial": {
        "label": "commercial key art",
        "visual_language": "clear product-like selling point, immediate readability, strong hero subject, clean impact",
        "texture": "polished studio finish, crisp contrast, platform-ready clarity",
    },
    "noir": {
        "label": "noir dramatic poster",
        "visual_language": "high contrast lighting, shadow-heavy composition, mystery and tension, restrained palette",
        "texture": "deep blacks, smoke, rim light, gritty cinematic grain",
    },
    "anime": {
        "label": "anime key visual",
        "visual_language": "anime key visual composition, expressive silhouette, clean shape language, emotional color design",
        "texture": "clean linework, painterly background, luminous highlights",
    },
}

POSTER_MODEL_TARGETS = {
    "general": {
        "label": "general image model",
        "prompt_hint": "balanced natural-language prompt with clear subject, scene, style and negative constraints",
        "params": {"aspect_ratio": "use requested ratio", "seed_policy": "fix seed after first good direction"},
    },
    "midjourney": {
        "label": "Midjourney",
        "prompt_hint": "front-load subject and style, keep a strong visual hierarchy, avoid overly technical parameter prose",
        "params": {"stylize": "150-300", "chaos": "5-12", "seed_policy": "reuse seed for controlled variations"},
    },
    "sdxl": {
        "label": "SDXL",
        "prompt_hint": "use explicit composition, lighting, materials, camera language and negative prompt",
        "params": {"cfg_scale": 6.5, "steps": 35, "sampler": "DPM++ 2M Karras"},
    },
    "dalle": {
        "label": "DALL-E",
        "prompt_hint": "write one coherent production brief with fewer comma fragments and stronger intent",
        "params": {"prompt_shape": "complete descriptive paragraph", "iteration": "revise by adding missing constraints"},
    },
    "comfyui": {
        "label": "ComfyUI / Stable Diffusion workflow",
        "prompt_hint": "separate subject, style, composition, lighting and negative prompt for node-based reuse",
        "params": {"cfg_scale": 6.5, "steps": 35, "seed_policy": "pin seed for batch comparison"},
    },
}

POSTER_QUALITY_MODES = {
    "fast": {
        "label": "fast draft",
        "detail_level": "lean prompt, one strong direction, fast iteration",
        "recommended_variations": 1,
    },
    "balanced": {
        "label": "balanced production",
        "detail_level": "complete prompt with scene, mood, style and clear negative constraints",
        "recommended_variations": 3,
    },
    "high": {
        "label": "high quality package",
        "detail_level": "full production prompt with refined hierarchy, continuity rules and multiple art directions",
        "recommended_variations": 5,
    },
}

THEME_PROFILE_RULES = [
    {
        "keywords": ["校园", "学校", "剧院", "舞台", "音乐", "独唱", "合唱", "演出"],
        "scene_family": "校园剧院与青春舞台",
        "emotions": ["青春", "紧张", "怀旧", "聚光灯下的神圣感"],
        "scenes": ["校园剧院", "排练厅", "舞台中央聚光灯", "空座观众席", "后台走廊"],
        "symbols": ["乐谱", "聚光灯", "幕布", "空座位", "钢琴", "尘埃光束"],
        "palette": "warm amber, deep red, ivory paper, muted navy",
        "avoid": ["廉价奇幻元素", "杂乱拼贴", "无关科技符号"],
    },
    {
        "keywords": ["科幻", "未来", "太空", "星球", "飞船", "机器人", "AI", "cyber", "space"],
        "scene_family": "未来科幻与未知世界",
        "emotions": ["未知", "宏大", "冷静", "探索欲"],
        "scenes": ["未来城市天际线", "飞船舷窗", "星云远景", "实验室冷光", "孤独观测台"],
        "symbols": ["星图", "全息界面", "金属结构", "轨道光线", "数据粒子"],
        "palette": "deep black, electric cyan, silver, cold violet",
        "avoid": ["复古校园元素", "卡通玩具感", "随机关联的星球贴图"],
    },
    {
        "keywords": ["悬疑", "侦探", "谜", "失踪", "秘密", "真相", "雨夜", "mystery", "suspense"],
        "scene_family": "悬疑调查与阴影叙事",
        "emotions": ["紧张", "孤独", "压迫感", "真相将现"],
        "scenes": ["雨夜街口", "昏暗房间", "档案墙", "门缝光线", "空荡走廊"],
        "symbols": ["雨滴", "旧照片", "档案纸", "手电光", "破碎玻璃"],
        "palette": "desaturated teal, charcoal, sodium orange, wet black",
        "avoid": ["明亮广告感", "可爱卡通", "无关奇幻生物"],
    },
    {
        "keywords": ["国风", "古风", "武侠", "山水", "江湖", "仙侠", "唐", "宋"],
        "scene_family": "东方诗意与山水叙事",
        "emotions": ["清冷", "侠气", "宿命", "诗意"],
        "scenes": ["雾中山水", "古城屋檐", "竹林小径", "月下桥面", "远山云海"],
        "symbols": ["水墨", "长风", "折扇", "灯笼", "飞檐", "墨迹"],
        "palette": "ink black, mist white, muted jade, warm lantern red",
        "avoid": ["过度网游感", "塑料质感盔甲", "混乱发光法术"],
    },
    {
        "keywords": ["城市", "都市", "创业", "商业", "品牌", "咖啡", "办公室", "街头"],
        "scene_family": "现代城市与人物品牌叙事",
        "emotions": ["专业", "清醒", "行动力", "现代感"],
        "scenes": ["城市街角", "玻璃幕墙", "夜间办公室", "咖啡桌面", "通勤人流"],
        "symbols": ["城市灯光", "玻璃反射", "笔记本", "霓虹字牌", "地铁线条"],
        "palette": "graphite, white, signal blue, warm city light",
        "avoid": ["杂乱营销素材", "廉价商务模板", "过度卡通化"],
    },
]


# =========================
# Data Models
# =========================

@dataclass
class ProjectInput:
    image_path: str
    theme: str
    output_dir: str
    language: str = "zh-CN"
    aspect_ratio: str = "2:3"
    style_preset: str = "cinematic"
    model_target: str = "general"
    quality_mode: str = "balanced"
    variations: int = 3


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


def has_valid_image_signature(image_path: Path) -> bool:
    with image_path.open("rb") as image_file:
        header = image_file.read(16)

    suffix = image_path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(bytes.fromhex("ffd8ff"))
    if suffix == ".png":
        return header.startswith(bytes.fromhex("89504e470d0a1a0a"))
    if suffix == ".webp":
        return header[0:4] == b"RIFF" and header[8:12] == b"WEBP"
    return False


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
    if not has_valid_image_signature(p):
        raise ValueError("Image content does not match a supported image format.")
    return p


def validate_theme(theme: str) -> str:
    cleaned = CONTROL_CHAR_PATTERN.sub("", theme)
    cleaned = " ".join(cleaned.strip().split())
    if not cleaned:
        raise ValueError("Theme cannot be empty.")
    if len(cleaned) > MAX_THEME_CHARS:
        raise ValueError(f"Theme is too long. Max characters: {MAX_THEME_CHARS}")
    if contains_sensitive_token(cleaned):
        raise ValueError("Theme appears to contain a secret token or API key.")
    return cleaned


def contains_sensitive_token(text: str) -> bool:
    return SECRET_PATTERN.search(text) is not None


def validate_aspect_ratio(aspect_ratio: str) -> str:
    cleaned = aspect_ratio.strip()
    if not re.fullmatch(r"\d{1,2}:\d{1,2}", cleaned):
        raise ValueError("Aspect ratio must look like 2:3, 1:1, 16:9, or 9:16.")
    width, height = (int(part) for part in cleaned.split(":"))
    if width <= 0 or height <= 0:
        raise ValueError("Aspect ratio values must be positive.")
    return cleaned


def validate_choice(value: str, *, name: str, allowed: set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in allowed:
        raise ValueError(f"Unsupported {name}: {value}. Allowed: {sorted(allowed)}")
    return normalized


def validate_variations(value: int) -> int:
    if value < 1 or value > MAX_VARIATIONS:
        raise ValueError(f"Variations must be between 1 and {MAX_VARIATIONS}.")
    return value


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
    return "\n".join(
        line.strip()
        for line in textwrap.dedent(text).strip().splitlines()
        if line.strip()
    )


def extract_theme_keywords(theme: str) -> List[str]:
    candidates = re.split(r"[\s,，、/|;；:：]+", theme)
    keywords = []
    for candidate in candidates:
        cleaned = candidate.strip("。.!?？（）()[]【】")
        if len(cleaned) >= 2 and cleaned not in keywords:
            keywords.append(cleaned)
    if not keywords and theme:
        keywords.append(theme[:24])
    return keywords[:8]


def infer_theme_profile(theme: str) -> Dict[str, Any]:
    lowered = theme.lower()
    keywords = extract_theme_keywords(theme)
    matched = None
    for rule in THEME_PROFILE_RULES:
        if any(keyword.lower() in lowered for keyword in rule["keywords"]):
            matched = rule
            break
    if matched is None:
        matched = {
            "scene_family": "人物主题叙事与情绪海报",
            "emotions": ["高级感", "故事感", "视觉冲击", "情绪集中"],
            "scenes": [
                f"{keywords[0] if keywords else '主题'}核心场景",
                "象征性背景空间",
                "人物记忆片段",
                "光影层次",
                "留白区域",
            ],
            "symbols": keywords + ["光影", "纹理", "空间层次", "象征物"],
            "palette": "theme-matched cinematic palette with one dominant color and two restrained accents",
            "avoid": ["杂乱拼贴", "无关元素", "模板化背景", "低质感装饰"],
        }
    return {
        "theme_keywords": keywords,
        "scene_family": matched["scene_family"],
        "core_emotion": matched["emotions"],
        "key_scenes": matched["scenes"],
        "symbols": matched["symbols"],
        "palette": matched["palette"],
        "avoid": matched["avoid"],
        "narrative_arc": build_narrative_arc(theme, matched["scene_family"], matched["emotions"]),
    }


def build_narrative_arc(theme: str, scene_family: str, emotions: List[str]) -> List[str]:
    emotion = emotions[0] if emotions else "情绪"
    return [
        f"人物被放置在“{theme}”的核心情境中",
        f"环境从{scene_family}逐渐展开，形成明确世界观",
        f"关键符号推动{emotion}情绪走向高潮",
        "画面最终停留在一个可被记住的主视觉形象上",
    ]


def join_items(items: List[str], limit: int = 6) -> str:
    return "、".join(str(item) for item in items[:limit] if item)


def build_prompt_variations(project: ProjectInput, theme: Dict[str, Any], base_prompt: str) -> List[Dict[str, str]]:
    variation_blueprints = [
        ("hero_silhouette", "强化人物剪影和主题世界观的融合，适合作为主海报方向。"),
        ("negative_space", "强化高级留白和编辑版式，适合作为封面、社交平台首图。"),
        ("dramatic_light", "强化戏剧性光线和情绪冲突，适合更有电影预告感的方向。"),
        ("symbol_focus", "强化主题符号和道具叙事，适合需要观众反复阅读细节的方向。"),
        ("premium_minimal", "减少背景元素，保留最高级、最克制、最容易落地的方向。"),
    ]
    style = POSTER_STYLE_PRESETS[project.style_preset]
    model = POSTER_MODEL_TARGETS[project.model_target]
    variations = []
    for index, (variant_id, direction) in enumerate(variation_blueprints[: project.variations], start=1):
        variations.append(
            {
                "variation_id": f"V{index:02d}_{variant_id}",
                "direction": direction,
                "prompt": compact_multiline(
                    f"""
                    {base_prompt}
                    Variation focus: {direction}
                    Keep theme keywords visible: {join_items(theme.get('theme_keywords', []), 5)}.
                    Style preset: {style['label']}. Model note: {model['prompt_hint']}.
                    """
                ),
            }
        )
    return variations


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
        profile = infer_theme_profile(theme)
        fallback = {
            "theme": theme,
            "theme_keywords": profile["theme_keywords"],
            "scene_family": profile["scene_family"],
            "core_pain_point": "普通 AI 海报容易像素材拼贴，缺少主题统一、叙事中心和可读世界观。",
            "core_emotion": profile["core_emotion"],
            "key_scenes": profile["key_scenes"],
            "symbols": profile["symbols"],
            "palette": profile["palette"],
            "narrative_arc": profile["narrative_arc"],
            "avoid": profile["avoid"],
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
        project = context["project"]
        character = context["character_analysis"].output
        theme = context["theme_analysis"].output

        fallback = {
            "layout": {
                "canvas_ratio": f"{project.aspect_ratio} premium poster canvas",
                "main_shape": "large left-facing profile silhouette occupying 65% height",
                "negative_space": "warm off-white paper background with large breathing space",
                "visual_hierarchy": [
                    "side profile silhouette",
                    f"{theme.get('scene_family', project.theme)} inside the silhouette",
                    f"main theme scene: {theme.get('key_scenes', [project.theme])[0]}",
                    f"secondary symbols: {join_items(theme.get('symbols', []), 5)}",
                ],
            },
            "inside_silhouette_world": {
                "upper_area": f"{theme.get('key_scenes', ['主题空间'])[0]}, atmospheric light, layered depth",
                "middle_area": f"{theme.get('key_scenes', ['核心动作'])[1] if len(theme.get('key_scenes', [])) > 1 else project.theme}, clear story action",
                "lower_area": f"{theme.get('key_scenes', ['环境线索'])[2] if len(theme.get('key_scenes', [])) > 2 else 'symbolic foreground details'}",
                "edge_treatment": "watercolor bleeding, dry brush edges, paper grain, subtle double exposure",
            },
            "camera_language": {
                "mood": join_items(theme.get("core_emotion", ["cinematic"]), 5),
                "lighting": "theme-matched key light, soft rim light, coherent shadow direction",
                "depth": "soft atmospheric perspective, layered mist",
                "palette": theme.get("palette", "coherent cinematic palette"),
            },
            "composition_rules": [
                "所有元素必须生长在侧脸剪影内部",
                "不要硬拼贴，不要贴图感",
                "场景之间用雾化和水彩晕染过渡",
                "保留大面积留白与高级克制版式",
                "主题关键词、人物气质和场景符号必须保持同一叙事方向",
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
        style = POSTER_STYLE_PRESETS[project.style_preset]
        model = POSTER_MODEL_TARGETS[project.model_target]
        quality = POSTER_QUALITY_MODES[project.quality_mode]
        theme_scenes = join_items(theme.get("key_scenes", []), 6)
        theme_symbols = join_items(theme.get("symbols", []), 8)
        theme_emotions = join_items(theme.get("core_emotion", []), 6)
        avoid_terms = join_items(theme.get("avoid", []), 8)

        final_prompt = compact_multiline(
            f"""
            收藏版叙事人物海报，基于输入人物肖像生成一个清晰可识别的侧脸剪影外轮廓，剪影内部自然生长出完整主题世界观。
            主题：{project.theme}。
            构图：{project.aspect_ratio} 画幅，{style['label']}，{style['visual_language']}；人物侧脸剪影占据画面主体，保留可用于标题或平台裁切的高级留白。
            剪影内部世界：{theme_scenes}。这些场景必须像同一段故事自然展开，而不是互相无关的素材拼贴。
            关键符号：{theme_symbols}。符号只服务主题，不添加与主题无关的随机装饰。
            情绪与色彩：{theme_emotions}；主色建议 {theme.get('palette', 'coherent cinematic palette')}；{style['texture']}。
            人物约束：保留输入肖像的核心五官比例、发型轮廓和气质，不直接复制原图背景；人物必须成为主题叙事中心。
            质量模式：{quality['label']}，{quality['detail_level']}。
            模型目标：{model['label']}；提示词策略：{model['prompt_hint']}。
            画面要求：不是普通拼贴，而是剪影轮廓填充式叙事合成；主题、人物、符号、光影必须强绑定；高级克制、可收藏、艺术展级质感。
            """
        )

        negative_prompt = compact_multiline(
            f"""
            low quality, cheap fantasy, messy collage, random objects, off-theme decoration, {avoid_terms},
            bad anatomy, distorted face, extra limbs, text errors, watermark, logo, noisy background, template poster,
            hard cutout, sticker-like elements, generic AI fantasy background, cluttered composition
            """
        )
        variations = build_prompt_variations(project, theme, final_prompt)

        output = {
            "model_target": project.model_target,
            "model_profile": model,
            "style_preset": project.style_preset,
            "quality_mode": project.quality_mode,
            "aspect_ratio": project.aspect_ratio,
            "final_prompt_zh": final_prompt,
            "negative_prompt": negative_prompt,
            "prompt_variations": variations,
            "recommended_params": {
                "aspect_ratio": project.aspect_ratio,
                "style_strength": 0.72,
                "cfg_scale": 6.5,
                "steps": 35,
                "seed_policy": "fix seed for iteration, random seed for exploration",
                "model_specific": model["params"],
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
        project = context["project"]
        theme = context["theme_analysis"].output
        prompt = context["visual_prompt"].output.get("final_prompt_zh", "")
        negative_prompt = context["visual_prompt"].output.get("negative_prompt", "")
        variations = context["visual_prompt"].output.get("prompt_variations", [])
        theme_keywords = [project.theme] + theme.get("theme_keywords", []) + theme.get("symbols", [])
        checks = {
            "has_profile_silhouette": "侧脸剪影" in prompt,
            "has_theme_reference": any(keyword and keyword in prompt for keyword in theme_keywords),
            "has_narrative_world": "世界观" in prompt or "叙事" in prompt,
            "has_style_constraints": POSTER_STYLE_PRESETS[project.style_preset]["label"] in prompt or project.style_preset in prompt,
            "has_anti_collage_constraint": "不是普通拼贴" in prompt or "不要杂乱" in prompt,
            "has_negative_prompt": bool(negative_prompt) and "watermark" in negative_prompt,
            "has_model_guidance": POSTER_MODEL_TARGETS[project.model_target]["label"] in prompt,
            "has_prompt_variations": len(variations) == project.variations,
            "no_detected_secret_tokens": not contains_sensitive_token(project.theme),
        }
        score = sum(1 for value in checks.values() if value) / len(checks)
        output = {
            "checks": checks,
            "score": round(score, 2),
            "status": "pass" if score >= 0.85 and checks["no_detected_secret_tokens"] else "needs_revision",
            "suggestions": build_poster_qa_suggestions(checks),
        }
        return self.result(output)


def build_poster_qa_suggestions(checks: Dict[str, bool]) -> List[str]:
    suggestions = []
    if not checks.get("has_theme_reference"):
        suggestions.append("主题关键词不够明确，建议在主题中加入具体地点、情绪或关键物件。")
    if not checks.get("has_prompt_variations"):
        suggestions.append("生成方向数量不足，建议增加 variations 便于快速比较。")
    if not checks.get("has_negative_prompt"):
        suggestions.append("负面词不足，可能导致水印、文字错误或杂乱背景。")
    if not checks.get("no_detected_secret_tokens"):
        suggestions.append("主题疑似包含 API key 或 token，请先移除敏感信息。")
    return suggestions


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
            f"FINAL PROMPT:\n{prompt}\n\nNEGATIVE PROMPT:\n{negative_prompt}\n",
        )
        return {
            "status": "placeholder_saved",
            "message": "Image rendering is not enabled. Prompt saved for external image model.",
            "file": str(render_instruction_path),
        }


def render_poster_prompt_markdown(project: ProjectInput, visual_prompt: Dict[str, Any], qa_report: Dict[str, Any]) -> str:
    lines = [
        "# Poster Prompt Package",
        "",
        f"- Theme: {project.theme}",
        f"- Target model: {visual_prompt.get('model_profile', {}).get('label', project.model_target)}",
        f"- Style preset: {project.style_preset}",
        f"- Quality mode: {project.quality_mode}",
        f"- Aspect ratio: {project.aspect_ratio}",
        f"- QA status: {qa_report.get('status', 'unknown')} ({qa_report.get('score', 0)})",
        "",
        "## Primary Prompt",
        "",
        visual_prompt.get("final_prompt_zh", ""),
        "",
        "## Negative Prompt",
        "",
        visual_prompt.get("negative_prompt", ""),
        "",
        "## Prompt Variations",
        "",
    ]
    for variation in visual_prompt.get("prompt_variations", []):
        lines.extend(
            [
                f"### {variation['variation_id']}",
                "",
                f"- Direction: {variation['direction']}",
                "",
                variation["prompt"],
                "",
            ]
        )
    lines.extend(["## Recommended Parameters", ""])
    for key, value in visual_prompt.get("recommended_params", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines).strip() + "\n"


def render_poster_production_brief(
    project: ProjectInput,
    theme_analysis: Dict[str, Any],
    composition_plan: Dict[str, Any],
    visual_prompt: Dict[str, Any],
    qa_report: Dict[str, Any],
) -> str:
    lines = [
        "# Poster Production Brief",
        "",
        f"- Theme: {project.theme}",
        f"- Scene family: {theme_analysis.get('scene_family', 'unknown')}",
        f"- Style preset: {project.style_preset}",
        f"- Model target: {project.model_target}",
        f"- Quality mode: {project.quality_mode}",
        f"- Aspect ratio: {project.aspect_ratio}",
        f"- Variations: {project.variations}",
        f"- QA status: {qa_report.get('status', 'unknown')} ({qa_report.get('score', 0)})",
        "",
        "## Creative Direction",
        "",
        f"- Emotions: {join_items(theme_analysis.get('core_emotion', []), 8)}",
        f"- Key scenes: {join_items(theme_analysis.get('key_scenes', []), 8)}",
        f"- Symbols: {join_items(theme_analysis.get('symbols', []), 10)}",
        f"- Palette: {theme_analysis.get('palette', '')}",
        "",
        "## Composition",
        "",
    ]
    layout = composition_plan.get("layout", {})
    for key, value in layout.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Workflow Order", ""])
    lines.extend(
        [
            "- 1. Generate the primary prompt once to find the strongest direction.",
            "- 2. Compare the prompt variations and keep the best seed or composition.",
            "- 3. Reuse the negative prompt on every iteration.",
            "- 4. Lock subject identity before changing color, symbols or background.",
            "- 5. Run the QA checklist before final export.",
            "",
            "## QA Checklist",
            "",
        ]
    )
    for check, passed in qa_report.get("checks", {}).items():
        lines.append(f"- {'PASS' if passed else 'REVIEW'}: {check}")
    suggestions = qa_report.get("suggestions", [])
    if suggestions:
        lines.extend(["", "## Suggestions", ""])
        lines.extend(f"- {suggestion}" for suggestion in suggestions)
    lines.extend(["", "## Model Note", "", visual_prompt.get("model_profile", {}).get("prompt_hint", "")])
    return "\n".join(lines).strip() + "\n"


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

        prompt_package_path = output_dir / "poster_prompt_package.md"
        save_text(prompt_package_path, render_poster_prompt_markdown(project, visual_prompt.output, qa.output))
        saved_files.append(str(prompt_package_path))

        production_brief_path = output_dir / "production_brief.md"
        save_text(
            production_brief_path,
            render_poster_production_brief(
                project,
                theme.output,
                composition.output,
                visual_prompt.output,
                qa.output,
            ),
        )
        saved_files.append(str(production_brief_path))

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
    parser.add_argument("--aspect-ratio", default="2:3", help="Poster aspect ratio, e.g. 2:3, 1:1, 16:9, 9:16")
    parser.add_argument(
        "--style-preset",
        choices=sorted(SUPPORTED_POSTER_STYLE_PRESETS),
        default="cinematic",
        help="Poster visual style preset",
    )
    parser.add_argument(
        "--model-target",
        choices=sorted(SUPPORTED_POSTER_MODEL_TARGETS),
        default="general",
        help="Prompt profile for the target image model",
    )
    parser.add_argument(
        "--quality-mode",
        choices=sorted(SUPPORTED_POSTER_QUALITY_MODES),
        default="balanced",
        help="fast creates fewer directions, balanced creates 3, high creates up to 5",
    )
    parser.add_argument("--variations", type=int, default=3, help="Number of prompt variations to save")
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
            aspect_ratio=validate_aspect_ratio(args.aspect_ratio),
            style_preset=validate_choice(args.style_preset, name="style preset", allowed=SUPPORTED_POSTER_STYLE_PRESETS),
            model_target=validate_choice(args.model_target, name="model target", allowed=SUPPORTED_POSTER_MODEL_TARGETS),
            quality_mode=validate_choice(args.quality_mode, name="quality mode", allowed=SUPPORTED_POSTER_QUALITY_MODES),
            variations=validate_variations(args.variations),
        )
        llm = LLMClient(use_openai=args.use_openai, model=args.model)
        orchestrator = PosterAgentOrchestrator(llm)
        result = orchestrator.run(project)

        print("\n=== Multi-Agent Poster Pipeline Finished ===")
        print(f"QA status: {result.qa_report.output['status']}")
        print(f"QA score: {result.qa_report.output['score']}")
        print(f"Style preset: {result.project.style_preset}")
        print(f"Target model: {result.project.model_target}")
        print(f"Quality mode: {result.project.quality_mode}")
        print(f"Aspect ratio: {result.project.aspect_ratio}")
        print(f"Prompt variations: {result.project.variations}")
        print("\nSaved files:")
        for file in result.saved_files:
            print(f"- {file}")
        print("\nFinal prompt saved to render_instruction.txt and poster_prompt_package.md")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
