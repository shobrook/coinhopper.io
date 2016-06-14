# Data pipelines need to be replaced (no rate limits), a more accurate exchange rate needs to be calculated (averaged across 
# exchanges or across open bids), and determining a time frame for updating exchange rate (to account for changes in volatility)

# expcoin = 86400 * [devhash / (4294.97 * (tlambda * nethash))] * (exrate * rlambda)

import urllib2, simplejson
from joblib import Parallel, delayed
import multiprocessing

inputs = ['QTL', 'FRK', 'BTC', 'GAME', 'DGB', 'LTC']
metrics = dict.fromkeys(inputs, 0)

devhash = float(raw_input('Enter your device\'s hashrate in MH/sec: '))
apikey = '5281ee161e4c4849a6ee81861f64f01b'

print('')

def estimate(i):
	rlambda = # line 40
	# diff = [(tlambda * nethash) / 4294.97] --> adjusted for MH/sec
	diff = # line 41
	exrate = float((simplejson.load(urllib2.urlopen('http://www.cryptonator.com/api/ticker/' + i + '-usd'))).get('ticker').get('price'))
	print('Calculating expected daily profit (in USD) for... ' + i)
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 2)
	return expcoin

num_cores = multiprocessing.cpu_count()

outputs = Parallel(n_jobs=num_cores)(delayed(estimate)(i) for i in inputs)

for x in range(len(inputs)):
	metrics[inputs[x]] = float(outputs[x])

ranked = (sorted(metrics.items(), key=lambda x: x[1]))
ranked.reverse()

print('')
print(ranked)

# rlambda = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('BlockReward')
# diff = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('Difficulty')