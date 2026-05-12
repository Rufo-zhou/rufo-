const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const dom = {
  canvas: $("#studio-canvas"),
  cursor: $("#cursor-orbit"),
  cursorLabel: $("#cursor-label"),
  scrollMeter: $("#scroll-meter"),
  hero: $("#hero"),
  heroObjectStage: $("#hero-object-stage"),
  hotspotButtons: $$(".object-hotspot"),
  languageButtons: $$(".lang-button"),
  form: $("#script-form"),
  scriptInput: $("#script-input"),
  inputMeter: $("#input-meter"),
  modelTarget: $("#model-target"),
  stylePreset: $("#style-preset"),
  aspectRatio: $("#aspect-ratio"),
  shotDepth: $("#shot-depth"),
  sceneLimit: $("#scene-limit"),
  sceneLimitOutput: $("#scene-limit-output"),
  statusLine: $("#status-line"),
  outputModel: $("#output-model"),
  outputCount: $("#output-count"),
  shotStack: $("#shot-stack"),
  characterGrid: $("#character-grid"),
  packageOutput: $("#package-output"),
  hudShots: $("#hud-shots"),
  hudCharacters: $("#hud-characters"),
  copyPackage: $("#copy-package"),
  downloadMd: $("#download-md"),
  downloadCsv: $("#download-csv"),
};

