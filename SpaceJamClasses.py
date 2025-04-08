from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from CollideObjectBase import *
from direct.task.Task import TaskManager
import DefensePaths as defensePaths
from direct.interval.IntervalGlobal import Sequence






class Planet(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 1.09)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)


class Drone(SphereCollideObject):
    
    dronecount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.5)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)

        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)




class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
       super(Universe, self).__init__(loader,modelPath, parentNode, nodeName, Vec3(0,0,0), 0.9)
       self.modelNode.setPos(posVec)
       self.modelNode.setScale(scaleVec)

       self.modelNode.setName(nodeName)
       tex = loader.loadTexture(texPath)
       self.modelNode.setTexture(tex, 1)

class SpaceStation(CapsuleCollidableObject):
    
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 1, -1, 5, 1, -1, -5, 10)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

    stationHP = 3
       

class Missile(SphereCollideObject):

    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)
        self.modelNode.setName(nodeName)
        

        Missile.missileCount += 1
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        print("fire torpedo #" + str(Missile.missileCount))

    
class LargeMissile(SphereCollideObject):

    fireModels = {}
    AltcNodes = {}
    collisionSolids = {}
    AltIntervals = {}
    LargeMissileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
        super(LargeMissile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)

        LargeMissile.LargeMissileCount += 1
        LargeMissile.fireModels[nodeName] = self.modelNode
        LargeMissile.AltcNodes[nodeName] = self.collisionNode

        # for debugging

        LargeMissile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        LargeMissile.AltcNodes[nodeName].show()
        print("fire alternate torpedo #" + str(LargeMissile.LargeMissileCount))


class Orbiter(SphereCollideObject):
    numOrbits = 0
    velocity = 0.005
    cloudTimer = 240

    def __init__(self, loader: Loader, taskMgr: TaskManager, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, centralObject: PlacedObject, orbitRadius: float, orbitType: str, staringAt: Vec3):
        super(Orbiter, self,).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.2)

        self.taskMgr = taskMgr
        self.orbitType = orbitType
        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.orbitObject = centralObject
        self.orbitRadius = orbitRadius
        self.staringAt = staringAt
        Orbiter.numOrbits += 1
        self.cloudClock = 0

        self.taskFlag = "Traveler-" + str(Orbiter.numOrbits)
        taskMgr.add(self.Orbit, self.taskFlag)   

    def Orbit(self, task):
        if self.orbitType == "MLB":
            positionVec = defensePaths.BaseballSeams(task.time * Orbiter.velocity, self.numOrbits, 2.0)
            self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())

        elif self.orbitType == "Cloud":
            if self.cloudClock < Orbiter.cloudTimer:
                self.cloudClock += 1
        
            else: 
                self.cloudClock = 0
                positionVec = defensePaths.Cloud(1)
                self.modelNode.setPos(positionVec * self.orbitRadius + self.orbitObject.modelNode.getPos())


        self.modelNode.lookAt(self.staringAt.modelNode)
        return task.cont
    

class Wanderer(SphereCollideObject):
    numWanderers = 0
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, staringAt: Vec3):
        super(Wanderer, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.2)

        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.staringAT = staringAt
        Wanderer.numWanderers += 1


        posInterval0 = self.modelNode.posInterval(20, Vec3(300, 6000, 500), startPos = Vec3(0,0,0))
        posInterval1 = self.modelNode.posInterval(20, Vec3(700, -2000, 100), startPos = Vec3(300, 6000,500))
        posInterval2 = self.modelNode.posInterval(20, Vec3(0, -900, -1400), startPos = Vec3(700,-2000,100))

        self.travelRoute = Sequence(posInterval0, posInterval1, posInterval2, name = "Traveler")

        self.travelRoute.loop()


class Wanderer2(SphereCollideObject):
    numWanderers = 0
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, scaleVec: Vec3, texPath: str, staringAt: Vec3):
        super(Wanderer2, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.2)

        self.modelNode.setScale(scaleVec)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        self.staringAT = staringAt
        Wanderer.numWanderers += 1


        posInterval0 = self.modelNode.posInterval(30, Vec3(50, 4000, 250), startPos = Vec3(0,0,0))
        posInterval1 = self.modelNode.posInterval(30, Vec3(350, -1700, 250), startPos = Vec3(600, 1500, 750))
        posInterval2 = self.modelNode.posInterval(30, Vec3(-10, -250, -2000), startPos = Vec3(150,-1000,300))

        self.travelRoute = Sequence(posInterval0, posInterval1, posInterval2, name = "Traveler2")

        self.travelRoute.loop()

        






