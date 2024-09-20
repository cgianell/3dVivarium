"""
Model our creature and wrap it in one class
First version at 09/28/2021

:author: micou(Zezhou Sun)
:version: 2021.2.1

Modified by Daniel Scrivener 08/2022
"""
import random
import numpy as np
from Component import Component
from Shapes import Cube
from Shapes import Cylinder
from Shapes import Sphere
from Point import Point
from Quaternion import Quaternion
import ColorType as Ct
from EnvironmentObject import EnvironmentObject

try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")

##### TODO 1: Construct your two different creatures
# Requirements:
#   1. For the basic parts of your creatures, feel free to use routines provided with the previous assignment.
#   You are also free to create your own basic parts, but they must be polyhedral (solid).
#   2. The creatures you design should have moving linkages of the basic parts: legs, arms, wings, antennae,
#   fins, tentacles, etc.
#   3. Model requirements:
#         1. Predator: At least one (1) creature. Should have at least two moving parts in addition to the main body
#         2. Prey: At least two (2) creatures. The two prey can be instances of the same design. Should have at
#         least one moving part.
#         3. The predator and prey should have distinguishable different colors.
#         4. You are welcome to reuse your PA2 creature in this assignment.

class Linkage(Component, EnvironmentObject):
    """
    A Linkage with animation enabled and is defined as an object in environment
    """
    components = None
    rotation_speed = None
    translation_speed = None
    update_speed_frequency = 1000  # Adjust this value based on desired frequency

    def __init__(self, parent, position, shaderProg):
        super(Linkage, self).__init__(position)
        arm1 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)        
        arm2 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)
        arm2.setDefaultAngle(90, arm2.vAxis)
        arm3 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)
        arm3.setDefaultAngle(180, arm3.vAxis)
        arm4 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)
        arm4.setDefaultAngle(270, arm4.vAxis)
        #print(f"Shape types: {type(arm1)}, {type(arm2)}, {type(arm3)}, {type(arm4)}")
        head = ModelHead(parent, Point((0, 0, 0)), shaderProg, [0.35, 0.35, 0.35], True, Ct.DARKORANGE2)
        head2 = ModelHead(parent, Point((0, 0, 0)), shaderProg, [0.25, 0.25, 0.25], False, Ct.DARKORANGE3)

        self.components = arm1.components + arm2.components + arm3.components + arm4.components
        self.addChild(head2)
        self.addChild(head)
        self.addChild(arm1)
        self.addChild(arm2)
        self.addChild(arm3)
        self.addChild(arm4)

        self.rotation_speed = []
        for comp in self.components:

            comp.setRotateExtent(comp.uAxis, 0, 32)
            comp.setRotateExtent(comp.vAxis, -45, 45)
            comp.setRotateExtent(comp.wAxis, -45, 45)
            self.rotation_speed.append([0, 0, 0])

        # Uncomment this for bounce/eat testing            
        #self.translation_speed = Point((0.01, 0.01, 0.01))
        # self.translation_speed = Point([random.random()-0.5 for _ in range(3)]).normalize() * 0.01
        
        self.bound_center = Point((0, 0, 0))
        self.bound_radius = 0.1 * 5
        self.species_id = 1        
        
        # Counter to control the frequency of speed updates
        self.update_speed_counter = 0
        

    def animationUpdate(self):
        ##### TODO 2: Animate your creature!
        # Requirements:
        #   1. Set reasonable joints limit for your creature
        #   2. The linkages should move back and forth in a periodic motion, as the creatures move about the vivarium.
        #   3. Your creatures should be able to move in 3 dimensions, not only on a plane.   
        count = self.rotation_speed.count([0, 0, 0])
               
        if self.translation_speed is not None:
            for i in range(count):        
                # Check if the creature is moving
                if (self.translation_speed.coords.all() != 0):
                    # Adjust rotation speeds based on translation speed
                    self.rotation_speed[i] = [0.5, 0, 0]
        
        '''
        for i in range(count):
            self.rotation_speed[i] = [1, 0, 0]            
        '''        
        for i, comp in enumerate(self.components):
            comp.rotate(self.rotation_speed[i][0], comp.uAxis)
            comp.rotate(self.rotation_speed[i][1], comp.vAxis)
            comp.rotate(self.rotation_speed[i][2], comp.wAxis)
            if comp.uAngle in comp.uRange:  # rotation reached the limit
                self.rotation_speed[i][0] *= -1
            if comp.vAngle in comp.vRange:
                self.rotation_speed[i][1] *= -1
            if comp.wAngle in comp.wRange:
                self.rotation_speed[i][2] *= -1
        #self.vAngle = (self.vAngle + 3) % 360
        
        self.update()
        

        ##### BONUS 6: Group behaviors
        # Requirements:
        #   1. Add at least 5 creatures to the vivarium and make it possible for creatures to engage in group behaviors,
        #   for instance flocking together. This can be achieved by implementing the
        #   [Boids animation algorithms](http://www.red3d.com/cwr/boids/) of Craig Reynolds.

        self.update()

    def stepForward(self, components, tank_dimensions, vivarium):
        ##### TODO 3: Interact with the environment
        # Requirements:
        #   1. Your creatures should always stay within the fixed size 3D "tank". You should do collision detection
        #   between the creature and the tank walls. When it hits the tank walls, it should turn and change direction to stay
        #   within the tank.
        #   2. Your creatures should have a prey/predator relationship. For example, you could have a bug being chased
        #   by a spider, or a fish eluding a shark. This means your creature should react to other creatures in the tank.
        #       1. Use potential functions to change its direction based on other creatures’ location, their
        #       inter-creature distances, and their current configuration.
        #       2. You should detect collisions between creatures.
        #           1. Predator-prey collision: The prey should disappear (get eaten) from the tank.
        #           2. Collision between the same species: They should bounce apart from each other. You can use a
        #           reflection vector about a plane to decide the after-collision direction.
        #       3. You are welcome to use bounding spheres for collision detection.   
                
        # Increment the counter on each step
        self.update_speed_counter += 1

        # Update speed when the counter reaches the desired frequency
        if self.update_speed_counter >= self.update_speed_frequency:
            # Get a new random direction
            new_direction = Point([random.random()-0.5 for _ in range(3)])
            new_direction.normalize()
            
            # Set the translation speed based on the new direction
            self.translation_speed = new_direction * 0.03
            
            # Use the rotateDirection function to set the new orientation
            self.rotateDirection(new_direction)               
            
            # Reset the counter
            self.update_speed_counter = 0
             
        if self.currentPos and self.translation_speed is not None:
            # Update translation
            new_position = self.currentPos + self.translation_speed
                
            # Check collision with tank walls
            tank_center = Point((0, 0, 0))
            
            # Calculate distance to tank center
            distance_to_tank_center = new_position.distance(tank_center)
            
            # Check for collision with tank walls (considering it as a sphere)
            if distance_to_tank_center + self.bound_radius > max(tank_dimensions) / 2:
                # Calculate the reflection direction based on the normal vector at the collision point
                reflection_direction = (tank_center - new_position).normalize()
            
                # Reverse the direction component that caused the collision
                self.translation_speed -= 2 * reflection_direction.dot(self.translation_speed) * reflection_direction
            
                # Use the reflected direction to update the orientation
                self.rotateDirection(self.translation_speed)
                
            # Update translation based on collision resolution
            self.currentPos += self.translation_speed 
            
            # Check for collisions with other creatures in the env_obj_list
            for other_creature in self.env_obj_list:                
                if other_creature != self:
                    if isinstance(other_creature, EnvironmentObject):
                        distance_to_other = self.currentPos.distance(other_creature.currentPos)
                        # Potential functions to check for nearby prey
                        if distance_to_other < (3 * self.bound_radius) and other_creature.species_id == 2:
                            # Predator-prey interaction: Change direction to move toward the prey
                            direction_to_prey = (other_creature.currentPos - self.currentPos).normalize()
                            print("Chasing the prey!")
                            # Update translation speed and orientation to move toward the prey
                            self.translation_speed = direction_to_prey * 0.03
                            self.rotateDirection(direction_to_prey)                    
                            
                        
                        if distance_to_other < self.bound_radius + other_creature.bound_radius:
                            # Handle collision response based on the relationship (predator-prey or same species)
                            if self.species_id == other_creature.species_id:
                                # Bounce apart from each other
                                # Calculate the reflection direction based on the normal vector at the collision point
                                reflection_direction = (other_creature.currentPos - self.currentPos).normalize()
                    
                                # Reverse the direction component that caused the collision for both creatures
                                self.translation_speed -= 2 * reflection_direction.dot(self.translation_speed) * reflection_direction
                                other_creature.translation_speed -= 2 * reflection_direction.dot(other_creature.translation_speed) * reflection_direction
                    
                                # Use the reflected direction to update the orientation for both creatures
                                self.rotateDirection(self.translation_speed)
                                other_creature.rotateDirection(other_creature.translation_speed)
                                print("I bounced")
                            else:
                                # Predator-prey collision: The prey should disappear (get eaten)
                                pass    
            
        '''
        # Check collision with tank walls
        for i in range(3):
            if new_position[i] < -tank_dimensions[i] / 2 or new_position[i] > tank_dimensions[i] / 2:
                # Reverse the direction component that caused the collision
                self.translation_speed = Point([-coord if i == j else coord for j, coord in enumerate(self.translation_speed.coords)])
                
                # Use the reflected direction to update the orientation
                self.rotateDirection(self.translation_speed)
        '''     
        
        self.update()
    
