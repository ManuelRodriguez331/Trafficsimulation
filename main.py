# coding: utf8
'''
titel: Trafficsimulation
Description: object-oriented Programming, Behavior-based robotics, head-up display, Intelligent Tutoring System, autonomous Driving, Threading
date: Sep 22, 2017
to do:
  - car high level planner (goal, path, blinker, speed)
  - number in textdisplay are too long
  - Autoscrolling to marked car with rectangle area
  - steering in opposite direction (u-turn)
  - virtualscreen attribute refactoring
  - Automode for every car seperat
  - obstacle slowdown
  - (geht nicht) zoom with touchpad

path: /home/user1/neu/texte/arbeitsprobe/programmieren/2017-Aug-26git
git:
  git init (neues Projekt erzeugen)
  git add 1.py (Datei hinzufügen)
  git commit -am "TEXT" (Commit)
  git tag v1.1 8930136ffbd83a (Tagging)
Autodia UML: /usr/local/bin/autodia.pl -l python -d .
Pylint UML:
  pyreverse -o png *.py -my
  -k (only classnames)
  -my (Module names)
Packages anzeigen:
  1. pyreverse -o dot *.py -my -k
  2. add cluster textfile:
     subgraph clusterAnimal {
       label = "Package animal"
       a -> b;
     }
  3. straight lines:
     digraph {
       splines=false;
     alternativ: neato -Tpng in.dot
  3. dot -Tpng 1.dot > 2.png
Show:
  git log --oneline --decorate --graph
  git status
  git diff
  gitk --all
Branches:
  neuen Branch: git branch issue12
  Branch wechseln: git checkout issue12
  merge: git checkout master
         git merge issue12 --no-ff -m "BESCHREIBUNG"
  Branch löschen: git branch -d issue12
Merge conflict:
  1. Datei in Texteditor bearbeiten
  3. merge abschließen: git commit -am "BESCHREIBUNG"
Lines of Code:
  wc -l $(git ls-files)
issue tracker:
  https://github.com/dspinellis/gi
Anleitung: https://wiki.ubuntuusers.de/Git/

history:
  Sep 20, 2017, 1125 lines of code
  Sep 19, 2017, 1000 lines of code
  Sep 18, 2017, 948 lines of code
  Sep 16, 2017, 884 lines of code
  Sep 15, 2017, 834 lines of code
  Sep 13, 2017, 764 lines of code
  Sep 12, 2017, 697 lines of code
  Sep 6, 2017, 694 lines of code
  Sep 3, 2017, 698 lines of code
  Sep 2, 2017, 638 lines of code
  Aug 26, 2017, 547 Lines of Code
  Aug 24, 2017, 448 Lines of Code

'''
import pygame, random, math, threading, sys

class Menusmall(object):
  def __init__(self):
    self.b = "welt"
  def out(self):
    print self.b

class Menubig(Menusmall):
  def __init__(self):
    self.a = "hallo"
    Menusmall.__init__(self)
  def show(self):
    print self.a

