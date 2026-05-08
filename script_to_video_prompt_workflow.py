"""
Script-to-Video Prompt Workflow

A runnable Python workflow that turns a screenplay or story draft into:
  - script structure analysis
  - character profiles
  - character three-view reference prompts
  - AI video storyboard prompts
  - model-ready prompt package
  - QA report

Run:
  python3 script_to_video_prompt_workflow.py --script ./script.txt --out ./outputs/video
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
from typing import Any, Dict, Iterable, List, Optional


# =========================
# Security / Stability Config
# =========================

ALLOWED_SCRIPT_EXTENSIONS = {".txt", ".md", ".markdown", ".fountain", ".screenplay"}
MAX_SCRIPT_BYTES = 512 * 1024
MAX_SCRIPT_CHARS = 60000
MAX_TITLE_CHARS = 120
MAX_SCENES = 40
MAX_CHARACTERS = 12
SCENE_SUMMARY_CHARS = 260

CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
API_KEY_PATTERN = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9_]{12,}|xox[baprs]-[A-Za-z0-9-]{12,})")
SPEAKER_PATTERN = re.compile(r"^\s*([\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9_·\-\s]{0,24})\s*[：:]\s*(\S.*)$")
SCENE_PATTERNS = [
    re.compile(r"^\s*(第[\u4e00-\u9fff0-9]+场|场景\s*[\u4e00-\u9fff0-9]+|镜头\s*[\u4e00-\u9fff0-9]+)\s*[：:.\-]?\s*(.*)$", re.I),
    re.compile(r"^\s*(INT\.|EXT\.|INT/EXT\.|内景|外景)\s+(.+)$", re.I),
    re.compile(r"^\s*(SCENE|SEQUENCE)\s+\d+\s*[：:.\-]?\s*(.*)$", re.I),
    re.compile(r"^\s*#{1,3}\s+(.+)$"),
]

STOP_CHARACTER_NAMES = {
    "内景",
    "外景",
    "场景",
    "镜头",
    "剧本",
    "字幕",
    "人物",
    "角色",
    "主要人物",
    "片名",
    "标题",
    "类型",
    "梗概",
    "旁白说明",
    "动作",
    "画面",
    "音乐",
    "音效",
    "cut",
    "fade",
    "scene",
    "int",
    "ext",
}

NARRATOR_NAMES = {"旁白", "narrator", "voiceover", "voice over", "v.o.", "vo"}
SUPPORTED_TARGET_MODELS = {"general", "sora", "runway", "kling", "pika", "luma"}
SUPPORTED_QUALITY_MODES = {"fast", "balanced", "high"}

MODEL_PROFILES = {
    "general": {
        "label": "General AI video model",
        "prompt_hint": "balanced prompt structure for broad AI video model compatibility",
        "motion_bias": "clear, physically plausible motion with stable continuity",
    },
    "sora": {
        "label": "Sora",
        "prompt_hint": "emphasize coherent world state, temporal continuity, natural camera movement",
        "motion_bias": "longer continuous motion, consistent physics, believable character behavior",
    },
    "runway": {
        "label": "Runway",
        "prompt_hint": "keep prompt concise, visual-first, with explicit camera and lighting direction",
        "motion_bias": "controlled camera movement, clean subject action, strong composition",
    },
    "kling": {
        "label": "Kling",
        "prompt_hint": "emphasize dynamic action, body movement, environment interaction and shot rhythm",
        "motion_bias": "expressive movement, readable action beats, strong subject-background relation",
    },
    "pika": {
        "label": "Pika",
        "prompt_hint": "use short vivid descriptions, strong visual hook, simple motion instruction",
        "motion_bias": "compact expressive motion, clear subject, minimal scene clutter",
    },
    "luma": {
        "label": "Luma",
        "prompt_hint": "emphasize cinematic realism, spatial depth, lens language and lighting continuity",
        "motion_bias": "smooth camera path, natural depth, consistent scene geometry",
    },
}

QUALITY_PROFILES = {
    "fast": {
        "label": "fast draft",
        "description": "每场只生成关键镜头，适合快速试方向。",
        "shot_types": ["key"],
    },
    "balanced": {
        "label": "balanced production",
        "description": "每场生成建立、动作、情绪三类镜头，适合默认制作。",
        "shot_types": ["establishing", "action", "emotion"],
    },
    "high": {
        "label": "high quality package",
        "description": "每场生成更完整的镜头包，适合精修和交付。",
        "shot_types": ["establishing", "action", "detail", "emotion", "transition"],
    },
}

SHOT_LIBRARY = {
    "key": {
        "duration": 6,
        "camera": "single decisive cinematic shot, clear subject, readable story beat",
        "purpose": "快速抓住本场最关键的视觉动作和情绪。",
    },
    "establishing": {
        "duration": 4,
        "camera": "wide establishing shot, slow dolly in, clear geography",
        "purpose": "建立空间、时间、气氛和人物站位。",
    },
    "action": {
        "duration": 6,
        "camera": "medium shot, motivated camera movement, readable body action",
        "purpose": "表现动作、关系和剧情推进。",
    },
    "detail": {
        "duration": 3,
        "camera": "insert shot, shallow depth of field, precise prop or gesture focus",
        "purpose": "补充道具、手部动作或关键视觉线索。",
    },
    "emotion": {
        "duration": 4,
        "camera": "close-up, subtle handheld breathing, expressive eyes",
        "purpose": "捕捉情绪变化和人物反应。",
    },
    "transition": {
        "duration": 4,
        "camera": "transition shot, motivated movement, scene-to-scene visual bridge",
        "purpose": "为下一场提供剪辑衔接和节奏缓冲。",
    },
}


# =========================
# Data Models
# =========================


@dataclass
class ProjectInput:
    script_path: str
    title: str
    output_dir: str
    language: str = "zh-CN"
    target_model: str = "general"
    quality_mode: str = "balanced"
    aspect_ratio: str = "16:9"
    max_scenes: int = MAX_SCENES
    max_characters: int = MAX_CHARACTERS


@dataclass
class AgentResult:
    agent_name: str
    output: Dict[str, Any]
    created_at: str


@dataclass
class VideoPromptWorkflowResult:
    project: ProjectInput
    script_analysis: AgentResult
    character_profiles: AgentResult
    storyboard_prompts: AgentResult
    video_package: AgentResult
    qa_report: AgentResult
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


def compact_text(text: str, max_chars: int = SCENE_SUMMARY_CHARS) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "…"


def safe_slug(value: str, fallback: str = "untitled") -> str:
    slug = re.sub(r"[^A-Za-z0-9_\-\u4e00-\u9fff]+", "_", value.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:60] or fallback


def normalize_name(name: str) -> str:
    cleaned = " ".join(name.strip().split())
    cleaned = cleaned.strip("[]【】（）()：:。,.，")
    return cleaned[:32]


def is_probable_character_name(name: str) -> bool:
    normalized = normalize_name(name)
    if not normalized:
        return False
    if normalized.lower() in STOP_CHARACTER_NAMES:
        return False
    if len(normalized) > 24:
        return False
    if any(char.isdigit() for char in normalized):
        return False
    return True


def sanitize_script_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = CONTROL_CHAR_PATTERN.sub("", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def validate_script_path(script_path: str | Path) -> Path:
    p = Path(script_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Script file not found: {p}")
    if not p.is_file():
        raise ValueError(f"Script path is not a file: {p}")
    if p.suffix.lower() not in ALLOWED_SCRIPT_EXTENSIONS:
        raise ValueError(
            f"Unsupported script extension: {p.suffix}. "
            f"Allowed: {sorted(ALLOWED_SCRIPT_EXTENSIONS)}"
        )
    if p.stat().st_size > MAX_SCRIPT_BYTES:
        raise ValueError(f"Script is too large. Max size: {MAX_SCRIPT_BYTES // 1024}KB")
    return p


def read_script_text(script_path: str | Path) -> str:
    p = validate_script_path(script_path)
    try:
        raw = p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Script must be UTF-8 encoded text.") from exc
    text = sanitize_script_text(raw)
    if not text:
        raise ValueError("Script cannot be empty.")
    if len(text) > MAX_SCRIPT_CHARS:
        raise ValueError(f"Script is too long. Max characters: {MAX_SCRIPT_CHARS}")
    return text


def validate_title(title: Optional[str], script_path: Path) -> str:
    if title:
        cleaned = compact_text(title, MAX_TITLE_CHARS)
        if cleaned:
            return cleaned
    return script_path.stem[:MAX_TITLE_CHARS] or "Untitled Script"


def validate_target_model(target_model: str) -> str:
    normalized = target_model.strip().lower()
    if normalized not in SUPPORTED_TARGET_MODELS:
        allowed = ", ".join(sorted(SUPPORTED_TARGET_MODELS))
        raise ValueError(f"Unsupported target model: {target_model}. Allowed: {allowed}")
    return normalized


def validate_quality_mode(quality_mode: str) -> str:
    normalized = quality_mode.strip().lower()
    if normalized not in SUPPORTED_QUALITY_MODES:
        allowed = ", ".join(sorted(SUPPORTED_QUALITY_MODES))
        raise ValueError(f"Unsupported quality mode: {quality_mode}. Allowed: {allowed}")
    return normalized


def validate_aspect_ratio(aspect_ratio: str) -> str:
    cleaned = aspect_ratio.strip()
    if not re.fullmatch(r"\d{1,2}:\d{1,2}", cleaned):
        raise ValueError("Aspect ratio must look like 16:9, 9:16, 1:1, or 2:3.")
    width, height = (int(part) for part in cleaned.split(":"))
    if width <= 0 or height <= 0:
        raise ValueError("Aspect ratio values must be positive.")
    return cleaned


def validate_limit(value: int, *, name: str, minimum: int, maximum: int) -> int:
    if value < minimum or value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return value


def contains_sensitive_token(text: str) -> bool:
    return API_KEY_PATTERN.search(text) is not None


# =========================
# Optional LLM Client
# =========================


class LLMClient:
    """Optional OpenAI JSON helper.

    The workflow runs without third-party dependencies by default.
    If --use-openai is enabled, OPENAI_API_KEY must exist and the OpenAI SDK must be installed.
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
                temperature=0.3,
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ValueError("LLM output must be a JSON object.")
            return parsed
        except Exception as exc:
            return {
                "warning": "OpenAI call failed; deterministic fallback returned.",
                "error_type": exc.__class__.__name__,
                "fallback": fallback,
            }


