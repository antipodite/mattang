from random import random

from scipy.spatial import ConvexHull
from numpy import cos, sin, pi, cumsum, linspace, column_stack


def chunk(seq, overlap):
    """Divide a sequence into a list of overlapping subsequences"""
    result = []
    for i in range(len(seq)):
        subseq = seq[i:i+overlap]
        if len(subseq) < overlap:
            break
        else:
            result.append(subseq)
    return result


def is_colinear(points):
    """Return True if all (x,y) points lie on same line.
    Building a convex hull only works if points are not colinear"""
    if len(points) < 3:
        raise ValueError("Can't compute colinearity of less than three points!")
    colinear = lambda a, b, c: (
        (b[1] - a[1]) * (c[0] - a[0]) == (b[0] - a[0]) * (c[1] - a[1])
    )
    return all([colinear(a, b, c) for a, b, c in chunk(points, 3)])


def midpoint(point_a, point_b, offset=(0, 0)):
    """Find the midpoint of the line defined by `point_a` and `point_b`"""
    return (
        (point_a[0] + point_b[0]) / 2 + offset[0],
        (point_a[1] + point_b[1]) / 2 + offset[1]
    )


def points_circumference(point, radius, n=10):
    """Generate `n` points on `radius` of `point`"""
    result = []
    for i in range(n):
        angle = random() * pi * 2
        x = point[0] + cos(angle) * radius
        y = point[1] + sin(angle) * radius
        result.append((x, y))
    return result


def buffer_convex_hull(hull: ConvexHull, stretch: float, n: int) -> ConvexHull:
    """Expand the boundaries of a convex hull `hull` and round the borders.
    `stretch` : how far from the original hull vertices to place points
    `n` : how many vertices on the new hull to generate. This controls the
    amount of roundedness at the corners of the polygon.
    """
    # TODO: This could be made more efficient by only generating rounding points
    # outside the boundaries of the input hull. But doesn't really matter
    new_points = []
    for point in zip(
            hull.points[hull.vertices, 0],
            hull.points[hull.vertices, 1]
    ):
        new_points.extend(points_circumference(point, stretch, n))

    return ConvexHull(new_points)


def build_isogloss(points, padding=.1, roundedness=100, scale=.001):
    if not points:
        raise ValueError("Input point sequence empty")

    # Check that we have at least 3 points
    pdiff = 3 - len(points)
    if pdiff > 0:
        points.extend(points_circumference(points[0], scale, pdiff))

    # Make sure that points are not colinear
    if is_colinear(points):
        points.extend(points_circumference(points[0], scale, 1))

    # Now we can build the hull
    hull = ConvexHull(points)
    
    # After computing the complex hull, we expand it and round the edges
    buff_hull = buffer_convex_hull(hull, padding, roundedness)

    isogloss = []
    for simplex in buff_hull.simplices:
        point = (buff_hull.points[simplex, 0], buff_hull.points[simplex, 1])
        isogloss.append(point)
    
    return isogloss


def pie_marker(n_slices):
    """Calculate geometry for a pie chart style marker"""
    cum = cumsum([2 for i in range(n_slices)])
    cum = cum / cum[-1]
    pie = [0] + cum.tolist()

    slices = []
    for r1, r2 in zip(pie[:-1], pie[1:]):
        # Build the pie slice
        angles = linspace(2 * pi * r1, 2 * pi * r2)
        x = [0] + cos(angles).tolist()
        y = [0] + sin(angles).tolist()
        xy = column_stack([x, y])
        slices.append(xy)
    return slices
