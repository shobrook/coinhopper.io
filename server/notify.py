import smtplib
import os
import datetime
from base64 import b64decode
from time import sleep
from sys import argv

def sendErrorMessage():
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.ehlo()

	server.login(b64decode('Y29pbmhvcHBlci5pbw=='),b64decode('ZGFua21lbWVz'))

	msg = 'Subject: %s\n\n%s' % ('The server is down!', 'Oh fuckedy shit! The server has been down since: '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+' PST')
	server.sendmail(b64decode('Y29pbmhvcHBlci5pb0BnbWFpbC5jb20='), [b64decode('YmxvYnozMTVAZ21haWwuY29t'),b64decode('c2hvYnJvb2tqQGdtYWlsLmNvbQ==')], msg)

if len(argv) != 2:
	print 'Error, invalid arguments'
	quit()

pid = int(argv[1])
while True:
	try:
		os.kill(pid, 0)
	except OSError:
		sendErrorMessage()
		quit()
	sleep(900)