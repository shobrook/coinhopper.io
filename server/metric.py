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

inputs = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME', 'PPC', 'BTC', 'ZET', 'MZC', 'TEK']

inputs_scrypt = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME']
inputs_sha = ['PPC', 'BTC', 'ZET', 'MZC', 'TEK']
metrics = dict.fromkeys(inputs, 0)

hashrates = {'DGB' : 100, 'GLD' : 100, 'CNC' : 100, 'NVC' : 100, 'GAME' : 100, 'PPC' : 100, 'BTC' : 100, 'ZET' : 100, 'MZC' : 100, 'TEK' : 100}
exchange_rates = {}
block_rewards = {}
difficulties = {}

apiCounters = {'DGB' : 0, 'GLD' : 5, 'CNC' : 10, 'NVC' : 15, 'GAME' : 20, 'PPC' : 25, 'BTC' : 30, 'ZET' : 35, 'MZC' : 40, 'TEK' : 45}
apikeys = ['520c4970e88949ba81e9db583711d439',
	'8d98a4fe80854fdebef12b7b758e9aec',
	'850e29b35e0042ee9c2f230e795db278',
	'1df54139e3924f5e8ebd9b3a96110462',
	'3859079deb804e5995f0f5e61215d4b9',
	'037a2bef22e549ef80c69d6a70a90ea6',
	'c0ff9ad2c6fc48cf8743bff2335e17d4',
	'5f03d75ee98f43adbad412ccdbdf9503',
	'bc6dd350dd7a4ebab43582f56f89882f',
	'cbdedc14aa904c30a7a8be7faf248d74',
	'e21225fc059b47d19c841b0d52b646e7',
	'f6343455cdfd427189a20dd9d32b3120',
	'0c1f733077ec4de39510d9e41174c780',
	'a7841786bc4c4da5afd75db4b2574c74',
	'5e68df33bdba4cbdaeabac20bfec2bce',
	'ebe42595f7174212b204f0cdb92b21da',
	'acc7fa8e448a4d1db6c058bd6bd67243',
	'd999af13466d4553b306396fff12bdf7',
	'b0fc0ea5a5e84aab9a50b978fa256faa',
	'e82a4ea0dc384f1b8a8a5c3414d932cf',
	'f108dd6f22ba447baa2fe10f2fb58791',
	'e92663f4ab7640ae83e53dc15d9556dc',
	'9a2042c9e37546d9a4aecade9edede29',
	'3629dc9f6aac499ea5fa5b50b599072d',
	'7165cfb39e4c42aea0268a6daabf2c41',
	'745b26f5e94841819474d0db9e013dff',
	'478d14b68d3f46bf8ab5e0b87a253a24',
	'b4d38b0776ed4a3bb6d8168ec79c7761',
	'1cdf321522524154978fbf6e4781cadf',
	'7fafe7ff418a41ec8f98861291c773bc',
	'04b3859baa424d38881e4e0b08eea123',
	'a6c62daea1234ee7b429da1e3cde9d99',
	'242d3574ebca438aa7d5b76a564d258a',
	'f9be8bf4c0a34a6e86cccff1baaba13a',
	'96f68b654a964b5c96ffb8c2c87e0d78',
	'88e80f525ff443f38cb4816a905f77a6',
	'558937bc6aab4ec7bc7a3fb7bba34d70',
	'bfa82d0c194746e9a76fd29cd4f3c2b4',
	'f14cc688f4c84d1b8682c82d7259b937',
	'6c99332a20344fb9841c650c7edcd82e',
	'3105e29859e849b3b3db16a5c317c91d',
	'5a2c03e0e10d4458b3afa12f29d424c6',
	'1ee7a45b7fff4d218d9100cbd6ded29a',
	'76069d77aece4655b347743e562e25d7',
	'6d591a13274a42c6b7d43e5002c1cbda',
	'bf7030f5cb014873b7fddfce10b36f7e',
	'a8753a3d98a54f34af767bdf8702c75e',
	'e0306e27d2234e6a802a9ed77c401dc1',
	'c2fe4bc752e64d48949b8c479c070d9c',
	'40c27fc5c3f8486da7ce94caecdc78ac',
	'd921e57d4e6c4569b2479b4bbf42d8f8',
	'a87c0cd7ed9143cf800c9be4f4cf2cc0',]

def estimate(i):
	if (apiCounters[i] % 5) == 0:
		if i == 'DGB' and apiCounters[i] != 0:
			apiCounters[i] -= 5
		elif i == 'GLD' and apiCounters[i] != 5:
			apiCounters[i] -= 5
		elif i == 'CNC' and apiCounters[i] != 10:
			apiCounters[i] -= 5
		elif i == 'NVC' and apiCounters[i] != 15:
			apiCounters[i] -= 5
		elif i == 'GAME' and apiCounters[i] != 20:
			apiCounters[i] -= 5
		elif i == 'PPC' and apiCounters[i] != 25:
			apiCounters[i] -= 5
		elif i == 'BTC' and apiCounters[i] != 30:
			apiCounters[i] -= 5
		elif i == 'ZET' and apiCounters[i] != 35:
			apiCounters[i] -= 5
		elif i == 'MZC' and apiCounters[i] != 40:
			apiCounters[i] -= 5
		elif i == 'TEK' and apiCounters[i] != 45:
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
	print "***SCRYPT CURRENCIES***"
	for i in inputs_scrypt:
		print "Profitibility of " + i + " is $" + str(profitibilities[i])
		commitData(i)

	print "***SHA CURRENCIES***"
	for i in inputs_sha:
		print "Profitibility of " + i + " is $" + str(profitibilities[i])
		commitData(i)

	#Need some sort of function that broadcasts the coin to mine

	time.sleep(1800)	#Sleep for 30 minutes