class Settings(object):
  screen = (600, 338)
  virtualsize = (1000, 650)
  virtualscreenorigin=(0,0)
  framestep=0
  scale=1.0 # zoom factor for screen
  mouse = (0,0)
  automode = False
  pygame.init()
  color = {"white" : (220, 220, 220),"clearwhite" : (240, 240, 240),"black":(0, 0, 0), "grey":(150, 150, 150),
    "red":(230, 0, 0),"blue":(0, 0, 230),"green":(33, 207, 0),"yellow":(223, 223, 33)}
  font = pygame.font.SysFont("freesans", 16)
  windowphysical = pygame.display.set_mode(screen)
  window = pygame.Surface(virtualsize) # surface
  # surface for buttons, not zoomable
  windowconst = pygame.Surface(virtualsize, pygame.SRCALPHA, 32) # make transparent
  windowconst = windowconst.convert_alpha()

  def painttext(self,text,position):
    myfont = self.font
    label = myfont.render(text, True, self.color["black"])
    self.window.blit(label, position)
  def painttextphysical(self,text,position):
    """ text is fixed, not scrolling """
    myfont = self.font
    label = myfont.render(text, True, self.color["black"])
    self.windowphysical.blit(label, position)
  def painttag(self,text,position):
    """ paint text on white background """
    # box
    width = len(text)*8
    height = 18
    pygame.draw.rect(self.window, (self.color["clearwhite"]), (position[0], position[1], width, height), 0)
    # text
    myfont = pygame.font.SysFont("freesans", 14)
    label = myfont.render(text, True, self.color["black"])
    self.window.blit(label, position)
  def getmouseabs(self):
    return (self.mouse[0]-self.virtualscreenorigin[0],self.mouse[1]-self.virtualscreenorigin[0])
  def floattoint(self,p):
    return (int(p[0]), int(p[1]))
  def polarpoint(self,p1, angle, radius):
    """ polar coordinates for a point on circle """
    angle = (angle - 90) * math.pi / 180
    x = p1[0] + radius * math.cos(angle)
    y = p1[1] + radius * math.sin(angle)
    return (x, y)
  def calcdistance(self,p1, p2):
    """ Euclidean ordinary distance """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
  def angle_between_two_points(self,p1, p2):
    angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
    angle += 90
    if angle < 0: angle += 360
    return angle
  def distancetest(self):
    return "hallo"
  def relativangle_between_two_points(self,p1,anglep1,p2):
    """ angle relative to p1 """
    angle=self.angle_between_two_points(p1,p2)
    diff = angle-anglep1
    if diff>180: steer=diff-360
    else: steer=diff
    return steer
  def anglediff(self,source,target):
    """ return difference between two angles """
    # https://stackoverflow.com/questions/1878907/the-smallest-difference-between-2-angles
    temp = target - source
    temp = (temp + 180) % 360 - 180
    return temp
  def incircle(self,p1,radius,p2):
    """ checks if p2 is in circle """
    square_dist = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    return square_dist <= radius ** 2
  def inrect(self,p1,p2,pcheck):
    """ checks if pcheck is in rectangle """
    rangex,rangey=False,False
    if pcheck[0]>=p1[0] and pcheck[0]<=p2[0]: rangex=True
    if pcheck[1]>=p1[1] and pcheck[1]<=p2[1]: rangey=True
    if rangex==True and rangey==True: return True
    else: return False
  def rectcollision(self,p1,p2,p3,p4):
    """ https://codereview.stackexchange.com/questions/31352/overlapping-rectangles """
    # rectangle1
    r1left   = min(p1[0], p2[0])
    r1right  = max(p1[0], p2[0])
    r1bottom = min(p1[1], p2[1])
    r1top    = max(p1[1], p2[1])
    # rectangle2
    r2left   = min(p3[0], p4[0])
    r2right  = max(p3[0], p4[0])
    r2bottom = min(p3[1], p4[1])
    r2top    = max(p3[1], p4[1])
    # calculating
    h_overlaps = (r1left <= r2right) and (r1right >= r2left)
    v_overlaps = (r1bottom <= r2top) and (r1top >= r2bottom)
    h_overlaps = (r1left <= r2right) and (r1right >= r2left)
    v_overlaps = (r1bottom <= r2top) and (r1top >= r2bottom)
    return h_overlaps and v_overlaps


class Hud(Settings):
  def __init__(self,physics):
    self.physics = physics
  def update(self):
    self.leftbar()
  def leftbar(self):
    text = []
    text.append("Automode "+str(Settings.automode))
    text.append("mouse window "+str(self.mouse))
    text.append("mouse abs "+str(self.getmouseabs()))
    text.append("frame "+str(self.framestep))
    text.append("car focus "+str(self.physics.carfocus))
    text.append("zoom start "+ str(Settings.virtualscreenorigin))
    text.append("zoom factor "+ str(Settings.scale))
    temp=self.physics.focusget("dist")
    temp=str(int(temp))
    text.append("dist goal "+ temp)
    text.append("car speed "+str(self.physics.focusget("speed")))
    text.append("max speed "+str(self.physics.focusget("maxspeed")))
    for i in range(len(text)):
      self.painttextphysical(text[i],(15,10+20*i))
  def setautomode(self):
    if Settings.automode==False:
      Settings.automode=True
    else: Settings.automode=False

class Scrollbutton(object):
  def __init__(self):
    self.p = [] # x,y,width,height
    self.p.append((0,70,30,150))
    self.p.append((570,70,30,150))
    self.p.append((230,0,150,30))
    self.p.append((230,300,150,30))
  def updatescrollbutton(self):
    scrollspeed=15
    for i in range(len(self.p)):
      # paint button
      p1 = self.p[i]
      width,height=self.p[i][2],self.p[i][3]
      p2 = (self.p[i][0]+width,self.p[i][1]+height)
      pygame.draw.rect(self.windowconst,(self.color["grey"]), (p1[0], p1[1], width, height), 1)
      # check mouse
      if self.inrect(p1,p2,Settings.mouse)==True:
        if i==0: self.scroll(-scrollspeed,0) # left
        if i==1: self.scroll(scrollspeed,0) # right
        if i==2: self.scroll(0,-scrollspeed) # up
        if i==3: self.scroll(0,scrollspeed) # down
  def scroll(self,x,y):
    p = self.virtualscreenorigin
    Settings.virtualscreenorigin=(p[0]+x,p[1]+y)

