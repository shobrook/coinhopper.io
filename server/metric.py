from joblib import Parallel, delayed
from pymongo import MongoClient
import urllib2
import simplejson
import multiprocessing
import time
import math
import timeit

client = MongoClient()
db = client.miner_io

############################GLOBALS############################
inputs = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME', 'PPC', 'BTC', 'ZET', 'MZC', 'TEK']
inputs_scrypt = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME']
inputs_sha = ['PPC', 'BTC', 'ZET', 'MZC', 'TEK']
expcoin_historical = []

hashrates = {'DGB' : 100, 'GLD' : 100, 'CNC' : 100, 'NVC' : 100, 'GAME' : 100, 'PPC' : 100, 'BTC' : 100, 'ZET' : 100, 'MZC' : 100, 'TEK' : 100}
exchange_rates_q = multiprocessing.Queue()
block_rewards_q = multiprocessing.Queue()
difficulties_q = multiprocessing.Queue()

metrics = dict.fromkeys(inputs, 0)
volatilities = dict.fromkeys(inputs_scrypt, 0)

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
	'b5e248c9640843ce9e4a82f677c81ee8',
	'8e0383fc5d25440496d7bd35c97ec8d0',
	'ed1dcfee670b4c0f96d45ec6a166f0d1',
	'9a1805fa5f5640df8239f6e3fc58a721',
	'3f165243e5954c04920f41f8ed71e2eb',
	'7d1000b6ca304353bcadc3d3396b2be4',
	'1eb61ba3976847faaeba6de118524000',
	'f3d6df1e3ee14ca1994c4fc5b73d87c2',
	'1eb8aace7c99478dadf8ec5582dcdc77',
	'ac3c3abd06fb465f9cade5e58172bed1',
	'18b90175f430451f850e838d5a1dee01',
	'7b95a0e6661b43acb4180d0631e9f424',
	'2dafc495462d4f6ba25748a96d3e7829',
	'2526820e7f974890a4dad5b1b3fbbe5b',
	'4a75e695fcd34046bb919e8f84aebf6e',
	'3b32884368514179accaec6c54637a5b',
	'9d53cf609d244c3099ffee52bf0d508b',
	'c4d2517baec34c5da2b1c489c0ce7835',
	'6481f6e98263406091fa58864e9872cb',
	'03f8bb8be9a94a3888482077f2fb8b62',
	'cba7de5a43cf43aea5e69e531dc9c5c4',]

###########################FUNCTIONS###########################
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
	difficulties_q.put([i, diff])
	exchange_rates_q.put([i, exrate])
	block_rewards_q.put([i, rlambda])
	return expcoin

def average(x):
	return sum(x) / len(x)

def delta(tuples):
	return [(v / tuples[abs(i - 1)]) - 1 for i, v in enumerate(tuples)]

def variance(tuples):
	perc = delta(tuples)
	avg = average(perc)
	return [(x - avg)**2 for x in perc]

def calcUncert(scrypt):
	client = MongoClient("ec2-54-191-245-35.us-west-2.compute.amazonaws.com")
	db = client.miner_io
	for document in db[scrypt].find().skip(db[scrypt].count() - 2):
		expcoin_historical.append(document.get('daily_profit'))
	expcoin_historical.reverse()
	print('Calculating expected profit volatility for... ' + scrypt)
	var = variance(expcoin_historical)
	volatility = math.sqrt(average(var))
	uncertainty = round((expcoin_historical[0] * volatility), 2)
	return uncertainty

def commitDataScrypt(i):
	result = db[i].insert_one(
		{
			'timestamp' : timestamp,				#UNIX timestamp for data data was collected
			'daily_profit' : profitibilities[i],	#Profitibility calculated in USD
    		'hash_rate' : hashrates[i],				#Hash rate for the given currency
    		'exchange_rate' : exchange_rates[i],	#Exchange rate for the given currency in USD
    		'block_reward' : block_rewards[i],		#Block reward for the given currency
    		'difficulty' : difficulties[i],			#Difficulty for the given currency
    		'uncertainty' : uncertainties[i]		#Uncertainty for the given currency
		}
	)
	print 'Inserted document with ID: ' + str(result.inserted_id) + ' into DB:miner_io Collection: ' + i

def commitDataSHA(i):
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

##############################MAIN#############################
while True:
	start = timeit.default_timer()
	timestamp = int(time.time())

	outputs = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(estimate)(i) for i in inputs)
	for x in range(len(inputs)):
		metrics[inputs[x]] = float(outputs[x])
	profitibilities = dict(sorted(metrics.items(), key=lambda x: x[1]))

	outputs_adj = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(calcUncert)(scrypt) for scrypt in inputs_scrypt)
	for x in range(len(inputs_scrypt)):
		volatilities[inputs_scrypt[x]] = float(outputs_adj[x])
	uncertainties = dict(sorted(volatilities.items(), key=lambda x: x[1]))

	exchange_rates = []
	block_rewards = []
	difficulties = []

	while not exchange_rates_q.empty():
		exchange_rates.append(exchange_rates_q.get())
		block_rewards.append(block_rewards_q.get())
		difficulties.append(difficulties_q.get())
	exchange_rates = dict(exchange_rates)
	block_rewards = dict(block_rewards)
	difficulties = dict(difficulties)

	client = MongoClient("ec2-54-191-245-35.us-west-2.compute.amazonaws.com")
	db = client.miner_io

	print "\n***SCRYPT CURRENCIES***"
	for i in inputs_scrypt:
		print "Profitibility of " + i + " is $" + str(profitibilities[i]) + " +/-" + str(uncertainties[i])
		commitDataScrypt(i)

	print "\n***SHA CURRENCIES***"
	for i in inputs_sha:
		print "Profitibility of " + i + " is $" + str(profitibilities[i])
		commitDataSHA(i)

	elapsed = timeit.default_timer() - start
	time.sleep(1800-elapsed)