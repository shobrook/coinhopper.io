import json
import urllib
import multiprocessing

#ALTERBNATE_url = "https://api.bitcoinaverage.com/ticker/global/USD/"

def getInfo(cur):
	CUR = cur.upper()
	url = "http://" + cur + ".blockr.io/api/v1/exchangerate/current"
	print "Fetching " + CUR + " data..."
	response = urllib.urlopen(url)

	try:
		data = json.loads(response.read())
	except ValueError:
		print "Error recieving " +  CUR + " info from server"
		raise SystemExit

	data_dictionary = {cur: float(data[u'data'][0][u'rates'][unicode(CUR,"utf-8")])}
	info_queue.put(data_dictionary)


if __name__ == '__main__':
	info_queue = multiprocessing.Queue()
	currencies = ['btc', 'ltc', 'dgc', 'ppc', 'qrk', 'mec']

	processes = []
	for coin in currencies:
		process = multiprocessing.Process(target=getInfo, args=(coin,))
		process.start()
		processes.append(process)

	for process in processes:
		process.join()

	exchange_rates_cur_per_usd = {}
	exchange_rates_usd_per_cur = {}
	while not info_queue.empty():
		exchange_rates_cur_per_usd.update(info_queue.get())

	for coin in exchange_rates_cur_per_usd:
		exchange_rates_usd_per_cur[coin] = 1/exchange_rates_cur_per_usd[coin]

	print "$1 per ___ cryptocurrency: ";	print exchange_rates_cur_per_usd
	print "\n1 cryptocurrency per $___: ";	print exchange_rates_usd_per_cur