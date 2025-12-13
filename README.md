mia-resume-builder
==========================

This repository is a separate project (mia-resume-builder) derived from the YAAC — Another Awesome CV template.
The original YAAC project (YAAC: Another Awesome CV) remains available at https://github.com/darwiin/yaac-another-awesome-cv and this fork builds on top of that reference template.

Overview
- Primary entry: `example/cv.tex` (engine: LuaLaTeX).
- Class file: `yaac-another-awesome-cv.cls`.

Changes in this fork
---------------------------
- Small layout and typographical fixes; removed malformed/duplicated `idphoto` code and cleaned up typos.
- CI workflow adjusted to upload and publish only `example/cv.pdf` as an artifact/release asset.

Build locally
-------------
Prerequisites: a TeX distribution with LuaLaX and `latexmk`.

Recommended (lightweight): TinyTeX

```bash
# Install TinyTeX (Unix/macOS)
curl -sL 'https://yihui.org/tinytex/install-bin-unix.sh' | sh
```

Install required packages (tlmgr) or use system package manager on CI:

```bash
# Update tlmgr and install common packages
tlmgr update --self --all
tlmgr install latexmk biber collection-latexrecommended collection-latexextra collection-luatex collection-langfrench collection-fontsrecommended fontawesome5 csquotes
```

Build the example CV:

```bash
cd example
latexmk -cd -f -lualatex -interaction=nonstopmode -synctex=1 cv.tex
# Open the generated PDF (macOS):
open cv.pdf
# or on Linux:
# xdg-open cv.pdf
```

Clean auxiliary files:

```bash
latexmk -C
```

Makefile
--------
A `Makefile` is included at the repo root with convenient targets:

- `make pdf` — build `example/cv.pdf` (uses `latexmk` + LuaLaTeX)
- `make deps` — attempts to install recommended TeX deps using `tlmgr` (if available)
- `make view` — build then open the PDF
- `make clean` — clean auxiliary files in `example/`

CI / GitHub Actions
-------------------
A GitHub Actions workflow is provided at `.github/workflows/latex-build.yml`.

Trigger options:
- Automatic: push to `main`/`master` or open a pull request.
- Manual: use the Actions tab and click **Run workflow** (the workflow includes `workflow_dispatch`).
- API: call the `workflow_dispatch` endpoint. Example:

```bash
# Replace placeholders
OWNER=<owner>
REPO=<repo>
WORKFLOW=latex-build.yml
REF=main
TOKEN="${GITHUB_TOKEN_OR_PAT}"

curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW/dispatches \
  -d '{"ref":"'$REF'"}'
```

The workflow supports optional inputs when manually dispatched:
- `use_tinytex` — install TinyTeX instead of apt packages
- `publish_release` — if true, the workflow creates a GitHub Release and uploads `cv.pdf`
- `release_tag` / `release_name` — optional release metadata

Create a Release and publish `cv.pdf`
------------------------------------
There are multiple ways to create a release that will trigger the workflow and attach the built `cv.pdf` to it:

- Push a tag to the remote (triggers the workflow on push & the release job will attach the PDF):

```bash
# create and push semantic tag
git tag -a v1.0 -m "Release v1.0"
git push origin v1.0
```

- Create a release in the GitHub UI (Releases → Draft a new release). Publishing the release triggers the workflow using the `release` event and the built PDF will be attached.

- Create the release via the GitHub CLI:

```bash
# Ensure 'gh' is authenticated and installed
gh release create v1.0 --title "v1.0" --notes "PDF build for v1.0"
```

- Manually: Run the workflow via the Actions tab and set `publish_release` to true, optionally providing `release_tag` and `release_name`.

Notes:
- We support `release` events and tag pushes; both will cause the pipeline to build `example/cv.pdf` and attach it to the corresponding release.
- If you prefer to directly trigger a release without creating a tag, use the GitHub UI or `gh release create` command above. This will trigger the `release` event in Actions and run the pipeline.

Publish the CV for other websites to embed
-----------------------------------------
The GitHub Actions workflow automatically generates `cv.pdf` and `cv.json` files, then publishes them to GitHub Pages so other websites can consume them.

**Published URLs:**
- PDF: `https://<owner>.github.io/<repo>/cv.pdf`
- JSON: `https://<owner>.github.io/<repo>/cv.json`

JSON Structure
--------------
The `cv.json` generator automatically parses all LaTeX source files and extracts structured CV data:

```json
{
  "name": "Mai Khoi Tieu",
  "tagline": "Data Scientist | Analytics Engineer",
  "socials": { "linkedin": "...", "github": "...", ... },
  "headline": "Full paragraph summary...",
  "experience": [
    {
      "role": "Research Intern",
      "company": "SINTEF",
      "location": "Oslo, Norway",
      "dates": "Apr 2025 - Sep 2025",
      "bullets": ["Bullet 1", "Bullet 2", "Bullet 3"],
      "tags": ["Knowledge Graphs", "Neo4j", "..."]
    }
  ],
  "education": [{"dates": "...", "details": "..."}, ...],
  "skills": [{"category": "...", "items": [...]}, ...],
  "awards": [{"year": "...", "title": "..."}, ...],
  "languages": [{"language": "...", "level": "..."}, ...],
  "strengths": ["...", "..."],
  "projects": [
    {
      "title": "Personal Blog",
      "dates": "2023 - present",
      "links": {
        "website": {"url": "https://tieukhoimai.me/", "display": "tieukhoimai.me"},
        "github": {"url": "https://github.com/tieukhoimai/mia-blog-v3", "display": "tieukhoimai/mia-blog-v3"}
      },
      "description": "Full project description...",
      "tech": ["Next.js", "TypeScript", "..."]
    }
  ],
  "publications": [
    {"type": "inproceedings", "author": "...", "title": "...", "year": "2025", "booktitle": "..."}
  ],
  "meta": {"generated_at": "2025-12-13T12:50:26Z"}
}
```

Consumer Usage (Next.js Example)
-------------------------------
Other websites can fetch and render this CV data:

**Render CV from JSON in Next.js:**
```typescript
// pages/cv.tsx
const cvData = await fetch('https://<owner>.github.io/<repo>/cv.json').then(r => r.json());

export default function CV({ cv }) {
  return (
    <div>
      <h1>{cv.name}</h1>
      <p>{cv.tagline}</p>
      
      {cv.experience.map(exp => (
        <section key={exp.role}>
          <h3>{exp.role} @ {exp.company}</h3>
          <p>{exp.dates}</p>
          <ul>
            {exp.bullets.map((bullet, i) => (
              <li key={i}>{bullet}</li>
            ))}
          </ul>
          <div>{exp.tags.join(', ')}</div>
        </section>
      ))}
    </div>
  );
}
```

**Or embed the PDF directly:**
```html
<iframe src="https://<owner>.github.io/<repo>/cv.pdf" width="100%" height="800" style="border: none;"></iframe>
```