const translations = {
  zh: {
    "nav.studio": "创作台",
    "nav.flow": "流程",
    "nav.systems": "系统",
    "nav.docs": "文档",
    "hero.eyebrow": "AI 视频创作工作流",
    "hero.title": "把剧本变成可导演的影像方案。",
    "hero.subtitle": "输入剧本，即刻生成分镜提示词、人物三视图、模型队列和制作交付包。",
    "hero.start": "开始创作",
    "hero.system": "查看流程",
    "hotspot.script": "剧本层",
    "hotspot.shots": "分镜层",
    "hotspot.model": "模型交付",
    "hud.package": "实时创作包",
    "hud.characters": "角色一致性",
    "hud.safety": "安全机制",
    "hud.local": "本地生成",
    "studio.eyebrow": "创作控制台",
    "studio.title": "直接在网页里生成创作包",
    "studio.script": "剧本",
    "control.model": "模型",
    "control.style": "风格",
    "control.aspect": "画幅",
    "control.depth": "镜头密度",
    "control.limit": "场次上限",
    "action.generate": "生成创作包",
    "action.copy": "复制提示词包",
    "tab.shots": "分镜",
    "tab.characters": "角色",
    "tab.package": "创作包",
    "workflow.eyebrow": "制作地图",
    "workflow.title": "从剧本到模型交付",
    "workflow.step1.title": "剧本识别",
    "workflow.step1.body": "识别场次、时间、地点、角色和冲突，把松散文本整理成镜头骨架。",
    "workflow.step2.title": "分镜导演",
    "workflow.step2.body": "生成景别、运动、镜头意图、画面层次和模型可读提示词。",
    "workflow.step3.title": "角色设定",
    "workflow.step3.body": "输出三视图提示词、造型规则和角色一致性约束。",
    "workflow.step4.title": "模型队列",
    "workflow.step4.body": "形成 Markdown 创作包和 CSV 队列，方便继续进入视频生成工具。",
    "gallery.eyebrow": "创意系统",
    "gallery.title": "一个仓库，两个生产系统",
    "gallery.poster.eyebrow": "海报工作流",
    "gallery.poster.title": "肖像到叙事海报",
    "gallery.poster.body": "风格预设 / 画幅 / 模型目标 / 多版本提示词",
    "gallery.video.eyebrow": "视频工作流",
    "gallery.video.title": "剧本到 AI 视频分镜",
    "gallery.video.body": "镜头队列 / 人物三视图 / CSV / 模型交付包",
    "gallery.qa.eyebrow": "安全系统",
    "gallery.qa.title": "生成前风险检查",
    "gallery.qa.body": "本地生成 / 无数据上传 / 输入清理 / 提示词完整度",
    "docs.eyebrow": "开源社区格式",
    "docs.title": "面向社区的规范入口",
    "docs.video": "剧本识别、分镜、角色三视图",
    "docs.poster": "人物海报提示词生产",
    "docs.quality": "质量模式和模型选择",
    "docs.ci": "自动测试和安全检查",
    "status.ready": "已准备好进行新的制作。",
    "status.empty": "请先粘贴剧本或场景梗概。",
    "status.secret": "检测到疑似密钥内容，请删除后再生成。",
    "status.generated": "已生成 {shots} 个镜头和 {characters} 个角色参考。",
    "status.copied": "提示词包已复制。",
    "status.copyFailed": "复制失败，可以直接使用创作包面板中的文字。",
    "status.md": "Markdown 创作包已下载。",
    "status.csv": "CSV 镜头队列已下载。",
    "status.hotspot.script": "剧本层会先整理场景、地点、动作和冲突。",
    "status.hotspot.shots": "分镜层会把故事拆成可交付给视频模型的镜头提示词。",
    "status.hotspot.model": "模型交付会把创作包整理成 Markdown 和 CSV 队列。",
  },
  en: {
    "nav.studio": "Studio",
    "nav.flow": "Flow",
    "nav.systems": "Systems",
    "nav.docs": "Docs",
    "hero.eyebrow": "AI video workflow",
    "hero.title": "Turn a script into directed video prompts.",
    "hero.subtitle": "Paste a script and generate storyboard prompts, character turnarounds, model queues, and a production handoff package.",
    "hero.start": "Start creating",
    "hero.system": "See the flow",
    "hotspot.script": "Script layer",
    "hotspot.shots": "Storyboard layer",
    "hotspot.model": "Model handoff",
    "hud.package": "Live package",
    "hud.characters": "Character lock",
    "hud.safety": "Safety",
    "hud.local": "Local only",
    "studio.eyebrow": "Creation console",
    "studio.title": "Generate the production pack in the browser",
    "studio.script": "Script",
    "control.model": "Model",
    "control.style": "Style",
    "control.aspect": "Aspect",
    "control.depth": "Shot depth",
    "control.limit": "Scene limit",
    "action.generate": "Generate package",
    "action.copy": "Copy prompt pack",
    "tab.shots": "Shots",
    "tab.characters": "Characters",
    "tab.package": "Package",
    "workflow.eyebrow": "Production map",
    "workflow.title": "From script to model handoff",
    "workflow.step1.title": "Script intelligence",
    "workflow.step1.body": "Detect scenes, time, locations, characters, and conflict, then turn loose text into a shot structure.",
    "workflow.step2.title": "Shot direction",
    "workflow.step2.body": "Create shot size, motion, intent, composition layers, and model-readable prompts.",
    "workflow.step3.title": "Character bible",
    "workflow.step3.body": "Output three-view prompts, wardrobe rules, and identity consistency constraints.",
    "workflow.step4.title": "Model queue",
    "workflow.step4.body": "Export Markdown packages and CSV queues for the next AI video tool.",
    "gallery.eyebrow": "Creative systems",
    "gallery.title": "One repository, two production systems",
    "gallery.poster.eyebrow": "Poster workflow",
    "gallery.poster.title": "Portrait to narrative poster",
    "gallery.poster.body": "Style presets / aspect ratio / model target / multi-version prompts",
    "gallery.video.eyebrow": "Video workflow",
    "gallery.video.title": "Script to AI storyboard",
    "gallery.video.body": "Shot queue / character turnarounds / CSV / model handoff",
    "gallery.qa.eyebrow": "Safety system",
    "gallery.qa.title": "Pre-generation risk checks",
    "gallery.qa.body": "Local generation / no upload / input cleanup / prompt completeness",
    "docs.eyebrow": "Open source ready",
    "docs.title": "Community-ready documentation",
    "docs.video": "Script detection, storyboards, character turnarounds",
    "docs.poster": "Character poster prompt production",
    "docs.quality": "Quality modes and model selection",
    "docs.ci": "Automated tests and safety checks",
    "status.ready": "Ready for a new production pass.",
    "status.empty": "Paste a script or scene outline before generating.",
    "status.secret": "Sensitive token-like text detected. Remove secrets before generating.",
    "status.generated": "Generated {shots} shots and {characters} character references.",
    "status.copied": "Prompt package copied.",
    "status.copyFailed": "Copy failed. Use the Package tab text.",
    "status.md": "Markdown package downloaded.",
    "status.csv": "CSV shot queue downloaded.",
    "status.hotspot.script": "The script layer organizes scenes, locations, action, and conflict first.",
    "status.hotspot.shots": "The storyboard layer turns story beats into video-model-ready prompts.",
    "status.hotspot.model": "The handoff layer formats the package as Markdown and CSV queues.",
  },
  ja: {
    "nav.studio": "制作台",
    "nav.flow": "流れ",
    "nav.systems": "システム",
    "nav.docs": "資料",
    "hero.eyebrow": "AI 動画制作ワークフロー",
    "hero.title": "脚本を演出可能な映像案へ。",
    "hero.subtitle": "脚本を入力すると、絵コンテプロンプト、人物三面図、モデル用キュー、制作パッケージを生成します。",
    "hero.start": "制作を始める",
    "hero.system": "流れを見る",
    "hotspot.script": "脚本層",
    "hotspot.shots": "絵コンテ層",
    "hotspot.model": "モデル納品",
    "hud.package": "ライブパッケージ",
    "hud.characters": "人物固定",
    "hud.safety": "安全",
    "hud.local": "ローカル生成",
    "studio.eyebrow": "制作コンソール",
    "studio.title": "ブラウザで制作パッケージを生成",
    "studio.script": "脚本",
    "control.model": "モデル",
    "control.style": "スタイル",
    "control.aspect": "比率",
    "control.depth": "ショット密度",
    "control.limit": "場面上限",
    "action.generate": "生成する",
    "action.copy": "プロンプトをコピー",
    "tab.shots": "ショット",
    "tab.characters": "人物",
    "tab.package": "パッケージ",
    "workflow.eyebrow": "制作マップ",
    "workflow.title": "脚本からモデル納品まで",
    "workflow.step1.title": "脚本解析",
    "workflow.step1.body": "場面、時間、場所、人物、対立を読み取り、テキストをショット構造に整理します。",
    "workflow.step2.title": "ショット演出",
    "workflow.step2.body": "画角、動き、意図、構図レイヤー、モデルが読みやすいプロンプトを生成します。",
    "workflow.step3.title": "人物設定",
    "workflow.step3.body": "三面図プロンプト、衣装ルール、同一性維持の条件を出力します。",
    "workflow.step4.title": "モデルキュー",
    "workflow.step4.body": "Markdown パッケージと CSV キューにまとめ、次の動画生成ツールへ渡します。",
    "gallery.eyebrow": "制作システム",
    "gallery.title": "ひとつのリポジトリ、ふたつの制作系統",
    "gallery.poster.eyebrow": "ポスターワークフロー",
    "gallery.poster.title": "ポートレートから物語ポスターへ",
    "gallery.poster.body": "スタイル / 比率 / モデル指定 / 複数案プロンプト",
    "gallery.video.eyebrow": "動画ワークフロー",
    "gallery.video.title": "脚本から AI 絵コンテへ",
    "gallery.video.body": "ショットキュー / 人物三面図 / CSV / モデル納品",
    "gallery.qa.eyebrow": "安全システム",
    "gallery.qa.title": "生成前リスクチェック",
    "gallery.qa.body": "ローカル生成 / アップロードなし / 入力整理 / 完整性チェック",
    "docs.eyebrow": "オープンソース対応",
    "docs.title": "コミュニティ向け資料入口",
    "docs.video": "脚本解析、絵コンテ、人物三面図",
    "docs.poster": "人物ポスタープロンプト制作",
    "docs.quality": "品質モードとモデル選択",
    "docs.ci": "自動テストと安全チェック",
    "status.ready": "新しい制作を開始できます。",
    "status.empty": "先に脚本または場面メモを入力してください。",
    "status.secret": "キーのような文字列を検出しました。削除してから生成してください。",
    "status.generated": "{shots} ショットと {characters} 人物参照を生成しました。",
    "status.copied": "プロンプトパッケージをコピーしました。",
    "status.copyFailed": "コピーに失敗しました。パッケージ欄の文字を使用してください。",
    "status.md": "Markdown パッケージをダウンロードしました。",
    "status.csv": "CSV ショットキューをダウンロードしました。",
    "status.hotspot.script": "脚本層では場面、場所、動き、対立を先に整理します。",
    "status.hotspot.shots": "絵コンテ層では物語を動画モデル向けのショットに分解します。",
    "status.hotspot.model": "納品層では Markdown と CSV キューとして整理します。",
  },
};

