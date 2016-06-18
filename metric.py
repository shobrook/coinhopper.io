# Data pipelines need to be replaced (no rate limits), a more accurate exchange rate needs to be calculated (averaged across 
# exchanges or across open bids), and determining a time frame for updating exchange rate (to account for changes in volatility)
# expcoin = 86400 * [devhash / (4294.97 * (tlambda * nethash))] * (exrate * rlambda)

import urllib2, simplejson
from joblib import Parallel, delayed
import multiprocessing

inputs = ['QTL', 'FRK', 'BTC', 'GAME', 'DGB', 'LTC'] # ['GLD', 'FRK', 'BTC', 'DGB', 'NLG', 'LTC']
metrics = dict.fromkeys(inputs, 0)
devhash = float(raw_input('Enter your device\'s hashrate in MH/sec: '))
apiCounters = {'QTL' : 0, 'FRK' : 5, 'BTC' : 10, 'GAME' : 15, 'DGB' : 20, 'LTC' : 25}


apikeys = ['b87f63f1bf954b1095307e325626535e',
'ffdf59fb30304bfa9e38ddc48e7c57e4',
'5281ee161e4c4849a6ee81861f64f01b',
'2e7e917857f74b95aa92f02f88d3a521',
'e966bad6c38147bd99ab2f5e619eec55',
'34d0e494b20a476d874839db13d6f32d',
'ead9013cf6d3414b8babc67973235b70',
'c1213206bb1b43a4a436f2be082a7473',
'b44779c23b894f5daf75d4ecc8820cb0',
'48396babcb404330a3dd0292795d2586',
'4ce5acf7092d4066a2ead3e06ae9a8ee',
'335ef57584174573949343a8fa830e21',
'fef00a8a121e431680752c9f76a97b0d',
'1a87d7fe31194e5395bf5fa4cc140f1f',
'2ef2cdfc15be4904a885c7acee409224',
'711a19fc34d54035b15f537cdb98be32',
'3c6d2499c3ae4f00940c8ad4e78df20b',
'ff31c5bbca504f88ac7424f0184b2169',
'b885d5fdfd084fc89e7fe928b808597e',
'8b8334e0e5594b68bc8ce30095d38efb',
'135c3c779e6647928258ad199312897d',
'0158728a2ac5446cbfe33e7c14cfe4cc',
'3189b02c4fbc4dfc8da3f540fe8c2bd5',
'a5589a850820421188a5204a2cdc5239',
'6bac4577fbe14d1dbe6978f4ff4c1395',
'218744a10e8b46c1b173ec024025320e',
'89b74ee5f0014878ac94a66722aca13d',
'e039c781a76640bf8c1d6cc3296369a9',
'd74003f52c6640edb488517448984c4d',
'626b7beca79f4d198b000dea4d402bd2',
'4bd560b12fca4e119684d41b3655c6ad']
print('')

def estimate(i):
	if (apiCounters[i] % 5) == 0:
		apiCounters[i] -= 5

	apikey = apikeys[apiCounters[i]]
	apiCounters[i] += 1

	rlambda = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('BlockReward') # line 38
	# diff = [(tlambda * nethash) / 4294.97] --> adjusted for MH/sec
	diff = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('Difficulty') # line 39
	exrate = float((simplejson.load(urllib2.urlopen('http://www.cryptonator.com/api/ticker/' + i + '-usd'))).get('ticker').get('price'))
	print('Calculating expected daily profit (in USD) for... ' + i)
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 2)
	return expcoin

outputs = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(estimate)(i) for i in inputs)

for x in range(len(inputs)):
	metrics[inputs[x]] = float(outputs[x])

ranked = (sorted(metrics.items(), key=lambda x: x[1]))
ranked.reverse()

print('')
print(ranked)