/*
titel: Trafficsimulation in C++
compile: clang++ -std=c++14 -lsfml-graphics -lsfml-window -lsfml-system -pthread version2.cpp
Font directory is Linux Fedora
press "2" for AI-Bot
date: 22 Okt 2917

*/

#include <iostream>
#include <SFML/Graphics.hpp>
#include <string>
#include <complex>
#include <math.h>
#include <fstream> // textfile
#include <random>
#include <thread>

class Settings {
  // sf::Color black(0x000000ff); // 0xRRGGBBAA, color hexadecimal
  //std::cout << "hallo" << "\n";
  // std::vector<std::string> event = {""};
  //event.push_back("event1");
public:
  sf::RenderWindow window;
  int framestep=0;
  int fps=60;
  sf::Vector2f mouse = {0,0};
  bool mousepressed=false;
  bool holdingobject=false;
  sf::Font font;
  sf::Text text;
  std::random_device myrandomdevice;     // random: only used once to initialise (seed) engine
  /// Settings constructor
  Settings()
  {
    font.loadFromFile("/usr/share/fonts/gnu-free/FreeSans.ttf");
    text.setFont(font);
    text.setCharacterSize(14);
    text.setFillColor(sf::Color::Black);
  }
  auto random_integer(int min, int max) {
    std::mt19937 rng(myrandomdevice());    // random-number engine used (Mersenne-Twister in this case)
    std::uniform_int_distribution<int> uni(min,max); // guaranteed unbiased
    return uni(rng);
  }
  /// paint text s on x,y
  void painttext(std::string s, int x, int y) {
    text.setString(s);
    text.setPosition(x,y);
    window.draw(text);
  }
  /// Euclidean ordinary distance
  auto calcdistance(sf::Vector2f p1, sf::Vector2f p2) {
    return std::sqrt(std::pow( p1.x-p2.x, 2.0 ) + std::pow( p1.y-p2.y, 2.0 ) );
  }
  /// polar coordinates for a point on circle
  auto polarpoint(sf::Vector2f p1, double angle, double radius) {
    angle = (angle-90)*M_PI/180;
    sf::Vector2f result;
    result.x = p1.x + radius * cos(angle);
    result.y = p1.y + radius * sin(angle);
    return result;
  }
  /// angle between tww points
  auto angle_between_two_points(sf::Vector2f p1, sf::Vector2f p2) {
    auto angle = atan2(p2.y-p1.y,p2.x-p1.x);
    angle = angle * 180/M_PI; // degree
    angle = angle + 90;
    if (angle<0) angle = angle + 360;
    return angle;
  }
  void drawline(sf::Vector2f p1, sf::Vector2f p2) {
    sf::Vertex line[] = {
      sf::Vertex(p1,sf::Color::Black),
      sf::Vertex(p2,sf::Color::Black)
    };
    window.draw(line, 2, sf::Lines);
  }
  void drawcircle(sf::Vector2f pos, int radius) {
    sf::CircleShape circle(radius);
    circle.setFillColor(sf::Color::Black);
    circle.setPosition(pos);
    window.draw(circle);
  }
  /// checks if pcheck is in rectangle
  auto inrect(sf::Vector2f p1, sf::Vector2f p2, sf::Vector2f pcheck) {
    auto rangex=false,rangey=false;
    if (pcheck.x>=p1.x and pcheck.x<=p2.x) rangex=true;
    if (pcheck.y>=p1.y and pcheck.y<=p2.y) rangey=true;
    if (rangex==true and rangey==true) return true;
    else return false;
  }
  /// return difference between two angles
  auto anglediff(int source, int target) {
    auto temp = target-source;
    temp = (temp + 180) % 360 - 180;
    return temp;
  }
};

/// global variables
Settings mysettings;