const languageMeta = {
  zh: { html: "zh-CN", title: "Rufo AI 视频工作流工作室" },
  en: { html: "en", title: "Rufo AI Workflow Studio" },
  ja: { html: "ja", title: "Rufo AI ワークフロースタジオ" },
};

let activeLanguage = "en";

function translate(key) {
  return translations[activeLanguage]?.[key] || translations.zh[key] || key;
}

function formatMessage(key, values = {}) {
  return translate(key).replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ""));
}

const pointer = {
  x: window.innerWidth * 0.5,
  y: window.innerHeight * 0.5,
  tx: window.innerWidth * 0.5,
  ty: window.innerHeight * 0.5,
  nx: 0,
  ny: 0,
  down: false,
  label: "Studio",
  frame: 0,
};

const state = {
  packageText: "",
  csvText: "",
  shots: [],
  characters: [],
};

const styleProfiles = {
  cinematic: {
    label: "cinematic",
    lighting: "motivated cinematic lighting, atmospheric contrast, rich foreground depth",
    color: "muted teal highlights, warm practical glow, restrained film grain",
    camera: ["slow dolly in", "orbit reveal", "low-angle tracking", "crane pullback"],
  },
  documentary: {
    label: "documentary",
    lighting: "natural available light, practical realism, controlled handheld texture",
    color: "true-to-life palette, soft contrast, location-authentic details",
    camera: ["observational handheld", "patient locked frame", "gentle push in", "over-shoulder follow"],
  },
  commercial: {
    label: "commercial",
    lighting: "clean premium lighting, glossy edge highlights, high product clarity",
    color: "polished neutral base, precise accent color, sharp detail separation",
    camera: ["hero push in", "smooth slider pass", "macro detail reveal", "vertical reveal"],
  },
  anime: {
    label: "anime",
    lighting: "stylized rim light, graphic shadow shapes, expressive atmosphere",
    color: "clear color blocking, luminous highlights, painterly background depth",
    camera: ["dramatic parallax pan", "fast emotional close-up", "floating crane move", "impact cut-in"],
  },
  fantasy: {
    label: "fantasy",
    lighting: "mythic volumetric light, glowing particles, magical atmosphere",
    color: "deep jewel tones, silver highlights, warm amber accents",
    camera: ["enchanted orbit", "floating dolly", "wide reveal", "slow vertical ascent"],
  },
  noir: {
    label: "noir",
    lighting: "hard side light, negative fill, blade-like shadows",
    color: "monochrome base, cold steel highlights, restrained amber practicals",
    camera: ["shadow tracking", "slow cigarette-smoke push", "locked suspense frame", "Dutch-angle reveal"],
  },
};