class Virtualscreen(Settings,Scrollbutton):
  def __init__(self):
    Scrollbutton.__init__(self)
  def zoomin(self,change):
    """ zoom factor """
    Settings.scale += change
  def update(self):
    self.updatescrollbutton()
    zoom = Settings.window.copy()
    zoom = pygame.transform.scale(zoom, (int(self.virtualsize[0]*self.scale), int(self.virtualsize[1]*self.scale)))
    self.windowphysical.fill(self.color["clearwhite"])
    origincorrect = (-1*self.virtualscreenorigin[0],-1*self.virtualscreenorigin[1])
    self.windowphysical.blit(zoom, origincorrect)
    self.windowphysical.blit(self.windowconst, (0,0))


class Lesson(object):
  def __init__(self):
    self.statusbar = []
    self.lessonid=0
  def nextlesson(self):
    if self.lessonid==0: self.lesson1()
    if self.lessonid==1: self.lesson2()
    if self.lessonid==2: self.lesson3()
    self.lessonid+=1
    if self.lessonid>2: self.lessonid=0
  def lessonupdate(self):
    if len(self.statusbar)>0: self.printstatusbar()
  def lesson1(self):
    Settings.virtualscreenorigin=(0,-45)
    self.physics.mycar[0].pos=(200,50)
    self.physics.setpath(0,[1,2])
    self.statusbar = []
    self.statusbar.append("Lesson 1: Introduction")
    self.statusbar.append("- switch from automode to manual control")
    self.statusbar.append("- drive ahead to the marked waypoint")
  def lesson2(self):
    Settings.virtualscreenorigin=(0,-45)
    self.physics.mycar[0].pos=(200,50)
    self.physics.setpath(0,[1,4])
    self.statusbar = []
    self.statusbar.append("Lesson 2: Turn")
    self.statusbar.append("- at next crossing turn right")
    self.statusbar.append("- set the blinker")
  def lesson3(self):
    Settings.virtualscreenorigin=(0,50)
    self.physics.mycar[0].pos=(200,250)
    self.physics.setpath(0,[4,3])
    self.statusbar = []
    self.statusbar.append("Lesson 3: Trafficlight")
    self.statusbar.append("- at next crossing stop if the trafficlight is red")
    self.statusbar.append("- If light is green then drive")
  def printstatusbar(self):
    """ paint text on white background """
    """ text is fixed, not scrolling """
    position=(300,0)
    width = 300
    height = 65
    text = self.statusbar
    # box
    pygame.draw.rect(self.windowphysical, (self.color["clearwhite"]), (position[0], position[1], width, height), 0)
    # text
    myfont = pygame.font.SysFont("freesans", 14)
    for i in range(len(self.statusbar)):
      text = self.statusbar[i]
      postenp = (position[0],position[1]+18*i)
      label = myfont.render(text, True, self.color["black"])
      self.windowphysical.blit(label, postenp)

