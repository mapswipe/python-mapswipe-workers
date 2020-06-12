class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect(object):
    def __init__(self, p1, p2):
        """Store the top, bottom, left and right values for points
               p1 and p2 are the (corners) in either order
        """
        self.left = min(p1.x, p2.x)
        self.right = max(p1.x, p2.x)
        self.bottom = min(p1.y, p2.y)
        self.top = max(p1.y, p2.y)


def overlap(r1, r2):
    """
    Overlapping rectangles overlap both horizontally & vertically
    """
    return range_overlap(r1.left, r1.right, r2.left, r2.right) and range_overlap(
        r1.bottom, r1.top, r2.bottom, r2.top
    )


def range_overlap(a_min, a_max, b_min, b_max):
    """
    Neither range is completely greater than the other
    """
    return (a_min <= b_max) and (b_min <= a_max)


def groups_overlap(groups):
    group_ids = list(groups.keys())

    group_overlap = {}
    while len(group_ids) > 0:
        for group_id in group_ids:

            p1 = Point(groups[group_id]["xMin"], groups[group_id]["yMax"])
            p2 = Point(groups[group_id]["xMax"], groups[group_id]["yMin"])

            Rect1 = Rect(p1, p2)
            group_ids.remove(group_id)

            for group_id_B in group_ids:
                p1 = Point(groups[group_id_B]["xMin"], groups[group_id_B]["yMax"])
                p2 = Point(groups[group_id_B]["xMax"], groups[group_id_B]["yMin"])
                Rect2 = Rect(p1, p2)

                if overlap(Rect1, Rect2):
                    print("overlap!")
                    try:
                        group_overlap[group_id].append(group_id_B)
                    except KeyError:
                        group_overlap[group_id] = []
                        group_overlap[group_id].append(group_id_B)

    if len(group_overlap) > 0:
        print("Didn't pass test. There are %s overlapping groups." % len(group_overlap))
        print(group_overlap)
        return False
    else:
        print("No overlapping groups.")
        return True


if __name__ == "__main__":
    # projectId = 'E6L057UQ'
    projectId = "OLYY643L"
    assert groups_overlap(projectId), "Didn't pass test. There are overlapping groups."