const lenses = ["24mm wide", "35mm story lens", "50mm natural perspective", "85mm emotional close-up"];
const shotTypes = ["establishing", "medium", "close-up", "insert", "over-shoulder", "wide reveal"];
const secretPattern = /(sk-[a-z0-9_-]{12,}|sk-proj-[a-z0-9_-]{12,}|api[_-]?key|token|password|secret)/i;

function sanitizeText(value, limit = 5000) {
  return String(value || "")
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, "")
    .slice(0, limit)
    .trim();
}

function splitSentences(text) {
  return text
    .split(/[\n。！？!?]+/)
    .map((line) => sanitizeText(line, 260))
    .filter(Boolean);
}

function parseScenes(text, limit) {
  const cleaned = sanitizeText(text);
  const blocks = cleaned
    .split(/\n(?=(?:第\s*\d+\s*场|场景\s*\d+|scene\s*\d+|int\.|ext\.))/i)
    .map((part) => sanitizeText(part, 900))
    .filter(Boolean);
  const source = blocks.length > 1 ? blocks : splitSentences(cleaned).map((line, index) => `Scene ${index + 1}: ${line}`);
  return source.slice(0, limit).map((block, index) => {
    const lines = splitSentences(block);
    const heading = lines[0] || `Scene ${index + 1}`;
    const action = lines.slice(1).join("。") || heading;
    const time = /夜|night/i.test(block) ? "night" : /日|day|白天/i.test(block) ? "day" : "story time";
    const location = heading.replace(/^第\s*\d+\s*场[:：]?\s*/i, "").slice(0, 36) || "story space";
    return { index, heading, action, time, location };
  });
}

