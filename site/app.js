const pointer = {
  x: 0,
  y: 0,
  tx: 0,
  ty: 0,
};

const probe = document.querySelector("#probe");
const hero = document.querySelector("#hero");
const fallbackCanvas = document.querySelector("#fallback-canvas");
const fallbackCtx = fallbackCanvas.getContext("2d");
const shotStack = document.querySelector("#shot-stack");
const outputModel = document.querySelector("#output-model");
const outputCount = document.querySelector("#output-count");
const form = document.querySelector("#script-form");
const scriptInput = document.querySelector("#script-input");
const qualityToggle = document.querySelector("#quality-toggle");
let activeModel = "Sora";

function updatePointer(event) {
  pointer.tx = (event.clientX / window.innerWidth) * 2 - 1;
  pointer.ty = -((event.clientY / window.innerHeight) * 2 - 1);
  if (probe) {
    probe.style.left = `${event.clientX}px`;
    probe.style.top = `${event.clientY}px`;
  }
}

window.addEventListener("pointermove", updatePointer);
window.addEventListener("pointerleave", () => {
  if (probe) probe.style.opacity = "0.28";
});
window.addEventListener("pointerenter", () => {
  if (probe) probe.style.opacity = "0.86";
});

function resizeFallbackCanvas() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  fallbackCanvas.width = Math.floor(window.innerWidth * dpr);
  fallbackCanvas.height = Math.floor(window.innerHeight * dpr);
  fallbackCanvas.style.width = `${window.innerWidth}px`;
  fallbackCanvas.style.height = `${window.innerHeight}px`;
  fallbackCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function drawFallback(time = 0) {
  const width = window.innerWidth;
  const height = Math.max(window.innerHeight, hero?.offsetHeight || window.innerHeight);
  fallbackCtx.clearRect(0, 0, width, height);
  fallbackCtx.fillStyle = "#121412";
  fallbackCtx.fillRect(0, 0, width, height);

  const horizon = height * 0.58;
  fallbackCtx.save();
  fallbackCtx.translate(width * 0.5, horizon);
  fallbackCtx.rotate(-0.1 + pointer.x * 0.04);
  for (let i = 0; i < 24; i += 1) {
    const y = Math.sin(i * 0.7 + time * 0.001) * 18 + i * 7;
    fallbackCtx.strokeStyle = i % 3 === 0 ? "rgba(124,199,194,0.45)" : "rgba(243,240,232,0.2)";
    fallbackCtx.lineWidth = i % 3 === 0 ? 2 : 1;
    fallbackCtx.beginPath();
    fallbackCtx.moveTo(-width * 0.75, y);
    fallbackCtx.bezierCurveTo(-width * 0.18, y - 150, width * 0.2, y + 130, width * 0.76, y - 80);
    fallbackCtx.stroke();
  }
  fallbackCtx.restore();

  for (let i = 0; i < 80; i += 1) {
    const x = (i * 157 + time * 0.018) % width;
    const y = (i * 67 + Math.sin(time * 0.001 + i) * 18) % height;
    fallbackCtx.fillStyle = i % 4 === 0 ? "rgba(214,185,109,0.5)" : "rgba(243,240,232,0.2)";
    fallbackCtx.fillRect(x, y, i % 4 === 0 ? 2 : 1, i % 4 === 0 ? 12 : 5);
  }

  requestAnimationFrame(drawFallback);
}

function createShotCards() {
  const text = scriptInput.value.trim() || "镜头从一段未命名剧本开始。";
  const lines = text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 4);
  const quality = qualityToggle.checked ? "high detail" : "fast draft";
  const fallbackLines = [
    "主角进入一个尚未命名的空间，环境用光先建立情绪。",
    "镜头靠近关键物件，揭示故事中的冲突线索。",
    "角色做出选择，画面进入可生成的高潮镜头。",
  ];
  const source = lines.length ? lines : fallbackLines;
  const shots = source.map((line, index) => {
    const motion = ["slow dolly in", "orbit reveal", "handheld close pass", "crane pullback"][index % 4];
    const lens = ["35mm", "50mm", "85mm", "anamorphic wide"][index % 4];
    return {
      title: index === 0 ? "Opening atmosphere" : index === source.length - 1 ? "Emotional turn" : "Story reveal",
      prompt: `${activeModel} ${quality}: ${line} Use cinematic lighting, controlled subject continuity, layered foreground depth, ${motion}, ${lens}, coherent action across the shot.`,
      meta: [activeModel, quality, motion, lens],
    };
  });

  outputModel.textContent = `${activeModel} handoff`;
  outputCount.textContent = `${shots.length} shots`;
  shotStack.innerHTML = shots
    .map(
      (shot, index) => `
        <article class="shot-card" style="animation-delay: ${index * 90}ms">
          <div class="shot-number">${String(index + 1).padStart(2, "0")}</div>
          <div>
            <h3>${shot.title}</h3>
            <p>${shot.prompt}</p>
            <div class="shot-meta">
              ${shot.meta.map((item) => `<span>${item}</span>`).join("")}
            </div>
          </div>
        </article>
      `,
    )
    .join("");
}

