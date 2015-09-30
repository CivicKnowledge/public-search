public-search
=============

The Ambry Public Search application 

Development Setup
-----------------

It's best to setup a virtualenv, install ``public-source``, then install ambry:

    $ cdvirtualenv
    $ git clone https://github.com/CivicKnowledge/ambry.git
    $ cd ambry
    $ git checkout develop
    $ python setup.py develop
    
    
Then, install  ambry and import some bundles. Should also build one or two. 

    $ ambry config install 
    $ ambry import test/bundles/
    