function extractCharacters(text) {
  const names = new Set();
  const speakerMatches = sanitizeText(text).matchAll(/([\u4e00-\u9fa5A-Za-z]{2,16})\s*[：:]/g);
  for (const match of speakerMatches) {
    if (!/第\s*\d+\s*场|场景|内景|外景|scene|int|ext/i.test(match[1])) names.add(match[1]);
  }
  const actionNameMatches = sanitizeText(text).matchAll(/([\u4e00-\u9fa5]{2,4})(?=推开|站在|听见|看见|抬头|走向|回头|拿起|打开|说|望向|进入|离开)/g);
  for (const match of actionNameMatches) names.add(match[1]);
  const commonNames = sanitizeText(text).match(/[\u4e00-\u9fa5]{2,4}/g) || [];
  for (const name of commonNames) {
    if (names.size >= 4) break;
    if (!/第|内景|外景|夜晚|白天|舞台|剧院|镜头|观众|墙面|声音|提示|模型|最后|一行|座位|聚光|沉重/.test(name)) names.add(name);
  }
  if (!names.size) names.add("主角");
  return Array.from(names).slice(0, 4).map((name, index) => ({
    name,
    role: index === 0 ? "primary character" : "supporting presence",
    front: `${name}, front view, consistent face shape, wardrobe locked, neutral full-body reference`,
    side: `${name}, side view, same costume, profile silhouette, clear hair and body proportions`,
    back: `${name}, back view, same materials, recognizable posture, production turnaround sheet`,
  }));
}

function buildShots(scenes, config) {
  const profile = styleProfiles[config.style] || styleProfiles.cinematic;
  const perScene = config.depth === "high" ? 3 : config.depth === "fast" ? 1 : 2;
  const shots = [];
  scenes.forEach((scene) => {
    for (let local = 0; local < perScene; local += 1) {
      const shotIndex = shots.length;
      const camera = profile.camera[shotIndex % profile.camera.length];
      const shotType = shotTypes[shotIndex % shotTypes.length];
      const lens = lenses[shotIndex % lenses.length];
      const action = splitSentences(scene.action)[local] || scene.action || scene.heading;
      shots.push({
        number: shotIndex + 1,
        title: `${scene.location} / ${shotType}`,
        scene: scene.heading,
        prompt: [
          `${config.model} ${profile.label} video prompt.`,
          `Aspect ratio ${config.aspect}.`,
          `${action}.`,
          `Camera: ${camera}, ${lens}, ${shotType} composition.`,
          `Lighting: ${profile.lighting}.`,
          `Color: ${profile.color}.`,
          "Keep character identity consistent, preserve spatial continuity, avoid text artifacts and extra limbs.",
        ].join(" "),
        meta: [config.model, profile.label, config.aspect, camera, lens],
      });
    }
  });
  return shots.slice(0, 18);
}

function buildPackage({ text, scenes, characters, shots, config }) {
  const characterBlock = characters
    .map((item) => [`### ${item.name}`, `- Front: ${item.front}`, `- Side: ${item.side}`, `- Back: ${item.back}`].join("\n"))
    .join("\n\n");
  const shotBlock = shots
    .map((shot) => [`### Shot ${String(shot.number).padStart(2, "0")} - ${shot.title}`, shot.prompt].join("\n"))
    .join("\n\n");
  const negative = [
    "low quality",
    "warped anatomy",
    "extra fingers",
    "identity drift",
    "unreadable text",
    "random logo",
    "flickering face",
    "inconsistent costume",
  ].join(", ");
  return [
    "# Rufo AI Video Prompt Package",
    "",
    `- Target model: ${config.model}`,
    `- Creative style: ${config.style}`,
    `- Aspect ratio: ${config.aspect}`,
    `- Shot depth: ${config.depth}`,
    `- Source length: ${text.length} characters`,
    "",
    "## Production Intent",
    "Create a coherent cinematic sequence with clear scene continuity, controlled camera language, and reusable character references.",
    "",
    "## Character Three-View Prompts",
    characterBlock,
    "",
    "## Storyboard Prompt Queue",
    shotBlock,
    "",
    "## Negative Prompt",
    negative,
  ].join("\n");
}

function buildCsv(shots) {
  const escapeCsv = (value) => `"${String(value).replaceAll('"', '""')}"`;
  const rows = [["shot", "scene", "title", "prompt", "meta"]];
  shots.forEach((shot) => {
    rows.push([shot.number, shot.scene, shot.title, shot.prompt, shot.meta.join(" | ")]);
  });
  return rows.map((row) => row.map(escapeCsv).join(",")).join("\n");
}

