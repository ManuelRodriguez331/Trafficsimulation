/*
titel: trafficsimulation
dependencies: SFML
compile with: clang++ -std=c++14 -lsfml-graphics -lsfml-window -lsfml-system trafficsimulation.cpp

date: Okt 2, 2017
programming language: C++
path: /home/user1/neu/texte/arbeitsprobe/programmieren/2017-Aug-26git
Code formatting: bash -c "astyle --indent-classes -Y -s2 --style=attach --pad-oper"
to do:
  - car relativemove
  - richtungswahl

to do later:
  - sqlite https://www.tutorialspoint.com/sqlite/sqlite_c_cpp.htm
  - Beispiel: /home/user1/neu/texte/arbeitsprobe/programmieren/2017-Feb-24-c++robothand

C++ Libraries:
  - Boost,
  - OpenCV, Moveit, OMPL, Gazebo
  - SUMO (Simulation of Urban Mobility)
  - List of libraries: https://github.com/jslee02/awesome-robotics-libraries
  - TORCS, speeddreams
  - SmartBody (Charakter animation plattform)
  - sqlite ignition-math
C++11:
  Referenzen
  std::vector (Array) http://www.learncpp.com/cpp-tutorial/6-16-an-introduction-to-stdvector/
  auto Flag = true; // geht nicht in Klassen
git:
  git init (neues Projekt erzeugen)
  git add 1.py (Datei hinzufügen)
  git commit -am "TEXT" (Commit)
  git tag v1.1 8930136ffbd83a (Tagging)
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
Anleitung: https://wiki.ubuntuusers.de/Git/
UML mit doxygen:
  https://stackoverflow.com/questions/4755913/how-to-use-doxygen-to-create-uml-class-diagrams-from-c-source

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
  3. straight lines: http://www.graphviz.org/content/attrs#dsplines
     digraph {
       splines="polyline";
       or: splines="line";
       or: splines="ortho";
  3. dot -Tpng 1.dot > 2.png


history:
  Oct 9, 2017, 1836 lines of code
  Oct 8, 2017, 1789 lines of code
  Oct 7, 2017, 1816 lines of code
  Oct 6, 2017, 1643 lines of code
  Oct 4, 2017, 1601 lines of code
  Oct 3, 2017, 1530 lines of code
  Oct 2, 2017, 1481 lines of code
  Sep 29, 2017, 1320 lines of code
  Sep 28, 2017, 1269 lines of code
  Sep 27, 2017, 1266 lines of code
  Sep 25, 2017, 1194 lines of code
  Sep 24, 2017, 1208 lines of code
  Sep 23, 2017, 1197 lines of code
  Sep 22, 2017, 1159 lines of code
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

*/

#include <iostream>
#include <SFML/Graphics.hpp>
#include <string>
#include <complex>
#include <math.h>

enum Direction { left,right,up,down };

class Settings {
public:
  sf::RenderWindow window;
  int framestep=0;
  sf::Vector2f mouse = {0,0};
  sf::Font font;
  sf::Text text;
  /// Settings constructor
  Settings()
  {
    font.loadFromFile("/usr/share/fonts/gnu-free/FreeSans.ttf");
    text.setFont(font);
    text.setCharacterSize(14);
    text.setFillColor(sf::Color::Black);
  }
  /// paint text s on x,y
  auto painttext(std::string s, int x, int y) {
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
  auto drawline(sf::Vector2f p1, sf::Vector2f p2) {
    sf::Vertex line[] = {
      sf::Vertex(p1,sf::Color::Black),
      sf::Vertex(p2,sf::Color::Black)
    };
    window.draw(line, 2, sf::Lines);
  }
  auto drawcircle(sf::Vector2f pos, int radius) {
    sf::CircleShape circle(radius);
    circle.setFillColor(sf::Color::Black);
    circle.setPosition(pos);
    window.draw(circle);
  }
};

/// global variables
Settings mysettings;

class Roadsegment {
public:
  sf::Vector2f p1 {50,300};
  sf::Vector2f p2 {300,250};
  sf::Vector2f p1left,p1right;
  sf::Vector2f p2left,p2right;
  int size=20;
  auto set(sf::Vector2f p1_, sf::Vector2f p2_) {
    p1 = p1_;
    p2 = p2_;
  }
  auto calcpoints() {
    // getangle
    auto angle=mysettings.angle_between_two_points(p1,p2);
    // calcpoints
    p1left = mysettings.polarpoint(p1,angle-90,size);
    p1right = mysettings.polarpoint(p1,angle+90,size);
    p2left = mysettings.polarpoint(p2,angle-90,size);
    p2right = mysettings.polarpoint(p2,angle+90,size);
  }
  auto update() {
    calcpoints();
    //mysettings.drawline(p1,p2); // middle
    mysettings.drawline(p1left,p2left); // left
    mysettings.drawline(p1right,p2right); // right
    mysettings.drawcircle(p1,3);
    mysettings.drawcircle(p2,3);
  }
};


// array of points: https://www.daniweb.com/programming/software-development/threads/407469/c-array-of-points
// http://www.cplusplus.com/forum/beginner/13430/
class Roadnetwork {
public:
  int radius = 3;
  std::vector<sf::Vector2f> waypoint;
  std::vector<sf::Vector2f> edge;
  std::vector<int> path;
  std::vector<Roadsegment> segmentlist;

