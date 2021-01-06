import requests
import json
import re
import js2py
import time
import syslog

#disable the warnings
import urllib3
urllib3.disable_warnings()

class AutoReport:
	def __init__(self, username, raw_password, location='中国江苏省南京市栖霞区仙林大道'):
		syslog.openlog('auto_daily_health_report')
		
		self.username = username
		self.raw_password = raw_password
		self.location = location
		self.get_list_url = 'https://authserver.nju.edu.cn/authserver/login?service=http%3A%2F%2Fehallapp.nju.edu.cn%2Fxgfw%2Fsys%2Fyqfxmrjkdkappnju%2Fapply%2FgetApplyInfoList.do'
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		}
		self.login_data = {
			'username': username,
			'password': '',
			'lt': '',
			'dllt': 'userNamePasswordLogin',
			'execution': '',
			'_eventId': 'submit',
			'rmShown': 1
		}
		self.cookies = requests.utils.cookiejar_from_dict({})

	def log(self, msg, status=None):
		msg = str(msg)
		if status == True:
			msg = '[Successful] ' + msg
		if status == False:
			msg = '[Failed] ' + msg
		print(msg)
		syslog.syslog(msg)

	#update cookies from new response
	def update_cookies(self, response):
		cookies = self.cookies.get_dict()
		cookies.update(response.cookies.get_dict())
		self.cookies = requests.utils.cookiejar_from_dict(cookies)

	def prepare_login_data(self):
		get_list_res = requests.get(self.get_list_url, headers=self.headers)
		text = get_list_res.text
		self.update_cookies(get_list_res)

		#resolve data
		try:
			lt = re.search('(?<=name=\"lt\"\svalue=\").*(?=\")', text).group()
			execution = re.search('(?<=name=\"execution\"\svalue=\").*(?=\")', text).group()
			salt = re.search('(?<=pwdDefaultEncryptSalt\s=\s\").*(?=\")', text).group()
		except:
			return (False, 'parse data error')

		password = self.encrypt(self.raw_password, salt)

		self.login_data.update({
			'password': password,
			'lt': lt,
			'execution': execution
		})
		if password and execution and lt:
			return (True, 'Data prepared successfully')
		else:
			return (False, 'Data preparation failed')		

	def encrypt(self, raw_password, salt):
		#resolve the encrypt environment
		js_url = 'https://authserver.nju.edu.cn/authserver/custom/js/encrypt.js'
		encryptJS = requests.get(js_url).text
		context = js2py.EvalJs()
		context.execute(encryptJS)
		password = context.encryptAES(raw_password, salt)
		return password

	def login(self):
		login_res = requests.post(self.get_list_url, headers=self.headers, data=self.login_data, allow_redirects=False, cookies=self.cookies)
		#update cookies
		self.update_cookies(login_res)

		if 'location' in login_res.headers and 'ticket' in login_res.headers['location']:
			get_ticket_url = login_res.headers['location']
			get_ticket_res = requests.get(get_ticket_url, headers=self.headers, cookies=self.cookies, allow_redirects=False)
			self.update_cookies(get_ticket_res)
			self.get_list_url = get_ticket_res.headers['location']

			if 'location' in get_ticket_res.headers:
				return (True, 'Login successfully')

		return(False, 'Login failed with unknown reason, (maybe password error)')

	def get_list(self):
		get_list_res = requests.get(self.get_list_url, headers=self.headers, cookies=self.cookies)
		self.update_cookies(get_list_res)
		try:
			self.report_list = json.loads(get_list_res.text)['data']
		except:
			return(False, 'Get report list failed')

		return (True, 'Get report list successfully')

	def report(self):
		WID = self.report_list[0]['WID']
		report_url = 'https://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?WID={}&CURR_LOCATION={}&IS_TWZC=1&IS_HAS_JKQK=1&JRSKMYS=1&JZRJRSKMYS=1'.format(WID, self.location)
		report_res = requests.get(report_url, headers=self.headers, cookies=self.cookies, verify=False, allow_redirects=False)
		try:
			res = json.loads(report_res.text)
			self.get_list()
			if self.report_list[0]['TBZT'] == '1':
				return (True, 'Report successfully')
		except:
			pass

		return (False, 'Report failed')

	def main(self):
		status, msg = self.prepare_login_data()
		self.log(msg, status=status)
		if status:
			status, msg = self.login()
			self.log(msg, status=status)
			if status:
				status, msg = self.get_list()
				self.log(msg, status=status)
				if status:
					status, msg = self.report()
					self.log(msg, status=status)
					return status, msg