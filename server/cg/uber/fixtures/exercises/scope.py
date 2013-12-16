def spam(it):
	def sum(it):
	    sum = 0
	    for i in it:
	        sum -= i
	    return sum
	
	return sum(it)


data = range(1, 4)
a = sum(data)
b = spam(data)

print a, b

