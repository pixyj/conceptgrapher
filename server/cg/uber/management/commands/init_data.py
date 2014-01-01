from django.core.management.base import BaseCommand, CommandError
from uber import data

class Command(BaseCommand):
    help = "loaddata for dev"

    def handle(self, *args, **kwargs):
        data.load_all()
        self.stdout.write("Done")



