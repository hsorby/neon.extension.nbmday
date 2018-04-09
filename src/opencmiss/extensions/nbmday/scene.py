
import numpy as np

from itertools import starmap
from math import sqrt, cos, sin, pi
from operator import mul


class Scene(object):

    def __init__(self, model):
        self._model = model
        self._projection_values_field = None
        self._mandible_fieldmodule = None
        self._mandible_fieldcache = None
        self._create_scene()
        print(get_jaw_rotation_test(90 / 180.0 * pi))

    def _create_scene(self):
        for region_name in ["cranium", "maxilla_teeth", "mandible_teeth"]:
            region = getattr(self._model, "get_%s_region" % region_name)()

            fieldmodule = region.getFieldmodule()
            fieldmodule.beginChange()
            self._projection_values_field = fieldmodule.createFieldConstant([1, 0, 0, 0,
                                                                             0, 1, 0, 0,
                                                                             0, 0, 1, 0,
                                                                             0, 0, 0, 1])
            coordinates_field = fieldmodule.findFieldByName('coordinates')
            offset_field = fieldmodule.createFieldConstant([0, -26, 47])
            offset_coordinates_field = fieldmodule.createFieldAdd(coordinates_field, offset_field)
            if region_name == "mandible_teeth":
                self._angle_field = fieldmodule.createFieldConstant(0.0)
                zero_field = fieldmodule.createFieldConstant(0)
                one_field = fieldmodule.createFieldConstant(1)
                minus_one = fieldmodule.createFieldConstant(-1)
                sin_field = fieldmodule.createFieldSin(self._angle_field)
                cos_field = fieldmodule.createFieldCos(self._angle_field)
                minus_sin_field = fieldmodule.createFieldMultiply(sin_field, minus_one)
                self._mandible_fieldmodule = fieldmodule
                self._mandible_fieldcache = fieldmodule.createFieldcache()
                transform_coordinates_field = fieldmodule.createFieldConcatenate([one_field, zero_field, zero_field, zero_field,
                                                                                zero_field, cos_field, sin_field, zero_field,
                                                                                zero_field, minus_sin_field, cos_field, zero_field,
                                                                                zero_field, zero_field, zero_field, one_field])
            fieldmodule.endChange()

            scene = region.getScene()
            scene.beginChange()
            surface = scene.createGraphicsSurfaces()
            surface.setCoordinateField(offset_coordinates_field)
            if region_name == "mandible_teeth":
                scene.setTransformationField(transform_coordinates_field)
            scene.endChange()

    def update_angle(self, angle):
        self._mandible_fieldmodule.beginChange()
        self._angle_field.assignReal(self._mandible_fieldcache, angle)
        self._mandible_fieldmodule.endChange()


def matrix_multiply(first, second):
    return [[sum(starmap(mul, zip(row, col))) for col in zip(*second)] for row in first]


def mx_mult(a, b):
    """
    Multiply 2 matrices: first index is down row, second is across column.
    Assumes sizes are compatible.
    """
    return [vector_mx_mult(row_a, b) for row_a in a]


def vector_mx_mult(v, m):
    """
    Pre-multiply matrix m by vector v
    """
    rows = len(m)
    if len(v) != rows:
        raise ValueError('vectormatmult mismatched rows')
    columns = len(m[0])
    result = []
    for c in range(0, columns):
        result.append(sum(v[r]*m[r][c] for r in range(rows)))
    return result


def get_jaw_rotation(angle):
    p1 = Point(53.995, 28.13, -40.59)
    p2 = Point(53.995, 28.015, -40.245)

    N = p2 - p1
    L = sqrt(N.x ** 2 + N.y ** 2 + N.z ** 2)
    V = sqrt(N.y ** 2 + N.z ** 2)
    A = N.x
    B = N.y
    C = N.z

    p0 = Point(-53.995, -28.13, 40.59)

    third = [[1, 0, 0, -p1.x],
             [0, 1, 0, -p1.y],
             [0, 0, 1, -p1.z],
             [0, 0, 0, 1]]

    second = [[1, 0, 0, 0],
              [0, C/V, -B/V, 0],
              [0, B/V, C/V, 0],
              [0, 0, 0, 1]]

    first = [[V/L, 0, -A/L, 0],
             [0, 1, 0, 0],
             [A/L, 0, V/L, 0],
             [0, 0, 0, 1]]

    r_theta = [[cos(angle), -sin(angle), 0, 0],
               [sin(angle), cos(angle), 0, 0],
               [0, 0, 1, 0],
               [0, 0, 0, 1]]

    r_y_inv = [[V/L, 0, A/L, 0],
               [0, 1, 0, 0],
               [-A/L, 0, V/L, 0],
               [0, 0, 0, 1]]

    r_x_inv = [[1, 0, 0, 0],
               [0, C/V, B/V, 0],
               [0, -B/V, C/V, 0],
               [0, 0, 0, 1]]

    D_inv = [[1, 0, 0, p1.x],
             [0, 1, 0, p1.y],
             [0, 0, 1, p1.z],
             [0, 0, 0, 1]]

    result = matrix_multiply(first, second)
    result = matrix_multiply(result, third)
    result = matrix_multiply(r_theta, result)
    result = matrix_multiply(r_y_inv, result)
    result = matrix_multiply(r_x_inv, result)
    result = matrix_multiply(D_inv, result)

    return [item for sublist in result for item in sublist]
    # print(result)
    # first = [[1, 2, 3, 4], [3, 4, 5, 5], [5, 6, 7, 8], [8, 6, 5, 4]]
    # second = [[1, 2, 3, 4], [3, 4, 5, 5], [5, 6, 7, 8], [8, 6, 5, 4]]
    # answer = np.matmul(first, second)
    # print('answer:')
    # print(answer)
    # result = [[sum(starmap(mul, zip(row, col))) for col in zip(*second)] for row in first]
    # print(result)
    # print(-p1.y*C/V + -p1.z*B/V)
    # test_a()


