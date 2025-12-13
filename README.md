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

Credits & License
-----------------
Original author: Christophe Roger (Darwiin). This repo includes the LaTeX class `yaac-another-awesome-cv.cls`.

- Class license: LPPL Version 1.3c
- Content license: CC BY-SA 4.0

Publish the CV for other websites to embed
-----------------------------------------
You can publish the built `cv.pdf` (and a small `cv.json` metadata file) to GitHub Pages so another website repository can fetch and embed the resume directly. We use `gh-pages` branch to serve these files.

- Public PDF: `https://<owner>.github.io/<repo>/cv.pdf`
- Metadata JSON: `https://<owner>.github.io/<repo>/cv.json`

Embed options the other website can use:

- Iframe snippet to display the PDF directly:

```html
<iframe src="https://<owner>.github.io/<repo>/cv.pdf" width="100%" height="800" style="border: none;"></iframe>
```

- Use the `cv.json` metadata to get the latest PDF URL (for automation):

```js
fetch('https://<owner>.github.io/<repo>/cv.json')
  .then(r => r.json())
  .then(meta => {
    // Use meta.url to embed or provide download link
    document.getElementById('cvframe').src = meta.url;
  });
```

- Use PDF.js for better rendering on site (example in README) or render pages as images if you prefer.

Notes:
- Ensure GitHub Pages are enabled for this repository and the site is configured to serve from `gh-pages` branch.
- If you'd like automatic HTML conversion, we can also publish a `cv.html` generated with LaTeXML or Pandoc.
