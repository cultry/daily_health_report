import requests
import json
import re
import js2py
import time
from fire import Fire

#disable the warnings
import urllib3
urllib3.disable_warnings()

#update cookies for new response
def update_cookies(cookies, response):
	for key in response.cookies.get_dict():
		cookies[key] = response.cookies[key]
	return cookies

#dump cookies
def dump_cookies(cookies):
	return requests.utils.cookiejar_from_dict(cookies)

def main(username='', password='', file=''):
	#load username and password
	if file:
		with open(file, 'r') as f:
			username, raw_password = f.read().strip().split(':')
	else:
		username = username
		raw_password = password


	#get cookie
	get_list_url = 'http://authserver.nju.edu.cn/authserver/login?service=http%3A%2F%2Fehallapp.nju.edu.cn%2Fxgfw%2Fsys%2Fyqfxmrjkdkappnju%2Fapply%2FgetApplyInfoList.do'
	get_list_res = requests.get(get_list_url)
	text = get_list_res.text

	#resolve lt
	try:
		lt = re.search('(?<=name=\"lt\"\svalue=\").*(?=\")', text).group()
	except:
		print('get <lt> value failed')
		exit()

	#resolve execution
	try:
		execution = re.search('(?<=name=\"execution\"\svalue=\").*(?=\")', text).group()
	except:
		print('get <execution> value failed')
		exit()

	#resolve encrypt salt
	try:
		salt = re.search('(?<=pwdDefaultEncryptSalt\s=\s\").*(?=\")', text).group()
	except:
		print('get <salt> value failed')
		exit()

	#prepare headers
	cookies = get_list_res.cookies.get_dict()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
	}

	#resolve the encrypt environment
	js_url = 'http://authserver.nju.edu.cn/authserver/custom/js/encrypt.js'
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

	#continuously request the reports list
	while True:
		#request for the ticket
		req_cookies = dump_cookies(cookies)
		post_res = requests.post(get_list_url, headers=headers, data=data, allow_redirects=False, cookies=req_cookies)

		#update cookies
		cookies = update_cookies(cookies, post_res)

		if 'location' in post_res.headers:
			#ticket obtained then ask for new cookie
			get_cookies_url = post_res.headers['location']

			req_cookies = dump_cookies(cookies)
			get_cookies_res = requests.get(get_cookies_url, headers=headers, cookies=req_cookies, allow_redirects=False)
			
			#update cookies
			cookies = update_cookies(cookies, get_cookies_res)

			if 'location' in get_cookies_res.headers:
				get_list_url = get_cookies_res.headers['location']
				req_cookies = dump_cookies(cookies)
				get_list_res = requests.get(get_list_url, headers=headers, cookies=req_cookies)

				#update cookies
				cookies = update_cookies(cookies, get_list_res)
			#apply ticket failed
			else:
				continue
		else:
			continue

		#whether json obtained
		try:
			report_list = json.loads(get_list_res.text)['data']
			break
		except:
			#delay to avoid requesting too frequently
			time.sleep(3)
			continue
	
	#report the newest item
	WID = report_list[0]['WID']
	report_url = 'https://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?WID={}&CURR_LOCATION=中国江苏省南京市栖霞区仙林大道&IS_TWZC=1&IS_HAS_JKQK=1&JRSKMYS=1&JZRJRSKMYS=1'.format(WID)
	req_cookies = dump_cookies(cookies)
	print(requests.get(report_url, headers=headers, cookies=req_cookies, verify=False, allow_redirects=False).text)

if __name__ == '__main__':
	Fire(main)