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

* Python (>= 3.4, 3.5)
* Django (1.8, 1.9)

### Get the code

These instructions will get you a copy of the project up and running on your local machine for 
development and testing purposes. 

    $ git clone git@bitbucket.org:<your bitbucket username>/basin-3d.git
    $ cd basin-3d
    

## Documentation
Sphinx is used to generate documentation. You first need
to create a virtual environment for generating the docs.

    $ source .venv/bin/activate
    $ pip install sphinx
    $ python setup.py develop
    
Generate the documentation
   
    $ cd docs
    $ make html

Review the generated documentation

    $ open _build/html/index.html

## Develop
Setup virtualenv for development and testing purposes. All basin-3d tests
are in `basin3d.tests`. They can be

### Example Django Project
There is an example project for testing in directory `example-django`. 
   
Build the example Django project

    $ cd example-django
    $ make
    ...
    Registered  Parameter 'Ag' for Data Source 'Alpha'
    Registered  Parameter 'Al' for Data Source 'Alpha'
    Registered  Parameter 'As' for Data Source 'Alpha'
    
Create a superuser

    $ bin/python manage.py createsuperuser
    
Test the basin-3d framework. The basin-3d test reside in `basin3d.tests`. Tests
for new features should be added to this Python package.  They will be
automatically picked up by the test command.

    $ make test
    
Run the example application

    $ make run
    bin/python manage.py runserver
    DJango BASEDIR: /Users/val/workspace/basin-3d/example-django
    DJango BASEDIR: /Users/val/workspace/basin-3d/example-django
    Performing system checks...
    
    System check identified no issues (0 silenced).
    November 02, 2016 - 23:36:17
    Django version 1.9, using settings 'mybroker.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

# Install
 
TBD

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, 
see the [tags on this repository](https://github.com/Watershed-Function-SFA/wfsfa-broker/tags). 

## Authors

* **Charuleka Varadharajan** - [LBL](http://eesa.lbl.gov/profiles/charuleka-varadharajan/)
* **Valerie Hendrix**  - [LBL](https://dst.lbl.gov/people.php?p=ValHendrix)

See also the list of [contributors](contributors.txt) who 
participated in this project.

## License

TBD

## Acknowledgments

TBD
