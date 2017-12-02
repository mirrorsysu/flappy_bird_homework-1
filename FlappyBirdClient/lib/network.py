# -*- coding: utf-8 -*-
import socket, netstream
connected = False
sock = None

serialID = 0            #server向客户端发回的序列ID号
isSet = False

def connect(gameScene):
    global connected, sock
    if connected:
        return connected
    #connect server
    host = "127.0.0.1"
    port = 9234
    sock = socket.socket()
    try: 
    	sock.connect((host, port))
    except:
    	connected = False
    	return connected
    
    connected = True

    #始终接收服务端消息
    def receiveServer(dt):
    	global connected, serialID
        if not connected:
            return
        data = netstream.read(sock)
        if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
            return
        
        #客户端SID
        if 'sid' in data:
            serialID = data['sid']

        if 'notice_content' in data:
            import game_controller
            game_controller.showContent(data['notice_content']) #showContent is from game_controller

    gameScene.schedule(receiveServer)
    return connected

def get_send_data():
    send_data = {}
    send_data['sid'] = serialID
    return send_data

#向server请求公告
def request_notice():
    send_data = get_send_data()
    send_data['notice'] = 'request notice'
<<<<<<< HEAD
    netstream.send(sock, send_data)

def post_score(score):
    send_data = get_send_data()
    send_data['score'] = score
=======
>>>>>>> 5e8ee10ea1c78d5c16c2c6ffe0c926a3e3b8d6e8
    netstream.send(sock, send_data)