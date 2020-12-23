import requests
import json
import re
import js2py
import time
import syslog
from fire import Fire

#disable the warnings
import urllib3
urllib3.disable_warnings()

syslog.openlog('auto_daily_health_report')

#update cookies for new response
def update_cookies(cookies, response):
	for key in response.cookies.get_dict():
		cookies[key] = response.cookies[key]
	return cookies

#dump cookies
def dump_cookies(cookies):
	return requests.utils.cookiejar_from_dict(cookies)	

def log(msg):
	msg = str(msg)
	print(msg)
	syslog.syslog(msg)

def main(username='', password='', file=''):
	#load username and password
	if file:
		with open(file, 'r') as f:
			username, raw_password = f.read().strip().split(':')
	else:
		username = username
		raw_password = password

	while True:
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
		}

		#get cookie
		get_list_url = 'https://authserver.nju.edu.cn/authserver/login?service=http%3A%2F%2Fehallapp.nju.edu.cn%2Fxgfw%2Fsys%2Fyqfxmrjkdkappnju%2Fapply%2FgetApplyInfoList.do'
		get_list_res = requests.get(get_list_url, headers=headers)
		text = get_list_res.text

		#resolve data
		try:
			lt = re.search('(?<=name=\"lt\"\svalue=\").*(?=\")', text).group()
			execution = re.search('(?<=name=\"execution\"\svalue=\").*(?=\")', text).group()
			salt = re.search('(?<=pwdDefaultEncryptSalt\s=\s\").*(?=\")', text).group()
		except:
			log('parse data error')
			exit()

		#prepare headers
		cookies = get_list_res.cookies.get_dict()

		#resolve the encrypt environment
		js_url = 'https://authserver.nju.edu.cn/authserver/custom/js/encrypt.js'
		encryptJS = requests.get(js_url).text
		context = js2py.EvalJs()
		context.execute(encryptJS)
		password = context.encryptAES(raw_password, salt)

		#prepare data
		data = {
			'username': username,
			'password': password,
			'lt': lt,
			'dllt': 'userNamePasswordLogin',
			'execution': execution,
			'_eventId': 'submit',
			'rmShown': 1

		}

		if username and password and lt and execution:
			log('Data prepared successfully')
		else:
			log('Data prepared failed')
	
		#request for the ticket
		req_cookies = dump_cookies(cookies)
		#post_res = requests.post(get_list_url, headers=headers, data=data, allow_redirects=False, cookies=req_cookies)
		post_res = requests.post(get_list_url, headers=headers, data=data, allow_redirects=False, cookies=req_cookies)

		#update cookies
		cookies = update_cookies(cookies, post_res)

		if 'location' in post_res.headers:
			if 'ticket' in post_res.headers['location']:
				log('Login successfully')
			else:
				log('Get ticket failed, maybe login failed.')
				continue

			#ticket obtained then ask for new cookie
			get_cookies_url = post_res.headers['location']

			req_cookies = dump_cookies(cookies)
			get_cookies_res = requests.get(get_cookies_url, headers=headers, cookies=req_cookies, allow_redirects=False)
			
			#update cookies
			cookies = update_cookies(cookies, get_cookies_res)

			if 'location' in get_cookies_res.headers:
				log('Authenticate ticket successfully')
				get_list_url = get_cookies_res.headers['location']
				req_cookies = dump_cookies(cookies)
				get_list_res = requests.get(get_list_url, headers=headers, cookies=req_cookies)

				#update cookies
				cookies = update_cookies(cookies, get_list_res)
			#apply ticket failed
			else:
				log('Authenticate ticket failed')
				#continue
		else:
			log('login failed with unknown reason')
			time.sleep(1)
			continue

		#whether json obtained
		try:
			report_list = json.loads(get_list_res.text)['data']
			log('Get list data successfully')
			break
		except:
			#delay to avoid requesting too frequently
			log('Get list data failed')
			time.sleep(3)
			continue

	#report the newest item
	WID = report_list[0]['WID']
	report_url = 'https://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?WID={}&CURR_LOCATION=中国江苏省南京市栖霞区仙林大道&IS_TWZC=1&IS_HAS_JKQK=1&JRSKMYS=1&JZRJRSKMYS=1'.format(WID)
	req_cookies = dump_cookies(cookies)
	log(requests.get(report_url, headers=headers, cookies=req_cookies, verify=False, allow_redirects=False).text)


if __name__ == '__main__':
	Fire(main)