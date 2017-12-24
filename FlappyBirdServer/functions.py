# -*- coding: utf-8 -*-
def register(username, password):
	ret = u"OCCUR ERROR IN REGISTER"
	uname_list = []
	pwd_list = []
	#打开user_list.txt
	try:
		f = open('user_list.txt', 'r')
		for i in f.read().splitlines():
			uname_list.append(i.split('@')[0])
			pwd_list.append(i.split('@')[1])
		f.close()
	except Exception:
		print(u"读取user_list.txt错误")

	if username in uname_list:
		ret = u"该用户名已被注册"
	else:
		uname_list.append(username)
		pwd_list.append(password)
		try:
			f = open('user_list.txt', 'w+')
			for i in range(len(uname_list)):
				f.write(uname_list[i] + '@' + pwd_list[i] + '\n')
			f.close()
			ret = u"注册成功"
		except Exception, e:
			print(u"user_list.txt写入错误")
	#返回信息
	sendData = {"response": ret}
	return sendData

# -*- coding: utf-8 -*-
online_user = []
def login(username, password):
	ret = u"OCCUR ERROR IN LOGIN"
	uname_list = []
	pwd_list = []
	try:
		f = open('user_list.txt', 'r')
		for i in f.read().splitlines():
			uname_list.append(i.split('@')[0])
			pwd_list.append(i.split('@')[1])
		f.close()
	except Exception:
		print(u"读取user_list.txt错误")

	if username not in uname_list:
		ret = u"该用户名不存在"
	else :
		for i in range(len(uname_list)):
			if uname_list[i] == username:
				ret = "登录成功" if pwd_list[i] == password else "登录失败 密码错误"
				break
	sendData = {"response": ret}
	return sendData

def save_score(score, time, username, gametype):
	uname_list = []
	score_list = []
	time_list = []
	try:
		data = open(gametype + '_score.txt', 'r')
		for i in data.read().splitlines():
			uname_list.append(i.split('@')[0])
			score_list.append(i.split('@')[1])
			time_list.append(i.split('@')[2])
		data.close()
	except Exception, e:
		uname_list = []
		score_list = []
		time_list = []
	while len(uname_list) < 3:
		uname_list.append(" ")
	while len(score_list) < 3:
		score_list.append("0")
	while len(time_list) < 3:
		time_list.append("0")
	if score > int(score_list[0].encode("utf-8")):
		if time > float(time_list[0].encode("utf-8")):
			score_list[2], score_list[1], score_list[0] = score_list[1], score_list[0], str(score)
			uname_list[2], uname_list[1], uname_list[0] = uname_list[1], uname_list[0], username
			time_list[2], time_list[1], time_list[0] = time_list[1], time_list[0], str(time)
	elif score > int(score_list[1].encode("utf-8")):
		if time > float(time_list[1].encode("utf-8")):
			score_list[2], score_list[1] = score_list[1], str(score)
			uname_list[2], uname_list[1] = uname_list[1], username
			time_list[2], time_list[1] = time_list[1], str(time)
	elif score > int(score_list[2].encode("utf-8")):
		if time > float(time_list[2].encode("utf-8")):
			score_list[2] = str(score)
			uname_list[2] = username
			score_list[2] = str(time)
	try:
		data = open(gametype + '_score.txt', 'w+')
		for i in range(0, 3):
			data.write(uname_list[i] + "@" + str(score_list[i]) + "@" + str(time_list[i]) + '\n')
		data.close()
	except Exception, e:
		print("score.txt写入错误")

def get_score(gametype):
	uname_list = []
	score_list = []
	time_list = []

	try:
		data = open(gametype + '_score.txt', 'r')
		for i in data.read().splitlines():
			uname_list.append(i.split('@')[0])
			score_list.append(i.split('@')[1])
			time_list.append(i.split('@')[2])
		data.close()
	except Exception, e:
		uname_list = []
		score_list = []
		time_list = []
	while len(uname_list) < 3:
		uname_list.append(" ")
	while len(score_list) < 3:
		score_list.append("0")
	while len(time_list) < 3:
		time_list.append("0")
	return uname_list, score_list, time_list