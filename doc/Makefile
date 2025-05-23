# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
DOCSDIR       = doc
SOURCEDIR     = source
BUILDDIR      = _build
AUTOAPI_OUTDIR = source/examples/api
GALLERY_EXAMPLES = gallery-examples

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean pdf

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# customized clean due to api examples and sphinx-gallery
clean:
	rm -rf $(BUILDDIR)
	find . -type d -name "$(GALLERY_EXAMPLES)" -exec rm -rf {} +
	find . -type d -path "./$(AUTOAPI_OUTDIR)" -exec rm -rf {} +
	echo Cleanup complete.

# customized pdf due to svg issue
pdf:
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/ansys_sphinx*.pdf && echo pdf exists) || exit 1

# Serve docs
serve:
	@echo "Serving docs..."
	@cd ../ && stb serve $(DOCSDIR)/$(SOURCEDIR)
