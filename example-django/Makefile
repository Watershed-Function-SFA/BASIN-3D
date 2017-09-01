.PHONY: all

PYTHON=python3

all: bin/python keyset db.sqlite3

bin/python:
	$(PYTHON) -m venv .
	$(CURDIR)/bin/pip install -r $(CURDIR)/../requirements.txt

db.sqlite3:
	PYTHONPATH=$(PYTHONPATH):$(CURDIR)/..:. bin/python manage.py migrate

keyset:
	@mkdir -p $(CURDIR)/.keyset
	@test -e $(CURDIR)/.keyset/meta || $(CURDIR)/bin/keyczart create --location=$(CURDIR)/.keyset --purpose=crypt --name=basin3d
	@test -e $(CURDIR)/.keyset/1 || $(CURDIR)/bin/keyczart addkey --location=$(CURDIR)/.keyset --status=primary


.PHONY: run
run:
	PYTHONPATH=$(PYTHONPATH):$(CURDIR)/..:. bin/python manage.py runserver

.PHONY: test
test:
	cd .. && PYTHONPATH="$(PYTHONPATH):$(CURDIR)/..:." $(CURDIR)/bin/python  $(CURDIR)/manage.py test && cd $(CURDIR)


.PHONY: clean
clean:
	rm -rf bin lib  include build var .keyset db.sqlite3
	find  ./ -name *.pyc -exec rm {} +