# =========================
# Script Parsing
# =========================


def detect_scene_heading(line: str) -> Optional[str]:
    stripped = line.strip()
    if not stripped:
        return None
    for pattern in SCENE_PATTERNS:
        match = pattern.match(stripped)
        if match:
            parts = [part for part in match.groups() if part]
            return compact_text(" ".join(parts), 100)
    return None


def split_scene_blocks(script_text: str, max_scenes: int = MAX_SCENES) -> List[Dict[str, Any]]:
    lines = script_text.splitlines()
    scenes: List[Dict[str, Any]] = []
    current_title = "Opening"
    current_lines: List[str] = []

    for line in lines:
        heading = detect_scene_heading(line)
        if heading and current_lines:
            current_text = "\n".join(current_lines).strip()
            if not (current_title == "Opening" and is_metadata_block(current_text)):
                scenes.append({"title": current_title, "text": current_text})
            current_title = heading
            current_lines = []
            continue
        if heading and not current_lines:
            current_title = heading
            continue
        current_lines.append(line)

    if current_lines:
        current_text = "\n".join(current_lines).strip()
        if not (current_title == "Opening" and is_metadata_block(current_text)):
            scenes.append({"title": current_title, "text": current_text})

    if len(scenes) <= 1 and len(script_text) > 1400:
        scenes = split_by_paragraph_chunks(script_text, max_scenes=max_scenes)

    normalized = []
    for index, scene in enumerate(scenes[:max_scenes], start=1):
        text = scene["text"].strip()
        if not text:
            continue
        normalized.append(
            {
                "scene_id": f"S{index:02d}",
                "title": scene["title"] or f"Scene {index}",
                "summary": compact_text(text),
                "text_excerpt": compact_text(text, 900),
                "location": infer_location(scene["title"], text),
                "time_of_day": infer_time_of_day(scene["title"], text),
                "estimated_duration_seconds": estimate_duration_seconds(text),
            }
        )
    return normalized or [
        {
            "scene_id": "S01",
            "title": "Opening",
            "summary": compact_text(script_text),
            "text_excerpt": compact_text(script_text, 900),
            "location": "未明确地点",
            "time_of_day": "未明确时间",
            "estimated_duration_seconds": estimate_duration_seconds(script_text),
        }
    ]


