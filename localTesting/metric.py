# expcoin = 86400 * [devhash / (4294.97 * (tlambda * nethash))] * (exrate * rlambda)

from joblib import Parallel, delayed
from pymongo import MongoClient
import urllib2
import simplejson
import multiprocessing
import time
import math

inputs = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME', 'PPC', 'BTC', 'ZET', 'MZC', 'TEK']

inputs_scrypt = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME']
inputs_sha = ['PPC', 'BTC', 'ZET', 'MZC', 'TEK']

metrics = dict.fromkeys(inputs, 0)
volatilities = dict.fromkeys(inputs_scrypt, 0)

hashrates = {'DGB' : 100, 'GLD' : 100, 'CNC' : 100, 'NVC' : 100, 'GAME' : 100, 'PPC' : 100, 'BTC' : 100, 'ZET' : 100, 'MZC' : 100, 'TEK' : 100}

apikey = 'b416fadbb64a4a3eb51a2ec5db49c1da'

def estimate(i):
	devhash = hashrates[i]
	print 'Calculating expected daily profit (in USD) for... ' + i
	rlambda = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('BlockReward')
	# diff = [tlambda * nethash] / 4294.97 --> Scaled to 1 MH/sec
	diff = (simplejson.load(urllib2.urlopen('http://www.coinwarz.com/v1/api/coininformation/?apikey=' + apikey + '&cointag=' + i))).get('Data').get('Difficulty')
	exrate = float((simplejson.load(urllib2.urlopen('http://www.cryptonator.com/api/ticker/' + i + '-usd'))).get('ticker').get('price'))
	expcoin = round((86400*(devhash/(4294.97*diff))*(exrate*rlambda)), 2)
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
	for document in cursors[scrypt]:
		expcoin_historical.append(document.get('daily_profit'))
	expcoin_historical.reverse()
	print('Calculating expected profit volatility for... ' + scrypt)
	var = variance(expcoin_historical)
	volatility = math.sqrt(average(var))
	uncertainty = round((expcoin_historical[0] * volatility), 2)
	return uncertainty

print ''

outputs = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(estimate)(i) for i in inputs)
timestamp = int(time.time())

for x in range(len(inputs)):
	metrics[inputs[x]] = float(outputs[x])
ranked_profit = (sorted(metrics.items(), key=lambda x: x[1]))
ranked_profit.reverse()

client = MongoClient("ec2-54-191-245-35.us-west-2.compute.amazonaws.com")
db = client.miner_io
expcoin_historical = []
cursors = {'DGB': db.DGB.find().skip(db.DGB.count() - 2), 'GLD': db.GLD.find().skip(db.GLD.count() - 2), 'CNC': db.CNC.find().skip(db.CNC.count() - 2), 'NVC': db.NVC.find().skip(db.NVC.count() - 2), 'GAME': db.GAME.find().skip(db.GAME.count() - 2)}

outputs_adj = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(calcUncert)(scrypt) for scrypt in inputs_scrypt)

for x in range(len(inputs_scrypt)):
	volatilities[inputs_scrypt[x]] = float(outputs_adj[x])

ranked_uncert = (sorted(volatilities.items(), key=lambda x: x[1]))
ranked_uncert.reverse()

print ''

print "***SHA-256 CURRENCIES***"
for x in range(len(ranked_profit)):
	if str(ranked_profit[x][0]) in inputs_sha:
		print "Profitability of " + str(ranked_profit[x][0]) + " is $" + str(ranked_profit[x][1])

print ''

print "***SCRYPT CURRENCIES***"
for x in range(len(ranked_profit)):
	if str(ranked_profit[x][0]) in inputs_scrypt:
		print "Profitability of " + str(ranked_profit[x][0]) + " is $" + str(ranked_profit[x][1]) + " +/- " + str(ranked_uncert[x][1])