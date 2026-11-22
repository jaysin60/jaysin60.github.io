# jaysin60.github.io

Personal profile / résumé site — **live at <https://jaysin60.github.io>**

Built as plain HTML, CSS and JavaScript. No framework, no build step, no npm.
Just edit a file, commit, push — GitHub Pages does the rest.

---

## What's here

| File | What it is |
|---|---|
| `index.html` | The whole page: name, bio, experience, skills, education, contact |
| `style.css` | All the styling (light + dark theme, responsive layout) |
| `data.js` | **Edit this to curate your projects** |
| `app.js` | Theme toggle, animations, live GitHub project sync |
| `resume.html` | Clean, printable résumé you can read in the browser |
| `404.html` | On-brand not-found page |
| `assets/profile.jpg` | Your portrait |
| `assets/*.pdf`, `assets/*.docx` | The downloadable résumé files |
| `assets/favicon.svg` | Tab icon |
| `scripts/build_resume_pdf.py` | Regenerates the PDF + web-safe DOCX from the source `.docx` |

---

## Adding projects

**Nothing to do for new GitHub repos.** The page calls the public GitHub API on
load and shows every repo that isn't in `HIDDEN`. Create a repo and it appears.

To curate the grid, edit `data.js`:

```js
FEATURED: [
  { repo: 'looped-transformer' },       // pinned first, in this order
  { repo: 'cost-saver-claude-harness' },
],

OVERRIDES: {
  'my-new-repo': {
    blurb: 'A nicer, longer description than the GitHub one.',
    tags: ['Python', 'LLM', 'Side project'],
    badge: 'New',          // optional label
    url: 'https://…',      // optional: link somewhere other than GitHub
  },
},

HIDDEN: ['spark'],         // repos to leave off the page
```

To feature something that isn't on GitHub, add it to `FEATURED` with a `url`:

```js
{ repo: 'my-write-up', url: 'https://example.com/post', blurb: '…',
  tags: ['Writing'], language: null }
```

If the API is unreachable (offline, rate-limited), the grid falls back to
`OFFLINE_PROJECTS` in the same file, so it never renders empty.

---

## Updating the résumé

1. Replace `Jayant_Singh_Singoria_Resume_2025.docx` in this folder with your
   new version (keep the same filename, or update `BASENAME` in the script).
2. Run:

   ```bash
   python3 scripts/build_resume_pdf.py
   ```

   This rebuilds both downloadable files in `assets/`. It uses only the Python
   standard library — nothing to install.

3. Update the wording in `index.html` and `resume.html` if anything changed.
4. Commit and push.

> **Note:** `Jayant_Singh_Singoria_Resume_2025.docx` at the repo root is your
> untouched original and is gitignored, so it isn't published. The copy in
> `assets/` is a *web-safe* version with the phone number removed, matching
> the email + LinkedIn only contact info shown on the page. To keep the phone
> in the downloads, set `OMIT_PHONE = False` in the script and re-run it.

---

## Updating anything else

- **Bio, job history, skills, contact links** → `index.html` (and `resume.html`
  for the printable version).
- **Colours, fonts, spacing** → the `:root` / `[data-theme="dark"]` blocks at
  the top of `style.css`.
- **Portrait** → replace `assets/profile.jpg` (a square-ish photo works best).
- **Site title / SEO description** → the `<head>` of `index.html`.

---

## Running locally

Any static server works:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Opening `index.html` directly via `file://` also works, except the live GitHub
fetch may be blocked by the browser — the offline project list will show instead.

---

## Publishing (already done)

This repo is a GitHub Pages **user site**: repo name `jaysin60.github.io`,
source = `main` branch / root. `.nojekyll` tells GitHub to serve the files as-is.

```bash
git add .
git commit -m "Update profile"
git push
```

Changes go live in about a minute.

### If a change doesn't show up

GitHub Pages caches CSS/JS for ~10 minutes. Hard-refresh the page
(`Cmd`+`Shift`+`R` on Mac, `Ctrl`+`F5` on Windows) or wait a few minutes.

---

## Troubleshooting

- **Projects grid is empty / says "GitHub unreachable"** — the public GitHub API
  is rate-limited to 60 requests/hour per IP. It recovers on its own; the saved
  list in `OFFLINE_PROJECTS` keeps the grid populated meanwhile.
- **A new repo doesn't appear** — make sure it isn't listed in `HIDDEN`, and
  hard-refresh (the API response is fetched on every load, but the JS file
  itself may be cached).
- **Fonts look different** — Google Fonts needs a connection; otherwise the
  page falls back to Georgia / system sans / monospace, which still works.

---

Built by hand. ✳
