.PHONY: all
all: bin/python keyset db.sqlite3



bin/python:
	virtualenv --no-site-packages -p `which python3` $(CURDIR)
	cd $(CURDIR)/.. && $(CURDIR)/bin/python setup.py develop && cd $(CURDIR)

db.sqlite3:
	bin/python manage.py migrate

keyset:
	mkdir -p $(CURDIR)/.keyset
	$(CURDIR)/bin/keyczart create --location=$(CURDIR)/.keyset --purpose=crypt --name=basin3d
	$(CURDIR)/bin/keyczart addkey --location=$(CURDIR)/.keyset --status=primary


.PHONY: run
run:
	bin/python manage.py runserver

.PHONY: test
test:
	cd .. && PYTHONPATH="$(PYTHONPATH):." $(CURDIR)/bin/python  $(CURDIR)/manage.py test && cd $(CURDIR)


.PHONY: clean
clean:
	rm -rf bin lib  include build var .keyset db.sqlite3
	find  ./ -name *.pyc -exec rm {} +
