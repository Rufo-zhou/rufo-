# Rufo AI Workflow Studio Website

This static website presents the project as an interactive AI creative workflow studio.
It includes a local-only prompt workbench that can generate storyboard prompts, character three-view prompts, a Markdown handoff package, and a CSV shot queue directly in the browser.

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
- `app.js` - Canvas motion system, custom cursor, scroll reveals, and local prompt generation

The page is designed to work as a static GitHub Pages site. It does not send script input to a server and avoids external JavaScript dependencies.
