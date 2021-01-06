# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header
 
def send(username='', password='', host='smtp.exmail.qq.com'):
	mail_host = host
	mail_user = username
	mail_pass = password
	
	sender = username
	receivers = [username]
	 
	message = MIMEText('打卡成功提醒', 'plain', 'utf-8')
	message['From'] = Header('打卡成功提醒', 'utf-8')
	message['To'] =  Header(mail_user, 'utf-8')
	 
	subject = '打卡成功提醒邮件'
	message['Subject'] = Header(subject, 'utf-8')

	try:
	    smtpObj = smtplib.SMTP() 
	    smtpObj.connect(mail_host, 25)
	    smtpObj.login(mail_user,mail_pass)  
	    smtpObj.sendmail(sender, receivers, message.as_string())
	    return (True, '邮件发送成功')
	except smtplib.SMTPException:
	    return (False, '邮件发送失败')

if __name__ == '__main__':
	send(username='zhengqc@lamda.nju.edu.cn', password='ZqcAnnyTerfect123')