class Linkage2(Component, EnvironmentObject):
    """
    A Linkage with animation enabled and is defined as an object in environment
    """
    components = None
    rotation_speed = None
    translation_speed = None
    update_speed_frequency = 1000  # Adjust this value based on desired frequency

    def __init__(self, parent, position, shaderProg):
        super(Linkage2, self).__init__(position)
        body = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)                
        head3 = ModelHead(parent, Point((0, 0, 0)), shaderProg, [0.25, 0.25, 0.25], False, Ct.DARKORANGE2)
        
        self.components = body.components + head3.components
        self.addChild(body)
        self.addChild(head3)

        self.rotation_speed = []        
        for comp in self.components:

            comp.setRotateExtent(comp.uAxis, -30, 30)
            comp.setRotateExtent(comp.vAxis, -45, 45)
            comp.setRotateExtent(comp.wAxis, -90, 90)            
            # change to [1, 0, 0] for eating test
            self.rotation_speed.append([0, 0, 0])        
        
        # Uncomment this for bounce testing            
        #self.translation_speed = Point((0.01, 0.01, 0.01))
        
        self.bound_center = Point((0, 0, 0))
        self.bound_radius = 0.1 * 2
        self.species_id = 2
        
        # Append the current instance to the env_obj_list
        self.env_obj_list.append(self)        
        # Counter to control the frequency of speed updates
        self.update_speed_counter = 0
        # Initialize slerp_frame_counter
        self.slerp_frame_counter = 0
        # Frames
        self.slerp_duration_frames = 60
        
    def animationUpdate(self):
        ##### TODO 2: Animate your creature!
        # Requirements:
        #   1. Set reasonable joints limit for your creature
        #   2. The linkages should move back and forth in a periodic motion, as the creatures move about the vivarium.
        #   3. Your creatures should be able to move in 3 dimensions, not only on a plane.
        
        # Update animation speed depending on movement direction                                
        count = self.rotation_speed.count([0, 0, 0])
               
        if self.translation_speed is not None:
            for i in range(count):        
                # Check if the creature is moving
                if (self.translation_speed.coords.all() != 0):
                    # Adjust rotation speeds based on translation speed
                    self.rotation_speed[i] = [0, 1, 0]
        
        '''
        for i in range(count):
            self.rotation_speed[i] = [1, 0, 0]            
        '''        
        for i, comp in enumerate(self.components):
            comp.rotate(self.rotation_speed[i][0], comp.uAxis)
            comp.rotate(self.rotation_speed[i][1], comp.vAxis)
            comp.rotate(self.rotation_speed[i][2], comp.wAxis)
            if comp.uAngle in comp.uRange:  # rotation reached the limit
                self.rotation_speed[i][0] *= -1
            if comp.vAngle in comp.vRange:
                self.rotation_speed[i][1] *= -1
            if comp.wAngle in comp.wRange:
                self.rotation_speed[i][2] *= -1
        #self.vAngle = (self.vAngle + 3) % 360
        
        self.update()

    def stepForward(self, components, tank_dimensions, vivarium):
        ##### TODO 3: Interact with the environment
        # Requirements:
        #   1. Your creatures should always stay within the fixed size 3D "tank". You should do collision detection
        #   between the creature and the tank walls. When it hits the tank walls, it should turn and change direction to stay
        #   within the tank.
        #   2. Your creatures should have a prey/predator relationship. For example, you could have a bug being chased
        #   by a spider, or a fish eluding a shark. This means your creature should react to other creatures in the tank.
        #       1. Use potential functions to change its direction based on other creatures’ location, their
        #       inter-creature distances, and their current configuration.
        #       2. You should detect collisions between creatures.
        #           1. Predator-prey collision: The prey should disappear (get eaten) from the tank.
        #           2. Collision between the same species: They should bounce apart from each other. You can use a
        #           reflection vector about a plane to decide the after-collision direction.
        #       3. You are welcome to use bounding spheres for collision detection.   
        
        # Increment the counter on each step
        self.update_speed_counter += 1

        # Update speed when the counter reaches the desired frequency
        if self.update_speed_counter >= self.update_speed_frequency:
            # Get a new random direction
            new_direction = Point([random.random()-0.5 for _ in range(3)])
            new_direction.normalize()
            
            # Set the translation speed based on the new direction
            self.translation_speed = new_direction * 0.03
            
            # Use the rotateDirection function to set the new orientation
            self.rotateDirection(new_direction)               
            
            # Reset the counter
            self.update_speed_counter = 0
             
        if self.currentPos and self.translation_speed is not None:
            # Update translation
            new_position = self.currentPos + self.translation_speed
        
            # Check collision with tank walls
            tank_center = Point((0, 0, 0))  # Assuming the tank is centered at the origin
            
            # Calculate distance to tank center
            distance_to_tank_center = new_position.distance(tank_center)
            
            # Check for collision with tank walls (considering it as a sphere)
            if distance_to_tank_center + self.bound_radius > max(tank_dimensions) / 2:
                # Calculate the reflection direction based on the normal vector at the collision point
                reflection_direction = (tank_center - new_position).normalize()
            
                # Reverse the direction component that caused the collision
                self.translation_speed -= 2 * reflection_direction.dot(self.translation_speed) * reflection_direction
            
                # Use the reflected direction to update the orientation
                self.rotateDirection(self.translation_speed)
        
            # Update translation based on collision resolution
            self.currentPos += self.translation_speed
        
            # Check for collisions with other creatures in the env_obj_list
            for other_creature in self.env_obj_list:
                if other_creature != self:
                    if isinstance(other_creature, EnvironmentObject):
                        distance_to_other = self.currentPos.distance(other_creature.currentPos)
                        # Check for collision with other creatures (considering bounding spheres)
                        if distance_to_other < self.bound_radius + other_creature.bound_radius:
                            # Handle collision response based on the relationship (predator-prey or same species)
                            if self.species_id == other_creature.species_id:
                                # Bounce apart from each other
                                # Calculate the reflection direction based on the normal vector at the collision point
                                reflection_direction = (other_creature.currentPos - self.currentPos).normalize()
                    
                                # Reverse the direction component that caused the collision for both creatures
                                self.translation_speed -= 2 * reflection_direction.dot(self.translation_speed) * reflection_direction
                                other_creature.translation_speed -= 2 * reflection_direction.dot(other_creature.translation_speed) * reflection_direction
                    
                                # Use the reflected direction to update the orientation for both creatures
                                self.rotateDirection(self.translation_speed)
                                other_creature.rotateDirection(other_creature.translation_speed)
                                print("I bounced")
                            else:
                                # Predator-prey collision: The prey should disappear (get eaten)
                                self.env_obj_list.remove(self)
                                print("i got eaten")
        
            '''
            # Check for interactions with other creatures in the vivarium
            for creature in self.components:
                if creature != self and isinstance(creature, EnvironmentObject):
                    distance = self.currentPos.distance(creature.currentPos)
                    print("Distance:", distance)
                    print("Bounding Radii:", self.bound_radius, creature.bound_radius)
                    if distance < self.bound_radius + creature.bound_radius:
                        # Handle interactions between creatures (e.g., bouncing off or predator-prey relationship)
                        relative_position = creature.currentPos - self.currentPos
                        relative_distance = relative_position.norm()
                        print("i got here")
                        
                        # Potential function to determine the direction based on relative position
                        potential_direction = relative_position.normalize() * (1.0 / relative_distance)
                        
                        # Check if it's the same species
                        if self.species_id == creature.species_id:
                            # Collision between the same species: Bounce apart
                            # Use a reflection vector about a plane to decide the after-collision direction
                            reflection_direction = relative_position - 2 * relative_position.dot(potential_direction) * potential_direction
                            self.translation_speed += reflection_direction * 0.03
                            print("i tried to bounce")
                        else:
                            # Predator-prey relationship
                            # The prey should disappear (get eaten) from the tank
                            self.creatures_to_remove.append(creature)
                            print("i got eaten")
                            
                        # Update translation based on collision resolution
                        self.currentPos += self.translation_speed
            '''
                    
        self.update()

