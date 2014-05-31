import subprocess

from django.conf import settings
from topo import models as tm
from topo import graph

def exec_command(command):
    return subprocess.check_output(command, shell=True)


def deploy_static():
    print "Copying static files to static_root"
    exec_command("python manage.py compress")
    exec_command("rm -rf $HOME/.code/cg/static_root/CACHE")
    exec_command("cp -r cg/static/CACHE $HOME/.code/cg/static_root/CACHE")

def build_graph():
    print "Building graph"
    relationships = tm.ConceptRelationship.objects.all()
    graph.build_graph(relationships)


def deploy():

    deploy_static()
    build_graph()

    try:
        with open(settings.GUNICORN_PID_FILE, "r") as f:
            pid = f.read()

    except IOError:
        print "GUNICORN_PID_FILE not found"
        pid = None

    if pid:
        print "Stopping gunicorn"
        exec_command("kill -3 {pid}".format(pid=pid))

    print "Starting gunicorn"    
    exec_command("python manage.py run_gunicorn --workers={workers} --pid={pid}".format(
        workers=settings.GUNICORN_WORKERS, pid=settings.GUNICORN_PID_FILE))


if __name__ == "__main__":
    deploy()

