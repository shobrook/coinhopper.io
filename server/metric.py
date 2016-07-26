from joblib import Parallel, delayed
from pymongo import MongoClient
from base64 import b64decode
from sys import argv
import smtplib
import datetime
import os
import urllib2
import simplejson
import multiprocessing
import time
import math
import timeit

############################GLOBALS############################
inputs = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME', 'PPC', 'BTC', 'ZET', 'MZC', 'TEK']
inputs_scrypt = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME']
inputs_sha = ['PPC', 'BTC', 'ZET', 'MZC', 'TEK']
expcoin_historical = []

hashrates = {'DGB' : 0.002, 'GLD' : 0.002, 'CNC' : 0.002, 'NVC' : 0.002, 'GAME' : 0.002, 'PPC' : 1.4, 'BTC' : 1.4, 'ZET' : 1.4, 'MZC' : 1.4, 'TEK' : 1.4}
exchange_rates_q = multiprocessing.Queue()
block_rewards_q = multiprocessing.Queue()
difficulties_q = multiprocessing.Queue()

metrics = dict.fromkeys(inputs, 0)
volatilities = dict.fromkeys(inputs_scrypt, 0)

apiCounters = {'DGB' : 0, 'GLD' : 5, 'CNC' : 10, 'NVC' : 15, 'GAME' : 20, 'PPC' : 25, 'BTC' : 30, 'ZET' : 35, 'MZC' : 40, 'TEK' : 45}
apikeys = ['c38655b51d9f4f44a48ea0e6eaead00e',
	'c32104fcbf4042298fcaccfc73469bc2',
	'3a89841177af4a369cab3f2182e7715b',
	'05e1e4da564b4f12b82360d438eb1c6b',
	'd959ed79ef54467293952d882d4e37a4',
	'9b6f4fdc67444fce8144dee922046259',
	'b2f42e6ad3504b7cbaf27caa6863fe02',
	'de3a314e61be468f8e877d57b4f189d4',
	'b45a5549a28d4cc983f272e09775bdba',
	'e8cdaadba7204900bcb263dfb758243b',
	'21e4ad8d24c24528b805715bfe3650c4',
	'3cac67f5035f46d5acd81213f09f6f57',
	'6d7121712f0c47ec8d6816c4691e0d5d',
	'6983b8c7d888438bb6a7fd0864267734',
	'a18e92fa6990459f9cb46921d559d2e2',
	'460b21f06f224e60af8ccadc093329cd',
	'90b6f192659646b3939476b1c9dd7a4b',
	'f5817103d6a6495a9049654b5a986d23',
	'573d632f2c954f1bb06728c1013222dd',
	'4bbc9a2bc912493bb269a381cb2af2d2',
	'0a49f8e2d774455ead345f1a62fcc3fb',
	'5c8228f9786d43d195a927a4ff26b403',
	'62c2f90cd7bb4d7c8f6e668d4ee9582b',
	'f9e5ac48975b423c881158fa0cb143cf',
	'd8af95ac41f6492f8b8a4bdb540708d0',
	'd92aeb4cc52442ee8b6ae73663efe9b1',
	'071d1142349347a8bbb73b0b6ee5ff53',
	'e2ae7800f92446caa26375791c94f1ca',
	'a06e3c143a854f0184f1874bed9ce974',
	'eaacc9bbcafd4bda884c0da3fa9d2d00',
	'e93e12d057284ff39dfb84291fc4e104',
	'8778dd8759694873966a2034e73b0a04',
	'e9f7bce88e7e4e20ac90cdfa70ca45b9',
	'c4e5f827c23247e895543b5a475421ed',
	'33d6e8d4de0d4df5bb8c237b1564981e',
	'ae3704905bd840e288c248ae9a063713',
	'69063c7e2d2c4cbc9711e8ce2196c338',
	'e9ed6ea8e212438f9677e39b70b495cb',
	'343e39304569423b910e8d258901b5e2',
	'b9e140e52a974c429e2d4c35bf2e7a87',
	'a86f65496eb049b4a0d2299ab45c59e3',
	'ccf52127d4894fa4a7de4b6bac21d205',
	'418da6f76f7d4926bc859234bf7bded2',
	'279bbf8fb99f4b62ba16a26c9de1166d',
	'981670b01ccc4630a63631f35acdf6ff',
	'b635922825d445cd9ab391693ce2dfaa',
	'82809b7bf41f440da55e1274446b066c',
	'4bdf3c604ccf4e77a919491d58faaecb',
	'15372b9141f54643b0740ec57f24f141',
	'ee55a6712bb04996af0935d2b84eb7f0']

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
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 6)
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
	client = MongoClient()
	db = client.coinhopper
	for document in db[scrypt].find().skip(db[scrypt].count() - 2):
		expcoin_historical.append(document.get('daily_profit'))
	expcoin_historical.reverse()
	print('Calculating expected profit volatility for... ' + scrypt)
	var = variance(expcoin_historical)
	volatility = math.sqrt(average(var))
	uncertainty = round((expcoin_historical[0] * volatility), 6)
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
	print 'Inserted document with ID: ' + str(result.inserted_id) + ' into DB:coinhopper Collection: ' + i

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
	print 'Inserted document with ID: ' + str(result.inserted_id) + ' into DB:coinhopper Collection: ' + i

##############################MAIN#############################
while True:
	#try:
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

	client = MongoClient()
	db = client.coinhopper

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
"""
	except KeyboardInterrupt:
		quit()

	except:
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.ehlo()
		server.starttls()
		server.ehlo()

		server.login(b64decode('Y29pbmhvcHBlci5pbw=='),b64decode('ZGFua21lbWVz'))

		msg = 'Subject: %s\n\n%s' % ('The server is down!', 'Oh fuckedy shit! The server has been down since: '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+' PST')
		server.sendmail(b64decode('Y29pbmhvcHBlci5pb0BnbWFpbC5jb20='), [b64decode('YmxvYnozMTVAZ21haWwuY29t'),b64decode('c2hvYnJvb2tqQGdtYWlsLmNvbQ==')], msg)

		quit()
		"""