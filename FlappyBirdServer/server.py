# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback
from functions import *
HOST = "127.0.0.1"
disconnected_list = []#断开连接的客户端列表
onlineUser = {}
sid = 0

if __name__ == "__main__":
	s = socket.socket()

	host = HOST
	port = 9234

	s.bind((host, port))
	s.listen(4)

	inputs = []
	inputs.append(s)
	print 'server start! listening host:', host, ' port:', port

while inputs:
	try:
		rs, ws, es = select.select(inputs, [], [])
		for r in rs:
			if r is s:
				print 'sid:', sid
				# accept
				connection, addr = s.accept()
				print 'Got connection from' + str(addr)
				inputs.append(connection)
				sendData = {}
				sendData['sid'] = sid
				netstream.send(connection, sendData)

				cInfo = {}
				cInfo['connection'] = connection
				cInfo['addr'] = str(addr)
				cInfo['ready'] = False
				onlineUser[sid] = cInfo
				print(str(onlineUser))
				sid += 1
			else:
				# receive data
				recvData = netstream.read(r)
				# print 'Read data from ' + str(r.getpeername()) + '\tdata is: ' + str(recvData)
				# socket关闭
				if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT:
					if r.getpeername() not in disconnected_list:
						print str(r.getpeername()) + 'disconnected'
						inputs.remove(r)
						onlineUser.pop(r)
				else:  # 根据收到的request发送response
					#公告
					if recvData['type'] == 'notice':
						number = recvData['sid']
						print 'receive notice request from user id:', number
						sendData = {"notice_content": "This is a notice from server. Good luck!"}
						netstream.send(onlineUser[number]['connection'], sendData)
					if recvData['type'] == 'login':
						number = recvData['sid']
						username, password = recvData['username'], recvData['password']
						sendData = login(username, password)
						netstream.send(onlineUser[number]['connection'], sendData)
						print 'receive login from user id:', number

					if recvData['type'] == 'register':
						number = recvData['sid']
						username, password = recvData['username'], recvData['password']
						sendData = register(username, password)
						netstream.send(onlineUser[number]['connection'], sendData)
						print 'receive register from user id:', number

					if recvData['type'] == 'score':
						number = recvData['sid']
						score = recvData['score']
						username = recvData['username']
						gametype = recvData['gametype']
						time = recvData['time']
						save_score(score, time, username, gametype)
						print 'receive score from user id:', number

					if recvData['type'] == 'update_score':
						number = recvData['sid']
						score = recvData['score']
						username = recvData['username']
						gametype = recvData['gametype']
						print '%s %s %s:' % (username, number, gametype)

					if recvData['type'] == 'request_score':
						number = recvData['sid']
						gametype = recvData['gametype']
						users, score, time = get_score(gametype)
						print 'receive request_score from user id:', number
						sendData = {"users": users, "score":  score, "time": time}
						netstream.send(onlineUser[number]['connection'], sendData)
	except Exception:
		traceback.print_exc()
		print 'Error: socket 链接异常'
