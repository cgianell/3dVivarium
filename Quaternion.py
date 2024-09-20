'''
A Quaternion class, which includes basic Quaternion math operations

:author: micou(Zezhou Sun)
:version: 2021.1.1
'''
import time
import math
import numpy as np


class Quaternion:
    """
    Defines Quaternion object here, which includes several basic quaternion operations
    """
    # scalar component of this quaternion
    s = 0.0
    # vector components of this quaternion
    v = None

    def __init__(self, s=1, v0=0, v1=0, v2=0):
        self.v = [0, 0, 0]
        self.set(s, v0, v1, v2)

    def isNum(self, var):
        """
        Type checking if a variable is number
        :return: True if is number, Otherwise False
        :rtype: bool
        """
        return isinstance(var, int) or isinstance(var, float)

    def set(self, s, v0, v1, v2):
        """
        Set Quaternion Value for this one. Will apply type checking before the set
        :return: None
        """
        if (not self.isNum(s)) or (not self.isNum(v0)) or (not self.isNum(v1)) or (not self.isNum(v2)):
            raise TypeError("Incorrect type set for quaternion")
        self.s = s
        self.v[0] = v0
        self.v[1] = v1
        self.v[2] = v2
        
    def slerp(q1, q2, t):
        """
        Spherical linear interpolation between two quaternions.
    
        :param q1: The first quaternion
        :type q1: Quaternion
        :param q2: The second quaternion
        :type q2: Quaternion
        :param t: Interpolation parameter between 0 and 1
        :type t: float
        :return: Interpolated quaternion
        :rtype: Quaternion
        """
        # Ensure t is between 0 and 1
        t = max(0.0, min(t, 1.0))
    
        # Compute the cosine of the angle between the quaternions
        dot_product = q1.s * q2.s + q1.v[0] * q2.v[0] + q1.v[1] * q2.v[1] + q1.v[2] * q2.v[2]
    
        # Determine the direction of the interpolation
        if dot_product < 0:
            q2 = Quaternion(-q2.s, -q2.v[0], -q2.v[1], -q2.v[2])  # Ensure shortest path
    
        # Perform the spherical linear interpolation
        omega = math.acos(dot_product)
    
        # Check if sin_omega is close to zero
        tolerance = 1e-10
        if abs(math.sin(omega)) < tolerance:
            # Use linear interpolation instead
            scale_q1 = 1 - t
            scale_q2 = t
        else:
            sin_omega = math.sin(omega)
            scale_q1 = math.sin((1 - t) * omega) / sin_omega
            scale_q2 = math.sin(t * omega) / sin_omega
    
        # Interpolate scalar and vector components separately
        result = Quaternion(
            q1.s * scale_q1 + q2.s * scale_q2,
            q1.v[0] * scale_q1 + q2.v[0] * scale_q2,
            q1.v[1] * scale_q1 + q2.v[1] * scale_q2,
            q1.v[2] * scale_q1 + q2.v[2] * scale_q2
        )
    
        return result

    def multiply(self, q):
        """
        multiply with another Quaternion and return a new quaternion

        :return: a new Quaternion
        :rtype: Quaternion
        """
        if not isinstance(q, Quaternion):
            raise TypeError("Quaternion can only multiply Quaternion")
        # s = s1*s2 - v1.v2
        new_s = self.s * q.s - self.v[0] * q.v[0] - self.v[1] * q.v[1] - self.v[2] * q.v[2]
        # v = s1 v2 + s2 v1 + v1 x v2
        new_v0 = (self.s * q.v[0]) + (q.s * self.v[0]) + (self.v[1] * q.v[2] - self.v[2] * q.v[1])
        new_v1 = (self.s * q.v[1]) + (q.s * self.v[1]) + (self.v[2] * q.v[0] - self.v[0] * q.v[2])
        new_v2 = (self.s * q.v[2]) + (q.s * self.v[2]) + (self.v[0] * q.v[1] - self.v[1] * q.v[0])
        return Quaternion(new_s, new_v0, new_v1, new_v2)

    def norm(self):
        """
        Norm of this quaternion
        :return: norm of this quaternion
        :rtype: float
        """
        return math.sqrt(self.s * self.s + self.v[0] * self.v[0] + self.v[1] * self.v[1] + self.v[2] * self.v[2])

    def normalize(self):
        """
        Normalize this quaternion if this quaternion's norm if greater than 0
        :return: this quaternion
        :rtype: Quaternion
        """
        mag = self.norm()
        # Set a threshold for mag, to avoid divided by 0
        if mag > 1e-6:
            self.s /= mag
            self.v[0] /= mag
            self.v[1] /= mag
            self.v[2] /= mag
        return self

    def reset(self):
        """
        Reset this Quaternion. This is fast then rebuild a new Quaternion
        :return: None
        """
        self.s = 1
        self.v[0] = 0
        self.v[1] = 0
        self.v[2] = 0

    def toMatrix(self):
        """
        turn Quaternion to Matrix form(with numpy)
        :return: a (4, 4) matrix comes from current quaternion
        :rtype: numpy.ndarray
        """
        q_matrix = np.zeros((4, 4), dtype=np.float64)
        s = self.s
        a = self.v[0]
        b = self.v[1]
        c = self.v[2]
        q_matrix[0, 0] = 1 - 2 * b * b - 2 * c * c
        q_matrix[1, 0] = 2 * a * b + 2 * s * c
        q_matrix[2, 0] = 2 * a * c - 2 * s * b
        q_matrix[0, 1] = 2 * a * b - 2 * s * c
        q_matrix[1, 1] = 1 - 2 * a * a - 2 * c * c
        q_matrix[2, 1] = 2 * b * c + 2 * s * a
        q_matrix[0, 2] = 2 * a * c + 2 * s * b
        q_matrix[1, 2] = 2 * b * c - 2 * s * a
        q_matrix[2, 2] = 1 - 2 * a * a - 2 * b * b
        q_matrix[3, 3] = 1
        return q_matrix


if __name__ == "__main__":
    t1 = time.time()
    for _ in range(1000000):
        a = Quaternion()
    t2 = time.time()

    a = Quaternion(1, 1, 0, 0)
    b = Quaternion(1, 0, 1, 0)
    a.normalize()
    b.normalize()
    print(a.multiply(b))
    print(a.toMatrix())
    c = a.multiply(b).normalize()
    print(c.toMatrix())
    print("Cost time: ", t2 - t1)
