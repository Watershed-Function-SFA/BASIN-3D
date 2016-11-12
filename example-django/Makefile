.PHONY: all
all: bin/python keyset db.sqlite3

bin/python:
	virtualenv --no-site-packages -p `which python3` .
	cd ../ && example-django/bin/python setup.py sdist && cd $(CURDIR)
	bin/pip install ../dist/BASIN-3D-1.0.0a0.tar.gz

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
	cd .. && PYTHONPATH="$(PYTHONPATH):." $(CURDIR)/bin/python  $(CURDIR)/manage.py test && cd $(CURDIR)


.PHONY: clean
clean:
	rm -rf bin lib  include build var .keyset db.sqlite3
	find  ./ -name *.pyc -exec rm {} +
