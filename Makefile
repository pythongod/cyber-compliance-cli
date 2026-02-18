.PHONY: setup test dashboard

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e . pytest

test:
	. .venv/bin/activate && pytest -q

dashboard:
	. .venv/bin/activate && cybersec dashboard --assessment-file assessment.json
