from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, TransparencyAttrib, CollisionTraverser, CollisionHandlerEvent, CollisionSphere
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from SpaceJamClasses import LargeMissile
from direct.gui.OnscreenImage import OnscreenImage

from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
# Regex module import for string editing
import re
from SpaceJamClasses import SpaceStation



class SpaceShip(SphereCollideObject):
    def __init__(self, loader: Loader, traverser: CollisionTraverser, manager: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):

        super(SpaceShip, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3)
        self.accept = accept
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        self.taskMgr = manager
        self.loader = loader

        self.render = parentNode
        self.setKeyBinding()
        self.reloadTime = .25
        self.BoostCooldownTime = .85 # boost cooldown longer than bullet reload
        self.missileDistance = 4000 # until the missile explodes
        self.missileBay = 1 # only one missile in the missile bay to be launched
        self.dualmissileBay = 1 # should only fire if two keys are pressed
        self.altMissileBay = 1
        self.numBoosts = 1 # number of boosts availiable like with missiles

        self.altmissileDistance = 2500 # shorter distance since bullet is larger
        self.altReloadTime = .50 # longer reload time

        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)
        self.taskMgr.add(self.CheckAltIntervals, 'checkLargeMissiles', 50)
        self.EnableHud()
        self.cntExplode = 0
        self.explodeIntervals = {}
        self.altExplodeIntervals = {}
        
        self.traverser = traverser
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')
        self.explodeSound = base.loader.loadSfx("./Assets/Sounds/DeathFlash.flac")
        self.missileSound = base.loader.loadSfx("./Assets/Sounds/sfx_shoot.wav")
        self.altMissileSound = base.loader.loadSfx("./Assets/Sounds/rlauncher.ogg")
        #all missile sounds found on opengameart.org
        self.boostSound = base.loader.loadSfx("./Assets/Sounds/engine3.wav")
        #Space ship engine sounds by Tuomo Untinen on opengameart.org
    
    
        
       
        


    def Thrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyThrust,'forward-thrust')
        else:
            self.taskMgr.remove('forward-thrust')

    def applyThrust(self,task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont
    
    def Boost(self, keydown):
        if keydown:
            self.taskMgr.add(self.ApplyBoost, 'accelerate')
        else:
            self.taskMgr.remove('accelerate')


    def ApplyBoost(self, task):
        if self.numBoosts == 1:
        #rate should be must faster than normal movement
            rate = 500
        # still moves ship forward just like thrust

            trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
            trajectory.normalize()
            self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
            self.boostSound.play()

            self.numBoosts = self.numBoosts - 1

            return Task.done
        
        else:
            if not self.taskMgr.hasTaskNamed('cooldown'):
                print('initialize cooldown')
                self.taskMgr.doMethodLater(0, self.BoostCooldown, 'cooldown')
                return Task.cont
    
    def BoostCooldown(self, task):
        # similar to the reloading method used for the missiles

        if task.time > self.BoostCooldownTime:
            self.numBoosts += 1

            if self.numBoosts > 1:
                self.numBoosts = 1

            print('boost is ready to use')

            return Task.done
        
        elif task.time <= self.BoostCooldownTime:
            print('boost in cooldown...')

            return Task.cont


    

    def setKeyBinding(self):
        #all key bindings here
        self.accept('space',self.Thrust, [1])
        self.accept('space-up',self.Thrust, [0])

        self.accept('arrow_left', self.LeftTurn, [1])
        self.accept('arrow_left-up', self.LeftTurn, [0])

        self.accept('arrow_right', self.RightTurn, [1])
        self.accept('arrow_right-up', self.RightTurn, [0])

        self.accept('arrow_up', self.TurnUp, [1])
        self.accept('arrow_up-up', self.TurnUp, [0])

        self.accept('arrow_down', self.TurnDown, [1])
        self.accept('arrow_down-up', self.TurnDown, [0])

        self.accept('a', self.RollLeft, [1])
        self.accept('a-up', self.RollLeft, [0])

        self.accept('s', self.RollRight, [1])
        self.accept('s-up', self.RollRight, [0])

        self.accept('f', self.Fire)
        self.accept('l', self.AltFire)
        self.accept('k', self.DuoFire)

        self.accept('shift', self.Boost, [1])
        

    def LeftTurn(self,keyDown):
        if keyDown:
            self.taskMgr.add(self.applyLeftTurn, 'left-turn')

        else:
            self.taskMgr.remove('left-turn')

    def applyLeftTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)

        return Task.cont
    # turn right
    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRightTurn, 'right-turn')

        else:
            self.taskMgr.remove('right-turn')

    def applyRightTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() - rate)

        return Task.cont



    #turn up

    def TurnUp(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyTurnUp, 'up-turn')

        else:
            self.taskMgr.remove('up-turn')

    def applyTurnUp(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() + rate)

        return Task.cont

    #turn down

    def TurnDown(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyTurnDown, 'down-turn')

        else:
            self.taskMgr.remove('down-turn')

    def applyTurnDown(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() - rate)

        return Task.cont

    #roll right

    def RollRight(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRollRight, 'roll-right')

        else:
            self.taskMgr.remove('roll-right')

    def applyRollRight(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() - rate)

        return Task.cont

    #roll left

    def RollLeft(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRollLeft, 'roll-left')

        else:
            self.taskMgr.remove('roll-left')

    def applyRollLeft(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() + rate)

        return Task.cont
    
    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # the direction the spaceship is facing
            # normalize to avoid math mistakes
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150 - 50
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile'+ str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront # spawn missile in front of nose of ship
            currentMissile = Missile(self.loader,'./Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)
            self.missileSound.play()

         
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
            
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
    
            
            

        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('initialize reload')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont
            
    def DuoFire(self):
        if self.dualmissileBay:
            dualTravRate = self.missileDistance
            dualAim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) #also in forward direction
            dualAim.normalize()
            dualFireSolution = dualAim * dualTravRate
            DualDirection = dualAim * 150 + 25
            dualTravVec = dualFireSolution + self.modelNode.getPos()
            self.dualmissileBay -= 1
            dualTag = 'Missile'+ str(Missile.missileCount)
            dualPosVec = self.modelNode.getPos() + DualDirection
            dualMissile = Missile(self.loader,'./Assets/Phaser/phaser.egg', self.render, dualTag, dualPosVec, 4.0)
            self.missileSound.play()
            self.traverser.addCollider(dualMissile.collisionNode, self.handler)
            Missile.Intervals[dualTag] = dualMissile.modelNode.posInterval(2.0, dualTravVec, startPos = dualPosVec, fluid = 1)
            Missile.Intervals[dualTag].start()

        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('initialize reload')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

            

    def AltFire(self):
        if self.altMissileBay:
            travRate = self.altmissileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # the direction the spaceship is facing
            # normalize to avoid math mistakes
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 200
            travVec = fireSolution + self.modelNode.getPos()
            self.altMissileBay -= 1
            tag = 'LargeMissile'+ str(LargeMissile.LargeMissileCount)
            posVec = self.modelNode.getPos() + inFront # spawn missile in front of nose of ship
            currentMissile = LargeMissile(self.loader,'./Assets/Phaser/phaser.egg', self.render, tag, posVec, 8.0)
            self.altMissileSound.play()
            LargeMissile.AltIntervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            LargeMissile.AltIntervals[tag].start()

            self.traverser.addCollider(currentMissile.collisionNode, self.handler)

        else:
            if not self.taskMgr.hasTaskNamed('altreload'):
                print('initialize   large missile reload')
                self.taskMgr.doMethodLater(0, self.AltReload, 'altreload')
                return Task.cont

            

    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 2
            self.dualmissileBay += 2

            if self.missileBay > 2 and self.dualmissileBay > 2:
                self.missileBay = 2
                self.dualmissileBay = 2
        

            print('reload complete')

            return Task.done
        
        elif task.time <= self.reloadTime:
            print('reload proceeding...')

            return Task.cont
        

    def AltReload(self, task):
        if task.time > self.altReloadTime:
            self.altMissileBay += 1

            if self.altMissileBay > 1:
                self.altMissileBay = 1
        

            print('reload complete')

            return Task.done
        
        elif task.time <= self.altReloadTime:
            print('reload proceeding...')

            return Task.cont
        

    def CheckIntervals(self, tasK):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]

                print(i + ' has reached the end of its fire solution')

                break
                
        return Task.cont
    

    def CheckAltIntervals(self, tasK):
        for i in LargeMissile.AltIntervals:
            if not LargeMissile.AltIntervals[i].isPlaying():
                LargeMissile.AltcNodes[i].detachNode()
                LargeMissile.fireModels[i].detachNode()

                del LargeMissile.AltIntervals[i]
                del LargeMissile.fireModels[i]
                del LargeMissile.AltcNodes[i]
                del LargeMissile.collisionSolids[i]

                print(i + ' has reached the end of its fire solution')

                break
                
        return Task.cont
    

    def EnableHud(self):
        self.Hud = OnscreenImage(image = './Assets/HUD/center.png', pos = Vec3(0,0,0), scale = 0.3)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

    def HandleInto(self, entry):

        fromNode = entry.getFromNodePath().getName()
        #print("fromNode: " + fromNode)

        intoNode = entry.getIntoNodePath().getName()
        #print("intoNode: " + intoNode)

        intoPosition = Vec3(entry.getSurfacePoint(self.render))
        tempVar = fromNode.split('_')

        #print("tempVar: " + str(tempVar))
        shooter = tempVar[0]
        #print("Shooter: " + str(shooter))
        tempVar = intoNode.split('-')
        #print("tempVar1: " + str(tempVar))
        tempVar = intoNode.split('_')
        #print('tempVar2: ' + str(tempVar))
        victim = tempVar[0]
        #print("Victim: " + str(victim))

        strippedString = re.sub(r'[0-9]', '', victim)
        #gameObjects = ["Station", "Drone","Planet"]


        if (strippedString == "Station"):
       
            #print(victim, ' hit at ', intoPosition)
            self.checkStationHP(victim)
            #self.DestroyObject(victim, intoPosition)

            if shooter in LargeMissile.AltIntervals:
                LargeMissile.AltIntervals[shooter].finish() 
            
            else: 
                Missile.Intervals[shooter].finish()

        
            
        elif (strippedString == "Drone" or strippedString == "Planet" ):
            #print(victim, ' hit at ', intoPosition)
            
            
             
            if shooter in LargeMissile.AltIntervals:
                #print("alt intervals called")
                self.AltDestroyObject(victim, intoPosition)
                LargeMissile.AltIntervals[shooter].finish()  
            
            else:
                self.DestroyObject(victim, intoPosition)
                #print("missile.intervals called")
                Missile.Intervals[shooter].finish()



    
        print(shooter + ' is done.')
        


    def DestroyObject(self, hitID, hitPosition):
    
        nodeID = self.render.find(hitID)
        nodeID.detachNode()
        self.setParticles()
        self.explodeNode.setPos(hitPosition)
        self.Explode()
        self.explodeSound.play()
        

    
    def checkStationHP(self, victim):
        if SpaceStation.stationHP > 1:
            SpaceStation.stationHP -= 1
            print("stationHP reduced " + str(SpaceStation.stationHP))
            self.shrinkSize = 5
            stationID = self.render.find(victim)
            stationID.setScale(stationID.getScale() - self.shrinkSize)
           
                


        else:
            stationID = self.render.find(victim)
            stationID.detachNode()

        
    def AltDestroyObject(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()
    
        self.setAltParticles()
        self.explodeNode.setPos(hitPosition)
        self.AltExplode()
        self.explodeSound.play()

   

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
        self.explodeIntervals[tag].start()

    def AltExplode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.altExplodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 6.0)
        self.altExplodeIntervals[tag].start()


    
    def ExplodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    
    def setParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig('./Assets/Part-Efx/basic_xpld_efx.ptf')
        self.explodeEffect.setScale(20)
        
        

    def setAltParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig('./Assets/Part-Efx/basic_xpld_efx.ptf')
        self.explodeEffect.setScale(80)

    
        

        

                
        
        

        
    


                                



