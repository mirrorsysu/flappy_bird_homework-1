# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *  
from cocos.text  import *
from cocos.menu import *
import random
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from network import *
import common
import time
#vars
gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
ipTextField = None
errorLabel = None
isGamseStart = False
g_username = "username"
isOnline = 0
Rank1Scores = {}
Rank2Scores = {}
Rank3Scores = {}
Rank1Time = {}
Rank2Time = {}
Rank3Time = {}
pattern = -1
scorerank = None
starttime = 0
endtime = 0
def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    # 创建场景
    gameLayer = Layer() # gameLayer: 游戏场景所在的layer
    # 添加背景
    t = random.randint(0,1)
    if t == 0:
        bg = createAtlasSprite("bg_day")
    else:
        bg = createAtlasSprite("bg_night")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)
    #添加标题Logo
    titleLayer = Layer()
    title = createAtlasSprite("title")
    title.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 4 / 5)
    titleLayer.add(title, z=50)
    gameLayer.add(titleLayer, z=50, name="titleLayer")
    # 添加鸟
    spriteBird = creatBird()
    #spriteBird.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] / 3)
    # 添加移动的地面
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # 将gameLayer添加到scene中
    gameScene.add(gameLayer)
    if isOnline:
        ol = createAtlasSprite("online")
        ol.position = (common.visibleSize["width"] * 18 / 100, common.visibleSize["height"] * 97 / 100)
        gameLayer.add(ol, name="online", z=100)
def game_start(_gameScene):
    global gameScene
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    ini_button = StartMenu()
    gameLayer.add(ini_button, z=20, name="init_button")
    connect(gameScene)
#登录成功
def login_success():
    global isOnline
    isOnline = 1
    print("LOGIN SUCCESS UNAME:" + g_username)
    removeLayer("login_button")
    removeLayer("content")
    removeLayer("username")
    removeLayer("password")
    initGameLayer()
    start_botton = SingleGameStartMenu()
    gameLayer.add(start_botton, z=20, name="start_button")
def createLabel(value, x, y):
    label=Label(value,
        font_name='Times New Roman',
        font_size=15,
        color = (0,0,0,255), 
        width = common.visibleSize["width"] - 20,
        multiline = True,
        anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label
def removeLayer(name):
    try:
        gameLayer.remove(name)
    except Exception, e:
        print "remove error with " + name
        pass
# single game start button的回调函数
def singleGameReady(level = "easy",gtype = 'normal'):
    global spriteBird
    global pattern, starttime, endtime
    if gtype == 'normal':
        pattern = 0
    else:
        pattern = 1
    removeContent()
    removeLayer("titleLayer")
    gameLayer.add(spriteBird, z=10)
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])
    starttime = time.time()
    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super( ReadyTouchHandler, self).__init__()

        def on_mouse_press (self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)
    
        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            isGamseStart = True
            if gtype == 'normal':
                spriteBird.gravity = gravity
            else:
                spriteBird.gravity = -gravity
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird , gtype)
            score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            if level == "easy":
                pipes = createPipes(gameLayer, gameScene, spriteBird, score, "easy")
            elif level == "mid":
                pipes = createPipes(gameLayer, gameScene, spriteBird, score, "mid")
            elif level == "hard":
                pipes = createPipes(gameLayer, gameScene, spriteBird, score, "hard")
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2, gtype)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)
def backToMainMenu(gtype='normal'):
    global  endtime
    endtime = time.time()
    restart_button = RestartMenu()
    gameLayer.add(restart_button, z=50, name="restart_button")
def showNotice():
    connected = connect(gameScene) # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        request_notice() # request_notice is from network.py
def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(notice, z=70, name="content")
def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass
def goback():
    removeLayer("scorerank")
