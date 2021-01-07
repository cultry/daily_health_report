#-*- coding: utf-8 -*-
import base64
from AutoReport import AutoReport
from fire import Fire
from mail import send
from time import sleep
from log import log

def main(username='', password='', file='', b64=False, mail_notify=False, mail_user='', mail_pass='', mail_host='smtp.exmail.qq.com'):
	#load username and password
	if file:
		with open(file, 'r') as f:
			username, raw_password = f.read().strip().split(':')
	else:
		username = username
		raw_password = password

	if b64:
		raw_password = base64.b64decode(raw_password.encode()).decode()
		mail_pass = base64.b64decode(mail_pass.encode()).decode()

	for _ in range(3):
		try:
			app = AutoReport(username, raw_password)
			status, msg = app.main()
			if status:
				break
		except e:
			log('Operation failed, retrying in 3s.', status=False)
			sleep(3)
			continue

	if status and mail_notify:
		status, msg = send(mail_user, mail_pass, mail_host)
		log(msg, status)

if __name__ == '__main__':
	Fire(main)