# sudoself.dev

Source for [www.sudoself.dev](https://www.sudoself.dev). It is a static site: a small Python script turns the settings in `site.toml` and the Markdown files in `content/logs/` into the HTML that GitHub Pages serves.

The previous version of the site is kept on the `archive/v1` branch.

## Build

Set up once. The site's two Python libraries go into a private `.venv` folder, because recent Ubuntu and Debian versions do not allow `pip` to install into the system Python:

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

If the first command says `venv` is missing, run `sudo apt install python3-venv` and try again.

Then build after every change:

```bash
.venv/bin/python build.py
```

Commit the generated files along with your change. GitHub Pages serves this branch as it is, so a change is live only after the build output is committed and pushed.

To preview locally:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Write a log

Add a Markdown file to `content/logs/`. The file name becomes the address, so `content/logs/my-first-server.md` is published at `/blogs/my-first-server/`.

Start the file with this block:

```
---
title: My first server
date: 2026-12-01
log: 002
kind: Guide
subtitle: One line shown under the title.
summary: Two or three sentences shown on the logs list, the home page and in the feed.
---
```

`title`, `date` and `summary` are required. `log`, `kind`, `subtitle`, `description` (for search engines) and `page_title` (browser tab) are optional.

Then write normal Markdown. A few extras:

| You write | You get |
| --- | --- |
| `## Section title {#short-id}` | A section with a stable link, listed in the table of contents |
| A code fence opened with `bash title="Terminal"` | A highlighted code block with a label and a copy button |
| `> **Note:** text` | A callout box |
| `(1) Do this` at the start of a paragraph | A numbered step |

The build adds the table of contents, the reading time, the logs list entry, the feed entry and the sitemap entry.

## Settings

`site.toml` holds the site name, links and contact address. It also has optional blocks, commented out with examples:

- `linkedin` and `resume` add buttons to the contact section.
- `[[roadmap]]` entries add a progress tracker under "What I'm learning".
- `[[projects]]` entries add a Projects section and a nav link.

## Files

| Path | What it is |
| --- | --- |
| `build.py` | The generator. Page layout and home page text live here. |
| `site.toml` | Settings, roadmap and projects |
| `content/logs/*.md` | Log sources |
| `style.css`, `script.js` | Styles and behaviour, written by hand |
| `assets/` | Portraits, fonts (SIL Open Font License) and the social preview image |
| `index.html`, `blogs/`, `404.html`, `sitemap.xml`, `robots.txt` | Generated. Do not edit by hand. |
