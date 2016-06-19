# Data pipelines need to be replaced (no rate limits), a more accurate exchange rate needs to be calculated (averaged across 
# exchanges or across open bids), and determining a time frame for updating exchange rate (to account for changes in volatility)
# expcoin = 86400 * [devhash / (4294.97 * (tlambda * nethash))] * (exrate * rlambda)

import urllib2, simplejson
from joblib import Parallel, delayed
import multiprocessing
import time
from pymongo import MongoClient

client = MongoClient()
db = client.miner_io

inputs = ['QTL', 'FRK', 'BTC', 'GAME', 'DGB', 'LTC']
metrics = dict.fromkeys(inputs, 0)

hashrates = {'QTL' : 100, 'FRK' : 100, 'BTC' : 100, 'GAME' : 100, 'DGB' : 100, 'LTC' : 100}
exchange_rates = {}
block_rewards = {}
difficulties = {}

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

def estimate(i):
	if (apiCounters[i] % 5) == 0:
		if i == 'QTL' and apiCounters[i] != 0:
			apiCounters[i] -= 5
		elif i == 'FRK' and apiCounters[i] != 5:
			apiCounters[i] -= 5
		elif i == 'BTC' and apiCounters[i] != 10:
			apiCounters[i] -= 5
		elif i == 'GAME' and apiCounters[i] != 15:
			apiCounters[i] -= 5
		elif i == 'DGB' and apiCounters[i] != 20:
			apiCounters[i] -= 5
		elif i == 'LTC' and apiCounters[i] != 25:
			apiCounters[i] -= 5

	apikey = apikeys[apiCounters[i]]
	apiCounters[i] += 1
	devhash = hashrates[i]

	print 'Calculating expected daily profit (in USD) for... ' + i
	rlambda = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('BlockReward')
	diff = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('Difficulty')
	exrate = float((simplejson.load(urllib2.urlopen('http://www.cryptonator.com/api/ticker/' + i + '-usd'))).get('ticker').get('price'))
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 2)
	difficulties[i] = diff
	exchange_rates[i] = exrate
	block_rewards[i] = rlambda
	return expcoin

def commitData(i):
	result = db[i].insert_one(
		{
			'timestamp' : timestamp,				#UNIX timestamp for data data was collected
			'daily_profit' : profitibilities[i],	#Profitibility calculated in USD
    		'hash_rate' : hashrates[i],				#Hash rate for the given currency
    		'exchange_rate' : exchange_rates[i],	#Exchange rate for the given currency in USD
    		'block_reward' : block_rewards[i],		#Block reward for the given currency
    		'difficulty' : difficulties[i],			#Difficulty for the given currency
		}
	)
	print 'Inserted document with ID: ' + str(result.inserted_id) + ' into DB:miner_io Collection: ' + i

while True:
	print ''

	outputs = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(estimate)(i) for i in inputs)
	timestamp = int(time.time())
	print(timestamp)
	for x in range(len(inputs)):
		metrics[inputs[x]] = float(outputs[x])
	ranked = (sorted(metrics.items(), key=lambda x: x[1]))

	print ''

	profitibilities = dict(ranked)
	for i in inputs:
		print "Profitibility of " + i + " is $" + str(profitibilities[i])
		commitData(i)

	#Need some sort of function that broadcasts the coin to mine

	time.sleep(1800)	#Sleep for 30 minutes
