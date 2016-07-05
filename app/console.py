import sys
import json
import argparse
from termcolor import colored, cprint
from pymongo import MongoClient

##############################GLOBALS#############################

parser = argparse.ArgumentParser()
parser.add_argument("coin")
args = parser.parse_args()

currencies = {'DGB': 'Digibyte', 'GLD': 'GoldCoin', 'CNC': 'CHNCoin', 'NVC': 'Novacoin', 'GAME': 'GameCoin', 'PPC': 'Peercoin', 'BTC': 'Bitcoin', 'ZET': 'Zetacoin', 'MZC': 'Mazacoin', 'TEK': 'Tekcoin'}
currencies_scrypt = ['DGB', 'GLD', 'CNC', 'NVC', 'GAME']
currencies_sha = ['PPC', 'BTC', 'ZET', 'MZC', 'TEK']

MONGODB_HOST = 'ec2-54-191-245-35.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
DBS_NAME = 'miner_io'
COLLECTION_NAME = args.coin
FIELDS = {'_id': False, 'block_reward': True, 'daily_profit': True, 'difficulty': True, 'exchange_rate': True, 'hash_rate': True, 'timestamp': True, 'uncertainty': True}

##############################FUNCTIONS#############################

def getRecords(coin):
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][coin]
	data = collection.find(projection=FIELDS)
	json_data = []
	for x in data:
		json_data.append(x)
	connection.close()
	json_data.reverse()
	return json_data[0]

def getProfit():
	return getRecords(COLLECTION_NAME).get('daily_profit')

def getUncertainty():
	return getRecords(COLLECTION_NAME).get('uncertainty')

def getRate():
	return getRecords(COLLECTION_NAME).get('exchange_rate')

def getDifficulty():
	return getRecords(COLLECTION_NAME).get('difficulty')

def getReward():
	return getRecords(COLLECTION_NAME).get('block_reward')

def getRanking():
	json_data = dict.fromkeys(currencies_scrypt, 0)
	ranked = []
	for coins in currencies_scrypt:
		json_data[coins] = getRecords(coins).get('daily_profit')
	ranked = sorted(json_data, key=json_data.__getitem__, reverse=True)
	return ranked

##############################CLASSES#############################

class attributes:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   WHITE = '\033[0;37'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

##############################MAIN#############################

if len(str(getRate())) > len(str(getDifficulty())):
	if len(str(getRate())) > len(str(getReward())):
		length = len(str(getRate())) + len('Exchange Rate: $')
	else:
		length = len(str(getReward())) + len('Exchange Rate: $')
else:
	if len(str(getDifficulty())) > len(str(getReward())):
		length = len(str(getDifficulty())) + len('Exchange Rate: $')
	else:
		length = len(str(getReward())) + len('Exchange Rate: $')

#if length < len('Expected Profitability: $' + str(getProfit()) + ' +/- ' + str(getUncertainty())):
#	length = len('Expected Profitability: $' + str(getProfit()) + ' +/- ' + str(getUncertainty()))

print('')
print(colored(currencies[args.coin] + ' (' + args.coin + ') Overview', 'white', attrs=['bold']))
print('')
print((colored('Expected Profitability:', 'red', attrs=['underline'])) + ' $' + str(getProfit()) + ' +/- ' + str(getUncertainty()))
print('')
print((colored('\033[42mExchange Rate:', 'grey', attrs=['underline'])) + '\033[42m $' + str(getRate()) + (length - len('Exchange Rate: $' + str(getRate())))*'\033[42m ' + '\033[m')
print((colored('\033[42mDifficulty:', 'grey', attrs=['underline'])) + '\033[42m ' + str(getDifficulty()) + (length - len('Difficulty: ' + str(getDifficulty())))*'\033[42m ' + '\033[m')
print((colored('\033[42mBlock Reward:', 'grey', attrs=['underline'])) + '\033[42m ' + str(getReward()) + (length - len('Block Reward: ' + str(getReward())))*'\033[42m ' + '\033[m')
print('')
print((colored('Ranking (Scrypt):', 'red', attrs=['underline']) + ' ' + str(getRanking()))) #[BTC.......NVC..GAME....PPC...............TEK] (current one highlighted)
print('')
print(length * (attributes.BOLD + '*' + attributes.END))
print('')
print((colored('\033[46mYour Hash Rate:', 'grey', attrs=['underline'])) + '\033[46m 100 MH/s' + (length - len('Your Hash Rate: 100 MH/s'))*'\033[46m ' + '\033[m')
print((colored('\033[46mYour Earnings:', 'grey', attrs=['underline'])) + '\033[46m $24.91' + (length - len('Your Earnings: $24.91'))*'\033[46m ' + '\033[m')
print('')