class Autoscroll(object):
  def __init__(self):
    self.scrollrectanglep1 = (150,50)
    self.scrollrectanglep2 = (350,250)
  def updateautoscroll(self):
    #self.paintrectangle()
    #self.distancetocar()
    self.movescreen()
  def movescreen(self,center):
    old = Settings.virtualscreenorigin
    xmiddle=Settings.screen[0]/2
    ymiddle=Settings.screen[1]/2
    new = (0,0)
    Settings.virtualscreenorigin=(new[0],new[1])
  def distancetocar(self):
    focus = self.physics.carfocus
    posabs = self.physics.mycar[focus].pos
    pos = (posabs[0]-Settings.virtualscreenorigin[0],posabs[1]-Settings.virtualscreenorigin[1])
    # distance
    xdist1 = pos[0]-self.scrollrectanglep1[0]
    xdist2 = pos[0]-self.scrollrectanglep2[0]
    result = ""
    if xdist1>0 and xdist2>0: # car right and outside
      result = "right"
    if xdist1<0 and xdist2<0: # car left and outside
      result = "left"
    self.movescreen(pos)
    return result
  def paintrectangle(self):
    w = self.scrollrectanglep2[0]-self.scrollrectanglep1[0]
    h = self.scrollrectanglep2[1]-self.scrollrectanglep1[1]
    p = self.scrollrectanglep1
    pygame.draw.rect(self.windowconst,(self.color["black"]), (p[0], p[1], w, h), 1)
  def oldautoscrollupdate(self):
    # paint rectangle
    rectpos = (150,50)
    rectwidth = 200
    rectheight = 200
    pygame.draw.rect(self.windowconst,(self.color["black"]), (rectpos[0], rectpos[1], rectwidth, rectheight), 1)
    # check if car inside rectangle
    p2 = (rectpos[0]+rectwidth,rectpos[1]+rectheight)
    focus = self.physics.carfocus
    pos = self.physics.mycar[focus].pos
    relativepos = (pos[0]-Settings.virtualscreenorigin[0],pos[1]-Settings.virtualscreenorigin[1])
    inrect = self.inrect(rectpos,p2,relativepos)
    print inrect
    '''
    focus = self.physics.carfocus
    pos = self.physics.mycar[focus].pos
    org=Settings.virtualscreenorigin
    xmiddle=Settings.screen[0]/2
    ymiddle=Settings.screen[1]/2
    rectpos = (150,50)
    rectwidth = 200
    rectheight = 200
    pygame.draw.rect(self.windowconst,(self.color["black"]), (rectpos[0], rectpos[1], rectwidth, rectheight), 1)
    relpos = (pos[0]-Settings.virtualscreenorigin[0],pos[1]-Settings.virtualscreenorigin[1])
    p2 = (rectpos[0]+rectwidth,rectpos[1]+rectheight)
    inrect = self.inrect(rectpos,p2,relpos)
    print relpos, rectpos, inrect
    xmiddle,ymiddle=relpos[0],relpos[1]
    if inrect==False:
      #Settings.virtualscreenorigin=(pos[0]-xmiddle,pos[1]-ymiddle)
      Settings.virtualscreenorigin=(org[0]-xmiddle,org[0]-ymiddle)
    '''

