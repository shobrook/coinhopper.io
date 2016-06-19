from pymongo import MongoClient

client = MongoClient("mongodb://ec2-54-191-245-35.us-west-2.compute.amazonaws.com:27017")
db = client['miner_io']
coll = db['FRK']
cursor = coll.find()
for doc in cursor:
	print doc