function setStatus(message, isWarning = false) {
  dom.statusLine.textContent = message;
  dom.statusLine.toggleAttribute("data-warning", isWarning);
}

function makeEl(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function renderShots(shots) {
  const fragment = document.createDocumentFragment();
  shots.forEach((shot, index) => {
    const card = makeEl("article", "shot-card");
    card.style.animationDelay = `${index * 55}ms`;
    card.append(makeEl("div", "shot-number", String(shot.number).padStart(2, "0")));
    const body = makeEl("div");
    body.append(makeEl("h3", "", shot.title));
    body.append(makeEl("p", "", shot.prompt));
    const meta = makeEl("div", "shot-meta");
    shot.meta.forEach((item) => meta.append(makeEl("span", "", item)));
    body.append(meta);
    card.append(body);
    fragment.append(card);
  });
  dom.shotStack.replaceChildren(fragment);
}

function renderCharacters(characters) {
  const fragment = document.createDocumentFragment();
  characters.forEach((item) => {
    const card = makeEl("article", "character-card");
    card.append(makeEl("h3", "", item.name));
    const roleText = activeLanguage === "zh" ? (item.role === "primary character" ? "主角" : "辅助角色") : activeLanguage === "ja" ? (item.role === "primary character" ? "主要人物" : "補助人物") : item.role;
    card.append(makeEl("p", "", `${roleText}. ${item.front}`));
    const meta = makeEl("div", "shot-meta");
    meta.append(makeEl("span", "", "front"));
    meta.append(makeEl("span", "", "side"));
    meta.append(makeEl("span", "", "back"));
    card.append(meta);
    fragment.append(card);
  });
  dom.characterGrid.replaceChildren(fragment);
}

function getConfig() {
  return {
    model: dom.modelTarget.value,
    style: dom.stylePreset.value,
    aspect: dom.aspectRatio.value,
    depth: dom.shotDepth.value,
    limit: Number(dom.sceneLimit.value),
  };
}

function generatePackage() {
  const text = sanitizeText(dom.scriptInput.value);
  const config = getConfig();
  if (!text) {
    setStatus(translate("status.empty"), true);
    return;
  }
  if (secretPattern.test(text)) {
    setStatus(translate("status.secret"), true);
    return;
  }

  const scenes = parseScenes(text, config.limit);
  const characters = extractCharacters(text);
  const shots = buildShots(scenes, config);
  const packageText = buildPackage({ text, scenes, characters, shots, config });
  const csvText = buildCsv(shots);

  state.shots = shots;
  state.characters = characters;
  state.packageText = packageText;
  state.csvText = csvText;

  const shotCount = activeLanguage === "zh" ? `${shots.length} 个镜头` : activeLanguage === "ja" ? `${shots.length} ショット` : `${shots.length} shots`;
  const characterCount = activeLanguage === "zh" ? `${characters.length} 个角色` : activeLanguage === "ja" ? `${characters.length} 人物` : `${characters.length} profiles`;
  dom.outputModel.textContent = activeLanguage === "zh" ? `${config.model} 交付` : activeLanguage === "ja" ? `${config.model} 納品` : `${config.model} handoff`;
  dom.outputCount.textContent = shotCount;
  dom.hudShots.textContent = shotCount;
  dom.hudCharacters.textContent = characterCount;
  dom.packageOutput.textContent = packageText;
  renderShots(shots);
  renderCharacters(characters);
  setStatus(formatMessage("status.generated", { shots: shots.length, characters: characters.length }));
}

async function copyText(text) {
  if (!text) return false;
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const helper = document.createElement("textarea");
    helper.value = text;
    helper.setAttribute("readonly", "");
    helper.style.position = "fixed";
    helper.style.opacity = "0";
    document.body.append(helper);
    helper.select();
    const ok = document.execCommand("copy");
    helper.remove();
    return ok;
  }
}

function downloadText(filename, text, type) {
  if (!text) return;
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function updateInputMeter() {
  const count = sanitizeText(dom.scriptInput.value).length;
  dom.inputMeter.textContent = `${count} / 5000`;
}

function setupTabs() {
  $$(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      const panel = button.dataset.panel;
      $$(".tab-button").forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });
      $$(".output-panel").forEach((item) => item.classList.toggle("active", item.id === `panel-${panel}`));
    });
  });
}