def is_metadata_block(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    metadata_prefixes = ("片名", "标题", "人物", "角色", "主要人物", "类型", "梗概", "故事简介", "主题")
    metadata_count = sum(1 for line in lines if line.startswith(metadata_prefixes) and ("：" in line or ":" in line))
    return metadata_count == len(lines)


def split_by_paragraph_chunks(script_text: str, max_scenes: int = MAX_SCENES) -> List[Dict[str, str]]:
    paragraphs = [para.strip() for para in re.split(r"\n\s*\n", script_text) if para.strip()]
    chunks: List[Dict[str, str]] = []
    current: List[str] = []
    current_len = 0
    for para in paragraphs:
        if current and current_len + len(para) > 1200:
            chunks.append({"title": f"Scene {len(chunks) + 1}", "text": "\n\n".join(current)})
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para)
    if current:
        chunks.append({"title": f"Scene {len(chunks) + 1}", "text": "\n\n".join(current)})
    return chunks[:max_scenes]


def infer_location(title: str, text: str) -> str:
    source = f"{title} {text[:300]}"
    if any(word in source for word in ["教室", "校园", "学校", "操场"]):
        return "校园空间"
    if any(word in source for word in ["剧院", "舞台", "后台", "礼堂"]):
        return "剧院或舞台"
    if any(word in source for word in ["街", "路", "巷", "城市", "天桥"]):
        return "城市外景"
    if any(word in source for word in ["房间", "卧室", "客厅", "厨房", "公寓"]):
        return "室内生活空间"
    if re.search(r"\b(INT\.|内景)\b", source, re.I):
        return "室内"
    if re.search(r"\b(EXT\.|外景)\b", source, re.I):
        return "室外"
    return "未明确地点"


def infer_time_of_day(title: str, text: str) -> str:
    source = f"{title} {text[:300]}".lower()
    if any(word in source for word in ["夜", "晚上", "深夜", "night"]):
        return "夜晚"
    if any(word in source for word in ["清晨", "黎明", "早晨", "morning", "dawn"]):
        return "清晨"
    if any(word in source for word in ["黄昏", "傍晚", "sunset", "dusk"]):
        return "黄昏"
    if any(word in source for word in ["白天", "日", "day"]):
        return "白天"
    return "未明确时间"


def estimate_duration_seconds(text: str) -> int:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    words = len(re.findall(r"[A-Za-z0-9_]+", text))
    estimated = max(8, round((chinese_chars / 5 + words / 2) * 0.55))
    return min(90, estimated)


def infer_genre_and_tone(script_text: str) -> Dict[str, Any]:
    lowered = script_text.lower()
    genre_scores = {
        "科幻": ["未来", "飞船", "星球", "机器人", "ai", "space", "cyber"],
        "悬疑": ["秘密", "失踪", "真相", "侦探", "谜", "suspense", "mystery"],
        "青春": ["校园", "少年", "毕业", "同学", "青春", "school"],
        "奇幻": ["魔法", "王国", "预言", "精灵", "fantasy", "dragon"],
        "现实剧情": ["家庭", "城市", "工作", "生活", "母亲", "父亲"],
    }
    best_genre = "剧情短片"
    best_score = 0
    for genre, keywords in genre_scores.items():
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score > best_score:
            best_genre = genre
            best_score = score
    tones = []
    tone_keywords = {
        "紧张": ["紧张", "追", "逃", "危险", "倒计时"],
        "温柔": ["温柔", "安静", "微笑", "拥抱", "回忆"],
        "史诗": ["宏大", "命运", "战争", "远方", "传说"],
        "孤独": ["孤独", "空荡", "沉默", "雨", "独自"],
        "明亮": ["阳光", "希望", "清晨", "明亮"],
    }
    for tone, keywords in tone_keywords.items():
        if any(keyword in script_text for keyword in keywords):
            tones.append(tone)
    return {"genre": best_genre, "tone": tones or ["电影感", "叙事感"]}


