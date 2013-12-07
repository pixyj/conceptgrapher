from django.core.management.base import BaseCommand, CommandError
from uber import load_data

class Command(BaseCommand):
	help = "Clear sqlite3.db + redis keys"

	def handle(self, *args, **kwargs):
		load_data.clear_all()
		self.stdout.write("Done")




