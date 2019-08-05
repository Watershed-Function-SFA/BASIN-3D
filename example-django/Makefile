.PHONY: all

PYTHON=python3

all: bin/python keyset db.sqlite3

docs:
	cd $(CURDIR)/../docs; PYTHONPATH=$(CURDIR) DJANGO_SETTINGS_MODULE=mybroker.settings make html

develop:
	$(CURDIR)/bin/pip install -e $(CURDIR)/..

github:
	cd $(CURDIR)/../docs; PYTHONPATH=$(CURDIR):$(CURDIR)/.. GH_PAGES=$(GH_PAGES) DJANGO_SETTINGS_MODULE=mybroker.settings make github

bin/python:
	$(PYTHON) -m venv .
	$(CURDIR)/bin/pip install -r $(CURDIR)/../requirements.txt pytest sphinx sphinx_autodoc_typehints pytest-mypy pytest-flake8 pytest-django pytest-cov $(CURDIR)/..

db.sqlite3:
	$(CURDIR)/bin/python manage.py migrate

keyset:
	@mkdir -p $(CURDIR)/.keyset
	@test -e $(CURDIR)/.keyset/meta || $(CURDIR)/bin/keyczart create --location=$(CURDIR)/.keyset --purpose=crypt --name=basin3d
	@test -e $(CURDIR)/.keyset/1 || $(CURDIR)/bin/keyczart addkey --location=$(CURDIR)/.keyset --status=primary


.PHONY: run
run:
	PYTHONPATH=$(PYTHONPATH):$(CURDIR)/..:. bin/python manage.py runserver

.PHONY: test
test:
	$(CURDIR)/bin/pytest -v --flake8 --mypy --cov basin3d $(CURDIR)/.. $(CURDIR)/tests --ignore $(CURDIR)/../basin3d/migrations && cd $(CURDIR)

.PHONY: clean
clean:
	rm -rf bin lib  include build var .keyset db.sqlite3
	find  ./ -name *.pyc -exec rm {} +