def extract_speakers(script_text: str) -> Dict[str, Dict[str, Any]]:
    speakers: Dict[str, Dict[str, Any]] = {}
    lines = script_text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        match = SPEAKER_PATTERN.match(line)
        if not match:
            continue
        name = normalize_name(match.group(1))
        if not is_probable_character_name(name):
            continue
        entry = speakers.setdefault(name, {"dialogue_count": 0, "line_numbers": [], "sample_dialogue": []})
        entry["dialogue_count"] += 1
        entry["line_numbers"].append(line_number)
        if len(entry["sample_dialogue"]) < 3:
            entry["sample_dialogue"].append(compact_text(match.group(2), 80))
    return speakers


def extract_declared_characters(script_text: str) -> List[str]:
    declared: List[str] = []
    for pattern in [r"(?:人物|角色|主要人物)\s*[：:]\s*(.+)", r"cast\s*[：:]\s*(.+)"]:
        for match in re.finditer(pattern, script_text, re.I):
            values = re.split(r"[、,，/|；;]\s*", match.group(1))
            for value in values:
                name = normalize_name(value)
                if is_probable_character_name(name):
                    declared.append(name)
    return declared


def is_narrator_name(name: str) -> bool:
    return normalize_name(name).lower() in NARRATOR_NAMES


def build_character_profiles(
    script_text: str,
    scenes: List[Dict[str, Any]],
    max_characters: int = MAX_CHARACTERS,
) -> List[Dict[str, Any]]:
    speakers = extract_speakers(script_text)
    declared = extract_declared_characters(script_text)
    for name in declared:
        speakers.setdefault(name, {"dialogue_count": 0, "line_numbers": [], "sample_dialogue": []})

    if not speakers:
        speakers["主角"] = {"dialogue_count": 0, "line_numbers": [], "sample_dialogue": []}

    scene_text_by_id = {scene["scene_id"]: scene["text_excerpt"] for scene in scenes}
    profiles: List[Dict[str, Any]] = []
    sorted_names = sorted(speakers, key=lambda item: (-speakers[item]["dialogue_count"], item))
    for index, name in enumerate(sorted_names[:max_characters], start=1):
        appears_in = [
            scene_id
            for scene_id, text in scene_text_by_id.items()
            if name in text or speakers[name]["dialogue_count"] == 0 and index == 1
        ]
        role = "protagonist" if index == 1 else "supporting_character"
        if is_narrator_name(name):
            role = "narrator"
        is_voice_only = role == "narrator"
        profiles.append(
            {
                "character_id": f"C{index:02d}",
                "name": name,
                "role": role,
                "visual_role": "voice_only" if is_voice_only else "visible_character",
                "appears_in_scenes": appears_in[:MAX_SCENES],
                "dialogue_count": speakers[name]["dialogue_count"],
                "sample_dialogue": speakers[name]["sample_dialogue"],
                "visual_identity": build_visual_identity(name, role, index),
                "continuity_notes": build_character_continuity_notes(is_voice_only),
                "three_view_prompt": "" if is_voice_only else build_three_view_prompt(name, role, index),
                "voice_prompt": build_voice_prompt(name) if is_voice_only else "",
                "negative_prompt": ""
                if is_voice_only
                else "different face, inconsistent identity, extra limbs, distorted hands, wrong age, random costume, text watermark, logo",
            }
        )
    return profiles


def build_character_continuity_notes(is_voice_only: bool) -> List[str]:
    if is_voice_only:
        return [
            "旁白或画外音默认不生成三视图，避免把声音角色误做成可视人物。",
            "如旁白需要出镜，请在剧本中给出明确动作、外貌或出场描述。",
        ]
    return [
        "所有镜头保持同一五官比例、发型轮廓、服装主色和年龄感",
        "不要在不同分镜中改变角色年龄、发色、脸型或标志性配饰",
        "三视图、分镜和视频提示词使用同一个 character_id 绑定角色",
    ]


def build_voice_prompt(name: str) -> str:
    return compact_text(
        f"""
        Voice-over reference for {name}: calm cinematic narration, clear emotion, natural pacing,
        no visible body required, keep voice tone consistent across scenes.
        """,
        400,
    )


def build_visual_identity(name: str, role: str, index: int) -> Dict[str, str]:
    palette = ["深蓝与白", "黑色与暖灰", "酒红与米白", "墨绿与灰", "浅棕与象牙白"]
    return {
        "identity_seed": f"{safe_slug(name)}_{role}_{index:02d}",
        "age_range": "young adult / adult, adjust to script context",
        "face": "clear facial structure, memorable silhouette, realistic cinematic character design",
        "hair": "consistent hairstyle across all shots",
        "costume": f"story-appropriate costume, primary palette {palette[(index - 1) % len(palette)]}",
        "props": "only include props that are mentioned or strongly implied by the script",
    }


def build_three_view_prompt(name: str, role: str, index: int) -> str:
    identity = f"{safe_slug(name)}_{role}_{index:02d}"
    return compact_text(
        f"""
        Character reference sheet for {name}, identity seed {identity}, three-view turnaround,
        front view, side view, back view, full body, neutral A-pose, consistent face and hair,
        consistent costume and color palette, clean studio background, cinematic realistic design,
        production-ready for AI video continuity, no text, no watermark, no extra characters.
        """,
        900,
    )