function setupForm() {
  dom.form.addEventListener("submit", (event) => {
    event.preventDefault();
    generatePackage();
  });
  [dom.modelTarget, dom.stylePreset, dom.aspectRatio, dom.shotDepth, dom.sceneLimit].forEach((control) => {
    control.addEventListener("change", generatePackage);
    control.addEventListener("input", () => {
      dom.sceneLimitOutput.textContent = dom.sceneLimit.value;
    });
  });
  dom.scriptInput.addEventListener("input", updateInputMeter);
  dom.copyPackage.addEventListener("click", async () => {
    const ok = await copyText(state.packageText);
    setStatus(ok ? translate("status.copied") : translate("status.copyFailed"), !ok);
  });
  dom.downloadMd.addEventListener("click", () => {
    downloadText("rufo-video-prompt-package.md", state.packageText, "text/markdown;charset=utf-8");
    setStatus(translate("status.md"));
  });
  dom.downloadCsv.addEventListener("click", () => {
    downloadText("rufo-shot-prompt-queue.csv", state.csvText, "text/csv;charset=utf-8");
    setStatus(translate("status.csv"));
  });
}

function applyLanguage(lang, options = {}) {
  const nextLang = translations[lang] ? lang : "zh";
  activeLanguage = nextLang;
  document.documentElement.lang = languageMeta[nextLang].html;
  document.title = languageMeta[nextLang].title;
  $$("[data-i18n]").forEach((element) => {
    element.textContent = translate(element.dataset.i18n);
  });
  dom.languageButtons.forEach((button) => {
    const active = button.dataset.lang === nextLang;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  if (!options.skipGenerate) generatePackage();
}

function setupLanguage() {
  dom.languageButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.classList.contains("active")));
    button.addEventListener("click", () => applyLanguage(button.dataset.lang));
  });
  applyLanguage(activeLanguage, { skipGenerate: true });
  setStatus(translate("status.ready"));
}

function setupHeroObject() {
  dom.hotspotButtons.forEach((button) => {
    button.addEventListener("click", () => {
      dom.hotspotButtons.forEach((item) => item.classList.toggle("active", item === button));
      setStatus(translate(`status.hotspot.${button.dataset.hotspot}`));
    });
  });
}

function setupCursor() {
  const interactive = "a, button, input, select, textarea, label";
  const updateObjectInteraction = () => {
    pointer.frame = 0;
    if (!dom.heroObjectStage) return;
    const rect = dom.heroObjectStage.getBoundingClientRect();
    const localX = ((pointer.tx - rect.left) / Math.max(rect.width, 1)) * 100;
    const localY = ((pointer.ty - rect.top) / Math.max(rect.height, 1)) * 100;
    const inside = localX >= 0 && localX <= 100 && localY >= 0 && localY <= 100;
    dom.hero?.style.setProperty("--mx", `${pointer.tx}px`);
    dom.hero?.style.setProperty("--my", `${pointer.ty}px`);
    dom.heroObjectStage.style.setProperty("--reveal-x", `${Math.max(0, Math.min(100, localX))}%`);
    dom.heroObjectStage.style.setProperty("--reveal-y", `${Math.max(0, Math.min(100, localY))}%`);
    dom.heroObjectStage.style.setProperty("--tilt-x", `${pointer.ny * -2.2}deg`);
    dom.heroObjectStage.style.setProperty("--tilt-y", `${pointer.nx * 3.2}deg`);
    dom.heroObjectStage.classList.toggle("is-active", inside);
  };
  window.addEventListener("pointermove", (event) => {
    pointer.tx = event.clientX;
    pointer.ty = event.clientY;
    pointer.nx = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.ny = (event.clientY / window.innerHeight) * 2 - 1;
    if (!pointer.frame) pointer.frame = requestAnimationFrame(updateObjectInteraction);
    const target = event.target.closest(interactive);
    dom.cursor.classList.toggle("is-action", Boolean(target));
    dom.cursor.classList.toggle("is-typing", Boolean(event.target.closest("textarea, input, select")));
    dom.cursorLabel.textContent = target?.dataset.cursor || target?.textContent?.trim()?.slice(0, 12) || "Studio";
  });
  window.addEventListener("pointerdown", () => {
    pointer.down = true;
    dom.cursor.classList.add("is-down");
    dom.heroObjectStage?.classList.add("is-dragging");
  });
  window.addEventListener("pointerup", () => {
    pointer.down = false;
    dom.cursor.classList.remove("is-down");
    dom.heroObjectStage?.classList.remove("is-dragging");
  });

  function animateCursor() {
    pointer.x += (pointer.tx - pointer.x) * 0.18;
    pointer.y += (pointer.ty - pointer.y) * 0.18;
    dom.cursor.style.transform = `translate3d(${pointer.x - 56}px, ${pointer.y - 56}px, 0)`;
    requestAnimationFrame(animateCursor);
  }
  animateCursor();
}

