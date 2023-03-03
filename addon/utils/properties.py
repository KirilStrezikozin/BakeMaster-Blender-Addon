# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


def BM_PROPUTIL_Highpoly_get_items(self, self_object, objects, include: list):
    items = []
    added = []

    for object in objects:
        # add current chosen high
        if all([any([object.index == self.object_index,
                     object.name in include]), object.index not in added]):
            items.append((str(object.index), object.name,
                          "Highpoly Object"))
            added.append(object.index)
            continue

        # skip the item itself and all cages, lows, highs already
        if any([any([object.hl_is_cage, object.hl_is_lowpoly,
                     object.hl_is_highpoly]),
                object.index == self.object_index]):
            continue

        if any([all([objects[object.nm_lc_index].nm_is_hl_lc,
                object.nm_uni_index == self_object.nm_uni_index]),
                object.nm_is_detached == self_object.nm_is_detached]):
            items.append((str(object.index), object.name,
                          "Highpoly Object"))
            added.append(object.index)

    if len(items) == 0:
        items = [('NONE', "None",
                  "No highpoly available within the Bake Job's Objects")]
    return items


def BM_PROPUTIL_CageHighpoly_get_include(self_object):
    include_cages = []
    include_highpolies = []
    skip_highpolies = []
    self_map = self_object.maps[self_object.maps_active_index]

    if self_object.hl_use_unique_per_map:
        return include_cages, include_highpolies

    for map in self_object.maps:
        if all([map.hl_use_cage, map.hl_cage_object_index != -1,
                map.hl_cage_name_old not in include_cages,
                map.index != self_map.index]):
            include_cages.append(map.hl_cage_name_old)
        for highpoly in map.hl_highpolies:
            if highpoly.object_index == -1:
                continue
            if map.index == self_map.index:
                skip_highpolies.append(highpoly.name_old)
                continue
            if all([highpoly.name_old not in include_highpolies,
                    highpoly.name_old not in skip_highpolies]):
                include_highpolies.append(highpoly.name_old)
    return include_cages, include_highpolies