#游戏结束菜单
class RestartMenu(Layer):
    global pattern, starttime, endtime
    def __init__(self):
        super(RestartMenu, self).__init__()
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.begin_game)),  #返回主菜单
                (ImageMenuItem(common.load_image("button_score.png"), self.showscore))      #显示排行榜
                ]   
        menu = Menu()
        menu.menu_valign = BOTTOM
        menu.menu_halign = LEFT
        positions = [(common.visibleSize["width"] / 6, common.visibleSize["height"] / 3), (common.visibleSize["width"] * 3 / 5, common.visibleSize["height"] / 3)]
        menu.create_menu(items, selected_effect=shake(), unselected_effect=shake_back())    #修改按钮位置
        setMenuItemPos(menu, positions)
        self.add(menu, z=52)
        alivetime = int(endtime - starttime)    #记录存活时间

        #保存分数
        import pipe
        now_score = pipe.g_score
        alivetime = endtime - starttime
        level = pipe.g_level

        score_list = []
        time_list = []
        #打开文件
        try:
            #判断是否为地狱模式
            if pattern != 0:
                 level = 'reverse'
            data = open(level + '_score.txt', 'r')
            for i in data.read().splitlines():    #分割数据  
                score_list.append(i.split('@')[0])
                time_list.append(i.split('@')[1])
                data.close()
        except Exception, e:
            score_list = []
            time_list = []
        #格式化数据
        while len(score_list) < 3:
            score_list.append("0")
        while len(time_list) < 3:
            time_list.append("0")
        panel_name = "score_panel_4"
        #判断排名，并更新排序
        if now_score >= int(score_list[0].encode("utf-8")):
            if alivetime > float(time_list[0].encode("utf-8")):
                score_list[2], score_list[1], score_list[0] = score_list[1], score_list[0], str(now_score)
                time_list[2], time_list[1], time_list[0] = time_list[1], time_list[0], str(alivetime)
                panel_name = "score_panel_1"
        elif now_score >= int(score_list[1].encode("utf-8")):
            if alivetime > float(time_list[1].encode("utf-8")):
                score_list[2], score_list[1] = score_list[1], str(now_score)
                time_list[2], time_list[1] = time_list[1], str(alivetime)
                panel_name = "score_panel_2"
        elif now_score >= int(score_list[2].encode("utf-8")):
            if alivetime > float(time_list[2].encode("utf-8")):
                score_list[2] = str(now_score)
                time_list[2] = str(alivetime)
                panel_name = "score_panel_3"
        #写入文件
        try:
            if pattern != 0:
                 level = 'reverse'
            data = open(level + '_score.txt', 'w+')
            for i in range(0, 3):
                data.write(score_list[i] + "@" + time_list[i] + '\n')
            data.close()
        except Exception, e:
            print("score.txt写入错误")

        #上传分数
        if isOnline:
            global g_username
            if pattern == 0:
                gametype = level
            else: gametype = 'reverse'
            post_score(now_score, alivetime, g_username, gametype)
        setPanelScores(now_score)                           #放置奖牌
        setBestScores(int(score_list[0].encode("utf-8")))   #放置最高分
        #放置gameover以及分数板
        gameoverLogo = createAtlasSprite("text_game_over") 
        gameoverLogo.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 4 / 5)
        self.add(gameoverLogo, z=50)
        _scoreLayer = Layer()
        scorepanel = createAtlasSprite(panel_name)
        scorepanel.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 6 / 11)
        _scoreLayer.add(scorepanel, z=50)
        self.add(_scoreLayer, z=51)

    def begin_game(self):
        removeLayer("restart_button")
        initGameLayer()
        start_botton = SingleGameStartMenu()
        gameLayer.add(start_botton, z=20, name="start_button")
    def showscore(self):
        global pattern, scorerank
    	scorerank = Layer()

        if isOnline: rank = createAtlasSprite("scorerank_online")
        else: rank = createAtlasSprite("scorerank")

    	rank.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    	scorerank.add(rank,z=60)
    	turnback = Menu()
    	turnback.menu_valign = BOTTOM
    	turnback.menu_halign = RIGHT
    	items = [
    			(ImageMenuItem(common.load_image("back.png"),goback))
    			]
    	turnback.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())
        scorerank.add(turnback,z = 61)
        #获得分数信息
        import pipe
        level = pipe.g_level
        if isOnline:    #在线
            if pattern == 0:
                gametype = level
            else: gametype = 'reverse'
            request_score(gametype)
        else:           #离线
            score_list = []
            time_list = []
            try:
                if pattern != 0:
                    level = 'reverse'
                data = open(level + '_score.txt', 'r')
                for i in data.read().splitlines():
                    score_list.append(i.split('@')[0])
                    time_list.append(i.split('@')[1])
                    data.close()
            except Exception, e:
                score_list = []
            while len(score_list) < 3:
                score_list.append('0')
            #放置分数和时间
            setRank1Scores(scorerank,int(score_list[0].encode("utf-8")))
            setRank2Scores(scorerank,int(score_list[1].encode("utf-8")))
            setRank3Scores(scorerank,int(score_list[2].encode("utf-8")))
            setRank1Time(scorerank,int(time_list[0][0].encode("utf-8")))
            setRank2Time(scorerank,int(time_list[1][0].encode("utf-8")))
            setRank3Time(scorerank,int(time_list[2][0].encode("utf-8")))
        gameLayer.add(scorerank,z = 60,name = "scorerank")