  Roadnetwork() // constructor
  {
    waypoint.push_back({350, 50});
    waypoint.push_back({500, 50});
    waypoint.push_back({500, 220});
    waypoint.push_back({300, 220});
    waypoint.push_back({320, 50});
    
    edge.push_back({0, 1});
    edge.push_back({1, 2});
    edge.push_back({1, 3});
    edge.push_back({2, 3});

    path.push_back(0);
    path.push_back(1);
    path.push_back(3);
    path.push_back(0);
    generatesegment();
  }
  void generatesegment() { 
    for (auto i=0; i<edge.size(); i++) {
      segmentlist.push_back({});
      segmentlist[i].set(waypoint[edge[i].x],waypoint[edge[i].y]);
    }
  }
  void paintwaypoint(int i) {
    sf::CircleShape circle(radius);
    circle.setFillColor(sf::Color::Black);
    circle.setPosition(waypoint[i].x, waypoint[i].y);
    mysettings.window.draw(circle);
    mysettings.painttext(std::to_string(i),waypoint[i].x+4,waypoint[i].y+4);
  }
  void update() {
    for (int i=0; i<waypoint.size(); i++) {
      paintwaypoint(i);
    }
    for (auto i=0; i<segmentlist.size(); i++) {
      segmentlist[i].update();
    }
  }
};

class Car {
public:
  int x=0,y=0;
  int waypointstart=0, waypointend=1; // between two waypoints
  int distancerelative=10; /// distance from waypointstart
  void paint() {
    // body
    sf::CircleShape circle(20.f);
    circle.setFillColor(sf::Color::Yellow);
    circle.setPosition(x, y);
    mysettings.window.draw(circle);
    // eye
    sf::CircleShape eye(5.f);
    sf::CircleShape eyeinside(3.f);
    eye.setFillColor(sf::Color::White);
    eyeinside.setFillColor(sf::Color::Blue);
    eye.setPosition(x+6, y+10);
    eyeinside.setPosition(x+8, y+11);
    mysettings.window.draw(eye);
    mysettings.window.draw(eyeinside);
    eye.setPosition(x+26, y+10);
    eyeinside.setPosition(x+28, y+11);
    mysettings.window.draw(eye);
    mysettings.window.draw(eyeinside);
    
    // nose
    sf::CircleShape nose(3.f);
    nose.setFillColor(sf::Color::Blue);
    nose.setPosition(x+17, y+20);
    mysettings.window.draw(nose);
    
    // hat
    sf::RectangleShape hat(sf::Vector2f(20.f, 15.f));
    hat.setFillColor(sf::Color::Blue);
    hat.setPosition(x+10, y-10);
    mysettings.window.draw(hat);
  }
  /// change relative position of car to waypoint
  void move(Direction action) {
    auto step=10;
    if (action==up) distancerelative += step;
    if (action==down) distancerelative -= step;
  }

};


class Physics  {
public:
  Roadnetwork myroadnetwork;
  Car mycar;
  std::vector<std::string> event = {""};