def scene_characters(scene: Dict[str, Any], profiles: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    text = scene["text_excerpt"]
    visible_profiles = [profile for profile in profiles if profile.get("visual_role") != "voice_only"]
    selected = [
        {"character_id": profile["character_id"], "name": profile["name"]}
        for profile in visible_profiles
        if profile["name"] in text
    ]
    if not selected and visible_profiles:
        selected = [{"character_id": visible_profiles[0]["character_id"], "name": visible_profiles[0]["name"]}]
    return selected[:4]


def build_shot_prompt(
    scene: Dict[str, Any],
    characters: List[Dict[str, str]],
    genre: str,
    tone: List[str],
    shot_type: str,
    shot_index: int,
    target_model: str,
    quality_mode: str,
    aspect_ratio: str,
) -> Dict[str, Any]:
    character_names = ", ".join(f"{char['character_id']} {char['name']}" for char in characters) or "no visible character"
    tone_text = ", ".join(tone)
    model_profile = MODEL_PROFILES[target_model]
    quality_profile = QUALITY_PROFILES[quality_mode]
    shot_profile = SHOT_LIBRARY[shot_type]
    prompt = compact_text(
        f"""
        AI video storyboard prompt for {model_profile['label']}, aspect ratio {aspect_ratio}, {genre}, tone {tone_text}.
        Scene {scene['scene_id']} {scene['title']}, location {scene['location']}, time {scene['time_of_day']}.
        Characters: {character_names}. Story beat: {scene['summary']}.
        Shot type: {shot_type}. Purpose: {shot_profile['purpose']}. Camera: {shot_profile['camera']}.
        Lighting: cinematic natural light, coherent shadows, scene-matched color temperature.
        Target model note: {model_profile['prompt_hint']}. Motion: {model_profile['motion_bias']}.
        Quality mode: {quality_profile['label']} - {quality_profile['description']}
        Continuity: keep character identity, costume, props and screen direction consistent.
        Output: realistic cinematic video, high detail, no subtitles, no watermark, no logo.
        """,
        1200,
    )
    return {
        "shot_id": f"{scene['scene_id']}-{shot_index:02d}",
        "scene_id": scene["scene_id"],
        "shot_type": shot_type,
        "duration_seconds": shot_profile["duration"],
        "camera": shot_profile["camera"],
        "target_model": target_model,
        "quality_mode": quality_mode,
        "aspect_ratio": aspect_ratio,
        "characters": characters,
        "prompt": prompt,
        "negative_prompt": "low quality, flicker, inconsistent character, face morphing, extra fingers, broken hands, unreadable text, watermark, logo, random cuts, jumpy camera",
    }


def build_storyboard(
    scenes: List[Dict[str, Any]],
    profiles: List[Dict[str, Any]],
    genre: str,
    tone: List[str],
    target_model: str,
    quality_mode: str,
    aspect_ratio: str,
) -> List[Dict[str, Any]]:
    storyboard = []
    for scene in scenes:
        characters = scene_characters(scene, profiles)
        shots = [
            build_shot_prompt(
                scene,
                characters,
                genre,
                tone,
                shot_type,
                index,
                target_model,
                quality_mode,
                aspect_ratio,
            )
            for index, shot_type in enumerate(QUALITY_PROFILES[quality_mode]["shot_types"], start=1)
        ]
        storyboard.append(
            {
                "scene_id": scene["scene_id"],
                "scene_title": scene["title"],
                "scene_summary": scene["summary"],
                "location": scene["location"],
                "time_of_day": scene["time_of_day"],
                "estimated_duration_seconds": scene["estimated_duration_seconds"],
                "shots": shots,
            }
        )
    return storyboard


def render_storyboard_markdown(storyboard: List[Dict[str, Any]]) -> str:
    lines = ["# Storyboard Video Prompts", ""]
    for scene in storyboard:
        lines.extend(
            [
                f"## {scene['scene_id']} {scene['scene_title']}",
                "",
                f"- Location: {scene['location']}",
                f"- Time: {scene['time_of_day']}",
                f"- Summary: {scene['scene_summary']}",
                "",
            ]
        )
        for shot in scene["shots"]:
            lines.extend(
                [
                    f"### {shot['shot_id']} {shot['shot_type']}",
                    "",
                    f"- Duration: {shot['duration_seconds']}s",
                    f"- Camera: {shot['camera']}",
                    "",
                    "Prompt:",
                    "",
                    shot["prompt"],
                    "",
                    "Negative prompt:",
                    "",
                    shot["negative_prompt"],
                    "",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def render_character_markdown(profiles: List[Dict[str, Any]]) -> str:
    lines = ["# Character Three-View Prompts", ""]
    for profile in profiles:
        is_voice_only = profile.get("visual_role") == "voice_only"
        lines.extend(
            [
                f"## {profile['character_id']} {profile['name']}",
                "",
                f"- Role: {profile['role']}",
                f"- Visual role: {profile.get('visual_role', 'visible_character')}",
                f"- Identity seed: {profile['visual_identity']['identity_seed']}",
                f"- Appears in: {', '.join(profile['appears_in_scenes']) or 'not detected'}",
                "",
            ]
        )
        if is_voice_only:
            lines.extend(["Voice prompt:", "", profile.get("voice_prompt", ""), ""])
        else:
            lines.extend(
                [
                    "Three-view prompt:",
                    "",
                    profile["three_view_prompt"],
                    "",
                    "Negative prompt:",
                    "",
                    profile["negative_prompt"],
                    "",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def render_production_brief_markdown(
    project: ProjectInput,
    script_analysis: Dict[str, Any],
    character_profiles: Dict[str, Any],
    storyboard_prompts: Dict[str, Any],
    video_package: Dict[str, Any],
    qa_report: Dict[str, Any],
) -> str:
    style = video_package.get("global_style_bible", {})
    source = video_package.get("source_summary", {})
    lines = [
        "# Video Prompt Production Brief",
        "",
        f"- Project: {project.title}",
        f"- Target model: {style.get('target_model', project.target_model)}",
        f"- Quality mode: {style.get('quality_mode', project.quality_mode)}",
        f"- Aspect ratio: {style.get('aspect_ratio', project.aspect_ratio)}",
        f"- Genre: {source.get('genre', script_analysis.get('genre', 'unknown'))}",
        f"- Tone: {', '.join(source.get('tone', script_analysis.get('tone', [])))}",
        f"- Scenes: {script_analysis.get('scene_count', 0)}",
        f"- Characters: {character_profiles.get('character_count', 0)}",
        f"- Visible character refs: {character_profiles.get('visual_character_count', 0)}",
        f"- Shot prompts: {qa_report.get('shot_prompt_count', 0)}",
        f"- QA status: {qa_report.get('status', 'unknown')} ({qa_report.get('score', 0)})",
        "",
        "## Model Guidance",
        "",
        f"- Prompt note: {style.get('target_model_profile', {}).get('prompt_hint', '')}",
        f"- Motion bias: {style.get('target_model_profile', {}).get('motion_bias', '')}",
        "",
        "## Handoff Order",
        "",
    ]
    lines.extend(f"- {step}" for step in video_package.get("handoff_order", []))
    lines.extend(["", "## Quality Checklist", ""])
    for check, passed in qa_report.get("checks", {}).items():
        marker = "PASS" if passed else "REVIEW"
        lines.append(f"- {marker}: {check}")
    suggestions = qa_report.get("suggestions", [])
    if suggestions:
        lines.extend(["", "## Suggestions", ""])
        lines.extend(f"- {suggestion}" for suggestion in suggestions)
    lines.extend(["", "## Storyboard Index", ""])
    for scene in storyboard_prompts.get("storyboard", []):
        lines.append(f"- {scene['scene_id']} {scene['scene_title']}: {len(scene.get('shots', []))} shots")
    return "\n".join(lines).strip() + "\n"


# =========================
# Agents
# =========================


class BaseAgent:
    name = "BaseAgent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def result(self, output: Dict[str, Any]) -> AgentResult:
        return AgentResult(agent_name=self.name, output=output, created_at=now_iso())


class ScriptStructureAgent(BaseAgent):
    name = "ScriptStructureAgent"

    def run(self, project: ProjectInput, script_text: str) -> AgentResult:
        scenes = split_scene_blocks(script_text, max_scenes=project.max_scenes)
        genre_tone = infer_genre_and_tone(script_text)
        fallback = {
            "title": project.title,
            "script_chars": len(script_text),
            "scene_count": len(scenes),
            "genre": genre_tone["genre"],
            "tone": genre_tone["tone"],
            "scenes": scenes,
            "warnings": build_script_warnings(script_text, scenes),
        }
        system = "你是剧本拆解 Agent。只输出 JSON 对象，不输出解释文字。"
        user = json.dumps(
            {
                "task": "识别剧本场次、核心角色线索、类型、情绪和视频分镜需要的结构。",
                "fallback_schema": fallback,
                "script_excerpt": script_text[:8000],
            },
            ensure_ascii=False,
        )
        output = self.llm.complete_json(system, user, fallback)
        if "fallback" in output and "warning" in output:
            output = fallback | {"llm_warning": output["warning"], "llm_error_type": output["error_type"]}
        elif not has_valid_scene_output(output):
            output = fallback | {"llm_warning": "OpenAI output did not include a valid scene structure; deterministic fallback used."}
        return self.result(output)


class CharacterProfileAgent(BaseAgent):
    name = "CharacterProfileAgent"

    def run(self, script_text: str, script_analysis: Dict[str, Any], max_characters: int) -> AgentResult:
        profiles = build_character_profiles(script_text, script_analysis.get("scenes", []), max_characters=max_characters)
        visual_profiles = [profile for profile in profiles if profile.get("visual_role") != "voice_only"]
        output = {
            "character_count": len(profiles),
            "visual_character_count": len(visual_profiles),
            "characters": profiles,
            "three_view_usage": [
                "先用 three_view_prompt 生成角色三视图或角色设定图",
                "将 character_id 与分镜 prompt 一起使用，增强视频模型的人物一致性",
                "同一角色在所有镜头中保持 visual_identity 字段不变",
                "旁白等 voice_only 角色默认只生成声音提示词，不生成三视图",
            ],
        }
        return self.result(output)


class StoryboardPromptAgent(BaseAgent):
    name = "StoryboardPromptAgent"

    def run(self, project: ProjectInput, script_analysis: Dict[str, Any], character_profiles: Dict[str, Any]) -> AgentResult:
        scenes = script_analysis.get("scenes", [])
        characters = character_profiles.get("characters", [])
        storyboard = build_storyboard(
            scenes=scenes,
            profiles=characters,
            genre=script_analysis.get("genre", "剧情短片"),
            tone=script_analysis.get("tone", ["电影感"]),
            target_model=project.target_model,
            quality_mode=project.quality_mode,
            aspect_ratio=project.aspect_ratio,
        )
        output = {
            "storyboard_count": len(storyboard),
            "target_model": project.target_model,
            "quality_mode": project.quality_mode,
            "aspect_ratio": project.aspect_ratio,
            "target_models": ["Sora", "Runway", "Kling", "Pika", "Luma", "可兼容其他 AI 视频模型"],
            "storyboard": storyboard,
        }
        return self.result(output)


class VideoPackageAgent(BaseAgent):
    name = "VideoPackageAgent"

    def run(
        self,
        project: ProjectInput,
        script_analysis: Dict[str, Any],
        character_profiles: Dict[str, Any],
        storyboard_prompts: Dict[str, Any],
    ) -> AgentResult:
        visible_characters = [
            character
            for character in character_profiles.get("characters", [])
            if character.get("visual_role") != "voice_only"
        ]
        voice_roles = [
            {
                "character_id": character["character_id"],
                "name": character["name"],
                "voice_prompt": character.get("voice_prompt", ""),
            }
            for character in character_profiles.get("characters", [])
            if character.get("visual_role") == "voice_only"
        ]
        output = {
            "project_title": project.title,
            "global_style_bible": {
                "format": "cinematic short film storyboard prompt package",
                "target_model": project.target_model,
                "target_model_profile": MODEL_PROFILES[project.target_model],
                "quality_mode": project.quality_mode,
                "quality_profile": QUALITY_PROFILES[project.quality_mode],
                "aspect_ratio": project.aspect_ratio,
                "visual_style": "realistic cinematic, coherent color palette, consistent production design",
                "camera_language": "motivated movement, readable geography, no random cuts",
                "continuity_rules": [
                    "Use character_id and identity_seed in every shot involving that character.",
                    "Keep wardrobe, hairstyle, props, time of day and screen direction stable inside each scene.",
                    "Generate character three-view references before generating final video shots.",
                ],
            },
            "character_reference_prompts": [
                {
                    "character_id": character["character_id"],
                    "name": character["name"],
                    "three_view_prompt": character["three_view_prompt"],
                    "negative_prompt": character["negative_prompt"],
                }
                for character in visible_characters
            ],
            "voice_reference_prompts": voice_roles,
            "shot_prompts": [
                shot
                for scene in storyboard_prompts.get("storyboard", [])
                for shot in scene.get("shots", [])
            ],
            "global_negative_prompt": (
                "low quality, visual flicker, inconsistent character identity, face morphing, wrong costume, "
                "extra limbs, bad hands, unreadable text, watermark, logo, random scene changes, unstable camera"
            ),
            "handoff_order": [
                "1. Generate or approve character three-view references.",
                "2. Lock visual_identity and identity_seed for each character.",
                "3. Generate storyboard shots scene by scene.",
                "4. Review continuity before final video rendering.",
            ],
            "source_summary": {
                "scene_count": script_analysis.get("scene_count", 0),
                "character_count": character_profiles.get("character_count", 0),
                "visual_character_count": character_profiles.get("visual_character_count", 0),
                "genre": script_analysis.get("genre", "unknown"),
                "tone": script_analysis.get("tone", []),
                "target_model": project.target_model,
                "quality_mode": project.quality_mode,
                "aspect_ratio": project.aspect_ratio,
            },
        }
        return self.result(output)


class QualityAssuranceAgent(BaseAgent):
    name = "QualityAssuranceAgent"

    def run(
        self,
        script_text: str,
        script_analysis: Dict[str, Any],
        character_profiles: Dict[str, Any],
        storyboard_prompts: Dict[str, Any],
        video_package: Dict[str, Any],
    ) -> AgentResult:
        shot_prompts = video_package.get("shot_prompts", [])
        character_refs = video_package.get("character_reference_prompts", [])
        style_bible = video_package.get("global_style_bible", {})
        checks = {
            "has_scene_analysis": script_analysis.get("scene_count", 0) > 0,
            "has_character_profiles": character_profiles.get("character_count", 0) > 0,
            "has_visible_character_refs": character_profiles.get("visual_character_count", 0) == len(character_refs),
            "has_three_view_prompts": all(ref.get("three_view_prompt") for ref in character_refs),
            "has_storyboard_prompts": len(shot_prompts) >= max(1, script_analysis.get("scene_count", 1)),
            "has_negative_prompts": all(shot.get("negative_prompt") for shot in shot_prompts),
            "has_continuity_rules": bool(style_bible.get("continuity_rules")),
            "has_target_model_profile": bool(style_bible.get("target_model_profile")),
            "has_aspect_ratio": bool(style_bible.get("aspect_ratio")),
            "no_detected_secret_tokens": not contains_sensitive_token(script_text),
        }
        score = sum(1 for value in checks.values() if value) / len(checks)
        suggestions = []
        if not checks["no_detected_secret_tokens"]:
            suggestions.append("剧本文本疑似包含 API key 或 token，请先移除敏感信息。")
        if script_analysis.get("scene_count", 0) == 1:
            suggestions.append("如果剧本较长，建议用“第 1 场 / 场景 1 / INT. / EXT.”标明场次。")
        if character_profiles.get("character_count", 0) == 1:
            suggestions.append("如果有多位角色，建议使用“角色名：台词”的格式帮助识别。")
        status = "pass" if score >= 0.85 else "needs_revision"
        if not checks["no_detected_secret_tokens"]:
            status = "needs_revision"
        output = {
            "checks": checks,
            "score": round(score, 2),
            "status": status,
            "suggestions": suggestions,
            "storyboard_count": storyboard_prompts.get("storyboard_count", 0),
            "shot_prompt_count": len(shot_prompts),
        }
        return self.result(output)


def has_valid_scene_output(output: Dict[str, Any]) -> bool:
    scenes = output.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        return False
    required = {"scene_id", "title", "summary", "text_excerpt", "location", "time_of_day"}
    return all(isinstance(scene, dict) and required.issubset(scene) for scene in scenes)


def build_script_warnings(script_text: str, scenes: List[Dict[str, Any]]) -> List[str]:
    warnings = []
    if contains_sensitive_token(script_text):
        warnings.append("Script appears to contain a secret token or API key.")
    if len(scenes) == 1 and len(script_text) > 1200:
        warnings.append("Only one scene detected. Add scene headings for better storyboard segmentation.")
    if not extract_speakers(script_text):
        warnings.append("No dialogue speaker markers detected. Use '角色名：台词' for better character recognition.")
    return warnings


# =========================
# Orchestrator
# =========================


class VideoPromptWorkflow:
    def __init__(self, llm: LLMClient):
        self.script_agent = ScriptStructureAgent(llm)
        self.character_agent = CharacterProfileAgent(llm)
        self.storyboard_agent = StoryboardPromptAgent(llm)
        self.video_package_agent = VideoPackageAgent(llm)
        self.qa_agent = QualityAssuranceAgent(llm)

    def run(self, project: ProjectInput, script_text: str) -> VideoPromptWorkflowResult:
        output_dir = ensure_dir(project.output_dir)
        saved_files: List[str] = []

        script_analysis = self.script_agent.run(project, script_text)
        path = output_dir / "01_script_analysis.json"
        save_json(path, asdict(script_analysis))
        saved_files.append(str(path))

        character_profiles = self.character_agent.run(script_text, script_analysis.output, project.max_characters)
        path = output_dir / "02_character_profiles.json"
        save_json(path, asdict(character_profiles))
        saved_files.append(str(path))

        storyboard_prompts = self.storyboard_agent.run(project, script_analysis.output, character_profiles.output)
        path = output_dir / "03_storyboard_prompts.json"
        save_json(path, asdict(storyboard_prompts))
        saved_files.append(str(path))

        video_package = self.video_package_agent.run(
            project,
            script_analysis.output,
            character_profiles.output,
            storyboard_prompts.output,
        )
        path = output_dir / "04_video_prompt_package.json"
        save_json(path, asdict(video_package))
        saved_files.append(str(path))

        qa_report = self.qa_agent.run(
            script_text,
            script_analysis.output,
            character_profiles.output,
            storyboard_prompts.output,
            video_package.output,
        )
        path = output_dir / "05_qa_report.json"
        save_json(path, asdict(qa_report))
        saved_files.append(str(path))

        storyboard_md = output_dir / "storyboard_prompts.md"
        save_text(storyboard_md, render_storyboard_markdown(storyboard_prompts.output["storyboard"]))
        saved_files.append(str(storyboard_md))

        character_md = output_dir / "character_three_view_prompts.md"
        save_text(character_md, render_character_markdown(character_profiles.output["characters"]))
        saved_files.append(str(character_md))

        production_brief_md = output_dir / "production_brief.md"
        save_text(
            production_brief_md,
            render_production_brief_markdown(
                project,
                script_analysis.output,
                character_profiles.output,
                storyboard_prompts.output,
                video_package.output,
                qa_report.output,
            ),
        )
        saved_files.append(str(production_brief_md))

        package_path = output_dir / "video_workflow_result.json"
        result = VideoPromptWorkflowResult(
            project=project,
            script_analysis=script_analysis,
            character_profiles=character_profiles,
            storyboard_prompts=storyboard_prompts,
            video_package=video_package,
            qa_report=qa_report,
            saved_files=saved_files + [str(package_path)],
        )
        save_json(package_path, asdict(result))
        saved_files.append(str(package_path))

        return result


# =========================
# CLI
# =========================


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Script-to-Video Prompt Workflow")
    parser.add_argument("--script", required=True, help="Path to screenplay text: txt/md/fountain/screenplay")
    parser.add_argument("--title", default=None, help="Project title. Defaults to script file name.")
    parser.add_argument("--out", default="./outputs/video", help="Output directory")
    parser.add_argument("--language", default="zh-CN", help="Output language hint")
    parser.add_argument(
        "--target-model",
        choices=sorted(SUPPORTED_TARGET_MODELS),
        default="general",
        help="Prompt profile for a target video model",
    )
    parser.add_argument(
        "--quality-mode",
        choices=sorted(SUPPORTED_QUALITY_MODES),
        default="balanced",
        help="fast creates 1 shot per scene, balanced creates 3, high creates 5",
    )
    parser.add_argument("--aspect-ratio", default="16:9", help="Video aspect ratio, e.g. 16:9 or 9:16")
    parser.add_argument("--max-scenes", type=int, default=MAX_SCENES, help="Maximum scenes to process")
    parser.add_argument("--max-characters", type=int, default=MAX_CHARACTERS, help="Maximum characters to profile")
    parser.add_argument("--use-openai", action="store_true", help="Enable optional OpenAI JSON enhancement")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    try:
        args = parse_args(argv)
        script_path = validate_script_path(args.script)
        script_text = read_script_text(script_path)
        output_dir = ensure_dir(args.out)
        project = ProjectInput(
            script_path=str(script_path),
            title=validate_title(args.title, script_path),
            output_dir=str(output_dir),
            language=args.language,
            target_model=validate_target_model(args.target_model),
            quality_mode=validate_quality_mode(args.quality_mode),
            aspect_ratio=validate_aspect_ratio(args.aspect_ratio),
            max_scenes=validate_limit(args.max_scenes, name="max-scenes", minimum=1, maximum=MAX_SCENES),
            max_characters=validate_limit(args.max_characters, name="max-characters", minimum=1, maximum=MAX_CHARACTERS),
        )
        workflow = VideoPromptWorkflow(LLMClient(use_openai=args.use_openai, model=args.model))
        result = workflow.run(project, script_text)

        print("\n=== Script-to-Video Prompt Workflow Finished ===")
        print(f"QA status: {result.qa_report.output['status']}")
        print(f"QA score: {result.qa_report.output['score']}")
        print(f"Scenes: {result.script_analysis.output.get('scene_count', 0)}")
        print(f"Characters: {result.character_profiles.output.get('character_count', 0)}")
        print(f"Target model: {result.project.target_model}")
        print(f"Quality mode: {result.project.quality_mode}")
        print(f"Aspect ratio: {result.project.aspect_ratio}")
        print(f"Shot prompts: {result.qa_report.output.get('shot_prompt_count', 0)}")
        print("\nSaved files:")
        for file in result.saved_files:
            print(f"- {file}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