def BM_PROPUTIL_Highpoly_Items(self, context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[self.bakejob_index].objects
    self_object = objects[self.object_index]
    _, include = BM_PROPUTIL_CageHighpoly_get_include(self_object)
    return BM_PROPUTIL_Highpoly_get_items(self, self_object, objects, include)


def mark_highpolies(objects, data):
    for highpoly in data.hl_highpolies:
        if highpoly.object_index == -1:
            continue
        objects[highpoly.object_index].hl_is_highpoly = True


def BM_PROPUTIL_Highpoly_EnsureHighpolyMarked(objects):
    for object in objects:
        if object.hl_use_unique_per_map is False:
            mark_highpolies(objects, object)
            continue
        for map in object.maps:
            mark_highpolies(objects, map)


def BM_PROPUTIL_Highpoly_Update(self, context):
    if self.name == self.name_old:
        return

    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[self.bakejob_index].objects
    update_name = False

    if self.name_old == 'NONE':
        update_name = True
    self.name_old = self.name
    if self.object_index != -1:
        objects[self.object_index].hl_is_highpoly = False
        self.object_index = int(self.name_old)
        objects[self.object_index].hl_is_highpoly = True
    self.object_include = objects[self.object_index].name
    if update_name:
        self.name = self.name_old

    BM_PROPUTIL_Highpoly_EnsureHighpolyMarked(objects)


def BM_PROPUTIL_Highpoly_UpdateOnRemove(self, context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[self.bakejob_index].objects
    if self.object_index != -1:
        objects[self.object_index].hl_is_highpoly = False


def BM_PROPUTIL_Highpoly_unset_none(data):
    to_remove = []
    highpoly_index = 0
    for highpoly in data.hl_highpolies:
        if highpoly.object_index == -1:
            to_remove.append(highpoly.index)
            continue
        highpoly.index = highpoly_index
        highpoly_index += 1

    for index in reversed(to_remove):
        data.hl_highpolies.remove(index)
    data.hl_highpoles_active_index = highpoly_index - 1


def BM_PROPUTIL_Highpoly_UpdateOnAddOT(context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[bakemaster.bakejobs_active_index].objects

    for object in objects:
        if object.hl_use_unique_per_map is False:
            BM_PROPUTIL_Highpoly_unset_none(object)
            object.hl_is_lowpoly = len(object.hl_highpoles) != 0
            continue

        len_of_highpolies = 0
        for map in object.maps:
            BM_PROPUTIL_Highpoly_unset_none(map)
            len_of_highpolies += len(map.hl_highpolies)
        object.hl_is_lowpoly = len_of_highpolies != 0


def reset_highpoly_props(data, objects, from_index, to_index):
    for highpoly in data.hl_highpolies:
        if highpoly.object_index == from_index:
            highpoly.object_index = to_index
        elif highpoly.object_index == to_index:
            highpoly.object_index = from_index
        if highpoly.self_object_index == from_index:
            highpoly.self_object_index = to_index
        elif highpoly.self_object_index == to_index:
            highpoly.self_object_index = from_index
        if highpoly.object_index != -1:
            objects[highpoly.object_index].hl_is_highpoly = True
        try:
            highpoly.name_old = str(highpoly.object_index)
            highpoly.name = str(highpoly.object_index)
        except (ValueError, TypeError):
            pass


def BM_PROPUTIL_Highpoly_UpdateOnMoveOT(context, from_index=-2, to_index=-2):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[bakemaster.bakejobs_active_index].objects

    for object in objects:
        if object.hl_use_unique_per_map is False:
            reset_highpoly_props(object, objects, from_index, to_index)
            continue
        for map in object.maps:
            reset_highpoly_props(map, objects, from_index, to_index)
            continue
        for map in object.maps:
            reset_highpoly_props(map)


def getnew_highpoly_object_index(self, objects):
    for object in objects:
        if object.name == self.object_include and not any([object.nm_is_lc,
                                                           object.nm_is_uc]):
            self.self_object_index = object.index
            return object.index
    return -1


def updateHighpolyProps_and_removeNone(data, objects):
    to_remove = []
    highpoly_index = 0
    for highpoly in data.hl_highpolies:
        new_index = getnew_highpoly_object_index(highpoly, objects)
        highpoly.object_index = new_index
        try:
            highpoly.name_old = str(highpoly.object_index)
            highpoly.name = str(highpoly.object_index)
        except (ValueError, TypeError):
            pass

        if highpoly.object_index == -1:
            to_remove.append(highpoly.index)
        else:
            objects[highpoly.object_index].hl_is_highpoly = True
            highpoly.index = highpoly_index
            highpoly_index += 1

    for highpoly_index in reversed(to_remove):
        data.hl_highpolies.remove(highpoly_index)
    if data.hl_highpolies_active_index >= highpoly_index - 1:
        data.hl_highpolies_active_index = highpoly_index - 1
    return not highpoly_index == 0


def BM_PROPUTIL_Highpoly_UpdateAfterRemoveOT(context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[bakemaster.bakejobs_active_index].objects

    for object in objects:
        leave_lowpoly = False
        if object.hl_use_unique_per_map is False:
            leave_lowpoly = updateHighpolyProps_and_removeNone(object, objects)
            continue
        for map in object.maps:
            leave_lowpoly = updateHighpolyProps_and_removeNone(map, objects)
        object.hl_is_lowpoly = leave_lowpoly


def remove_highpolies(context, data):
    to_remove = []
    for highpoly in data.hl_highpolies:
        BM_PROPUTIL_Highpoly_UpdateOnRemove(highpoly, context)
        to_remove.append(highpoly.index)
    for index in reversed(to_remove):
        data.hl_highpolies.remove(index)


def set_removed_highpoly_to_none(data, removed_index):
    for highpoly in data.hl_highpolies:
        if highpoly.object_index != removed_index:
            continue
        highpoly.object_index = -1
        highpoly.name_old = 'NONE'
        highpoly.object_include = "NONE"


def BM_PROPUTIL_Highpoly_UpdateOnRemoveOT(context, removed_index, type: str):
    bakemaster = context.scene.bakemaster
    bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
    objects = bakejob.objects

    if type == 'OBJECT':
        object = objects[removed_index]
        if object.hl_is_highpoly is False:
            if object.hl_use_unique_per_map is False:
                remove_highpolies(context, object)
                return
            for map in object.maps:
                remove_highpolies(context, map)
        for object in objects:
            if object.hl_use_unique_per_map is False:
                set_removed_highpoly_to_none(object, removed_index)
                continue
            for map in object.maps:
                set_removed_highpoly_to_none(map, removed_index)
    elif type == 'MAP':
        self_object = objects[bakejob.objects_active_index]
        if self_object.hl_use_unique_per_map is False:
            return
        map = self_object.maps[removed_index]
        remove_highpolies(context, map)