class Box {
public:
  sf::Vector2f position;
  sf::Vector2f positioncenter;
  int width=25, height=25;
  std::string type="lane";
  int direction;
  void update() {
    positioncenter={position.x+width/2,position.y+height/2};
    if (type=="lane" or type=="obstacle") paintrect();
    if (type=="car") paintcircle();
  }
  void paintrect() {
    sf::RectangleShape box(sf::Vector2f(width, height));
    if (type=="obstacle")
      box.setFillColor(sf::Color(250,210,200));
    if (type=="lane")
      box.setFillColor(sf::Color(230,230,230));
    box.setPosition(position);
    mysettings.window.draw(box);
  }
  void paintcircle() {
    sf::CircleShape box(width/2);
    box.setFillColor(sf::Color::Yellow);
    box.setPosition(position);
    mysettings.window.draw(box);
    // direction
    sf::Vector2f p2=mysettings.polarpoint(positioncenter,direction,width);
    mysettings.drawline(positioncenter,p2);
  }
  void move(std::string action) {
    if (action=="left") direction-=90;
    if (action=="right") direction+=90;
    if (action=="up") {
      position=mysettings.polarpoint(position,direction,width);
    }
  }
};

class Physics {
public:
  std::vector<Box> mybox;

  Physics() {
    mybox.push_back({});
    mybox[mybox.size()-1].position={200,150};
    mybox[mybox.size()-1].type="car";
    mybox.push_back({});
    mybox[mybox.size()-1].position={300,50};
    mybox[mybox.size()-1].width=50;
    mybox[mybox.size()-1].height=250;
    mybox.push_back({});
    mybox[mybox.size()-1].position={150,150};
    mybox[mybox.size()-1].width=375;
    mybox[mybox.size()-1].height=50;
    mybox.push_back({});
    mybox[mybox.size()-1].position={150,25};
    mybox[mybox.size()-1].width=375;
    mybox[mybox.size()-1].height=50;
    mybox.push_back({});
    mybox[mybox.size()-1].position={150,250};
    mybox[mybox.size()-1].width=375;
    mybox[mybox.size()-1].height=50;
    mybox.push_back({});
    mybox[mybox.size()-1].position={100,25};
    mybox[mybox.size()-1].width=50;
    mybox[mybox.size()-1].height=275;
    mybox.push_back({});
    mybox[mybox.size()-1].position={525,25};
    mybox[mybox.size()-1].width=50;
    mybox[mybox.size()-1].height=275;
    mybox.push_back({});
    mybox[mybox.size()-1].position={200,250};
    mybox[mybox.size()-1].type="obstacle";
    mybox.push_back({});
    mybox[mybox.size()-1].position={250,100};
    mybox[mybox.size()-1].type="obstacle";

  }
  void update() {
    for (auto i=1;i<mybox.size();i++)
      mybox[i].update();
    mybox[0].update(); // car at last
  }

};

class Sensorbase {
public:
  Physics myphysics;
  void set(Physics myphysics_) {
    myphysics=myphysics_;
  }
};