document.querySelectorAll("[data-model]").forEach((button) => {
  button.addEventListener("click", () => {
    activeModel = button.dataset.model || "Sora";
    document.querySelectorAll("[data-model]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    createShotCards();
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  createShotCards();
});

qualityToggle.addEventListener("change", createShotCards);

function revealSections() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        entry.target.toggleAttribute("data-visible", entry.isIntersecting);
      });
    },
    { threshold: 0.2 },
  );
  document.querySelectorAll(".band").forEach((section) => observer.observe(section));
}

async function startThreeScene() {
  const canvas = document.querySelector("#studio-canvas");
  try {
    const THREE = await import("https://esm.sh/three@0.164.1");
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x11110f, 0.035);

    const camera = new THREE.PerspectiveCamera(44, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 2.2, 9.8);

    const ambient = new THREE.AmbientLight(0xf3f0e8, 1.5);
    const key = new THREE.DirectionalLight(0x7cc7c2, 2.2);
    key.position.set(2, 6, 4);
    const warm = new THREE.PointLight(0xd6b96d, 2.5, 18);
    warm.position.set(-5, -1, 4);
    scene.add(ambient, key, warm);

    const curveGroup = new THREE.Group();
    const materialA = new THREE.MeshStandardMaterial({
      color: 0x4d5c45,
      roughness: 0.78,
      metalness: 0.08,
    });
    const materialB = new THREE.MeshStandardMaterial({
      color: 0xc8d4cf,
      roughness: 0.46,
      metalness: 0.18,
      emissive: 0x102c2a,
      emissiveIntensity: 0.16,
    });

    for (let i = 0; i < 7; i += 1) {
      const points = [];
      for (let j = 0; j < 9; j += 1) {
        points.push(
          new THREE.Vector3(
            -7 + j * 1.75,
            Math.sin(j * 0.9 + i) * 0.5 - i * 0.18,
            Math.cos(j * 0.7 + i) * 0.7 - i * 0.42,
          ),
        );
      }
      const curve = new THREE.CatmullRomCurve3(points);
      const tube = new THREE.TubeGeometry(curve, 80, 0.045 + i * 0.012, 12, false);
      const mesh = new THREE.Mesh(tube, i % 2 ? materialA : materialB);
      mesh.rotation.z = -0.18 + i * 0.035;
      mesh.position.y = -1.6 + i * 0.18;
      curveGroup.add(mesh);
    }
    scene.add(curveGroup);

    const panelGroup = new THREE.Group();
    const panelMaterial = new THREE.MeshStandardMaterial({
      color: 0xf3f0e8,
      roughness: 0.62,
      transparent: true,
      opacity: 0.38,
      side: THREE.DoubleSide,
    });
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0xf3f0e8, transparent: true, opacity: 0.55 });
    for (let i = 0; i < 9; i += 1) {
      const geo = new THREE.PlaneGeometry(1.55, 0.9);
      const panel = new THREE.Mesh(geo, panelMaterial.clone());
      panel.position.set(-5.3 + i * 1.35, 0.85 + Math.sin(i) * 0.3, -1.2 - i * 0.12);
      panel.rotation.set(-0.16, -0.34 + i * 0.06, 0.07);
      panel.userData.seed = i;
      panelGroup.add(panel);

      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), edgeMaterial);
      edges.position.copy(panel.position);
      edges.rotation.copy(panel.rotation);
      panelGroup.add(edges);
    }
    scene.add(panelGroup);

    const particleGeometry = new THREE.BufferGeometry();
    const particleCount = 420;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i += 1) {
      positions[i * 3] = (Math.random() - 0.5) * 14;
      positions[i * 3 + 1] = Math.random() * 6 - 0.3;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particles = new THREE.Points(
      particleGeometry,
      new THREE.PointsMaterial({
        color: 0xd6b96d,
        size: 0.028,
        transparent: true,
        opacity: 0.8,
      }),
    );
    scene.add(particles);

    function handleResize() {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", handleResize);
    handleResize();

    function animate(time) {
      pointer.x += (pointer.tx - pointer.x) * 0.06;
      pointer.y += (pointer.ty - pointer.y) * 0.06;
      curveGroup.rotation.y = pointer.x * 0.11;
      curveGroup.rotation.x = -0.08 + pointer.y * 0.05;
      curveGroup.position.x = pointer.x * 0.24;
      panelGroup.rotation.y = pointer.x * 0.08;
      panelGroup.children.forEach((child) => {
        if (child.isMesh) {
          child.material.opacity = 0.24 + Math.sin(time * 0.001 + child.userData.seed) * 0.08 + Math.abs(pointer.x) * 0.1;
        }
      });
      particles.rotation.y = time * 0.00008;
      particles.position.x = pointer.x * 0.55;
      camera.position.x += (pointer.x * 0.9 - camera.position.x) * 0.03;
      camera.position.y += (2.2 + pointer.y * 0.45 - camera.position.y) * 0.03;
      camera.lookAt(0, -0.25, 0);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  } catch (error) {
    canvas.style.display = "none";
    console.info("Three scene fallback active", error);
  }
}

resizeFallbackCanvas();
drawFallback();
createShotCards();
revealSections();
startThreeScene();
window.addEventListener("resize", resizeFallbackCanvas);
