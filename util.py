#!/usr/bin/env python
import math
import random

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def random_permutation(lst):
    res = []
    while len(lst):
        idx = random.randint(0, len(lst)-1)
        res.append(lst[idx])
        lst.remove(lst[idx])
    return res

def find_path(passability_map, source, dest):
    q = [source]
    w = len(passability_map[0])
    h = len(passability_map)
    path_map = [[None for x in range(w)] for y in range(h)]
    seen = set()
    while len(q) > 0:
        (x, y) = q.pop()
        for dx in random_permutation([-1, 0, 1]):
            for dy in random_permutation([-1, 0, 1]):
                if (dx == 0 and dy == 0) or \
                   x + dx < 0 or y + dy < 0 or \
                   x + dx >= w or y + dy >= h or (x+dx, y+dy) in seen or passability_map[y+dy][x+dx] == False:
                    continue
                path_map[y+dy][x+dx] = (x, y)
                seen = seen | set([(x+dx, y+dy)])
                q = [(x+dx, y+dy)] + q
        if (x, y) == dest:
            break
    path_map[source[1]][source[0]] = None
    xx, yy = dest
    path = [dest]
    while path_map[yy][xx] is not None:
        path = [path_map[yy][xx]] + path
        xx, yy = path_map[yy][xx]
    return path

def copy_dict(other):
    d = {}
    for (k, v) in other.items():
        d[k] = v
    return d

def abbrev(value):
    if value > 999999999999999:
        return "{0:.1f}Q".format(value / 1000000000000000)
    if value > 999999999999:
        return "{0:.1f}T".format(value / 1000000000000)
    if value > 999999999:
        return "{0:.1f}B".format(value / 1000000000)
    if value > 999999:
        return "{0:.1f}M".format(value / 1000000)
    if value > 9999:
        return str(value // 1000) + "K"
    return str(value)

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))