class GUI(Settings,Lesson,Autoscroll):
  def __init__(self,physics):
    Lesson.__init__(self)
    Autoscroll.__init__(self)
    self.physics = physics
    self.myhud = Hud(self.physics)
    self.myvirtualscreen = Virtualscreen()
    self.fps = 20
    self.run()
  def run(self):
    for Settings.framestep in range(10000000):
      self.updateGUI()
      self.physics.update()
      self.inputhandling()
      self.myvirtualscreen.update()
      self.myhud.update()
      self.lessonupdate()
      #self.updateautoscroll()
      pygame.display.update()
  def updateGUI(self):
    pygame.time.wait(1000/self.fps)
    self.window.fill(self.color["white"])
  def inputhandling(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT: sys.exit(0)
      if event.type == pygame.MOUSEMOTION:
        Settings.mouse=event.pos
      if event.type == pygame.MOUSEBUTTONDOWN: pass
      if event.type == pygame.MOUSEBUTTONUP: pass
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_TAB: self.physics.setcarfocus()
        if event.key == pygame.K_1: self.myhud.setautomode()
        if event.key == pygame.K_2: self.physics.car1.parking()
        if event.key == pygame.K_3: self.physics.mytrafficlight[0].setstatus()
        if event.key == pygame.K_4: self.physics.mytrafficlight[1].setstatus()
        if event.key == pygame.K_5: self.physics.focuscontrol("turnlight","left")
        if event.key == pygame.K_6: self.physics.focuscontrol("turnlight","right")
        if event.key == pygame.K_7: self.physics.focuscontrol("marker","up")
        if event.key == pygame.K_8: self.physics.focuscontrol("marker","down")
        if event.key == pygame.K_9: self.nextlesson()
        if (event.key == pygame.K_PLUS) or (event.key == pygame.K_KP_PLUS):
          self.myvirtualscreen.zoomin(+0.10)
        if (event.key == pygame.K_MINUS) or (event.key == pygame.K_KP_MINUS):
          self.myvirtualscreen.zoomin(-0.10)
        if event.key == pygame.K_LEFT: self.physics.focuscontrol("wheel",-10)
        if event.key == pygame.K_RIGHT: self.physics.focuscontrol("wheel",10)
        if event.key == pygame.K_UP: self.physics.focuscontrol("speed",+1)
        if event.key == pygame.K_DOWN: self.physics.focuscontrol("speed",-1)

class Subwaypoint(object):
  def __init__(self):
    self.subwaylist = []
    self.marker = 0
  def paintsubwaypoints(self):
    for i in range(len(self.subwaylist)):
      p = self.subwaylist[i]
      pygame.draw.circle(self.window, self.color["black"], self.floattoint(p), 3, 0)
  def paintmarker(self):
    p1 = self.subwaylist[self.marker]
    pygame.draw.circle(self.window, self.color["red"], self.floattoint(p1), 6, 0)
  def setmarker(self,direction):
    """ change marker up/down """
    if direction=="up":
      if self.marker<len(self.subwaylist)-1:
        self.marker+=1
    if direction=="down":
      if self.marker>0:
        self.marker-=1

class Pathanalytics(object):
  def __init__(self):
    self.step = 25
  def subwaypointlist(self):
    """ return coordinates of subwaypoints along the path """
    plist = []
    for i in range(len(self.path)-1):
      for a in range(30):
        temp=self.pointonpath(i,a) # temp[0],temp[1],temp[2]
        dist1=self.calcdistance(temp[0],temp[1])
        dist2=self.calcdistance(temp[0],temp[2])
        if (dist1+self.step/2)>dist2: break
        else:
          plist.append(temp[1])
          #print i,a,dist1,dist2,temp
    return plist
  def pointonpath(self,main,sub):
    id1 = self.path[main]
    id2 = self.path[main+1]
    p1 = self.getsection(id1)[0]
    p2 = self.getsubwaypoint(id1,id2,sub)
    p3 = self.getsection(id1)[1]
    return (p1,p2,p3)
  def getsection(self,waypointid):
    """ returns section of path """
    p1 = self.waypoint[waypointid]
    temp = self.path.index(waypointid)+1
    id2=self.path[temp]
    p2 = self.waypoint[id2]
    return (p1,p2)
  def getsubwaypoint(self,id1,id2,index):
    """ return subwaypoint which is index*step from id1 away """
    p1 = self.waypoint[id1]
    p2 = self.waypoint[id2]
    angle = self.angle_between_two_points(p1,p2)
    temp=self.polarpoint(p1,angle,self.step*index)
    return temp

class Pathplanner(object):
  def nearestnode(self,p):
    """ returns node near point p """
    mindist = 99999
    minid = -1
    for i in range(len(self.waypoint)):
      dist=self.calcdistance(self.waypoint[i],p)
      if dist<mindist:
        mindist=dist
        minid=i
    return minid
  def follownode(self,nodeid):
    """ returns random follow node """
    follownode=-1
    maxtrial=40
    for i in range(maxtrial):
      temp = random.randint(0,len(self.edge)-1)
      if nodeid==self.edge[temp][0]:
        follownode=self.edge[temp][1]
        break
      if nodeid==self.edge[temp][1]:
        follownode=self.edge[temp][0]
        break
    return follownode
  def searchpath(self,start,goal):
    """ shorest path between startid and goalid """
    maxtrial=100
    bestpath = []
    bestdist=9999
    for trial in range(maxtrial):
      nodelist=[]
      dist=9999
      nodelist.append(start)
      for i in range(len(self.waypoint)):
        nodelist.append(self.follownode(nodelist[-1]))
        if nodelist[-1]==goal:
          dist=i
          break
      if dist<bestdist:
        bestdist=dist
        bestpath=nodelist
    return bestpath

class Roadnetwork(Settings,Pathplanner,Pathanalytics,Subwaypoint):
  def __init__(self):
    self.waypoint = []
    self.waypoint.append((100,50))
    self.waypoint.append((330,60))
    self.waypoint.append((500,50))
    self.waypoint.append((530,280))
    self.waypoint.append((327,260))
    self.waypoint.append((80,280))
    self.waypoint.append((50,130))
    self.waypoint.append((850,300))
    self.waypoint.append((850,100))
    self.waypoint.append((810,500))
    self.waypoint.append((300,550))
    self.waypoint.append((200,350))
    self.edge = [] #id1,id2
    self.edge.append((0,1))
    self.edge.append((1,2))
    self.edge.append((1,4))
    self.edge.append((2,3))
    self.edge.append((3,4))
    self.edge.append((4,5))
    self.edge.append((5,6))
    self.edge.append((6,0))
    self.edge.append((3,7))
    self.edge.append((7,8))
    self.edge.append((2,8))
    self.edge.append((7,9))
    self.edge.append((9,10))
    self.edge.append((10,11))
    self.edge.append((11,5))
    Subwaypoint.__init__(self)
    Pathanalytics.__init__(self)
    self.path = []
    self.updatepath()
  def updatepath(self):
    self.path = self.searchpath(0,3)
    self.path=[0,1,4,3]
    self.subwaylist = self.subwaypointlist()
  def paintwaypoints(self):
    myfont = self.font
    for i in range(len(self.waypoint)):
      p = self.waypoint[i]
      pygame.draw.circle(self.window, self.color["black"], self.floattoint(p), 5, 1)
      self.painttext(str(i),p)
  def paintedge(self):
    for i in range(len(self.edge)):
      id1 = self.edge[i][0]
      id2 = self.edge[i][1]
      p1,p2 = self.waypoint[id1],self.waypoint[id2]
      pygame.draw.line(self.window, self.color["grey"], p1, p2, 1)
  def paintpath(self):
    for i in range(len(self.path)-1):
      id1= self.path[i]
      id2= self.path[i+1]
      p1,p2 = self.waypoint[id1],self.waypoint[id2]
      pygame.draw.line(self.window, self.color["black"], p1, p2, 2)
  def paint(self):
    self.paintwaypoints()
    self.paintedge()
    #self.paintsubwaypoints()
    #self.paintpath()
    #self.paintmarker()

class Carlight(object):
  def __init__(self):
    self.turnlightside = "off"
    self.frame=0
    self.framemax=20
  def setturnlight(self,side):
    if self.turnlightside==side: self.turnlightside="off"
    else: self.turnlightside=side
  def paintturnlight(self):
    if self.turnlightside!="off":
      posA,posB,posC = self.gettriangle()
      if self.turnlightside=="left": temp=posB
      if self.turnlightside=="right": temp=posC
      temp=self.floattoint(temp)
      if self.frame<self.framemax/2: # turn on while half framemax
        pygame.draw.circle(self.window, self.color["green"], temp, 5, 0)
      self.frame+=1
      if self.frame==self.framemax: self.frame=0

class Speedcontrol(object):
  def __init__(self):
    self.maxspeed=3 # according to trafficlight
  def speedcontrol(self):
    self.speed=self.maxspeed


class Steering(Speedcontrol):
  # to do: Klasse aufteilen in marker und steering
  def __init__(self):
    Speedcontrol.__init__(self)
    self.subwaypointlist = []
    self.marker = 0 # goalid for car
    self.path=[]
  def paintlinetogoal(self):
    """ help-lines for steering, return angle for wheel """
    # carfront to obstacle
    p1 = self.getmarkerpos()
    p2= self.gettriangle()[0]
    targetAngle=self.angle_between_two_points(p2,p1)
    pygame.draw.line(self.window, self.color["red"], p2, p1, 1)
    # wheel projection
    radius = 40
    anglewheel=self.direction+self.wheeldirection
    p3 = self.polarpoint(p2,anglewheel,radius)
    pygame.draw.line(self.window, self.color["blue"], p2, p3, 2)
    # without wheel
    p4 = self.polarpoint(p2,self.direction,radius)
    pygame.draw.line(self.window, self.color["red"], p2, p4, 1)
    return targetAngle
  def steeringrun(self):
    targetAngle=self.paintlinetogoal()
    # angle diff
    steer= self.anglediff(self.direction,targetAngle)
    if Settings.automode==True:
      self.setwheelabsolute(steer)
      if self.getdistancetogoal()<20: self.setmarker("up")
      self.speedcontrol()
  def paintsteering(self):
    for i in range(len(self.subwaypointlist)):
      p = self.subwaypointlist[i]
      pygame.draw.circle(self.window, self.color["black"], self.floattoint(p), 3, 0)
  def paintmarker(self):
    p = self.getmarkerpos()
    pygame.draw.circle(self.window, self.color["red"], p, 6, 0)
  def getdistancetogoal(self):
    p1 = self.getmarkerpos()
    p2 = self.gettriangle()[0]
    dist = self.calcdistance(p2,p1)
    return dist
  def getmarkerpos(self):
    p = self.subwaypointlist[self.marker]
    p = self.floattoint(p)
    return p
  def setmarker(self,direction):
    """ change marker up/down """
    if direction=="up":
      if self.marker<len(self.subwaypointlist)-1:
        self.marker+=1
      else: self.marker=0
    if direction=="down":
      if self.marker>0:
        self.marker-=1
      else: self.marker=len(self.subwaypointlist)-1

class Parking(object):
  def parking(self):
    print "parking"
    thread1 = threading.Thread(target=self.task2)
    thread1.daemon = True  # stops, if mainprogram ends
    thread1.start()
  def task2(self):
    action=[] # wheel, speed
    action.append((0,4))
    action.append((40,0))
    action.append((40,-2))
    action.append((0,-2))
    action.append((-40,-2))
    action.append((0,1))
    action.append((0,0))
    for i in range(len(action)):
      print i,action[i]
      self.wheeldirection = action[i][0]
      self.speed=action[i][1]
      pygame.time.delay(1000)

class Wheel(object):
  def __init__(self):
    self.wheeldirection = 0
  def paintwheel(self):
    left1,left2,right1,right2=self.getwheelpos()
    # paint
    pygame.draw.line(self.window, self.color["blue"], left1, left2, 3)
    pygame.draw.line(self.window, self.color["blue"], right1, right2, 3)
  def getwheelpos(self):
    temp = self.polarpoint(self.pos,self.direction,0.5*self.radius)
    leftwheel = self.polarpoint(temp,self.direction-90,0.7*self.radius)
    leftwheel2 = self.polarpoint(leftwheel,self.wheeldirection+self.direction,1.0*self.radius)
    rightwheel = self.polarpoint(temp,self.direction+90,0.7*self.radius)
    rightwheel2 = self.polarpoint(rightwheel,self.wheeldirection+self.direction,1.0*self.radius)
    return (leftwheel,leftwheel2,rightwheel,rightwheel2)
  def setwheel(self,value):
    """ relative change of wheel """
    maxvalue=45
    self.wheeldirection+=value
    if self.wheeldirection>maxvalue:
      self.wheeldirection=maxvalue
    elif self.wheeldirection<-maxvalue:
      self.wheeldirection=-maxvalue
  def setwheelabsolute(self,direction):
    temp = direction-self.wheeldirection
    self.setwheel(temp)

class Highlevelplanner():
  def __init__(self):
    pass
  def highlevelplannerrun(self):
    print "run highlevelplanner"
    # check blinker

    # set goal

    # set path

    # set speed



class Car(Settings,Wheel,Parking,Carlight,Steering,Highlevelplanner):
  def __init__(self,pos,physicalmaxspeed):
    Wheel.__init__(self)
    Carlight.__init__(self)
    Steering.__init__(self)
    self.pos = pos
    self.physicalmaxspeed=physicalmaxspeed # according to car physics
    self.radius = 20
    self.speed = 0
    self.direction = 90
    self.highlevelplannerrun()

  def update(self,focus):
    self.driveforward()
    self.paintcar()
    self.paintwheel()
    self.paintturnlight()
    self.steeringrun()
    if focus==True:
      p=self.pos
      pygame.draw.circle(self.window, self.color["blue"], self.floattoint(p), 6, 0)
      self.paintsteering()
      self.paintmarker()
  def paintcar(self):
    posA,posB,posC=self.gettriangle()
    # triangle paint
    pygame.draw.line(self.window, self.color["blue"], posA, posB, 3)
    pygame.draw.line(self.window, self.color["blue"], posA, posC, 3)
    pygame.draw.line(self.window, self.color["blue"], posB, posC, 3)
    # semantic tagging
    self.painttag("car",self.getpos())
    self.painttag("goal",self.getmarkerpos())
  def gettriangle(self):
    posA = self.polarpoint(self.pos,self.direction,1.3*self.radius)
    temp = self.polarpoint(self.pos,self.direction+180,self.radius)
    posB = self.polarpoint(temp,self.direction-90,0.8*self.radius)
    posC = self.polarpoint(temp,self.direction+90,0.8*self.radius)
    return (posA,posB,posC)
  def getpos(self):
    p = self.pos
    p= (int(p[0]), int(p[1]))
    return p
  def setspeed(self,value):
    """ -1 = slower, 1=faster """
    # check for break
    fullstop=False
    if (self.speed>0 and value<0) or (self.speed<0 and value>0):
      fullstop=True
    # set speed
    speeddict = {0:0.25, 0.25:1, 1:3, 3:6, 6:6}
    if fullstop==False:
      currentspeed=math.fabs(self.speed)
      self.speed= speeddict[currentspeed]* value
    else: self.speed=0
  def driveforward(self):
    angle=self.direction+self.wheeldirection
    self.pos = self.polarpoint(self.pos,angle,self.speed)
    factor=40*1.0
    self.direction+= (self.speed*self.wheeldirection)/factor

class Obstacle(Settings):
  def __init__(self,p1,p2):
    self.p1 = p1
    self.p2 = p2
  def update(self):
    width = self.p2[0]-self.p1[0]
    height = self.p2[1]-self.p1[1]
    tempp = self.p1
    pygame.draw.rect(self.window, self.color["grey"], (tempp[0],tempp[1],width,height), 0)
    self.painttag("obstacle",tempp) # semantic tagging


class Trafficlight(Settings):
  def __init__(self,pos):
    self.pos = pos
    self.radius = 60
    self.status = "green"
  def setstatus(self):
    thread1 = threading.Thread(target=self.statusthread)
    thread1.start()
  def statusthread(self):
    """ switch status """
    if self.status == "green": goal = "red"
    if self.status == "red": goal = "green"
    self.status = "yellow"
    pygame.time.delay(1000)
    self.status = goal
  def getpos(self):
    """ return (pos,color) of trafficlight"""
    if self.status=="green": color=self.color["green"]
    if self.status=="red": color=self.color["red"]
    if self.status=="yellow": color=self.color["yellow"]
    return (self.pos,color)
  def paint(self):
    pos,color = self.getpos()
    pygame.draw.circle(self.window, color, pos, 10, 0) # light
    pygame.draw.circle(self.window, color, pos, self.radius, 1) # environment
    self.painttag("trafficlight",pos) # semantic tagging

class Collision(Settings):
  def collisioncheck(self):
    # check car n
    for carid in range(len(self.mycar)):
      lightisred=False
      for i in range(len(self.mytrafficlight)):
        p1 = self.mycar[carid].getpos()
        p2 = self.mytrafficlight[i].getpos()[0]
        status = self.mytrafficlight[i].status
        radius=self.mytrafficlight[i].radius
        incircle = self.incircle(p1,radius,p2)
        if incircle==True and status=="red":
          lightisred=True
      if lightisred==True:
        self.mycar[carid].maxspeed=0
      else: self.mycar[carid].maxspeed=self.mycar[carid].physicalmaxspeed


class Physics(Collision):
  def __init__(self):
    self.mycar = []
    self.mycar.append(Car((430,70),2))

    self.carfocus=0
    self.myobstacle = []
    self.myobstacle.append(Obstacle((200,100),(270,170)))
    self.myobstacle.append(Obstacle((400,100),(470,170)))
    self.myobstacle.append(Obstacle((5,5),(10,330))) # left
    self.myobstacle.append(Obstacle((700,200),(770,270)))
    self.mytrafficlight = []
    self.mytrafficlight.append(Trafficlight((345,245)))
    #self.mytrafficlight.append(Trafficlight((320,45)))
    self.myroadnetwork = Roadnetwork()
    self.setpath(0,[2,3])
    self.setpathwithplanner(0,2,5)

  def setpath(self,carid,path):
    self.myroadnetwork.path=path
    self.mycar[carid].subwaypointlist = self.myroadnetwork.subwaypointlist()
  def setpathwithplanner(self,carid,start,goal):
    """ shortest path between startid and goalid """
    self.myroadnetwork.path=self.myroadnetwork.searchpath(start,goal)
    self.mycar[carid].subwaypointlist = self.myroadnetwork.subwaypointlist()

  def update(self):
    for i in self.myobstacle: i.update()
    for i in self.mytrafficlight: i.paint()
    for i in range(len(self.mycar)):
      self.mycar[i].update(self.carfocus==i) # has focus?
    self.myroadnetwork.paint()
    self.collisioncheck()
  def setcarfocus(self):
    maxcar=len(self.mycar)-1
    self.carfocus+=1
    if self.carfocus>maxcar: self.carfocus=0
  def focusget(self,name):
    """ get value according to focus """
    temp = 0
    if name=="dist":
      temp=self.mycar[self.carfocus].getdistancetogoal()
    if name=="speed":
      temp=self.mycar[self.carfocus].speed
    if name=="maxspeed":
      temp=self.mycar[self.carfocus].maxspeed
    return temp
  def focuscontrol(self,name,value):
    """ name=wheel, name=speed for car with focus"""
    if name=="wheel":
      self.mycar[self.carfocus].setwheel(value)
    if name=="speed":
      self.mycar[self.carfocus].setspeed(value)
    if name=="turnlight":
      self.mycar[self.carfocus].setturnlight(value)
    if name=="marker":
      self.mycar[self.carfocus].setmarker(value)


class Game(object):
  def __init__(self):
    random.seed()
    self.myphysics = Physics()
    self.mygui = GUI(self.myphysics)

if __name__ == "__main__":
  myGame = Game()


