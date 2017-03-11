import json
import sys
import string
from collections import Counter
if len(sys.argv) <= 2:
	print("error")

model = {}
with open(sys.argv[1]) as modelFile:
	model = json.load(modelFile)

RemovePunctTable = {ord(c): None for c in string.punctuation+string.whitespace}

inputStr = sys.argv[2].translate(RemovePunctTable).lower()

N = model["ngram_size"]
del model["ngram_size"]

#Chi square test
ngrams = dict(Counter([inputStr[i:i+N] for i in range(len(inputStr)-N)]))
total = sum(ngrams.values())

expected = {}
for elem in model:
	expected[elem] = model[elem] * total

chi_square = 0
for ngram in expected:
	#this could happen due to floating point
	if expected[ngram] == 0:
		continue
	actual = 0
	if ngram in ngrams:
		actual = ngrams[ngram]
	chi_square += (actual - expected[ngram])**2 / expected[ngram]

#Correction from Campbell(2007)
chi_square = chi_square * (total - 1) / total

degrees_of_freedom = len(expected) - 1
print("Degrees of freedom: ", end="")
print(degrees_of_freedom)
print("Chi square: ", end="")
print(chi_square)
if (degrees_of_freedom == 1295):
	crit_value = 1380.86379464
	print("Crit value at alpha = .05: ", end = "")
	print(crit_value)
	if (chi_square > crit_value):
		print("unusual text detected")
	else:
		print("text fits the model")
