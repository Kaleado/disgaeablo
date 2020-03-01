#!/usr/bin/env python

class EntityListView:
    def __init__(self, entity_list):
        self.entity_list = entity_list

    def in_formation(self, formation, position, rotation, group='x'):
        return self.with_component('Position').where(lambda ent: formation.in_formation(position, ent.component('Position').get(), rotation, group))

    def with_all_components(self, identifiers):
        def pred(e):
            for identifier in identifiers:
                if not e.has_component(identifier):
                    return False
            return True

        return self.where(pred)

    def without_components(self, identifiers):
        def pred(e):
            for identifier in identifiers:
                if e.has_component(identifier):
                    return False
            return True

        return self.where(pred)

    def size(self):
        return len(self.entity_list)

    def with_component(self, identifier):
        return self.with_all_components([identifier])

    def with_any_components(self, identifiers):
        def pred(e):
            for identifier in identifiers:
                if e.has_component(identifier):
                    return True
            return False

        return self.where(pred)

    def where(self, pred):
        return EntityListView(list(filter(pred, self.entity_list)))

    def transform(self, func):
        return EntityListView(list(map(func, self.entity_list)))

    def for_each_until(self, func):
        for ent in self.entity_list:
            if func(ent):
                return True
        return False

    def as_list(self):
        return self.entity_list
