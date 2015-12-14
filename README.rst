public-search
=============

The Ambry Public Search application 

Running
-----------------

To Run the application in development, use the `run-public-search.sh` script.

Run with gunicorn:

    gunicorn ambrydoc:app -b 0.0.0.0:80

gunicorn 19.1.1 seems to be broken ( or maybe py 3 only? ) , so run with version 18:

    pip install gunicorn==18




Development Setup
-----------------

It's best to setup a virtualenv, install ``public-search``, then install ambry:

    $ cdvirtualenv
    $ git clone https://github.com/CivicKnowledge/ambry.git
    $ cd ambry
    $ git checkout develop
    $ python setup.py develop
    
    
Then, install  ambry and import some bundles. Should also build one or two. 

    $ ambry config install 
    $ ambry import test/bundles/
    

