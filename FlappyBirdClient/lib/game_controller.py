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
username = "username"
isOnline = 0

def getUsername():
    global username
    return username

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

def game_start(_gameScene):
    global gameScene
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    ini_button = StartMenu()
    gameLayer.add(ini_button, z=20, name="init_button")
    connect(gameScene)

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
def singleGameReady(level = "easy"):
    global spriteBird
    removeContent()
    removeLayer("titleLayer")
    gameLayer.add(spriteBird, z=10)
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

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
        
            spriteBird.gravity = gravity #gravity is from bird.py
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird)
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
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)

def backToMainMenu():
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

class RestartMenu(Layer):
    def __init__(self):  
        super(RestartMenu, self).__init__()
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.begin_game)),
                (ImageMenuItem(common.load_image("button_score.png"), showNotice))
                ]
        menu = Menu()
        menu.menu_valign = BOTTOM
        menu.menu_halign = LEFT
        positions = [(common.visibleSize["width"] / 6, common.visibleSize["height"] / 3), (common.visibleSize["width"] * 3 / 5, common.visibleSize["height"] / 3)]
        menu.create_menu(items, selected_effect=shake(), unselected_effect=shake_back())
        width, height = director.get_window_size()
        for idx, i in enumerate(menu.children):
            item = i[1]
            pos_x = positions[idx][0]
            pos_y = positions[idx][1]
            item.transform_anchor = (pos_x, pos_y)
            item.generateWidgets(pos_x, pos_y, menu.font_item,
                                 menu.font_item_selected)
        self.add(menu, z=52)
        import pipe
        now_score = pipe.g_score
        level = pipe.g_level
        try:
            data = open(level + '_score.txt', 'r')
            f = data.read().splitlines()
            data.close()
        except Exception, e:
            data = None
            f = []

        while len(f) < 3:
            f.append("0")
        panel_name = "score_panel_4"
        if now_score >= int(f[0].encode("utf-8")):
            f[2], f[1], f[0] = f[1], f[0], str(now_score)
            panel_name = "score_panel_1"
        elif now_score >= int(f[1].encode("utf-8")):
            f[2], f[1] = f[1], str(now_score)
            panel_name = "score_panel_2"
        elif now_score >= int(f[2].encode("utf-8")):
            f[2] = str(now_score)
            panel_name = "score_panel_3"
        try:
            data = open(level +'_score.txt', 'w+')
            for i in f:
                data.write(str(i) + '\n')
            data.close()
        except Exception, e:
            print("score.txt写入错误")
        setPanelScores(now_score)
        setBestScores(int(f[0].encode("utf-8")))

        gameoverLogo = createAtlasSprite("text_game_over")
        gameoverLogo.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 4 / 5)
        self.add(gameoverLogo, z=50)
        scoreLayer = Layer()
        scorepanel = createAtlasSprite(panel_name)
        scorepanel.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 6 / 11)
        scoreLayer.add(scorepanel, z=50)
        self.add(scoreLayer, z=51, name="scoreLayer")

    def begin_game(self):
        removeLayer("restart_button")
        initGameLayer()
        if isOnline == 0:
            start_botton = SingleGameStartMenu()
        else:
            pass
        gameLayer.add(start_botton, z=20, name="start_button")

class SingleGameStartMenu(Menu):
    def __init__(self):  
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = BOTTOM
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("easy.png"), self.easy_degree)),
                (ImageMenuItem(common.load_image("mid.png"), self.mid_degree)),
                (ImageMenuItem(common.load_image("hard.png"), self.hard_degree)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
                (ImageMenuItem(common.load_image("exit.png"), self.exit)),
                (ImageMenuItem(common.load_image("back.png"), self.back))
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def easy_degree(self):
        removeLayer("start_button")
        singleGameReady("easy") 
    def mid_degree(self):
        removeLayer("start_button")
        singleGameReady("mid") 
    def hard_degree(self):
        removeLayer("start_button")
        singleGameReady("hard") 
    def back(self):
        removeLayer("start_button")
        ini_button = StartMenu()
        gameLayer.add(ini_button, z=20, name="init_button")
    def exit(self):
        exit()
class StartMenu(Menu):
    def __init__(self):
        super(StartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_start.png"), self.begin_game)),
                (ImageMenuItem(common.load_image("Login.png"), None))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def begin_game(self):
        removeLayer("init_button")
        start_botton = SingleGameStartMenu()
        gameLayer.add(start_botton, z=20, name="start_button")

class InputBox(Menu):
    def __init__(self):
        super(InputBox, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
            (ImageMenuItem(common.load_image("Login.png"), None))
        ]
        self.create_menu(items)
        self.str = ""

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key
        if key.A <= symbol <= key.Z and len(self.str) <= 8:
            self.str += chr(symbol - key.A + 65)

        if symbol == key.BACKSPACE:
            self.str = self.str[0:-1]
        showContent(self.str)
    def text(self):
        return self.str