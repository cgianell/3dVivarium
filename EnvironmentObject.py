'''
Define Our class which is stores collision detection and environment information here
Created on Nov 1, 2018

:author: micou(Zezhou Sun)
:version: 2021.1.1

modified by Daniel Scrivener 08/2022
'''

import math
from Point import Point
from Quaternion import Quaternion
import numpy as np


class EnvironmentObject:
    """
    Define properties and interface for a object in our environment
    """
    env_obj_list = []  # list<Environment>
    item_id = 0
    species_id = 0

    bound_radius = None
    bound_center = Point((0,0,0))
    first_rotation = True
    
    should_be_removed = False

    def addCollisionObj(self, a):
        """
        Add an environment object for this creature to interact with
        """
        if isinstance(a, EnvironmentObject):
            self.env_obj_list.append(a)

    def rmCollisionObj(self, a):
        """
        Remove an environment object for this creature to interact with
        """
        if isinstance(a, EnvironmentObject):
            self.env_obj_list.remove(a)

    def animationUpdate(self):
        """
        Perform the next frame of this environment object's animation.
        """
        self.update()

    def stepForward(self):
        """
        Have this environment object take a step forward in the simulation.
        """
        return

    ##### TODO 4: Eyes on the road!
        # Requirements:
        #   1. Creatures should face in the direction they are moving. For instance, a fish should be facing the
        #   direction in which it swims. Remember that we require your creatures to be movable in 3 dimensions,
        #   so they should be able to face any direction in 3D space.
        
    def rotateDirection(self, v1):
        """
        change this environment object's orientation to v1.
        :param v1: targed facing direction
        :type v1: Point
        """
        # Current facing direction when creating creature is along z axis
        current_direction = Point([0, 0, 1])
        # Normalize the target direction
        target_direction = v1.normalize()
    
        # Calculate the rotation quaternion to rotate from the current direction to the target direction
        rotation_axis = current_direction.cross3d(target_direction).normalize()
        rotation_angle = math.acos(current_direction.dot(target_direction))
    
        # Directly compute the rotation matrix
        s = math.cos(rotation_angle / 2.0)
        v0 = (rotation_axis[0] * math.sin(rotation_angle / 2.0))
        v1 = (rotation_axis[1] * math.sin(rotation_angle / 2.0))
        v2 = (rotation_axis[2] * math.sin(rotation_angle / 2.0))
        
        # Apply the rotation to the object's orientation
        rotation_matrix = Quaternion(s, v0, v1, v2).toMatrix()
        self.setPostRotation(rotation_matrix)
        
        # Create quaternions for the current and target orientations
        #current_quaternion = Quaternion(1, 0, 0, 0)  # Identity quaternion for the current orientation
        #target_quaternion = Quaternion(s, v0, v1, v2)
        
        # Use slerp to interpolate between the current and target quaternions
        #interpolated_quaternion = Quaternion.slerp(current_quaternion, target_quaternion, 0.5)
    
        # Apply the rotation to the object's orientation
        #rotation_matrix = interpolated_quaternion.toMatrix()
        #self.setPostRotation(rotation_matrix)
        
        if self.species_id == 1:
            # Rotate the entire object by 90 degrees around the x-axis
            if self.first_rotation:
                self.rotate(90, Point((1, 0, 0)))
                # Set the flag to False after the first rotation
                self.first_rotation = False
        
        if self.species_id == 2:
            # Rotate the entire object by 180 degrees around the x-axis
            if self.first_rotation:
                self.rotate(180, Point((1, 0, 0)))
                # Set the flag to False after the first rotation
                self.first_rotation = False
        