function setupScrollAnimation() {
  const panels = $$(".page-panel");
  const blocks = $$(".reveal-block");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        entry.target.classList.toggle("is-visible", entry.isIntersecting);
      });
    },
    { threshold: 0.18 },
  );
  panels.forEach((panel) => observer.observe(panel));
  blocks.forEach((block) => observer.observe(block));

  const updateScroll = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const progress = max > 0 ? window.scrollY / max : 0;
    dom.scrollMeter.style.transform = `scaleX(${Math.max(0, Math.min(1, progress))})`;
  };
  window.addEventListener("scroll", updateScroll, { passive: true });
  updateScroll();
}

function setupCanvas() {
  const canvas = dom.canvas;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let width = 0;
  let height = 0;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const nodes = Array.from({ length: 58 }, (_, index) => ({
    lane: index % 9,
    phase: index / 58,
    speed: 0.000055 + (index % 7) * 0.00001,
    radius: 1.2 + (index % 5) * 0.32,
  }));

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function flowPoint(progress, lane = 0, time = 0) {
    const t = Math.max(0, Math.min(1, progress));
    const x = width * (-0.08 + t * 1.17) + pointer.nx * (28 - t * 34);
    const baseY = height * (0.78 - t * 0.43);
    const wave = Math.sin(t * Math.PI * 4.2 + lane * 0.68 + time * 0.0008) * height * 0.028;
    const laneOffset = (lane - 4) * height * 0.012;
    return { x, y: baseY + wave + laneOffset + pointer.ny * 18 };
  }

  function drawFlowLine(lane, time) {
    ctx.beginPath();
    for (let i = 0; i <= 80; i += 1) {
      const point = flowPoint(i / 80, lane, time);
      if (i === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    }
    const alpha = lane % 3 === 0 ? 0.34 : 0.18;
    ctx.strokeStyle = `rgba(0, 198, 230, ${alpha})`;
    ctx.lineWidth = lane % 3 === 0 ? 1.15 : 0.7;
    ctx.stroke();
  }

  function draw(time) {
    ctx.clearRect(0, 0, width, height);
    ctx.globalCompositeOperation = "screen";
    ctx.save();
    ctx.shadowColor = "rgba(0, 216, 255, 0.78)";
    ctx.shadowBlur = 14;
    for (let lane = 0; lane < 9; lane += 1) {
      drawFlowLine(lane, time);
    }

    nodes.forEach((node, index) => {
      const progress = (node.phase + time * node.speed) % 1;
      const point = flowPoint(progress, node.lane, time);
      const pulse = 0.55 + Math.sin(time * 0.004 + index) * 0.32;
      const radius = node.radius + pulse;
      const halo = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, radius * 8);
      halo.addColorStop(0, "rgba(0, 225, 255, 0.76)");
      halo.addColorStop(0.28, "rgba(0, 194, 226, 0.26)");
      halo.addColorStop(1, "rgba(0, 194, 226, 0)");
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(point.x, point.y, radius * 8, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = index % 4 === 0 ? "rgba(255,255,255,0.92)" : "rgba(0,230,255,0.92)";
      ctx.beginPath();
      ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();

    const glow = ctx.createRadialGradient(pointer.tx, pointer.ty, 0, pointer.tx, pointer.ty, pointer.down ? 320 : 240);
    glow.addColorStop(0, pointer.down ? "rgba(0, 220, 255, 0.42)" : "rgba(0, 205, 230, 0.24)");
    glow.addColorStop(1, "rgba(0, 205, 230, 0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, width, height);
    ctx.globalCompositeOperation = "source-over";

    if (!reducedMotion) requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  resize();
  requestAnimationFrame(draw);
}

setupCursor();
setupLanguage();
setupHeroObject();
setupTabs();
setupForm();
setupScrollAnimation();
setupCanvas();
updateInputMeter();
dom.sceneLimitOutput.textContent = dom.sceneLimit.value;
generatePackage();