#主菜单
class SingleGameStartMenu(Layer):
    def __init__(self):
        global isOnline
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        menu = Menu()
        items = [
                (ImageMenuItem(common.load_image("seeme.png"), self.select_diff)),  #选择难度
                (ImageMenuItem(common.load_image("reverse.png"),self.enter)),       #地狱模式
                (ImageMenuItem(common.load_image("exit.png"), self.exit)),          #退出游戏
                (ImageMenuItem(common.load_image("back.png"), self.back)),          #返回按钮
                ]
        if isOnline == 1:
            print("111")
        menu.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())
        self.add(menu)
    def select_diff(self):
    	removeLayer("start_button")
    	diff_degree = DiffDegreeMenu()
    	gameLayer.add(diff_degree, z=20, name="diff_button")
    def enter(self):
        removeLayer("start_button")
        singleGameReady("hard",'reverse')
    def back(self):
        global isOnline
        removeLayer("start_button")
        removeLayer("online")
        isOnline = 0
        ini_button = StartMenu()
        gameLayer.add(ini_button, z=20, name="init_button")

    def exit(self):
        exit()
#开始菜单
class StartMenu(Menu):
    def __init__(self):
        super(StartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_start.png"), self.begin_game)),    #单机入口
                (ImageMenuItem(common.load_image("Login.png"), self.login_menu))            #登陆入口
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def begin_game(self):
        removeLayer("init_button")
        start_botton = SingleGameStartMenu()
        gameLayer.add(start_botton, z=20, name="start_button")
    def login_menu(self):
        removeLayer("init_button")
        login_botton = loginMenu()
        gameLayer.add(login_botton, name="login_button")
#登陆菜单
class loginMenu(Layer):
    def __init__(self):
        super(loginMenu, self).__init__()  
        #用户名以及密码输入框
        position = [common.visibleSize["width"] / 2 + 5, common.visibleSize["height"] * 3 / 5]
        self.uname_input = InputBox("username", position)
        position = [common.visibleSize["width"] / 2 + 5, common.visibleSize["height"] * 31 / 60]
        self.pwd_input = InputBox("password", position, type="*")
        menu = Menu()
        items = [
            (ImageMenuItem(common.load_image("Login.png"), self.login)),        #登陆
            (ImageMenuItem(common.load_image("register.png"), self.register))   #注册
        ]
        menu.create_menu(items, selected_effect=shake(), unselected_effect=shake_back())
        positions = [(common.visibleSize["width"] / 3, common.visibleSize["height"] * 2/ 5), (common.visibleSize["width"] * 3 / 5, common.visibleSize["height"] * 2/ 5)]
        setMenuItemPos(menu, positions)
        self.add(self.uname_input)
        self.add(self.pwd_input)
        self.add(menu)

    def login(self):
        global g_username
        username = self.uname_input.text()
        password = self.pwd_input.text()
        connected = connect(gameScene)  # connect is from network.py
        if not connected:
            content = "Cannot connect to server"
            showContent(content)
        else:
            g_username = username
            request_login(username, password)  # request_notice is from network.py

    def register(self):
        username = self.uname_input.text()
        password = self.pwd_input.text()
        connected = connect(gameScene)  # connect is from network.py
        if not connected:
            content = "Cannot connect to server"
            showContent(content)
        else:
            request_register(username, password)  # request_notice is from network.py
#难度选择菜单
class DiffDegreeMenu(Menu):
    def __init__(self):
        super(DiffDegreeMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("easy.png"), self.easy_degree)),
                (ImageMenuItem(common.load_image("mid.png"), self.mid_degree)),
                (ImageMenuItem(common.load_image("hard.png"), self.hard_degree))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def easy_degree(self):
        removeLayer("diff_button")
        singleGameReady("easy",'normal') 
    def mid_degree(self):
        removeLayer("diff_button")
        singleGameReady("mid",'normal')
    def hard_degree(self):
        removeLayer("diff_button")
        singleGameReady("hard",'normal')
