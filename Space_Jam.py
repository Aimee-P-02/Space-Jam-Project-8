from direct.showbase.ShowBase import ShowBase
import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, AudioSound
import Player as playerClass





                                            

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        #base.disableMouse()
        
       
        


        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)

        self.setUpScene()
        self.setCamera()
        self.playMusic() 
        

        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.spaceShip.collisionNode, self.spaceShip.modelNode)
        self.cTrav.addCollider(self.spaceShip.collisionNode, self.pusher)

        #self.cTrav.showCollisions(self.render)

        fullCycle = 60

        theta =  0

        
        
        
        # changed the way x y and z drones are placed to avoid the glitch with
        for j in range(fullCycle):
            spaceJamClasses.Drone.dronecount += 1
            
            nickName = "Drone" + str(spaceJamClasses.Drone.dronecount)

            self.DrawCloudDefense(self.Planet1, nickName)
            self.drawBaseBallSeams(self.spaceStation, nickName, j, fullCycle, 2)



        self.DroneCircleX(self.Planet4, nickName, theta)
        self.DroneCircleY(self.Planet4, nickName, theta)
        self.DroneCircleZ(self.Planet4, nickName, theta)
        

        
        
        
        

    def setUpScene(self):
        self.Universe = spaceJamClasses.Universe(self.loader,"./Assets/Universe/Universe.x",self.render,"Universe","./Assets/Universe/universe_bg.jpeg",(0,0,0), 10000)
        
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet1", "./Assets/Planets/sprinkle_texture.jpg", (150, 5000, 67), 350)

        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet2", "./Assets/Planets/planet texture2.png", (-4500, 1000, 34), 450)
        
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet3", "./Assets/Planets/planet_texture.png" , (2500, -3000, 90), 250)

        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet4", "./Assets/Planets/gas_giant_texture.jpg" , (-2000, 4500, 20), 100)

        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet5", "./Assets/Planets/ice_texture.jpeg", (-4000, 5000, 15), 200)
        
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, "Planet6", "./Assets/Planets/titan_texture.jpg", (7500, -3500, 90), 350)
        
        self.spaceShip = playerClass.SpaceShip(self.loader, self.cTrav, self.taskMgr, self.accept, "./Assets/Spaceships/Dumbledore.egg", self.render, "Spaceship", "./Assets/Spaceships/spacejet_C.png", (1500,1000, -100), 50)

        self.spaceStation = spaceJamClasses.SpaceStation(self.loader, "./Assets/Space Station/spaceStation.egg", self.render,"Station", "./Assets/Space Station/SpaceStation1_Dif2.png", (750, 275, 90), 25)
        self.Sentinal1 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet5, 300, "MLB", self.spaceShip)
        self.Sentinal2 = spaceJamClasses.Orbiter(self.loader, self.taskMgr,"./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet3, 300, "Cloud", self.spaceShip)
        self.Sentinal3 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 7.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet5, 400, "MLB", self.spaceShip)
        self.Sentinal4 = spaceJamClasses.Orbiter(self.loader, self.taskMgr,"./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 7.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Planet3, 400, "Cloud", self.spaceShip)
        self.Wanderer1 = spaceJamClasses.Wanderer(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.8, "./Assets/DroneDefender/octotoad1_auv.png", self.spaceShip)
        self.Wanderer2 = spaceJamClasses.AltWanderer(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.8, "./Assets/DroneDefender/octotoad1_auv.png", self.spaceShip)
    def drawBaseBallSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader,"./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    
    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader,"./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 10)
        
    # functions for circle x, y and z can be set similar to cloud and baseball seams since it is also a defense path
    # also takes in centralObject, droneName 
    # position of circles is small since planet it is attached to is small
    # drones are placed in a loop similar to warm up 1
    def DroneCircleX(self, centralObject, droneName, droneCircle):
        for i in range(60):
            spaceJamClasses.Drone.dronecount += 1
            droneName = "Drone" + str(spaceJamClasses.Drone.dronecount)
            unitVec = defensePaths.CircleX(droneCircle)
            unitVec.normalize()
            droneCircle = droneCircle + 1
            position = unitVec * 275 + centralObject.modelNode.getPos()
            spaceJamClasses.Drone(self.loader,"./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 4)

    def DroneCircleY(self, centralObject, droneName, droneCircle):
        for i in range(60):
            spaceJamClasses.Drone.dronecount += 1
            droneName = "Drone" + str(spaceJamClasses.Drone.dronecount)
            unitVec = defensePaths.CircleY(droneCircle)
            unitVec.normalize()
            droneCircle = droneCircle + 1
            position = unitVec * 275 + centralObject.modelNode.getPos()
            spaceJamClasses.Drone(self.loader,"./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 4)
        
    def DroneCircleZ(self, centralObject, droneName, droneCircle):
        for i in range(60):
            spaceJamClasses.Drone.dronecount += 1
            droneName = "Drone" + str(spaceJamClasses.Drone.dronecount)
            unitVec = defensePaths.CircleZ(droneCircle)
            unitVec.normalize()
            droneCircle = droneCircle + 1
            position = unitVec * 275 + centralObject.modelNode.getPos()
            spaceJamClasses.Drone(self.loader,"./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 4)
    
    
    def setCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.spaceShip.modelNode)
        self.camera.setFluidPos(0,1,0)


    def playMusic(self):
        backgroundMusic = base.loader.loadMusic("./Assets/Sounds/space_shooter.mp3")
        # audio belongs to Alex McCulloch on opengameart.org
        backgroundMusic.setLoop(True)
        backgroundMusic.setVolume(0.5)
        backgroundMusic.play()
        

app = MyApp()
app.run()