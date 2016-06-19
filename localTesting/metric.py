# Data pipelines need to be replaced (no rate limits), a more accurate exchange rate needs to be calculated (averaged across 
# exchanges or across open bids), and determining a time frame for updating exchange rate (to account for changes in volatility)
# expcoin = 86400 * [devhash / (4294.97 * (tlambda * nethash))] * (exrate * rlambda)

import urllib2, simplejson
from joblib import Parallel, delayed
import multiprocessing
import time

inputs = ['QTL', 'FRK', 'BTC', 'GAME', 'DGB', 'LTC']
metrics = dict.fromkeys(inputs, 0)

hashrates = {'QTL' : 100, 'FRK' : 100, 'BTC' : 100, 'GAME' : 100, 'DGB' : 100, 'LTC' : 100}

apikey = '6c727839f13346b0b9a453e7a9780a53'

def estimate(i):
	devhash = hashrates[i]

	print 'Calculating expected daily profit (in USD) for... ' + i
	rlambda = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('BlockReward')
	diff = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('Difficulty')
	exrate = float((simplejson.load(urllib2.urlopen('http://www.cryptonator.com/api/ticker/' + i + '-usd'))).get('ticker').get('price'))
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 2)
	return expcoin

print ''

outputs = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(estimate)(i) for i in inputs)
timestamp = int(time.time())
print(timestamp)
for x in range(len(inputs)):
	metrics[inputs[x]] = float(outputs[x])
ranked = (sorted(metrics.items(), key=lambda x: x[1]))
ranked.reverse()

print ''

profitibilities = dict(ranked)
for i in inputs:
	print "Profitibility of " + i + " is $" + str(profitibilities[i])