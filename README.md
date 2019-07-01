# BASIN-3D
Broker for Assimilation, Synthesis and Integration of eNvironmental Diverse, Distributed Datasets



## Development Practices

* BASIN-3D uses the [cactus model](https://barro.github.io/2016/02/a-succesful-git-branching-model-considered-harmful/) 
  of branching and code versioning in git. 
* Code development will be peformed in a forked copy of the repo. Commits will not be made directly to the basin-3d repo.  Developers will submit a pull request that is then merged by another team member, if another team member is available.
* Each pull request should contain only related modifications to a feature or bug fix.  
* Sensitive information (secret keys, usernames etc) and configuration data (e.g database host port) should not be checked in to the repo.
* A practice of rebasing with the main repo should be used rather that merge commmits.  

## Getting Started

### Prerequisities
BASIN-D3 is a Django application which requires:

* Python (>= 3.6)
* Django (>=2.0,<2.1)

### Get the code

These instructions will get you a copy of the project up and running on your local machine for 
development and testing purposes. 

    $ git clone git@bitbucket.org:<your bitbucket username>/basin-3d.git
    $ cd basin-3d
    

## Develop
Setup virtualenv for development and testing purposes. All basin-3d tests
are in `basin3d.tests`. They can be

### Example Django Project
There is an example project for testing in directory `example-django`. 
   
Create an Anaconda environment

    conda create -y -n basin3d python=3.6.5
	
Activate the new environment and prepare it for development

	source activate basin3d
	conda develop -npf -n basin3d .

Install  BASIN-3D and its dependencies

	python setup.py develop 
	pip install $(cat requirements.txt ) pytest-django pytest-cov

BASIN-3D stores datasource credentials.  This requires an encryption secrect key.

    cd example-django
	mkdir -p .keyset
	keyczart create --location=.keyset --purpose=crypt --name=basin3d
	keyczart addkey --location=.keyset --status=primary
	
Migrate the database

	./manage.py migrate
	
Run the tests

    pytest -v --cov basin3d  tests 


Run  the server

    ./manage.py runserver

    
Create a superuser

    ./manage.py createsuperuser
    

## Documentation
Sphinx is used to generate documentation. You first need
to create a virtual environment for generating the docs.

    $ source activate basin3d
    $ pip install sphinx sphinx-autodoc-typehints
    
Generate the documentation
   
    $ cd docs
    $ make html

Review the generated documentation

    $ open _build/html/index.html

# Install
 
Install a source distribution with pip:

    $ pip install BASIN-3D-<version>.tar.gz
    
To get started read the [setup](./docs/setup.rst) documentation

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, 
see the [tags on this repository](https://github.com/Watershed-Function-SFA/wfsfa-broker/tags). 

Workflow for tagging and building release:

1. checkout the version to tag from `master`
1. `git tag -a v[version]-[release] -m "Tagging release v[version]-[release]"`
1. build distribution with `setup.py`
1. `git push origin v[version]-[release]`

## Authors

* **Charuleka Varadharajan** - [LBL](http://eesa.lbl.gov/profiles/charuleka-varadharajan/)
* **Valerie Hendrix**  - [LBL](https://dst.lbl.gov/people.php?p=ValHendrix)
* **Danielle Svehla Christianson** - [LBL](https://crd.lbl.gov/departments/data-science-and-technology/uss/staff/danielle-christianson/)


See also the list of [contributors](contributors.txt) who 
participated in this project.

## License

See [LICENSE.md](LICENSE.md) file for licensing details

## Acknowledgments

TBD
