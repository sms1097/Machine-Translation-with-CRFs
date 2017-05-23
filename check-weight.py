import pickle
from util import load_weights
from processing import load_parses_separate

#savepath1 = '../parses/eps-2k/weights/full/trained-1-'
#savepath2 = '../parses/eps-2k/weights/full/trained-2-'
#savepath3 = '../parses/eps-2k/weights/full/trained-3-'
#savepath9 = '../parses/eps-2k/weights/full/trained-9-'
#savepath10 = '../parses/eps-2k/weights/full/trained-10-'
savepath1 = '../trained-weights/eps-40k-ml10-3trans/trained-1-'
savepath2 = '../trained-weights/eps-40k-ml10-5trans/trained-1-'

w1 = load_weights(savepath1)
w2 = load_weights(savepath2)
#w3 = load_weights(savepath3)
#w9 = load_weights(savepath9)
#w10 = load_weights(savepath10)
print(len(w1)) = 218

def check(w):
	for k, v in sorted(w.items(), key=lambda x: x[1], reverse=True):
		print('{}'.format(k).ljust(25) + '{}'.format(v))

def compare(w1, w2):
	for k, v in sorted(w1.items(), key=lambda x: x[1], reverse=True):
		print('{}'.format(k).ljust(25) + '{}'.format(v))
		print('\t{}'.format(k).ljust(25) + '{}'.format(w2[k]))

def check_difference(w1, w2):
	for k, v in sorted(w1.items(), key=lambda x: x[1], reverse=True):
		print('{}'.format(k).ljust(25) + '{}'.format(v - w2[k]))

check(w1)

#compare(w1, w2)
#check_difference(w1, w2)