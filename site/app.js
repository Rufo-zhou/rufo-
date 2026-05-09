const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const dom = {
  canvas: $("#studio-canvas"),
  cursor: $("#cursor-orbit"),
  cursorLabel: $("#cursor-label"),
  scrollMeter: $("#scroll-meter"),
  hero: $("#hero"),
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

const pointer = {
  x: window.innerWidth * 0.5,
  y: window.innerHeight * 0.5,
  tx: window.innerWidth * 0.5,
  ty: window.innerHeight * 0.5,
  nx: 0,
  ny: 0,
  down: false,
  label: "Studio",
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
    .split(/(?=(?:第\s*\d+\s*场|场景\s*\d+|scene\s*\d+|int\.|ext\.|内景|外景))/i)
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
  for (const match of speakerMatches) names.add(match[1]);
  const commonNames = sanitizeText(text).match(/[\u4e00-\u9fa5]{2,4}/g) || [];
  for (const name of commonNames) {
    if (names.size >= 4) break;
    if (!/第|内景|外景|夜晚|舞台|剧院|镜头|观众|墙面|声音|提示|模型/.test(name)) names.add(name);
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
    card.append(makeEl("p", "", `${item.role}. ${item.front}`));
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
    setStatus("Paste a script or scene outline before generating.", true);
    return;
  }
  if (secretPattern.test(text)) {
    setStatus("Sensitive token-like text detected. Remove secrets before generating.", true);
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

  dom.outputModel.textContent = `${config.model} handoff`;
  dom.outputCount.textContent = `${shots.length} shots`;
  dom.hudShots.textContent = `${shots.length} shots`;
  dom.hudCharacters.textContent = `${characters.length} profiles`;
  dom.packageOutput.textContent = packageText;
  renderShots(shots);
  renderCharacters(characters);
  setStatus(`Generated ${shots.length} shots and ${characters.length} character references.`);
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
      $$(".tab-button").forEach((item) => item.classList.toggle("active", item === button));
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
    setStatus(ok ? "Prompt package copied." : "Copy failed. Use the Package tab text.", !ok);
  });
  dom.downloadMd.addEventListener("click", () => {
    downloadText("rufo-video-prompt-package.md", state.packageText, "text/markdown;charset=utf-8");
    setStatus("Markdown package downloaded.");
  });
  dom.downloadCsv.addEventListener("click", () => {
    downloadText("rufo-shot-prompt-queue.csv", state.csvText, "text/csv;charset=utf-8");
    setStatus("CSV shot queue downloaded.");
  });
}

function setupCursor() {
  const interactive = "a, button, input, select, textarea, label";
  window.addEventListener("pointermove", (event) => {
    pointer.tx = event.clientX;
    pointer.ty = event.clientY;
    pointer.nx = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.ny = (event.clientY / window.innerHeight) * 2 - 1;
    dom.hero?.style.setProperty("--mx", `${event.clientX}px`);
    dom.hero?.style.setProperty("--my", `${event.clientY}px`);
    const target = event.target.closest(interactive);
    dom.cursor.classList.toggle("is-action", Boolean(target));
    dom.cursor.classList.toggle("is-typing", Boolean(event.target.closest("textarea, input, select")));
    dom.cursorLabel.textContent = target?.dataset.cursor || target?.textContent?.trim()?.slice(0, 12) || "Studio";
  });
  window.addEventListener("pointerdown", () => {
    pointer.down = true;
    dom.cursor.classList.add("is-down");
  });
  window.addEventListener("pointerup", () => {
    pointer.down = false;
    dom.cursor.classList.remove("is-down");
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
  const ctx = canvas.getContext("2d");
  let width = 0;
  let height = 0;
  const particles = Array.from({ length: 180 }, (_, index) => ({
    x: Math.random(),
    y: Math.random(),
    z: Math.random(),
    speed: 0.0003 + (index % 9) * 0.00004,
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

  function drawPanel(x, y, w, h, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = "rgba(244,241,232,0.34)";
    ctx.fillStyle = "rgba(244,241,232,0.055)";
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);
    ctx.restore();
  }

  function draw(time) {
    const t = time * 0.001;
    ctx.clearRect(0, 0, width, height);
    const gradient = ctx.createRadialGradient(width * 0.52, height * 0.38, 0, width * 0.52, height * 0.38, width * 0.8);
    gradient.addColorStop(0, "#202820");
    gradient.addColorStop(0.45, "#111411");
    gradient.addColorStop(1, "#090a09");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    particles.forEach((particle, index) => {
      particle.y += particle.speed;
      if (particle.y > 1.05) particle.y = -0.05;
      const x = particle.x * width + pointer.nx * 34 * particle.z;
      const y = particle.y * height + Math.sin(t + index) * 10;
      ctx.fillStyle = index % 6 === 0 ? "rgba(223,191,97,0.62)" : "rgba(244,241,232,0.22)";
      ctx.fillRect(x, y, index % 6 === 0 ? 2 : 1, index % 6 === 0 ? 12 : 5);
    });

    ctx.save();
    ctx.translate(width * 0.5 + pointer.nx * 56, height * 0.67 + pointer.ny * 26);
    ctx.rotate(-0.08 + pointer.nx * 0.04);
    for (let i = 0; i < 18; i += 1) {
      const y = -82 + i * 11 + Math.sin(t * 1.3 + i) * 7;
      ctx.strokeStyle = i % 3 === 0 ? "rgba(111,212,203,0.52)" : "rgba(244,241,232,0.16)";
      ctx.lineWidth = i % 3 === 0 ? 2 : 1;
      ctx.beginPath();
      ctx.moveTo(-width * 0.62, y);
      ctx.bezierCurveTo(-width * 0.2, y - 90, width * 0.12, y + 96, width * 0.68, y - 42);
      ctx.stroke();
    }
    ctx.restore();

    for (let i = 0; i < 9; i += 1) {
      const x = width * 0.28 + i * 82 + pointer.nx * (i - 4) * 7;
      const y = height * 0.27 + Math.sin(t + i) * 18 + pointer.ny * 16;
      drawPanel(x, y, 92, 58, 0.28 + i * 0.018);
    }

    const glow = ctx.createRadialGradient(pointer.tx, pointer.ty, 0, pointer.tx, pointer.ty, 220);
    glow.addColorStop(0, pointer.down ? "rgba(138,168,255,0.34)" : "rgba(111,212,203,0.22)");
    glow.addColorStop(1, "rgba(111,212,203,0)");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, width, height);

    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  resize();
  requestAnimationFrame(draw);
}

setupCursor();
setupTabs();
setupForm();
setupScrollAnimation();
setupCanvas();
updateInputMeter();
dom.sceneLimitOutput.textContent = dom.sceneLimit.value;
generatePackage();
