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

def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    # add background
    t = random.randint(0,1)
    if t == 0:
        bg = createAtlasSprite("bg_day")
    else:
        bg = createAtlasSprite("bg_night")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)
    # add title
    titleLayer = Layer()
    title = createAtlasSprite("title")
    title.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] * 4 / 5)
    titleLayer.add(title, z=50)
    gameLayer.add(titleLayer, z=50, name="titleLayer")
    # add moving bird
    spriteBird = creatBird()
    #spriteBird.position = (common.visibleSize["width"] / 2, common.visibleSize["height"] / 3)
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # add gameLayer to gameScene
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
    print "remove"
    gameLayer.remove(name)

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
    restartButton = RestartMenu()
    gameLayer.add(restartButton, z=50)

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
    

class RestartMenu(Menu):
    def __init__(self):  
        super(RestartMenu, self).__init__()
        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice))
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        ini_button = StartMenu()
        gameLayer.add(ini_button, z=20, name="init_button")

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
        gameLayer.remove("start_button")
        singleGameReady("easy") 
    def mid_degree(self):
        gameLayer.remove("start_button")
        singleGameReady("mid") 
    def hard_degree(self):
        gameLayer.remove("start_button")
        singleGameReady("hard") 
    def back(self):
        gameLayer.remove("start_button")
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
        gameLayer.remove("init_button")
        start_botton = SingleGameStartMenu()
        gameLayer.add(start_botton, z=20, name="start_button")