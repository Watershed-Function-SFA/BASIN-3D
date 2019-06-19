.PHONY: all

PYTHON=python

all: bin/python keyset db.sqlite3

develop: 
	$(CURDIR)/bin/pip install -e $(CURDIR)/..

bin/python:
	$(PYTHON) -m venv .
	$(CURDIR)/bin/pip install -r $(CURDIR)/../requirements.txt pytest-mypy pytest-flake8 pytest-django pytest-cov $(CURDIR)/..

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
	$(CURDIR)/bin/pytest -v --flake8 --mypy --cov basin3d $(CURDIR)/.. $(CURDIR)/tests && cd $(CURDIR)

.PHONY: clean
clean:
	rm -rf bin lib  include build var .keyset db.sqlite3
	find  ./ -name *.pyc -exec rm {} +
