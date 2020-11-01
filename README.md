# 自动每日健康打卡程序

近日对该高校的统一身份认证协议进行了解析，并开发出了基于python的自动健康打卡程序（不熟悉的用户可以使用[旧版](https://github.com/AnnyTerfect/daily_health_attendance/blob/master/README_old.md)）

## 安装

该项目依赖于一些python包，在使用前请务必保证这些包已经被正常安装

```bash
pip install -r requirements.txt
```

## 使用

### 直接传入用户名密码

在bash中执行

```bash
python main.py --username=<username> --password=<password>
```

其中上面的<code>\<username\></code>处填写用户名（学号/工号），例如DZ20000001，其中的<code>\<password\></code>处填写统一身份认证平台的密码。

### 通过文件传入密码

新建passwd.txt文件，按照以下格式填入用户名和密码

```bash
username:password
```

保存好文件后在bash中执行

```bash
python main.py --file=/path/to/passwd.txt
```

例如在当前目录下

```bash
python main.py --file=./passwd.txt
```

### 添加任务计划

#### linux

在linux平台下，可以编辑<code>/etc/crontab</code>文件，并添加行

```bash
0 12 * * * <user> /path/to/your/python /path/to/main.py --file=/path/to/passwd.txt
```

#### 其他平台

（待更新）

## 承诺&&免责声明

### 请放心使用

该程序**不会访问**除了校园网以外的所有资源，**不会收集**任何与用户账号相关的信息，请各位用户放心使用，不放心的用户可以自行阅读程序源码。

### 免责声明

该程序仅为大家提供便利，如果因故离校或者出现任何健康状况请如实上报，因使用该程序导致的后果作者概不负责。