class Knowledgebase : public Sensorbase {
public:
  int getobject(sf::Vector2f, std::string);
  int scanlane(sf::Vector2f, int);
  int scanobstacle(sf::Vector2f, int);
  int lanedirection(sf::Vector2f);
  int drivedirection(sf::Vector2f);
  int nextstepajunction();
  std::vector<std::string> behavior();
  
};
/// identify object
/// return: 1=object found, 0=not found
int Knowledgebase::getobject(sf::Vector2f position, std::string name) {
  int result=0;
  for (auto i=0;i<myphysics.mybox.size();i++) {
    sf::Vector2f p1 = myphysics.mybox[i].position;
    sf::Vector2f p2 = {p1.x+myphysics.mybox[i].width,p1.y+myphysics.mybox[i].height};
    bool recognize = mysettings.inrect(p1,p2,position);
    if (recognize==true and name==myphysics.mybox[i].type)
      result=1;
  }
  return result;
}
/// search for end of lane
/// return number of steps
int Knowledgebase::scanlane(sf::Vector2f position, int direction) {
  auto width = myphysics.mybox[0].width;
  int count;
  for (count=1; count<30; count++) {
    sf::Vector2f p1=mysettings.polarpoint(position,direction,count*width);
    if (getobject(p1,"lane")!=1)
      break;
  }
  return count;
}
/// search for obstacle
/// return number of steps
int Knowledgebase::scanobstacle(sf::Vector2f position, int direction) {
  auto width = myphysics.mybox[0].width;
  int max=30;
  int count;
  for (count=1; count<max; count++) {
    sf::Vector2f p1=mysettings.polarpoint(position,direction,count*width);
    if (getobject(p1,"obstacle")==1 or getobject(p1,"car")==1)
      break;
  }
  if (count==max) count=0;
  return count;
}
/// get lane direction
/// return: 0=unknown,1=horizontal,2=vertical
int Knowledgebase::lanedirection(sf::Vector2f position) {
  int result=0;
  if (scanlane(position,0)+scanlane(position,180)-1==2) // horizontal?
    result=1;
  if (scanlane(position,90)+scanlane(position,270)-1==2) // vertical?
    result=2;
  return result;
}
/// direction in which a car drives on the lane
/// return: -1=unknown, 0..360=direction in degree
int Knowledgebase::drivedirection(sf::Vector2f position) {
  int result=-1;
  if (lanedirection(position)==1 // horizontal lane
    and scanlane(position,0)==1 ) // steps to north
    result=270;
  if (lanedirection(position)==1 // horizontal lane
    and scanlane(position,180)==1 ) // steps to south
    result=90;
  if (lanedirection(position)==2 // vertical lane
    and scanlane(position,90)==1 ) // steps to east
    result=0;
  if (lanedirection(position)==2 // vertical lane
    and scanlane(position,270)==1 ) // steps to west
    result=180;
  return result;
}
/// tests if next step a junction
/// 0=nojunction, 1=junction
int Knowledgebase::nextstepajunction() {
  // get pos
  sf::Vector2f robotpos ={myphysics.mybox[0].position.x+myphysics.mybox[0].width/2,myphysics.mybox[0].position.y+myphysics.mybox[0].width/2};  
  int robotdirection=myphysics.mybox[0].direction;
  int width =myphysics.mybox[0].width;
  sf::Vector2f p1 = mysettings.polarpoint(robotpos,robotdirection,width);
  // lane test
  int openlanes=0;
  if (scanlane(p1,robotdirection)>2) // forward
    openlanes++;
  if (scanlane(p1,robotdirection+90)>2) // right
    openlanes++;
  if (scanlane(p1,robotdirection-90)>2) // left
    openlanes++;
  // decision
  if (openlanes>1) return 1;
  else return 0;
}
/// generate an action sequence
std::vector<std::string> Knowledgebase::behavior() {
  std::vector<std::string> result;
  // wait for junction
  if (nextstepajunction()==1)
    result.push_back("wait");
  // action planning
  std::vector<std::string> action1,action2,action3,action4;
  action1 = {"up"}; // normal forward
  action2 = {"up","up"}; // junction straight ahead
  action3 = {"right","up"}; // junction right
  action4 = {"up","left","up","up"}; // junction left
  std::vector<int> selectaction;
  sf::Vector2f robotpos ={myphysics.mybox[0].position.x+myphysics.mybox[0].width/2,myphysics.mybox[0].position.y+myphysics.mybox[0].width/2};  
  int robotdirection=myphysics.mybox[0].direction;
  int lane=lanedirection(robotpos);
  if (lane==1 or lane==2) selectaction.push_back(1);
  else {
    if (scanlane(robotpos,robotdirection)>2)
      selectaction.push_back(2);
    if (scanlane(robotpos,robotdirection+90)>2) // right
      selectaction.push_back(3);
    if (scanlane(robotpos,robotdirection-90)>2) // left
      selectaction.push_back(4);
  }
  // random element
  int r = mysettings.random_integer(0,selectaction.size()-1);
  if (selectaction[r]==1) 
    result.push_back("up"); // normal forward
  if (selectaction[r]==2) { // junction straight ahead
    result.push_back("up");
    result.push_back("up");
  }
  if (selectaction[r]==3) { // junction right
    result.push_back("right");
    result.push_back("up");
  }
  if (selectaction[r]==4) { // junction left
    result.push_back("up");
    result.push_back("left");
    result.push_back("up");
    result.push_back("up");
  }
  return result;
}


class Sensor : public Knowledgebase {
public:
  void paintrectangle(sf::Vector2f position) {
    auto width = myphysics.mybox[0].width;
    sf::RectangleShape box(sf::Vector2f(width, width));
    box.setFillColor(sf::Color::Transparent);
    box.setOutlineThickness(1);
    box.setOutlineColor(sf::Color::Blue);
    box.setPosition({position.x-width/2,position.y-width/2});
    mysettings.window.draw(box);
  }
  void paintmarker(sf::Vector2f position) {
    auto width = myphysics.mybox[0].width;
    std::vector<int> direction = {0,90,180,270};
    sf::Vector2f p1;
    for (int i=0;i<direction.size();i++) {
      // lane
      int count=scanlane(position,direction[i]);
      if (count!=0) {
        p1=mysettings.polarpoint(position,direction[i],count*width);
        mysettings.drawcircle(p1,4);
      }
      // obstacle
      count=scanobstacle(position,direction[i]);
      if (count!=0) {
        p1=mysettings.polarpoint(position,direction[i],count*width);
        mysettings.drawcircle(p1,2);
      }
    }
  }
  void paintsensor(sf::Vector2f position) {
    paintrectangle(position);
    paintmarker(position);
  }

};


