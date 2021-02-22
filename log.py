#-*- coding: utf-8 -*-
import syslog

syslog.openlog('auto_daily_health_report')

def log(msg, status=None):
	msg = str(msg)
	if status == True:
		msg = '[Successful] ' + msg
	if status == False:
		msg = '[Failed] ' + msg
	print(msg)
	syslog.syslog(msg)