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

def getProfit(coin):
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_NAME]
	data = collection.find(projection=FIELDS)
	json_data = []
	for x in data:
		json_data.append(x)
	connection.close()
	json_data.reverse()
	return json_data[0].get('daily_profit')

def getRate(coin):
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_NAME]
	data = collection.find(projection=FIELDS)
	json_data = []
	for x in data:
		json_data.append(x)
	connection.close()
	json_data.reverse()
	return json_data[0].get('exchange_rate')

def getDifficulty(coin):
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_NAME]
	data = collection.find(projection=FIELDS)
	json_data = []
	for x in data:
		json_data.append(x)
	connection.close()
	json_data.reverse()
	return json_data[0].get('difficulty')

def getReward(coin):
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_NAME]
	data = collection.find(projection=FIELDS)
	json_data = []
	for x in data:
		json_data.append(x)
	connection.close()
	json_data.reverse()
	return json_data[0].get('block_reward')

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

if len(str(getRate(args.coin))) > len(str(getDifficulty(args.coin))):
	if len(str(getRate(args.coin))) > len(str(getReward(args.coin))):
		length = len(str(getRate(args.coin))) + len('Exchange Rate: $')
	else:
		length = len(str(getReward(args.coin))) + len('Exchange Rate: $')
else:
	if len(str(getDifficulty(args.coin))) > len(str(getReward(args.coin))):
		length = len(str(getDifficulty(args.coin))) + len('Exchange Rate: $')
	else:
		length = len(str(getReward(args.coin))) + len('Exchange Rate: $')

print('')
print(colored(currencies[args.coin] + ' (' + args.coin + ') Overview', 'white', attrs=['bold']))
print('')
print((colored('Expected Profitability:', 'red', attrs=['underline'])) + ' $' + str(getProfit(args.coin)))
print('')
print((colored('\033[42mExchange Rate:', 'grey', attrs=['underline'])) + '\033[42m $' + str(getRate(args.coin)) + (length - len('Exchange Rate: $' + str(getRate(args.coin))))*'\033[42m ' + '\033[m')
print((colored('\033[42mDifficulty:', 'grey', attrs=['underline'])) + '\033[42m ' + str(getDifficulty(args.coin)) + (length - len('Difficulty: ' + str(getDifficulty(args.coin))))*'\033[42m ' + '\033[m')
print((colored('\033[42mBlock Reward:', 'grey', attrs=['underline'])) + '\033[42m ' + str(getReward(args.coin)) + (length - len('Block Reward: ' + str(getReward(args.coin))))*'\033[42m ' + '\033[m')
print('')
#print((colored('Ranking (Scrypt):', 'red', attrs=['underline']) + ' [')

# [BTC.......NVC..GAME....PPC...............TEK] (current one highlighted)
# ************
# Your Hash Rate:
# Your Earnings: 