class ModelArm(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, color1=None, color2=Ct.DARKORANGE2, color3=Ct.DARKORANGE3, color4=Ct.DARKORANGE4, linkageLength=0.5, display_obj=None):
        if not isinstance(color1, Ct.ColorType):
            color1 = Ct.DARKORANGE1        
        super().__init__(position, display_obj)
        self.components = []
        self.contextParent = parent

        link1 = Cube(Point((0, 0, 0)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], color1)
        link2 = Cube(Point((0, 0, linkageLength)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], color2)
        link3 = Cube(Point((0, 0, linkageLength)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], color3)
        link4 = Cube(Point((0, 0, linkageLength)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], color4)

        self.addChild(link1)
        link1.addChild(link2)
        link2.addChild(link3)
        link3.addChild(link4)

        self.components = [link1, link2, link3, link4]

class ModelHead(Component):
    components = None
    contextParent = None
    
    def __init__(self, parent, position, shaderProg, size, isCube=True, color=Ct.GREEN, display_obj=None):        
        super().__init__(position, display_obj)
        self.components = []
        self.contextParent = parent
        if isCube:
            head = Cube(Point((0, 0, 0)), shaderProg, size, color)
        else:            
            head = Sphere(Point((0, 0, 0)), shaderProg, size, color)
        
        self.addChild(head)
        
        self.components = [head]