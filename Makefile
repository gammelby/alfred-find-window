WORKFLOW_SRC := $(CURDIR)/window-switcher
WORKFLOW_DST := $(HOME)/Library/Application Support/Alfred/Alfred.alfredpreferences/workflows/user.workflow.window-switcher

.PHONY: test link unlink

test:
	python3 -I -m unittest discover -s window-switcher/tests -t window-switcher

link:
	ln -sfn "$(WORKFLOW_SRC)" "$(WORKFLOW_DST)"

unlink:
	rm -f "$(WORKFLOW_DST)"
