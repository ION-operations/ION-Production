% Makefile for building PDF from LaTeX
# Usage: make pdf

PYTHON = python
LATEX = pdflatex
BIBTEX = bibtex
MAKEINDEX = makeindex

MAIN = main.tex
OUTPUT = THE_NORTH_STAR_DOCUMENT.pdf

.PHONY: all pdf clean convert

all: convert pdf

convert:
	$(PYTHON) scripts/markdown_to_latex.py

pdf: $(MAIN)
	$(LATEX) $(MAIN)
	$(BIBTEX) $(basename $(MAIN))
	$(MAKEINDEX) $(basename $(MAIN))
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)
	mv $(basename $(MAIN)).pdf $(OUTPUT)

clean:
	rm -f *.aux *.log *.toc *.out *.bbl *.blg *.idx *.ilg *.ind *.lof *.lot

