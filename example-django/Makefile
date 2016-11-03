.PHONY: all
all: bin/python keyset db.sqlite3

bin/python:
	virtualenv --no-site-packages -p `which python3` .
	cd .. && $(CURDIR)/bin/python setup.py develop && cd $(CURDIR)

db.sqlite3:
	bin/python manage.py migrate

keyset:
	mkdir -p .keyset
	bin/keyczart create --location=.keyset --purpose=crypt --name=basin3d
	bin/keyczart addkey --location=.keyset --status=primary


.PHONY: run
run:
	bin/python manage.py runserver

.PHONY: test
test:
	cd .. && $(CURDIR)/bin/python $(CURDIR)/manage.py test && cd $(CURDIR)


.PHONY: clean
clean:
	rm -rf bin lib  include build var .keyset db.sqlite3
	find  ./ -name *.pyc -exec rm {} +