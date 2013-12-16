class Person(object):
	def __init__(this, name):
		this.name = name
	def capitalize_name(self):
		return self.name[0].upper() + self.name[1:]



p = Person(name="spam")
in_caps = p.capitalize_name
name = in_caps()
 
