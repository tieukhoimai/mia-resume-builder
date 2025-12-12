# Makefile for YAAC: Another Awesome CV
# Targets:
#  - all/pdf: build the PDF using latexmk (LuaLaTeX)
#  - deps: install recommended TeX packages with tlmgr
#  - view: open the generated PDF (macOS/Linux)
#  - clean: remove auxiliary files

TEX := latexmk
LATEXMKFLAGS := -cd -f -lualatex -interaction=nonstopmode -synctex=1
EXAMPLE_DIR := example
TEXFILE := $(EXAMPLE_DIR)/cv.tex
PDF := $(EXAMPLE_DIR)/cv.pdf

.PHONY: all pdf deps view clean
all: pdf

pdf:
	@if command -v $(TEX) >/dev/null 2>&1; then \
		cd $(EXAMPLE_DIR) && $(TEX) $(LATEXMKFLAGS) cv.tex; \
	else \
		echo "latexmk not found. Install latexmk (tlmgr install latexmk) or use your TeX distribution."; exit 1; \
	fi

deps:
ifeq (, $(shell command -v tlmgr))
	@echo "tlmgr not found — please install TinyTeX or TeX Live with tlmgr. See README.md for instructions." 
else
	tlmgr update --self --all
	tlmgr install latexmk biber collection-latexrecommended collection-latexextra collection-luatex collection-langfrench collection-fontsrecommended fontawesome5 csquotes
endif

view: pdf
	@if [ "$(shell uname)" = "Darwin" ]; then \
		open $(PDF); \
	else \
		xdg-open $(PDF) || true; \
	fi

clean:
	cd $(EXAMPLE_DIR) && $(TEX) -C || true
