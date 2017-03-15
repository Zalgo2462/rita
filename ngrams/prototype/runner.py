total = 0
good = 0

while(True):
	line = input()
	if ('Degrees of freedom' in line):
		total += 1
		line = input()
		line = input()
		line = input()
		if ('unusual' in line):
			good += 1
			print(good / total)
