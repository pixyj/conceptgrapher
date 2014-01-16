Overview
==============


Concept Grapher is a django project that complements tutorials using quizzes to test your understanding each concept before you move on the next one. 

How does it work?
----------------
Visit the [site](http://conceptgrapher.org) for more info!

Tech Stack
------------------
1. [django](http://github.com/django/django) for the heavy lifting.
2. A bunch of python dependencies including `networkx` for maintaining concepts in the topological order.
3. Redis for caching the concept-graph. The entire graph fits in memory as of now.
Future improvements include using a graph store like `neo4j`
4. jQuery + underscore + backbone + bootstrap for the frontend
5. Standard nginx + gunicorn + django + postgresql stack used for production.

Running ConceptGrapher on your local machine
----------
Install [Redis](http://redis.io) (Used for caching).

Create a virtualenv using [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) and work on it.

        mkvirtualenv cg
        workon cg

`cd` into your favorite directory and clone the repo
    
        git clone git@github.com:pramodliv1/conceptgrapher.git

Install python dependencies

        cd server
        pip install requirements.txt

Set the `DJANGO_SETTINGS_MODULE` environment variable to `dev`
        
        export DJANGO_SETTINGS_MODULE="cg.settings.dev"

Load some initial data from the fixtures from the custom `init_data` management command.

        cd cg
        python manage.py init_data



Run the local server

        cd cg
        python manage.py runserver

[And... you're done!](http://localhost:8000)