#输入框实现
class InputBox(Menu):
    def __init__(self, name, position = [common.visibleSize["width"] / 2 + 5, common.visibleSize["height"] * 9 / 10], type=""):
        super(InputBox, self).__init__()
        self.pos_x = position[0]
        self.pos_y = position[1]
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        self.len = 6
        items = [
            (ImageMenuItem(common.load_image("inputbox.png"), None))    #输入框背景图
        ]
        self.create_menu(items)
        width, height = director.get_window_size()
        for idx, i in enumerate(self.children):
            item = i[1]
            item.transform_anchor = (self.pos_x - 8, self.pos_y - 3)
            item.generateWidgets(self.pos_x - 8, self.pos_y - 3, self.font_item,
                                 self.font_item_selected)

        self.str = ""
        self.name = name
        self.is_selected = 0
        self.type = type
    def on_mouse_release(self, x, y, buttons, modifiers):
        (x, y) = director.get_virtual_coordinates(x, y)
        if self.children[self.selected_index][1].is_inside_box(x, y):   
            #鼠标点击选中输入框 然后才可以输入
            self._activate_item()
            self.is_selected = 1
        else:
            self.is_selected = 0
    def on_key_press(self, symbol, modifiers):
        #输入
        from pyglet.window import key
        if self.is_selected == 1:
            if symbol == key.BACKSPACE:
                self.str = self.str[0:-1]
            if len(self.str) == self.len:
                pass
            elif key.A <= symbol <= key.Z:
                self.str += chr(symbol - key.A + 65)
            elif symbol == key.SPACE:
                self.str += " "
            elif key._0 <= symbol <= key._9:
                self.str += chr(symbol - key._0 + 48)
            elif key.NUM_0 <= symbol <= key.NUM_9:
                self.str += chr(symbol - key.NUM_0 + 48)

            self.showInput(self.str)
    def text(self):
        #返回内容
        return self.str
    def showInput(self, content):
        removeLayer(self.name)
        if self.type != "":
            content = list(content)
            for i in range(len(content)):
                content[i] = self.type
            content = ''.join(content)

        notice = self.createLabel(content, self.pos_x, self.pos_y)
        gameLayer.add(notice, z=70, name=self.name)
    def createLabel(self, value, x, y):
        label = Label(value,
                      font_name='MarkerFelt-Thin',
                      font_size=15,
                      color=(0, 0, 0, 255),
                      width=common.visibleSize["width"]/2,
                      multiline=True,
                      anchor_x='center', anchor_y='center')
        label.position = (x, y)
        return label
