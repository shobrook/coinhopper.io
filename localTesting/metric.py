# expcoin = 86400 * [devhash / (4294.97 * (tlambda * nethash))] * (exrate * rlambda)

import urllib2, simplejson
from joblib import Parallel, delayed
import multiprocessing
import time

inputs = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME', 'PPC', 'BTC', 'ZET', 'MZC', 'TEK']

inputs_scrypt = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME']
inputs_sha = ['PPC', 'BTC', 'ZET', 'MZC', 'TEK']

metrics = dict.fromkeys(inputs, 0)

hashrates = {'DGB' : 100, 'GLD' : 100, 'CNC' : 100, 'NVC' : 100, 'GAME' : 100, 'PPC' : 100, 'BTC' : 100, 'ZET' : 100, 'MZC' : 100, 'TEK' : 100}

apikey = '21abcbe4ccf74b5c96174da91325d40f'

def estimate(i):
	devhash = hashrates[i]
	print 'Calculating expected daily profit (in USD) for... ' + i
	rlambda = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('BlockReward')
	# diff = [tlambda * nethash] / 4294.97 --> Scaled to 1 MH/sec
	diff = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('Difficulty')
	exrate = float((simplejson.load(urllib2.urlopen('http://www.cryptonator.com/api/ticker/' + i + '-usd'))).get('ticker').get('price'))
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 2)
	return expcoin

print ''

outputs = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(estimate)(i) for i in inputs)
timestamp = int(time.time())

for x in range(len(inputs)):
	metrics[inputs[x]] = float(outputs[x])
ranked = (sorted(metrics.items(), key=lambda x: x[1]))
ranked.reverse()

print ''

print "***SCRYPT CURRENCIES***"
for x in range(len(ranked)):
	if str(ranked[x][0]) in inputs_scrypt:
		print "Profitability of " + str(ranked[x][0]) + " is $" + str(ranked[x][1])

print "***SHA-256 CURRENCIES***"
for x in range(len(ranked)):
	if str(ranked[x][0]) in inputs_sha:
		print "Profitability of " + str(ranked[x][0]) + " is $" + str(ranked[x][1])

profitabilities = dict(ranked)