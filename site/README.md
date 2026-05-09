# Rufo AI Workflow Studio Website

This static website presents the project as an interactive AI creative workflow studio.

## Local Preview

From the repository root:

```bash
python3 -m http.server 4173 --directory site
```

Then open:

```text
http://localhost:4173
```

## Files

- `index.html` - page structure and content
- `styles.css` - responsive visual design
- `app.js` - Three.js hero scene, fallback canvas, and demo interaction

The page is designed to work as a static GitHub Pages site. The Three.js scene loads from a public ESM CDN and falls back to a native canvas animation if the module cannot be loaded.