class GUI {
public:
  Physics myphysics;
  Sensor mysensor;
  void run() {
    mysettings.window.create(sf::VideoMode(600, 338), "SFML");
    while(mysettings.window.isOpen())
    {
      // wait
      sf::sleep(sf::milliseconds(1000/mysettings.fps));
      // update
      mysettings.window.clear(sf::Color(200,200,200));
      myphysics.update();
      mysensor.set(myphysics);
      sf::Vector2f pos=mysettings.mouse;
      mysensor.paintsensor(pos);
      mysettings.painttext("frame "+std::to_string(mysettings.framestep),10,10);
      mysettings.painttext("mouse "+std::to_string(mysettings.mouse.x)+" "+std::to_string(mysettings.mouse.y),10,30);
      mysettings.painttext("fps "+std::to_string(mysettings.fps),10,50);
      mysettings.painttext("kb car "+std::to_string(mysensor.getobject(pos,"car")),10,70);
      mysettings.painttext("kb lane "+std::to_string(mysensor.getobject(pos,"lane")),10,90);
      mysettings.painttext("kb obstacle "+std::to_string(mysensor.getobject(pos,"obstacle")),10,110);
      mysettings.painttext("kb scan lane east "+std::to_string(mysensor.scanlane(pos,90)),10,130);
      mysettings.painttext("kb scan obstacle south "+std::to_string(mysensor.scanobstacle(pos,180)),10,150);
      mysettings.painttext("kb lanedirection "+std::to_string(mysensor.lanedirection(pos)),10,170);
      mysettings.painttext("kb drivedirection "+std::to_string(mysensor.drivedirection(pos)),10,190);
      mysettings.painttext("robot direction "+std::to_string(myphysics.mybox[0].direction),10,210);
      
      inputhandling();
      mysettings.window.display();
      mysettings.framestep++;
    }
  }
  void inputhandling() {
    sf::Event event;
    while(mysettings.window.pollEvent(event)) {
      if (event.type == sf::Event::Closed)
        mysettings.window.close();
      if (event.type == sf::Event::MouseMoved) {
        mysettings.mouse.x = sf::Mouse::getPosition(mysettings.window).x;
        mysettings.mouse.y = sf::Mouse::getPosition(mysettings.window).y;
      }
      if (event.type == sf::Event::MouseButtonPressed) {
         mysettings.mousepressed=true;
      }

      if (event.key.code == sf::Keyboard::Num1 and event.type == sf::Event::KeyPressed)
        std::cout<<mysensor.nextstepajunction()<<"\n";
      if (event.key.code == sf::Keyboard::Num2 and event.type == sf::Event::KeyPressed)
        taskmain();
      if (event.key.code == sf::Keyboard::Left and event.type == sf::Event::KeyPressed)
        myphysics.mybox[0].move("left");
      if (event.key.code == sf::Keyboard::Right and event.type == sf::Event::KeyPressed)
        myphysics.mybox[0].move("right");
      if (event.key.code == sf::Keyboard::Up and event.type == sf::Event::KeyPressed)
        myphysics.mybox[0].move("up");
    }
  }
  void task3() {
    auto pause=50;
    for (auto trial=0;trial<10000;trial++) {
      std::vector<std::string> actions=mysensor.behavior();
      for (auto i=0;i<actions.size();i++) {
        //std::cout << actions[i] << " ";
        if (actions[i]=="wait")
          sf::sleep(sf::milliseconds(1000/(0.1*pause)));
        else myphysics.mybox[0].move(actions[i]);
        sf::sleep(sf::milliseconds(1000/pause));
      }
    }
    //std::cout << "\n";
  }
  void taskmain() {
    std::thread t1;
    t1=std::thread(&GUI::task3, this);
    t1.detach();
  }

};



int main()
{
  GUI mygui;
  mygui.run();
  return 0;
}


