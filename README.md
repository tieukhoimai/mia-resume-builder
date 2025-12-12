mia-resume-builder (derived from YAAC — Another Awesome CV)
==========================

This repository is a separate project (mia-resume-builder) derived from the YAAC — Another Awesome CV template.
The original YAAC project (YAAC: Another Awesome CV) remains available at https://github.com/darwiin/yaac-another-awesome-cv and this fork builds on top of that reference template.

- Overview
- Primary entry: `example/cv.tex` (engine: LuaLaTeX).
- Class file: `yaac-another-awesome-cv.cls`.

Notable changes in this fork
---------------------------
- Default theme color changed to RoyalBlue.
- Added a GitHub link for the personal blog: `tieukhoimai/mia-blog-v3`.
- Replaced header photo with `example/ava.jpeg` and applied a subtle RoyalBlue-tinted overlay in the class.
- Small layout and typographical fixes; removed malformed/duplicated `idphoto` code and cleaned up typos.
- CI workflow adjusted to upload and publish only `example/cv.pdf` as an artifact/release asset.

Repository location
-------------------
This fork has been moved to https://github.com/tieukhoimai/mia-resume-builder.git to keep the original `resume-v1` repository untouched; it remains available as `upstream` for reference.

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

Credits & License
-----------------
Original author: Christophe Roger (Darwiin). This repo includes the LaTeX class `yaac-another-awesome-cv.cls`.

- Class license: LPPL Version 1.3c
- Content license: CC BY-SA 4.0