def setRank3Scores(scorerank,score):
    global Rank3Scores
    for k in Rank3Scores:
        try:
            scorerank.remove(Rank3Scores[k])
            Rank3Scores[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"] *79/100 + 36 - 18 * len(scoreStr) + 18*i, common.visibleSize["height"]* 30/66
        scorerank.add(s, z=62)
        Rank3Scores[i] = s
        i = i + 1
def setRank2Scores(scorerank,score):
    global Rank2Scores
    for k in Rank2Scores:
        try:
            scorerank.remove(Rank2Scores[k])
            Rank2Scores[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"] *79/100 + 36 - 18 * len(scoreStr) + 18*i, common.visibleSize["height"]* 39/66
        scorerank.add(s, z=62)
        Rank2Scores[i] = s
        i = i + 1
def setRank1Scores(scorerank,score):
    global Rank1Scores
    for k in Rank1Scores:
        try:
            scorerank.remove(Rank1Scores[k])
            Rank1Scores[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"] *79/100 + 36 - 18 * len(scoreStr) + 18*i, common.visibleSize["height"]* 49/66
        scorerank.add(s, z=62)
        Rank1Scores[i] = s
        i = i + 1
def setRank1Time(scorerank,score):
    global Rank1Time
    for k in Rank1Time:
        try:
            scorerank.remove(Rank1Time[k])
            Rank1Time[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"] *43/100 + 36 - 18 * len(scoreStr) + 18*i, common.visibleSize["height"]* 49/66
        scorerank.add(s, z=62)
        Rank1Time[i] = s
        i = i + 1
def setRank2Time(scorerank,score):
    global Rank2Time
    for k in Rank2Time:
        try:
            scorerank.remove(Rank2Time[k])
            Rank2Time[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"] *43/100 + 36 - 18 * len(scoreStr) + 18*i, common.visibleSize["height"]* 39/66
        scorerank.add(s, z=62)
        Rank2Time[i] = s
        i = i + 1
def setRank3Time(scorerank,score):
    global Rank3Time
    for k in Rank3Time:
        try:
            scorerank.remove(Rank3Time[k])
            Rank3Time[k] = None
        except:
            pass

    scoreStr = str(score)
    i = 0
    for d in scoreStr:
        s = createAtlasSprite("number_score_0"+d)
        s.position = common.visibleSize["width"] *43/100 + 36 - 18 * len(scoreStr) + 18*i, common.visibleSize["height"]* 30/66
        scorerank.add(s, z=62)
        Rank3Time[i] = s
        i = i + 1
def setRank1Name(name):
    global scorerank
    removeLayer("name1")
    label = Label(name,
                  font_name='MarkerFelt-Thin',
                  font_size=12,
                  color=(0, 0, 0, 255),
                  width=common.visibleSize["width"] / 2,
                  multiline=True,
                  anchor_x='center', anchor_y='center')
    label.position = (common.visibleSize["width"] *15/50, common.visibleSize["height"]* 49/66)
    scorerank.add(label, z=70, name="name1")
def setRank2Name(name):
    global scorerank
    removeLayer("name2")
    label = Label(name,
                  font_name='MarkerFelt-Thin',
                  font_size=12,
                  color=(0, 0, 0, 255),
                  width=common.visibleSize["width"] / 2,
                  multiline=True,
                  anchor_x='center', anchor_y='center')
    label.position = (common.visibleSize["width"] *15/50, common.visibleSize["height"]* 39/66)
    scorerank.add(label, z=70, name="name2")
def setRank3Name(name):
    global scorerank
    removeLayer("name3")
    label = Label(name,
                  font_name='MarkerFelt-Thin',
                  font_size=12,
                  color=(0, 0, 0, 255),
                  width=common.visibleSize["width"] / 2,
                  multiline=True,
                  anchor_x='center', anchor_y='center')
    label.position = (common.visibleSize["width"] *15/50, common.visibleSize["height"]* 30/66)
    scorerank.add(label, z=70, name="name3")

def setMenuItemPos(menu, positions):
    width, height = director.get_window_size()
    for idx, i in enumerate(menu.children):
        item = i[1]
        pos_x = positions[idx][0]
        pos_y = positions[idx][1]
        item.transform_anchor = (pos_x, pos_y)
        item.generateWidgets(pos_x, pos_y, menu.font_item,
                             menu.font_item_selected)