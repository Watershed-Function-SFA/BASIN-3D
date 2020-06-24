.PHONY: all

PYTHON=python3.7

all: bin/python db.sqlite3

docs:
	cd $(CURDIR)/../docs; PYTHONPATH=$(CURDIR) DJANGO_SETTINGS_MODULE=mybroker.settings make html

develop:
	$(CURDIR)/bin/pip install -e $(CURDIR)/..

github:
	cd $(CURDIR)/../docs; PYTHONPATH=$(CURDIR):$(CURDIR)/.. GH_PAGES=$(GH_PAGES) DJANGO_SETTINGS_MODULE=mybroker.settings make github

bin/python:
	$(PYTHON) -m venv .
	$(CURDIR)/bin/pip install -r $(CURDIR)/../requirements.txt
	$(CURDIR)/bin/pip install pytest sphinx sphinx_autodoc_typehints pytest-mypy pytest-flake8 pytest-django pytest-cov $(CURDIR)/..

db.sqlite3:
	$(CURDIR)/bin/python manage.py migrate


.PHONY: run
run:
	PYTHONPATH=$(PYTHONPATH):$(CURDIR)/..:. bin/python manage.py runserver

.PHONY: test
test:
	$(CURDIR)/bin/pytest -vv --flake8 --mypy --cov django_basin3d --cov-report term --cov-report html $(CURDIR)/.. $(CURDIR)/tests --ignore $(CURDIR)/../django_basin3d/migrations && cd $(CURDIR)

.PHONY: clean
clean:
	rm -rf bin lib  include build var db.sqlite3
	find  ./ -name *.pyc -exec rm {} +
