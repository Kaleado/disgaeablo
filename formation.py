#!/usr/bin/env python

class Formation:
    def __init__(self, origin, formation):
        self._formation = formation
        self._origin = origin
        self._groups = set([c for r in formation for c in r])

    def _rotated_formation(self, rotations):
        rotated = self._formation if rotations % 2 == 0 else [*zip(*self._formation)]
        rotated = [r[::-1] for r in rotated] if rotations == 1 or rotations == 2 else rotated
        rotated = rotated[::-1] if rotations == 2 or rotations == 3 else rotated
        return rotated

    def _rotated_origin(self, rotations):
        x, y = self._origin
        x, y = (y, x) if rotations % 2 == 1 else (x, y)
        w, h = self._rotated_dimensions(rotations)
        x = w - x - 1 if rotations == 1 or rotations == 2 else x
        y = h - y - 1 if rotations == 2 or rotations == 3 else y
        return (x, y)

    def _rotated_dimensions(self, rotations):
        w, h = (len(self._formation[0]) if len(self._formation) > 0 else 0, len(self._formation))
        return (w, h) if rotations % 2 == 0 else (h, w)

    def _log_formation(self, formation):
        import settings
        for row in formation:
            settings.message_panel.info(str(row))
        settings.message_panel.info("----------------------")

    def groups(self):
        return self._groups

    def positions_in_formation(self, formation_position, rotations, group='x'):
        result = []
        rotated_formation = self._rotated_formation(rotations)
        rotated_origin = self._rotated_origin(rotations)
        w, h = self._rotated_dimensions(rotations)
        tl_x, tl_y = (formation_position[0] - rotated_origin[0], formation_position[1] - rotated_origin[1])
        for x in range(tl_x, tl_x + w):
            for y in range(tl_y, tl_y + h):
                if rotated_formation[y - tl_y][x - tl_x] == group:
                    result.append((x, y))
        return result

    def in_formation(self, formation_position, test_position, rotations, group='x'):
        rotated_formation = self._rotated_formation(rotations)
        rotated_origin = self._rotated_origin(rotations)
        w, h = self._rotated_dimensions(rotations)
        tl_x, tl_y = (formation_position[0] - rotated_origin[0], formation_position[1] - rotated_origin[1])
        t_x, t_y = test_position
        return t_x >= tl_x and t_x < tl_x + w and t_y >= tl_y and t_y < tl_y + h and rotated_formation[t_y - tl_y][t_x - tl_x] == group