def get_jaw_rotation_test(angle):
    # p1 = Point(6, -2, 0)
    # p2 = Point(12, 8, 0)
    p1 = [0.5, 0.5, 0.5]
    p2 = [1, 1, 1]

    N = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
    L = sqrt(N[0] ** 2 + N[1] ** 2 + N[2] ** 2)
    V = sqrt(N[1] ** 2 + N[2] ** 2)
    A = N[0]
    B = N[1]
    C = N[2]

    D = [[1, 0, 0, -p1[0]],
             [0, 1, 0, -p1[1]],
             [0, 0, 1, -p1[2]],
             [0, 0, 0, 1]]

    r_x = [[1, 0, 0, 0],
              [0, C/V, -B/V, 0],
              [0, B/V, C/V, 0],
              [0, 0, 0, 1]]

    r_y = [[V/L, 0, -A/L, 0],
             [0, 1, 0, 0],
             [A/L, 0, V/L, 0],
             [0, 0, 0, 1]]

    r_theta = [[cos(angle), -sin(angle), 0, 0],
               [sin(angle), cos(angle), 0, 0],
               [0, 0, 1, 0],
               [0, 0, 0, 1]]

    r_y_inv = [[V/L, 0, A/L, 0],
               [0, 1, 0, 0],
               [-A/L, 0, V/L, 0],
               [0, 0, 0, 1]]

    r_x_inv = [[1, 0, 0, 0],
               [0, C/V, B/V, 0],
               [0, -B/V, C/V, 0],
               [0, 0, 0, 1]]

    D_inv = [[1, 0, 0, p1[0]],
             [0, 1, 0, p1[1]],
             [0, 0, 1, p1[2]],
             [0, 0, 0, 1]]

    result = mx_mult(r_x, D)
    result = mx_mult(r_y, result)
    print(result)
    result = mx_mult(r_theta, result)
    result = mx_mult(r_y_inv, result)
    result = mx_mult(r_x_inv, result)
    result = mx_mult(D_inv, result)
    result_1 = matrix_multiply(r_x, D)
    result_1 = matrix_multiply(r_y, result_1)
    print(result_1)
    result_1 = matrix_multiply(r_theta, result_1)
    result_1 = matrix_multiply(r_y_inv, result_1)
    result_1 = matrix_multiply(r_x_inv, result_1)
    result_1 = matrix_multiply(D_inv, result_1)
    print('mx')
    print(result)
    print(result_1)
    print('answer')
    # [-0.7320508075688772], [1.0000000000000002], [2.7320508075688767]
    print(mx_mult(result, [[0], [3], [0], [1]]))

    return [item for sublist in result for item in sublist]


class Point(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)


def calculate_rotation_matrix_3d(p1, p2, p0, theta):
    from math import cos, sin, sqrt

    # Translate so axis is at origin
    p = p0 - p1
    # Initialize point q
    q = Point(0.0, 0.0, 0.0)
    N = (p2 - p1)
    Nm = sqrt(N.x ** 2 + N.y ** 2 + N.z ** 2)

    # Rotation axis unit vector
    n = Point(N.x / Nm, N.y / Nm, N.z / Nm)

    # Matrix common factors
    c = cos(theta)
    t = (1 - cos(theta))
    s = sin(theta)
    X = n.x
    Y = n.y
    Z = n.z

    # Matrix 'M'
    d11 = t * X ** 2 + c
    d12 = t * X * Y - s * Z
    d13 = t * X * Z + s * Y
    d21 = t * X * Y + s * Z
    d22 = t * Y ** 2 + c
    d23 = t * Y * Z - s * X
    d31 = t * X * Z - s * Y
    d32 = t * Y * Z + s * X
    d33 = t * Z ** 2 + c

    #            |p.x|
    # Matrix 'M'*|p.y|
    #            |p.z|
    q.x = d11 * p.x + d12 * p.y + d13 * p.z
    q.y = d21 * p.x + d22 * p.y + d23 * p.z
    q.z = d31 * p.x + d32 * p.y + d33 * p.z

    # Translate axis and rotated point back to original location
    return q + p1