  void updateevent() {
    // car position
    sf::Vector2f p1=myroadnetwork.waypoint[mycar.waypointstart];
    sf::Vector2f p2=myroadnetwork.waypoint[mycar.waypointend];
    auto angle=mysettings.angle_between_two_points(p1,p2);
    sf::Vector2f p3 = mysettings.polarpoint(p1,angle,mycar.distancerelative);
    // clear
    event.clear();
    // event traffic Junction
    auto dist1=mycar.distancerelative;
    auto dist2=mysettings.calcdistance(p1,p2);
    auto scale=0.1f; /// percent of waylength for enter traffic junction
    if ((dist1>(1-scale)*dist2) or dist1<scale*dist2) {
      event.push_back("trafficjunction");
    }
    else {
      event.push_back("road");
    }
    
  }
  void run() {
    myroadnetwork.update();
    updateevent();
    mycar.paint();
    carrelativemove();
  }
  /// to do: ausglieder von p1,p2 calculation
  void carrelativemove() {
    // get startposition
    sf::Vector2f p1=myroadnetwork.waypoint[mycar.waypointstart];
    // distance from start
    sf::Vector2f p2=myroadnetwork.waypoint[mycar.waypointend];
    auto angle=mysettings.angle_between_two_points(p1,p2);
    sf::Vector2f p3 = mysettings.polarpoint(p1,angle,mycar.distancerelative);
    // check for end
    if (mycar.distancerelative>mysettings.calcdistance(p1,p2)) {

      if (mycar.waypointstart<myroadnetwork.waypoint.size()) {
        mycar.waypointstart++;
        mycar.distancerelative=0;
        mycar.waypointend++;
        mycar.move(Direction(up)); // one tick forward
      }
    }
    // check for start
    if (mycar.distancerelative<0 and mycar.waypointstart>0) {
      mycar.waypointstart--;
      mycar.waypointend--;
      sf::Vector2f p1=myroadnetwork.waypoint[mycar.waypointstart];
      sf::Vector2f p2=myroadnetwork.waypoint[mycar.waypointend];
      mycar.distancerelative = mysettings.calcdistance(p1,p2);
      mycar.move(Direction(down)); // one tick backward
    }
    // set car position
    mycar.x=p3.x;
    mycar.y=p3.y;
  }
};



/// example: https://github.com/eXpl0it3r/Examples/blob/master/SFML/SimpleAABB.cpp
class GUI {
public:
  Physics myphysics;
  float fpsexact;

  auto updateGUI() {
    // text
    mysettings.painttext("frame "+std::to_string(mysettings.framestep),10,10);
    mysettings.painttext("mouse "+std::to_string(mysettings.mouse.x)+" "+std::to_string(mysettings.mouse.y),10,30);
    mysettings.painttext("fps "+std::to_string(fpsexact),10,50);
    mysettings.painttext("event1 "+myphysics.event[0],10,70);
    auto temp = std::to_string(myphysics.mycar.waypointstart)+" "+std::to_string(myphysics.mycar.waypointend);
    mysettings.painttext("waypoint "+temp,10,90);
    
    // update
    mysettings.window.display();
    mysettings.framestep++;
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
      if (event.key.code == sf::Keyboard::Left) 
        myphysics.mycar.move(Direction(left));
      if (event.key.code == sf::Keyboard::Right) 
        myphysics.mycar.move(Direction(right));
      if (event.key.code == sf::Keyboard::Up) 
        myphysics.mycar.move(Direction(up));
      if (event.key.code == sf::Keyboard::Down) 
        myphysics.mycar.move(Direction(down));
    }
  }
  void run() {
    mysettings.window.create(sf::VideoMode(600, 338), "SFML");
    sf::Clock clock;
    auto lastTime = 0;

    while(mysettings.window.isOpen())
    {
      mysettings.window.clear(sf::Color(200,200,200));
      myphysics.run();
      inputhandling();
      updateGUI();
      // wait
      auto fps=30;
      sf::sleep(sf::milliseconds(1000/fps));
      // measure frames per seconds (over a long timespan)
      if (mysettings.framestep%fps==0) {
        auto currentTime = clock.restart().asSeconds();
        fpsexact = 1.0f*fps/currentTime;
      }

     }
  }
};


class Game {
public:
  GUI mygui;
  void run() {
    mygui.run();
  }
};

int main()
{
  //std::cout << angle << "\n";
  Game mygame;
  mygame.run();
  return 0;
}
