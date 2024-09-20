"""
All creatures should be added to Vivarium. Some help functions to add/remove creature are defined here.
Created on 20181028

:author: micou(Zezhou Sun)
:version: 2021.1.1

modified by Daniel Scrivener
"""

import numpy as np
import ModelLinkage as ml
from Point import Point
from Component import Component
from ModelTank import Tank
from EnvironmentObject import EnvironmentObject

class Vivarium(Component):
    """
    The Vivarium for our animation
    """
    components = None  # List
    parent = None  # class that have current context
    tank = None
    tank_dimensions = None

    ##### BONUS 5(TODO 5 for CS680 Students): Feed your creature
    # Requirements:
    #   Add chunks of food to the vivarium which can be eaten by your creatures.
    #     * When ‘f’ is pressed, have a food particle be generated at random within the vivarium.
    #     * Be sure to draw the food on the screen with an additional model. It should drop slowly to the bottom of
    #     the vivarium and remain there within the tank until eaten.
    #     * The food should disappear once it has been eaten. Food is eaten by the first creature that touches it.

    def __init__(self, parent, shaderProg):
        self.parent = parent
        self.shaderProg = shaderProg

        self.tank_dimensions = [12, 12, 12]
        tank = Tank(Point((0,0,0)), shaderProg, self.tank_dimensions)
        super(Vivarium, self).__init__(Point((0, 0, 0)))

        # Build relationship
        self.addChild(tank)
        self.tank = tank

        # Store all components in one list, for us to access them later
        self.components = [tank]

        self.addNewObjInTank(ml.Linkage(parent, Point((0,0,0)), shaderProg))
        self.addNewObjInTank(ml.Linkage2(parent, Point((2,2,2)), shaderProg))        
        self.addNewObjInTank(ml.Linkage2(parent, Point((0,2,0)), shaderProg))
        self.addNewObjInTank(ml.Linkage2(parent, Point((0,-2,0)), shaderProg))
        self.addNewObjInTank(ml.Linkage2(parent, Point((3,0,0)), shaderProg))
        self.addNewObjInTank(ml.Linkage2(parent, Point((-3,0,0)), shaderProg))
        self.addNewObjInTank(ml.Linkage2(parent, Point((-2,-2,-2)), shaderProg))
        
        # For testing
        self.addNewObjInTank(ml.Linkage(parent, Point((0,3,3)), shaderProg))
        #self.addNewObjInTank(ml.Linkage2(parent, Point((0,3,3)), shaderProg))        
        

    def animationUpdate(self):
        """
        Update all creatures in vivarium
        """
        # Create a list to store creatures that need to be removed
        creatures_to_remove = []
        
        for c in self.components[::-1]:
            if isinstance(c, EnvironmentObject):
                c.animationUpdate()
                c.stepForward(self.components, self.tank_dimensions, self)
                
                # Check if the creature should be removed
                if c.env_obj_list is not None and c not in c.env_obj_list:
                    creatures_to_remove.append(c)
                    
        # Remove creatures after the iteration
        for creature in creatures_to_remove:
            self.delObjInTank(creature)
        
        self.update()

    def delObjInTank(self, obj):
        if isinstance(obj, Component):
            try:
                self.tank.children.remove(obj)
                if obj in self.components:
                    self.components.remove(obj)
                del obj
            except ValueError:
                # Handle the case where obj is not found in the list
                pass

    def addNewObjInTank(self, newComponent):
        if isinstance(newComponent, Component):
            self.tank.addChild(newComponent)
            self.components.append(newComponent)
        if isinstance(newComponent, EnvironmentObject):
            # add environment components list reference to this new object's
            newComponent.env_obj_list = self.components

