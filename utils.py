# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on
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

import bpy
from .labels import BM_Labels

###############################################################
### BM Gets Funcs ###
###############################################################
def BM_Object_Get(self, context):
    if self is None:
        object = [context.scene.bm_table_of_objects[context.scene.bm_props.global_active_index], True] 
    else:
        if hasattr(self, "global_map_object_index"):
            object1 = context.scene.bm_table_of_objects[self.global_map_object_index]
        else:
            object1 = self
        object = [object1, True]
    try:
        context.scene.objects[object[0].global_object_name]
    except (KeyError, AttributeError, UnboundLocalError):
        object[1] = False
    return object

def BM_Map_Get(self, object):
    if self is not None and hasattr(self, "global_map_object_index"):
        return self
    map = object.global_maps[object.global_maps_active_index]
    return map

###############################################################
### Name Matching Funcs ###
###############################################################
def BM_Table_of_Objects_NameMatching_GetAllObjectNames(context):
    names = []
    for object in context.scene.bm_table_of_objects:
        names.append(object.global_object_name)
    return names

def BM_Table_of_Objects_NameMatching_GenerateNameChunks(name: str):
    chunks = []
    chunk_start_index = 0
    for index, char in enumerate(name):
        if char == "_":
            chunks.append(name[chunk_start_index:index])
            chunk_start_index = index + 1
        if index == len(name) - 1:
            chunks.append(name[chunk_start_index:len(name)])
    return [chunk for chunk in chunks if chunk.replace(" ", "") != ""]

def BM_Table_of_Objects_NameMatching_GetNameChunks(chunks: list, combine_type: str, context=None):
    # get prefixes
    lowpoly_prefix_raw = context.scene.bm_props.global_lowpoly_tag
    highpoly_prefix_raw = context.scene.bm_props.global_highpoly_tag
    cage_prefix_raw = context.scene.bm_props.global_cage_tag
    decal_prefix_raw = context.scene.bm_props.global_decal_tag
    combined_name = []

    if combine_type == 'ROOT':
        for index, chunk in enumerate(chunks):
            if chunk in [lowpoly_prefix_raw, highpoly_prefix_raw, cage_prefix_raw]:
                break
            else:
                combined_name.append(chunk)

    elif combine_type == 'TALE':
        combine_from_index = 0
        for index, chunk in enumerate(chunks):
            if chunk in [lowpoly_prefix_raw, highpoly_prefix_raw, cage_prefix_raw]:
                combine_from_index = index + 1
                break
        for index in range(combine_from_index, len(chunks)):
            combined_name.append(chunks[index])

    elif combine_type == 'FULL':
        for chunk in chunks:
            combined_name.append(chunk)

    return combined_name

def BM_Table_of_Objects_NameMatching_CombineToRaw(chunked_name: str):
    combined_name = ""
    for chunk in chunked_name:
        combined_name += chunk + "_"
    return combined_name[:-1]
        
def BM_Table_of_Objects_NameMatching_IndexesIntersaction(indexes: list):
    # removing empty shells
    indexes = [shell for shell in indexes if len(shell) != 0]
    intersaction = []
    # loop through every number
    for shell in indexes:
        for number in shell:
            # count how many times this number is present
            number_presents = len([shell1 for shell1 in indexes if number in shell1])
            # if that count = len of all shells -> presented in all shells
            if number_presents == len(indexes):
                intersaction.append(number)
    # remove duplicates and return
    return list(dict.fromkeys(intersaction))

def BM_Table_of_Objects_NameMatching_CombineGroups(groups: list):
    sorted_groups = []
    groups_lens = []
    combined = []
    # sorting each groups' shell and all shells by their len
    for group in groups:
        sorted_groups.append(sorted(group))
        groups_lens.append(len(group))
    sorted_groups = [g for _, g in sorted(zip(groups_lens, sorted_groups), reverse=False)]
    combined = [list(g) for g in sorted_groups]

    # remove repetitive indexes
    deleted = []
    for index, group in enumerate(sorted_groups):
        deleted.append([])
        for n_index, number in enumerate(group):
            for index_1, group_1 in enumerate(sorted_groups):
                if number in group_1 and index_1 != index:
                    try:
                        # if index was already deleted
                        deleted[index].index(number)
                    except (IndexError, ValueError):
                        try:
                            # if found was already deleted
                            deleted[index_1].index(number)
                        except (IndexError, ValueError):
                            # delete the index
                            deleted[index].append(number)
                            del combined[index][combined[index].index(number)]
                            break
                        else:
                            pass
                    else:
                        continue
    # return non-empty groups
    return [group for group in combined if len(group)]

def BM_Table_of_Objects_NameMatching_Construct(context, objects_names_input):
    # funcs pointers
    NameChunks = BM_Table_of_Objects_NameMatching_GenerateNameChunks
    GetChunks = BM_Table_of_Objects_NameMatching_GetNameChunks
    Intersaction = BM_Table_of_Objects_NameMatching_IndexesIntersaction
    CombineToRaw = BM_Table_of_Objects_NameMatching_CombineToRaw
    CombineGroups = BM_Table_of_Objects_NameMatching_CombineGroups
    # get prefixes
    lowpoly_prefix_raw = context.scene.bm_props.global_lowpoly_tag
    highpoly_prefix_raw = context.scene.bm_props.global_highpoly_tag
    cage_prefix_raw = context.scene.bm_props.global_cage_tag
    decal_prefix_raw = context.scene.bm_props.global_decal_tag
    roots = []
    detached = []

    ### calculating roots[]
    used_obj_names = []
    # loop through all names
    for object_name in objects_names_input:
        # if name contains 'lowpoly'
        if lowpoly_prefix_raw in NameChunks(object_name):
            used_obj_names.append(object_name)
            
            # create root_name
            object_name_chunked = NameChunks(object_name)
            root_name = GetChunks(object_name_chunked, 'ROOT', context)
            tale_name = GetChunks(object_name_chunked, 'TALE', context)

            # find any objects in the input_objects with the same root_name and tale_name
            pairs = [object_name]
            for object_name_pair in objects_names_input:
                if object_name_pair in used_obj_names:
                    continue
                pair_name_chunked = NameChunks(object_name_pair)
                pair_name_chunked_no_decal = NameChunks(object_name_pair)
                try:
                    pair_name_chunked_no_decal.remove(decal_prefix_raw)
                except ValueError:
                    pass
                pair_root = GetChunks(pair_name_chunked, 'ROOT', context)
                pair_tale = GetChunks(pair_name_chunked_no_decal, 'TALE', context)
                if pair_root == root_name and pair_tale == tale_name:
                    # add it to the current shell
                    pairs.append(object_name_pair)
                    used_obj_names.append(object_name_pair)
            # add current shell to the roots[]
            roots.append([root_name, pairs])

    # try pairing highs and cages that are left to lowpolies
    for root in roots:
        for object_name in objects_names_input:
            if object_name in root[1] or object_name in used_obj_names:
                continue

            if highpoly_prefix_raw in NameChunks(object_name) or cage_prefix_raw in NameChunks(object_name):

                object_name_chunked = NameChunks(object_name)
                try:
                    object_name_chunked.remove(decal_prefix_raw)
                except ValueError:
                    pass
                root_name = GetChunks(object_name_chunked, 'ROOT', context)

                if CombineToRaw(root_name).find(CombineToRaw(root[0])) == 0:
                    used_obj_names.append(object_name)
                    root[1].append(object_name)

    # roots with no pairs - add to detached[], and items not added to roots as well
    detached = [object_name for root in roots for object_name in root[1] if len(root[1]) <= 1]
    for object_name in objects_names_input:
        if len([object_name for root in roots if object_name in root[1]]) == 0:
            # object_name is nowhere in roots
            detached.append(object_name)
    # recalculate roots
    roots = [root for root in roots if len(root[1]) > 1]

    ### sorting roots from shortest root to longest
    roots_lens = []
    for root in roots:
        roots_lens.append(len(CombineToRaw(root[0])))
    roots = [root for _, root in sorted(zip(roots_lens, roots), reverse=False)]

    ### grouping roots (finding all pairs)
    used_root_indexes = []
    groups = []
    for index, shell in enumerate(roots):
        # add current shell to checked
        used_root_indexes.append(index)
        root_chunked = shell[0]
        root_matched_chunks_indexes = []

        # loop through chunked root_name
        for chunk_index, chunk in enumerate(root_chunked):
            root_matched_chunks_indexes.append([index])
            # loop through all roots
            for index_pair, shell_pair in enumerate(roots):
                root_pair_chunked = shell_pair[0]
                # if found root contains the chunk
                try:
                    root_pair_chunked.index(chunk)
                except ValueError:
                    continue
                else:
                    # found root chunk is on the same place as the root_name chunk -> found pair
                    if root_pair_chunked.index(chunk) == chunk_index:
                        root_matched_chunks_indexes[chunk_index].append(index_pair)
                        used_root_indexes.append(index_pair)
        # add intersaction of matched roots indexes to the groups[] shell
        groups.append(Intersaction(root_matched_chunks_indexes))

    ### groups checked_combine
    # combine repetitive groups' shells
    groups = CombineGroups(groups)

    # return
    return groups, roots, detached

def BM_Table_of_Objects_NameMatching_Deconstruct(context):
    to_remove = []
    for index, object in enumerate(context.scene.bm_table_of_objects):
        if any([object.nm_is_universal_container, object.nm_is_local_container]):
            to_remove.append(index)
        object.nm_is_detached = False
        object.nm_master_index = -1
        object.nm_container_name_old = ""
        object.nm_container_name = ""
        object.nm_this_indent = 0
        object.nm_is_universal_container = False
        object.nm_is_local_container = False
        object.nm_is_expanded = True
        object.nm_item_container = ""
        object.nm_container_items = []
    for index in to_remove[::-1]:
        context.scene.bm_table_of_objects.remove(index)
    context.scene.bm_props.global_active_index = 0

def BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context):
    uni_index = -1
    local_index = -1
    item_index = -1
    for object in context.scene.bm_table_of_objects:
        if object.nm_is_universal_container:
            uni_index += 1
            local_index = -1
            item_index = -1
            object.nm_master_index = uni_index
        elif object.nm_is_local_container:
            local_index += 1
            item_index = -1
            object.nm_master_index = local_index
            object.nm_item_uni_container_master_index = uni_index
        elif object.nm_is_detached is False:
            item_index += 1
            object.nm_master_index = item_index
            object.nm_item_local_container_master_index = local_index
            object.nm_item_uni_container_master_index = uni_index
        else:
            uni_index += 1
            local_index = -1
            item_index = -1
            object.nm_master_index = uni_index

# NameMatching Update
def BM_SCENE_PROPS_global_use_name_matching_Update(self, context):
    if len(context.scene.bm_table_of_objects) == 0:
        return
    GetAllObjectNames = BM_Table_of_Objects_NameMatching_GetAllObjectNames
    NameChunks = BM_Table_of_Objects_NameMatching_GenerateNameChunks
    CombineToRaw = BM_Table_of_Objects_NameMatching_CombineToRaw
    # get prefixes
    lowpoly_prefix_raw = context.scene.bm_props.global_lowpoly_tag
    highpoly_prefix_raw = context.scene.bm_props.global_highpoly_tag
    cage_prefix_raw = context.scene.bm_props.global_cage_tag
    decal_prefix_raw = context.scene.bm_props.global_decal_tag

    # trash texsets
    to_remove = []
    for index, item in enumerate(context.scene.bm_props.global_texturesets_table):
        to_remove.append(index)
    for index in to_remove[::-1]:
        context.scene.bm_props.global_texturesets_table.remove(index)

    if self.global_use_name_matching is True:
        # trash all highpolies and unset cages
        for object in context.scene.bm_table_of_objects:
            object.hl_use_cage = False
            object.hl_use_unique_per_map = False
            BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(object, object, context)
            object.hl_is_lowpoly = False
            object.hl_is_cage = False
            object.hl_is_highpoly = False
            object.hl_is_decal = False
            
        BM_Table_of_Objects_NameMatching_Deconstruct(context)

        # get groups, roots, detached from construct
        groups, roots, detached = BM_Table_of_Objects_NameMatching_Construct(context, GetAllObjectNames(context))

        # trash all from bm_table_of_objects
        to_remove = []
        for index, item in enumerate(context.scene.bm_table_of_objects):
            to_remove.append(index)
        context.scene.bm_props.global_active_index = 0
        for index in to_remove[::-1]:
            context.scene.bm_table_of_objects.remove(index)

        last_uni_c_index = 0
        ### constructing Table_of_Objects items
        for index, shell in enumerate(groups):
            # adding universal container to the bm_table_of_objects
            universal_container = context.scene.bm_table_of_objects.add()
            universal_container.nm_master_index = index
            last_uni_c_index = index
            # name is set to the root_name of the first object in the shell
            universal_container.nm_container_name_old = BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, CombineToRaw(roots[shell[0]][0]))
            universal_container.nm_container_name = universal_container.nm_container_name_old
            universal_container.nm_this_indent = 0
            universal_container.nm_is_universal_container = True
            universal_container.nm_is_expanded = True

            # objs[] : 0 - lowpolies, 1 - highpolies, 2 - cages
            object_names = [[], [], []]
            for number in shell:
                # adding each object_name in the root objects to matched categories
                # based on if their names contain low_ high_ cage_ prefixes
                for object_name in roots[number][1]:
                    try:
                        NameChunks(object_name).index(lowpoly_prefix_raw)
                    except ValueError:
                        pass
                    else:
                        object_names[0].append(object_name)

                    try:
                        NameChunks(object_name).index(highpoly_prefix_raw)
                    except ValueError:
                        pass
                    else:
                        object_names[1].append(object_name)

                    try:
                        NameChunks(object_name).index(cage_prefix_raw)
                    except ValueError:
                        pass
                    else:
                        object_names[2].append(object_name)
            # adding local containers to the bm_table_of_objects if needed
            # and adding all object_name in object_names to the bm_table_of_objects
            names_starters = ["Lowpolies", "Highpolies", "Cages"]
            prefix_props = ["hl_is_lowpoly", "hl_is_highpoly", "hl_is_cage"]
            container_types_props = ["nm_is_lowpoly_container", "nm_is_highpoly_container", "nm_is_cage_container"]
            local_containers_index = -1
            for local_index, local_names in enumerate(object_names):

                if len(local_names):
                    local_containers_index += 1
                    local_container = context.scene.bm_table_of_objects.add()
                    local_container.nm_master_index = local_containers_index
                    local_container.nm_container_name_old = names_starters[local_index]
                    local_container.nm_container_name = names_starters[local_index]
                    local_container.nm_this_indent = 1
                    local_container.nm_is_local_container = True
                    local_container.nm_item_uni_container_master_index = index
                    local_container.nm_is_expanded = True
                    setattr(local_container, container_types_props[local_index], True)

                    for obj_index, object_name in enumerate(local_names):
                        # do not add detached names
                        if object_name in detached:
                            continue
                        new_item = context.scene.bm_table_of_objects.add()
                        new_item.global_object_name = object_name
                        new_item.nm_master_index = obj_index
                        new_item.nm_this_indent = 2
                        new_item.nm_item_uni_container_master_index = index
                        new_item.nm_item_local_container_master_index = local_index
                        new_item.nm_is_expanded = True
                        # setattr(new_item, prefix_props[local_index], True)

            # auto configure decals, highpolies, and cages
            universal_container.nm_uni_container_is_global = True

        # adding detached as regular items
        last_uni_c_index += 1
        for index, object_name in enumerate(detached):
            new_item = context.scene.bm_table_of_objects.add()
            new_item.global_object_name = object_name
            new_item.nm_is_detached = True
            new_item.nm_master_index = index + last_uni_c_index
            new_item.nm_is_expanded = True
        # update uni containers names
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if object.nm_is_universal_container:
                object.nm_container_name = BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, object.nm_container_name, index)

    else:
        # trash all highpolies and unset cages
        for object in context.scene.bm_table_of_objects:
            object.hl_use_cage = False
            object.hl_use_unique_per_map = False
            BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(object, object, context)
            object.hl_is_lowpoly = False
            object.hl_is_cage = False
            object.hl_is_highpoly = False
            object.hl_is_decal = False
        BM_Table_of_Objects_NameMatching_Deconstruct(context)

def BM_ITEM_PROPS_nm_container_name_Update(self, context):
    # avoid setting name that already exists in the bm_table
    if self.nm_is_local_container:
        return
    if self.nm_container_name != self.nm_container_name_old:
        wrong_name = False
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if object == self:
                continue

            if context.scene.bm_props.global_use_name_matching and object.nm_container_name == self.nm_container_name:
                wrong_name = True
                break
            elif object.global_object_name == self.nm_container_name:
                wrong_name = True
                break
        if wrong_name:
            self.nm_container_name = self.nm_container_name_old
        else:
            self.nm_container_name_old = self.nm_container_name

def BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, name, index=-1):
    # when creating new container, make sure its name is unique
    name_index = 0
    for object_index, object in enumerate(context.scene.bm_table_of_objects):
        if object_index == index:
            continue
        if object.global_object_name == name:
            name_index += 1
    if name_index == 0:
        return name
    name_index_str = str(name_index)
    name_zeros = "0"*(3 - len(name_index_str)) if len(name_index_str) < 3 else ""
    return "{}.{}{}".format(name, name_zeros, str(name_index_str))

def BM_ITEM_PROPS_nm_uni_container_is_global_Update(self, context):
    if self.nm_uni_container_is_global:
        self.hl_use_cage = True
        container_objects = []
        for object in context.scene.bm_table_of_objects:
            if object.nm_item_uni_container_master_index == self.nm_master_index and object.nm_is_local_container is False:
                container_objects.append(object.global_object_name)

                # trash highpolies and unset cage
                object.hl_use_cage = False
                object.hl_use_unique_per_map = False
                BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(object, object, context)
                object.hl_is_lowpoly = False
                object.hl_is_cage = False
                object.hl_is_highpoly = False
                object.hl_is_decal = False
                object.decal_is_decal = False

        _, roots, detached = BM_Table_of_Objects_NameMatching_Construct(context, container_objects)
        GetChunks = BM_Table_of_Objects_NameMatching_GenerateNameChunks
        # get prefixes
        lowpoly_prefix_raw = context.scene.bm_props.global_lowpoly_tag
        highpoly_prefix_raw = context.scene.bm_props.global_highpoly_tag
        cage_prefix_raw = context.scene.bm_props.global_cage_tag
        decal_prefix_raw = context.scene.bm_props.global_decal_tag

        # decal objects are likely to be dropped into detached
        for detached_name in detached:
            detached_sources = [index for index, object in enumerate(context.scene.bm_table_of_objects) if object.global_object_name == detached_name]
            detached_object = None
            if len(detached_sources):
                detached_object = context.scene.bm_table_of_objects[detached_sources[0]]
                context.scene.bm_props.global_active_index = detached_sources[0]
            else:
                continue

            # set object as decal object
            if decal_prefix_raw in GetChunks(detached_name):
                detached_object.decal_is_decal = True

        for root in roots:
            # root[0] - root_name chunks
            # root[1] - objects' names

            # get object name, source object
            lowpoly_object_name = root[1][0]
            lowpoly_sources = [index for index, object in enumerate(context.scene.bm_table_of_objects) if object.global_object_name == lowpoly_object_name]
            lowpoly_object = None
            if len(lowpoly_sources):
                lowpoly_object = context.scene.bm_table_of_objects[lowpoly_sources[0]]
                context.scene.bm_props.global_active_index = lowpoly_sources[0]
            else:
                continue

            # set object as decal object, do not set highpolies and cage
            if decal_prefix_raw in GetChunks(lowpoly_object_name):
                lowpoly_object.decal_is_decal = True
                continue

            highpolies = []
            cage = "NONE"
            marked_decals = []

            # find highpolies, cage
            for object_name in root[1]:
                if object_name == lowpoly_object_name:
                    continue
                object_name_chunked = GetChunks(object_name)
                # found highpoly
                if highpoly_prefix_raw in object_name_chunked:
                    highpolies.append(object_name)
                    if decal_prefix_raw in object_name_chunked:
                        marked_decals.append(1)
                    else:
                        marked_decals.append(0)
                # found cage
                elif cage_prefix_raw in object_name_chunked and cage == "NONE":
                    cage = object_name

            # add highpolies
            lowpoly_object.hl_highpoly_table_active_index = 0
            for highpoly_index, highpoly in enumerate(highpolies):
                new_highpoly = lowpoly_object.hl_highpoly_table.add()
                new_highpoly.global_holder_index = lowpoly_sources[0]
                new_highpoly.global_item_index = highpoly_index + 1
                # try:
                BM_ITEM_PROPS_hl_add_highpoly_Update(new_highpoly, context)
                new_highpoly.global_object_name = highpoly
                lowpoly_object.hl_highpoly_table_active_index = len(lowpoly_object.hl_highpoly_table) - 1
                lowpoly_object.hl_is_lowpoly = True
                # except TypeError:
                    # lowpoly_object.hl_highpoly_table.remove(highpoly_index)
                    # pass

                # mark highpoly source object as decal if decal tag had been found previously
                if marked_decals[highpoly_index] == 1 and new_highpoly.global_highpoly_object_index != -1: 
                    context.scene.bm_table_of_objects[new_highpoly.global_highpoly_object_index].hl_is_decal = True

            # set cage
            if cage != "NONE" and len(highpolies) != 0:
                try:
                    lowpoly_object.hl_use_cage = True
                    lowpoly_object.hl_cage = cage
                except TypeError:
                    lowpoly_object.hl_use_cage = False

    else:
        data = {
            # 'decal_is_decal' : self.decal_is_decal,
            'decal_use_custom_camera' : self.decal_use_custom_camera,
            'decal_custom_camera' : self.decal_custom_camera,
            'decal_upper_coordinate' : self.decal_upper_coordinate,
            'decal_boundary_offset' : self.decal_boundary_offset,
            'hl_decals_use_separate_texset' : self.hl_decals_use_separate_texset,
            'hl_decals_separate_texset_prefix' : self.hl_decals_separate_texset_prefix,
            # 'hl_use_cage' : self.hl_use_cage,
            'hl_cage_type' : self.hl_cage_type,
            'hl_cage_extrusion' : self.hl_cage_extrusion,
            'hl_max_ray_distance' : self.hl_max_ray_distance,
            # 'hl_use_unique_per_map' : self.hl_use_unique_per_map,
            'uv_bake_data' : self.uv_bake_data,
            'uv_bake_target' : self.uv_bake_target,
            'uv_type' : self.uv_type,
            'uv_snap_islands_to_pixels' : self.uv_snap_islands_to_pixels,
            'uv_use_auto_unwrap' : self.uv_use_auto_unwrap,
            'uv_auto_unwrap_angle_limit' : self.uv_auto_unwrap_angle_limit,
            'uv_auto_unwrap_island_margin' : self.uv_auto_unwrap_island_margin,
            'uv_auto_unwrap_use_scale_to_bounds' : self.uv_auto_unwrap_use_scale_to_bounds,
            'uv_use_unique_per_map' : self.uv_use_unique_per_map,
            'out_use_denoise' : self.out_use_denoise,
            'out_file_format' : self.out_file_format,
            'out_exr_codec' : self.out_exr_codec,
            'out_compression' : self.out_compression,
            'out_res' : self.out_res,
            'out_res_height' : self.out_res_height,
            'out_res_width' : self.out_res_width,
            'out_margin' : self.out_margin,
            'out_margin_type' : self.out_margin_type,
            'out_use_32bit' : self.out_use_32bit,
            'out_use_alpha' : self.out_use_alpha,
            'out_use_transbg' : self.out_use_transbg,
            # 'out_udim_start_tile' : self.out_udim_start_tile,
            # 'out_udim_end_tile' : self.out_udim_end_tile,
            'out_super_sampling_aa' : self.out_super_sampling_aa,
            'out_samples' : self.out_samples,
            'out_use_adaptive_sampling' : self.out_use_adaptive_sampling,
            'out_adaptive_threshold' : self.out_adaptive_threshold,
            'out_min_samples' : self.out_min_samples,
            'out_use_unique_per_map' : self.out_use_unique_per_map,
            'csh_use_triangulate_lowpoly' : self.csh_use_triangulate_lowpoly,
            'csh_use_lowpoly_recalc_normals' : self.csh_use_lowpoly_recalc_normals,
            'csh_lowpoly_use_smooth' : self.csh_lowpoly_use_smooth,
            'csh_lowpoly_smoothing_groups_enum' : self.csh_lowpoly_smoothing_groups_enum,
            'csh_lowpoly_smoothing_groups_angle' : self.csh_lowpoly_smoothing_groups_angle,
            'csh_lowpoly_smoothing_groups_name_contains' : self.csh_lowpoly_smoothing_groups_name_contains,
            'csh_use_highpoly_recalc_normals' : self.csh_use_highpoly_recalc_normals,
            'csh_highpoly_use_smooth' : self.csh_highpoly_use_smooth,
            'csh_highpoly_smoothing_groups_enum' : self.csh_highpoly_smoothing_groups_enum,
            'csh_highpoly_smoothing_groups_angle' : self.csh_highpoly_smoothing_groups_angle,
            'csh_highpoly_smoothing_groups_name_contains' : self.csh_highpoly_smoothing_groups_name_contains,
            'bake_save_internal' : self.bake_save_internal,
            'bake_output_filepath' : self.bake_output_filepath,
            'bake_create_subfolder' : self.bake_create_subfolder,
            'bake_subfolder_name' : self.bake_subfolder_name,
            'bake_batchname' : self.bake_batchname,
            'bake_batchname_use_caps' : self.bake_batchname_use_caps,
            'bake_create_material' : self.bake_create_material,
            'bake_assign_modifiers' : self.bake_assign_modifiers,
            'bake_device' : self.bake_device,
        }

        # apply props values to all container objects
        local_c_master_index = -1
        for object_index, object in enumerate(context.scene.bm_table_of_objects):
            if object.nm_item_uni_container_master_index == self.nm_master_index and object.nm_is_lowpoly_container:
                local_c_master_index = object.nm_master_index

            if object.nm_item_uni_container_master_index == self.nm_master_index and object.nm_is_local_container is False and object.nm_item_local_container_master_index == local_c_master_index: 
                # maps
                # unset all previews
                BM_MAP_PROPS_MapPreview_Unset(None, context)
                # trash
                to_remove = []
                for map_index, map in enumerate(object.global_maps):
                    to_remove.append(map_index)
                for map_index in sorted(to_remove, reverse=True):
                    # unset highpolies
                    BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, map_index, 'MAP', False)
                    # update use_cage
                    BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, map_index, 'MAP')
                    object.global_maps.remove(map_index)
                    BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)
                object.global_maps_active_index = 0

                # add
                for map_index, map in enumerate(self.global_maps):
                    new_map = object.global_maps.add()
                    new_map.global_map_object_index = object_index
                    object.global_maps_active_index = map_index
                    map_data = {
                        'global_map_index' : map_index + 1,
                        'global_use_bake' : map.global_use_bake,
                        'global_map_type' : map.global_map_type,
                        'global_affect_by_hl' : map.global_affect_by_hl,

                        # 'hl_use_cage' : map.hl_use_cage,
                        'hl_cage_type' : map.hl_cage_type,
                        'hl_cage_extrusion' : map.hl_cage_extrusion,
                        'hl_max_ray_distance' : map.hl_max_ray_distance,

                        'uv_bake_data' : map.uv_bake_data,
                        'uv_bake_target' : map.uv_bake_target,
                        # 'uv_active_layer' : map.uv_active_layer,
                        'uv_type' : map.uv_type,
                        'uv_snap_islands_to_pixels' : map.uv_snap_islands_to_pixels,

                        'out_use_denoise' : map.out_use_denoise,
                        'out_file_format' : map.out_file_format,
                        'out_exr_codec' : map.out_exr_codec,
                        'out_compression' : map.out_compression,
                        'out_res' : map.out_res,
                        'out_res_height' : map.out_res_height,
                        'out_res_width' : map.out_res_width,
                        'out_margin' : map.out_margin,
                        'out_margin_type' : map.out_margin_type,
                        'out_use_32bit' : map.out_use_32bit,
                        'out_use_alpha' : map.out_use_alpha,
                        'out_use_transbg' : map.out_use_transbg,
                        # 'out_udim_start_tile' : map.out_udim_start_tile,
                        # 'out_udim_end_tile' : map.out_udim_end_tile,
                        'out_super_sampling_aa' : map.out_super_sampling_aa,
                        'out_samples' : map.out_samples,
                        'out_use_adaptive_sampling' : map.out_use_adaptive_sampling,
                        'out_adaptive_threshold' : map.out_adaptive_threshold,
                        'out_min_samples' : map.out_min_samples,

                        'map_ALBEDO_prefix' : map.map_ALBEDO_prefix,

                        'map_METALNESS_prefix' : map.map_METALNESS_prefix,

                        'map_ROUGHNESS_prefix' : map.map_ROUGHNESS_prefix,

                        'map_DIFFUSE_prefix' : map.map_DIFFUSE_prefix,

                        'map_SPECULAR_prefix' : map.map_SPECULAR_prefix,

                        'map_GLOSSINESS_prefix' : map.map_GLOSSINESS_prefix,

                        'map_OPACITY_prefix' : map.map_OPACITY_prefix,

                        'map_EMISSION_prefix' : map.map_EMISSION_prefix,

                        'map_PASS_prefix' : map.map_PASS_prefix,
                        # 'map_PASS_use_preview' : map.map_PASS_use_preview,
                        'map_pass_type' : map.map_pass_type,

                        'map_DECAL_prefix' : map.map_DECAL_prefix,
                        # 'map_DECAL_use_preview' : map.map_DECAL_use_preview,
                        'map_decal_pass_type' : map.map_decal_pass_type,
                        'map_decal_height_opacity_invert' : map.map_decal_height_opacity_invert,
                        'map_decal_normal_preset' : map.map_decal_normal_preset,
                        'map_decal_normal_custom_preset' : map.map_decal_normal_custom_preset,
                        'map_decal_normal_r' : map.map_decal_normal_r,
                        'map_decal_normal_g' : map.map_decal_normal_g,
                        'map_decal_normal_b' : map.map_decal_normal_b,

                        'map_VERTEX_COLOR_LAYER_prefix' : map.map_VERTEX_COLOR_LAYER_prefix,
                        # 'map_VERTEX_COLOR_LAYER_use_preview' : map.map_VERTEX_COLOR_LAYER_use_preview,
                        # 'map_vertexcolor_layer' : map.map_vertexcolor_layer,

                        'map_C_COMBINED_prefix' : map.map_C_COMBINED_prefix,

                        'map_C_AO_prefix' : map.map_C_AO_prefix,

                        'map_C_SHADOW_prefix' : map.map_C_SHADOW_prefix,

                        'map_C_POSITION_prefix' : map.map_C_POSITION_prefix,

                        'map_C_NORMAL_prefix' : map.map_C_NORMAL_prefix,

                        'map_C_UV_prefix' : map.map_C_UV_prefix,

                        'map_C_ROUGHNESS_prefix' : map.map_C_ROUGHNESS_prefix,

                        'map_C_EMIT_prefix' : map.map_C_EMIT_prefix,

                        'map_C_ENVIRONMENT_prefix' : map.map_C_ENVIRONMENT_prefix,

                        'map_C_DIFFUSE_prefix' : map.map_C_DIFFUSE_prefix,

                        'map_C_GLOSSY_prefix' : map.map_C_GLOSSY_prefix,

                        'map_C_TRANSMISSION_prefix' : map.map_C_TRANSMISSION_prefix,

                        'map_cycles_use_pass_direct' : map.map_cycles_use_pass_direct,
                        'map_cycles_use_pass_indirect' : map.map_cycles_use_pass_indirect,
                        'map_cycles_use_pass_color' : map.map_cycles_use_pass_color,
                        'map_cycles_use_pass_diffuse' : map.map_cycles_use_pass_diffuse,
                        'map_cycles_use_pass_glossy' : map.map_cycles_use_pass_glossy,
                        'map_cycles_use_pass_transmission' : map.map_cycles_use_pass_transmission,
                        'map_cycles_use_pass_ambient_occlusion' : map.map_cycles_use_pass_ambient_occlusion,
                        'map_cycles_use_pass_emit' : map.map_cycles_use_pass_emit,

                        'map_NORMAL_prefix' : map.map_NORMAL_prefix,
                        # 'map_NORMAL_use_preview' : map.map_NORMAL_use_preview,
                        'map_normal_data' : map.map_normal_data,
                        'map_normal_space' : map.map_normal_space,
                        'map_normal_preset' : map.map_normal_preset,
                        'map_normal_custom_preset' : map.map_normal_custom_preset,
                        'map_normal_r' : map.map_normal_r,
                        'map_normal_g' : map.map_normal_g,
                        'map_normal_b' : map.map_normal_b,

                        'map_DISPLACEMENT_prefix' : map.map_DISPLACEMENT_prefix,
                        # 'map_DISPLACEMENT_use_preview' : map.map_DISPLACEMENT_use_preview,
                        'map_displacement_data' : map.map_displacement_data,
                        'map_displacement_result' : map.map_displacement_result,
                        'map_displacement_subdiv_levels' : map.map_displacement_subdiv_levels,

                        'map_VECTOR_DISPLACEMENT_prefix' : map.map_VECTOR_DISPLACEMENT_prefix,
                        # 'map_VECTOR_DISPLACEMENT_use_preview' : map.map_VECTOR_DISPLACEMENT_use_preview,
                        'map_vector_displacement_use_negative' : map.map_vector_displacement_use_negative,
                        'map_vector_displacement_result' : map.map_vector_displacement_result,
                        'map_vector_displacement_subdiv_levels' : map.map_vector_displacement_subdiv_levels,

                        'map_POSITION_prefix' : map.map_POSITION_prefix,
                        # 'map_POSITION_use_preview' : map.map_POSITION_use_preview,

                        'map_AO_prefix' : map.map_AO_prefix,
                        # 'map_AO_use_preview' : map.map_AO_use_preview,
                        'map_AO_use_default' : map.map_AO_use_default,
                        'map_ao_samples' : map.map_ao_samples,
                        'map_ao_distance' : map.map_ao_distance,
                        'map_ao_black_point' : map.map_ao_black_point,
                        'map_ao_white_point' : map.map_ao_white_point,
                        'map_ao_brightness' : map.map_ao_brightness,
                        'map_ao_contrast' : map.map_ao_contrast,
                        'map_ao_opacity' : map.map_ao_opacity,
                        'map_ao_use_local' : map.map_ao_use_local,
                        'map_ao_use_invert' : map.map_ao_use_invert,

                        'map_CAVITY_prefix' : map.map_CAVITY_prefix,
                        # 'map_CAVITY_use_preview' : map.map_CAVITY_use_preview,
                        'map_CAVITY_use_default' : map.map_CAVITY_use_default,
                        'map_cavity_black_point' : map.map_cavity_black_point,
                        'map_cavity_white_point' : map.map_cavity_white_point,
                        'map_cavity_power' : map.map_cavity_power,
                        'map_cavity_use_invert' : map.map_cavity_use_invert,

                        'map_CURVATURE_prefix' : map.map_CURVATURE_prefix,
                        # 'map_CURVATURE_use_preview' : map.map_CURVATURE_use_preview,
                        'map_CURVATURE_use_default' : map.map_CURVATURE_use_default,
                        'map_curv_samples' : map.map_curv_samples,
                        'map_curv_radius' : map.map_curv_radius,
                        'map_curv_black_point' : map.map_curv_black_point,
                        'map_curv_mid_point' : map.map_curv_mid_point,
                        'map_curv_white_point' : map.map_curv_white_point,
                        'map_curv_body_gamma' : map.map_curv_body_gamma,

                        'map_THICKNESS_prefix' : map.map_THICKNESS_prefix,
                        # 'map_THICKNESS_use_preview' : map.map_THICKNESS_use_preview,
                        'map_THICKNESS_use_default' : map.map_THICKNESS_use_default,
                        'map_thick_samples' : map.map_thick_samples,
                        'map_thick_distance' : map.map_thick_distance,
                        'map_thick_black_point' : map.map_thick_black_point,
                        'map_thick_white_point' : map.map_thick_white_point,
                        'map_thick_brightness' : map.map_thick_brightness,
                        'map_thick_contrast' : map.map_thick_contrast,
                        'map_thick_use_invert' : map.map_thick_use_invert,

                        'map_ID_prefix' : map.map_ID_prefix,
                        # 'map_ID_use_preview' : map.map_ID_use_preview,
                        'map_matid_data' : map.map_matid_data,
                        'map_matid_vertex_groups_name_contains' : map.map_matid_vertex_groups_name_contains,
                        'map_matid_algorithm' : map.map_matid_algorithm,
                        'map_matid_jilter' : map.map_matid_jilter,

                        'map_MASK_prefix' : map.map_MASK_prefix,
                        # 'map_MASK_use_preview' : map.map_MASK_use_preview,
                        'map_mask_data' : map.map_mask_data,
                        'map_mask_vertex_groups_name_contains' : map.map_mask_vertex_groups_name_contains,
                        'map_mask_materials_name_contains' : map.map_mask_materials_name_contains,
                        'map_mask_color1' : map.map_mask_color1,
                        'map_mask_color2' : map.map_mask_color2,
                        'map_mask_use_invert' : map.map_mask_use_invert,

                        'map_XYZMASK_prefix' : map.map_XYZMASK_prefix,
                        # 'map_XYZMASK_use_preview' : map.map_XYZMASK_use_preview,
                        'map_XYZMASK_use_default' : map.map_XYZMASK_use_default,
                        'map_xyzmask_use_x' : map.map_xyzmask_use_x,
                        'map_xyzmask_use_y' : map.map_xyzmask_use_y,
                        'map_xyzmask_use_z' : map.map_xyzmask_use_z,
                        'map_xyzmask_coverage' : map.map_xyzmask_coverage,
                        'map_xyzmask_saturation' : map.map_xyzmask_saturation,
                        'map_xyzmask_opacity' : map.map_xyzmask_opacity,
                        'map_xyzmask_use_invert' : map.map_xyzmask_use_invert,

                        'map_GRADIENT_prefix' : map.map_GRADIENT_prefix,
                        # 'map_GRADIENT_use_preview' : map.map_GRADIENT_use_preview,
                        'map_GRADIENT_use_default' : map.map_GRADIENT_use_default,
                        'map_gmask_type' : map.map_gmask_type,
                        'map_gmask_location_x' : map.map_gmask_location_x,
                        'map_gmask_location_y' : map.map_gmask_location_y,
                        'map_gmask_location_z' : map.map_gmask_location_z,
                        'map_gmask_rotation_x' : map.map_gmask_rotation_x,
                        'map_gmask_rotation_y' : map.map_gmask_rotation_y,
                        'map_gmask_rotation_z' : map.map_gmask_rotation_z,
                        'map_gmask_scale_x' : map.map_gmask_scale_x,
                        'map_gmask_scale_y' : map.map_gmask_scale_y,
                        'map_gmask_scale_z' : map.map_gmask_scale_z,
                        'map_gmask_coverage' : map.map_gmask_coverage,
                        'map_gmask_contrast' : map.map_gmask_contrast,
                        'map_gmask_saturation' : map.map_gmask_saturation,
                        'map_gmask_opacity' : map.map_gmask_opacity,
                        'map_gmask_use_invert' : map.map_gmask_use_invert,

                        'map_EDGE_prefix' : map.map_EDGE_prefix,
                        # 'map_EDGE_use_preview' : map.map_EDGE_use_preview,
                        'map_EDGE_use_default' : map.map_EDGE_use_default,
                        'map_edgemask_samples' : map.map_edgemask_samples,
                        'map_edgemask_radius' : map.map_edgemask_radius,
                        'map_edgemask_edge_contrast' : map.map_edgemask_edge_contrast,
                        'map_edgemask_body_contrast' : map.map_edgemask_body_contrast,
                        'map_edgemask_use_invert' : map.map_edgemask_use_invert,

                        'map_WIREFRAME_prefix' : map.map_WIREFRAME_prefix,
                        # 'map_WIREFRAME_use_preview' : map.map_WIREFRAME_use_preview,
                        'map_wireframemask_line_thickness' : map.map_wireframemask_line_thickness,
                        'map_wireframemask_use_invert' : map.map_wireframemask_use_invert,
                    }

                    # set
                    for map_key in map_data:
                        setattr(new_map, map_key, map_data[map_key])
                
                # channel packs
                # trash
                to_remove = []
                for channelpack_index, _ in enumerate(object.chnlp_channelpacking_table):
                    to_remove.append(channelpack_index)
                for channelpack_index in sorted(to_remove, reverse=True):
                    object.chnlp_channelpacking_table.remove(channelpack_index)
                object.chnlp_channelpacking_table_active_index = 0

                # add 
                for channelpack_index, channelpack in enumerate(self.chnlp_channelpacking_table):
                    object.chnlp_channelpacking_table_active_index = channelpack_index
                    channelpack_data = {
                        'global_channelpack_name' : channelpack.global_channelpack_name,
                        'global_channelpack_index' : channelpack_index + 1,
                        'global_channelpack_type' : channelpack.global_channelpack_type,

                        'R1G1B_use_R' : channelpack.R1G1B_use_R,
                        'R1G1B_map_R' : channelpack.R1G1B_map_R,
                        'R1G1B_use_G' : channelpack.R1G1B_use_G,
                        'R1G1B_map_G' : channelpack.R1G1B_map_G,
                        'R1G1B_use_B' : channelpack.R1G1B_use_B,
                        'R1G1B_map_B' : channelpack.R1G1B_map_B,

                        'RGB1A_use_RGB' : channelpack.RGB1A_use_RGB,
                        'RGB1A_map_RGB' : channelpack.RGB1A_map_RGB,
                        'RGB1A_use_A' : channelpack.RGB1A_use_A,
                        'RGB1A_map_A' : channelpack.RGB1A_map_A,

                        'R1G1B1A_use_R' : channelpack.R1G1B1A_use_R,
                        'R1G1B1A_map_R' : channelpack.R1G1B1A_map_R,
                        'R1G1B1A_use_G' : channelpack.R1G1B1A_use_G,
                        'R1G1B1A_map_G' : channelpack.R1G1B1A_map_G,
                        'R1G1B1A_use_B' : channelpack.R1G1B1A_use_B,
                        'R1G1B1A_map_B' : channelpack.R1G1B1A_map_B,
                        'R1G1B1A_use_A' : channelpack.R1G1B1A_use_A,
                        'R1G1B1A_map_A' : channelpack.R1G1B1A_map_A,
                    }

                    # set
                    new_channelpack = object.chnlp_channelpacking_table.add()
                    new_channelpack.global_channelpack_object_index = object_index
                    for chnlp_key in channelpack_data:
                        setattr(new_channelpack, chnlp_key, channelpack_data[chnlp_key])

                # object
                # set
                for key in data:
                    setattr(object, key, data[key])

###############################################################
### Texture Sets Funcs ###
###############################################################
def BM_TEXSET_OBJECT_PROPS_global_object_name_Items(self, context):
    new_items = []

    for index, object in enumerate(context.scene.bm_table_of_objects):
        # do not use objects that are already somewhere in a texset but include chosen
        if object.global_is_included_in_texset and self.global_source_object_index != index:
            continue
        # no name matching
        if context.scene.bm_props.global_use_name_matching is False:
            new_items.append((object.global_object_name, object.global_object_name, "Object"))
            continue
        # with name matching
        if object.nm_is_detached:
            new_items.append((object.global_object_name, object.global_object_name, "Detached Object"))
        elif object.nm_is_universal_container:
            new_items.append((object.nm_container_name, object.nm_container_name, "Universal Container"))

    # if len(new_items) == 0:
    #     new_items.append(('NONE', "None", "All objects are added to Texture Sets"))
    return new_items

def BM_TEXSET_OBJECT_PROPS_global_object_name_Update(self, context):
    # order of props assign is important! self.global_object_name's items get called
    if self.global_object_name != self.global_object_name_old:
        context.scene.bm_table_of_objects[self.global_source_object_index].global_is_included_in_texset = False
        self.global_object_name_old = self.global_object_name

        for index, object in enumerate(context.scene.bm_table_of_objects):
            if context.scene.bm_props.global_use_name_matching and object.nm_container_name == self.global_object_name:
                self.global_source_object_index = index
                break
            elif object.global_object_name == self.global_object_name:
                self.global_source_object_index = index
                break
        
        self.global_object_name_include = self.global_object_name
        context.scene.bm_table_of_objects[self.global_source_object_index].global_is_included_in_texset = True

        # recreate subitems
        item = context.scene.bm_table_of_objects[self.global_source_object_index]
        if item.nm_is_universal_container and context.scene.bm_props.global_use_name_matching:
            # trash
            to_remove = []
            for index, subitem in enumerate(self.global_object_name_subitems):
                to_remove.append(index)
            for index in sorted(to_remove, reverse=True):
                self.global_object_name_subitems.remove(index)
            # add
            local_c_master_index = -1
            for index, subitem in enumerate(context.scene.bm_table_of_objects):
                if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_is_lowpoly_container:
                    local_c_master_index = subitem.nm_master_index

                if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_item_local_container_master_index == local_c_master_index:
                    new_subitem = self.global_object_name_subitems.add()
                    new_subitem.global_object_name = subitem.global_object_name
                    new_subitem.global_object_index = len(self.global_object_name_subitems)
                    new_subitem.global_source_object_index = index

        BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

# TODO: Texsets funcs on bm_table Add, Remove, Move OTs

def BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOnAddOT(context):
    pass

def BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOnRemoveOT(context, removed_index):
    # remove object from texset
    pass

def BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOnMoveOT(context, moved_from_index: int, moved_to_index: int):
    # update texsets' objects' global_source_object_index property
    texsets = context.scene.bm_props.global_texturesets_table
    for texset in texsets:
        for texset_item in texset.global_textureset_table_of_objects:
            try:
                if texset_item.global_source_object_index == moved_from_index:
                    texset_item.global_source_object_index = moved_to_index
                elif texset_item.global_source_object_index == moved_to_index:
                    texset_item.global_source_object_index = moved_from_index
                texset_item.global_object_name_old = texset_item.global_object_name_include
                texset_item.global_object_name = texset_item.global_object_name_include
            except (ValueError, TypeError):
                pass

def BM_TEXSET_OBJECT_PROPS_global_object_name_RecreateSubitems(context, texset_item):
    # recreate subitems
    item = context.scene.bm_table_of_objects[texset_item.global_source_object_index]
    if item.nm_is_universal_container and context.scene.bm_props.global_use_name_matching:
        # trash
        to_remove = []
        for index, subitem in enumerate(texset_item.global_object_name_subitems):
            to_remove.append(index)
        for index in sorted(to_remove, reverse=True):
            texset_item.global_object_name_subitems.remove(index)
        # add
        local_c_master_index = -1
        for index, subitem in enumerate(context.scene.bm_table_of_objects):
            if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_is_lowpoly_container:
                local_c_master_index = subitem.nm_master_index

            if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_item_local_container_master_index == local_c_master_index:
                new_subitem = texset_item.global_object_name_subitems.add()
                new_subitem.global_object_name = subitem.global_object_name
                new_subitem.global_object_index = len(texset_item.global_object_name_subitems)
                new_subitem.global_source_object_index = index

def BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context):
    # order of items in global_object_name might be changed
    # try to reassign to be equal to global_is_included_in_texset
    texsets = context.scene.bm_props.global_texturesets_table
    for texset in texsets:
        for object in texset.global_textureset_table_of_objects:
            try:
                # reassigning old name too to skip
                for index, object1 in enumerate(context.scene.bm_table_of_objects):
                    if context.scene.bm_props.global_use_name_matching and object1.nm_container_name == object.global_object_name_include:
                        object.global_source_object_index = index
                        break
                    elif object1.global_object_name == object.global_object_name_include:
                        object.global_source_object_index = index
                        break
                object.global_object_name_old = object.global_object_name_include
                object.global_object_name = object.global_object_name_include
            except (ValueError, TypeError):
                pass

def BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, index):
    # if object was in texset and its removed from bm_table, remove item from texset as well
    texsets = context.scene.bm_props.global_texturesets_table
    for texset in texsets:
        for object_index, object in enumerate(texset.global_textureset_table_of_objects):
            if object.global_source_object_index == index:

                # remove obj from texset
                for item in texset.global_textureset_table_of_objects:
                    if item.global_object_index > object.global_object_index:
                        item.global_object_index -= 1

                context.scene.bm_table_of_objects[object.global_source_object_index].global_is_included_in_texset = False
                BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

                texset.global_textureset_table_of_objects.remove(object_index)
                if texset.global_textureset_table_of_objects_active_index > 0:
                    texset.global_textureset_table_of_objects_active_index -= 1

            # recreate subitems
            item = context.scene.bm_table_of_objects[object.global_source_object_index]
            if item.nm_is_universal_container and context.scene.bm_props.global_use_name_matching:
                # trash
                to_remove = []
                for index, subitem in enumerate(object.global_object_name_subitems):
                    to_remove.append(index)
                for index in sorted(to_remove, reverse=True):
                    object.global_object_name_subitems.remove(index)
                # add
                local_c_master_index = -1
                for index, subitem in enumerate(context.scene.bm_table_of_objects):
                    if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_is_lowpoly_container:
                        local_c_master_index = subitem.nm_master_index

                    if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_item_local_container_master_index == local_c_master_index:
                        new_subitem = object.global_object_name_subitems.add()
                        new_subitem.global_object_name = subitem.global_object_name
                        new_subitem.global_object_index = len(object.global_object_name_subitems)
                        new_subitem.global_source_object_index = index

            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

###############################################################
### Channel Packs Funcs ###
###############################################################
def BM_CHANNELPACK_PROPS_map_Items_GetAllChosen(self):
    chosen_data = {
        'R1G1B' : ['_map_R', '_map_G', '_map_B'],
        'RGB1A' : ['_map_RGB', '_map_A'],
        'R1G1B1A' : ['_map_R', '_map_G', '_map_B', '_map_A'],
    }
    chosen = []
    for prop in chosen_data[self.global_channelpack_type]:
        index_value = getattr(self, '{}{}_index'.format(self.global_channelpack_type, prop))
        if index_value != -1:
            chosen.append(index_value)

    return chosen

def BM_CHANNELPACK_PROPS_map_Items_Get(self, context, prop_channel_index):
    new_items = [('NONE', "None", "Set None to identify usage of no map for the current channel or no maps available to set")]
    chosen = BM_CHANNELPACK_PROPS_map_Items_GetAllChosen(self)
    # need the actual object
    object = context.scene.bm_table_of_objects[self.global_channelpack_object_index]
    maps_names = {
        'ALBEDO' : "AlbedoM",
        'METALNESS' : "Metalness",
        'ROUGHNESS' : "Roughness",
        'DIFFUSE' : "AlbedoS",
        'SPECULAR' : "Specular",
        'GLOSSINESS' : "Glossiness",
        'OPACITY' : "Opacity",
        'EMISSION' : "Emission/Lightmap",

        'NORMAL' : "Normal",
        'DISPLACEMENT' : "Displacement",
        'VECTOR_DISPLACEMENT' : "Vector Displacement",
        'POSITION' : "Position",
        'DECAL' : "Decal Pass",
        'AO' : "AO",
        'CAVITY' : "Cavity",
        'CURVATURE' : "Curvature",
        'THICKNESS' : "Thickness",
        'ID' : "Material ID",
        'MASK' : "Mask",
        'XYZMASK' : "XYZ Mask",
        'GRADIENT' : "Gradient Mask",
        'EDGE' : "Edge Mask",
        'WIREFRAME' : "Wireframe Mask",

        'PASS' : "BSDF Pass",
        'VERTEX_COLOR_LAYER' : "VertexColor Layer",
        'C_COMBINED' : "Combined",
        'C_AO' : "Ambient Occlusion",
        'C_SHADOW' : "Shadow",
        'C_POSITION' : "Position",
        'C_NORMAL' : "Normal",
        'C_UV' : "UV",
        'C_ROUGHNESS' : "Roughness",
        'C_EMIT' : "Emit",
        'C_ENVIRONMENT' : "Environment",
        'C_DIFFUSE' : "Diffuse",
        'C_GLOSSY' : "Glossy",
        'C_TRANSMISSION' : "Transmission",
    }
    for index, map in enumerate(object.global_maps):
        if map.global_map_index in chosen and map.global_map_index != prop_channel_index:
            continue
        name = '{} {}'.format(map.global_map_index, maps_names[map.global_map_type])
        new_items.append((str(map.global_map_index), name, "Choose map from the Object's Table of Maps for the current channel"))
    return new_items

def BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, prop_name):
    try:
        setattr(self, prop_name.format("_index"), int(getattr(self, prop_name.format(""))))
    except ValueError:
        setattr(self, prop_name.format("_index"), -1)

def BM_CHANNELPACK_PROPS_map_UpdateNames(self):
    chosen_data = {
        'R1G1B' : ['_map_R', '_map_G', '_map_B'],
        'RGB1A' : ['_map_RGB', '_map_A'],
        'R1G1B1A' : ['_map_R', '_map_G', '_map_B', '_map_A'],
    }
    for prop in chosen_data[self.global_channelpack_type]:
        index_value_prop = '{}{}_index'.format(self.global_channelpack_type, prop)
        map_value_prop = '{}{}'.format(self.global_channelpack_type, prop)
        index_value = str(getattr(self, index_value_prop))
        if index_value != "-1" and getattr(self, map_value_prop) != index_value:
            setattr(self, map_value_prop, index_value)
        elif index_value == "-1" and getattr(self, map_value_prop) != 'NONE':
            setattr(self, map_value_prop, 'NONE')

# Items
def BM_CHANNELPACK_PROPS_map_Items_R1G1B_R(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B_map_R_index)
def BM_CHANNELPACK_PROPS_map_Items_R1G1B_G(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B_map_G_index)
def BM_CHANNELPACK_PROPS_map_Items_R1G1B_B(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B_map_B_index)

def BM_CHANNELPACK_PROPS_map_Items_RGB1A_RGB(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.RGB1A_map_RGB_index)
def BM_CHANNELPACK_PROPS_map_Items_RGB1A_A(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.RGB1A_map_A_index)

def BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_R(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B1A_map_R_index)
def BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_G(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B1A_map_G_index)
def BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_B(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B1A_map_B_index)
def BM_CHANNELPACK_PROPS_map_Items_R1G1B1A_A(self, context):
    return BM_CHANNELPACK_PROPS_map_Items_Get(self, context, self.R1G1B1A_map_A_index)

# Updates
def BM_CHANNELPACK_PROPS_map_Update_R1G1B_R(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B_map_R{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)
def BM_CHANNELPACK_PROPS_map_Update_R1G1B_G(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B_map_G{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)
def BM_CHANNELPACK_PROPS_map_Update_R1G1B_B(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B_map_B{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)

def BM_CHANNELPACK_PROPS_map_Update_RGB1A_RGB(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'RGB1A_map_RGB{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)
def BM_CHANNELPACK_PROPS_map_Update_RGB1A_A(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'RGB1A_map_A{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)

def BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_R(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B1A_map_R{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)
def BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_G(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B1A_map_G{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)
def BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_B(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B1A_map_B{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)
def BM_CHANNELPACK_PROPS_map_Update_R1G1B1A_A(self, context):
    BM_CHANNELPACK_PROPS_map_Update_SetGivenIndexProp(self, r'R1G1B1A_map_A{}')
    BM_CHANNELPACK_PROPS_map_UpdateNames(self)

###############################################################
### Batch Naming Funcs ###
###############################################################
# def BM_BATCHNAMINGKEY_PROPS_global_keyword_Items(self, context):
#     gen_items = {
#         "OBJECT_INDEX" : ('OBJECT_INDEX', "_objectindex_", "Write Object index in the Table of Objects"),
#         "OBJECT_NAME" : ('OBJECT_NAME', "_objectname_", "Write Object name"),
#         "CONTAINER_NAME" : ('CONTAINER_NAME', "_containername_", "Write Container name"),
#         "PACK_NAME" : ('PACK_NAME', "_packname_", "Write Channel Pack name if map is present in Channel Pack. If not then do not write anything"),
#         "TEXSET_NAME" : ('TEXSET_NAME', "_texsetname_", "Write Texture Set chosen name convention if Object is present in Texture Set. If not then do not write anything"),
#         "MAP_INDEX" : ('MAP_INDEX', "_mapindex_", "Write map index in the Object's Table of Maps"),
#         "MAP_NAME" : ('MAP_NAME', "_mapname_", "Write map name"),
#         "MAP_RES" : ('MAP_RES', "_mapres_", "Write map Resolution in chosen format"),
#         "MAP_BIT" : ('MAP_BIT', "_mapbit_", "Write _32bit_ if map uses 32bit Float, otherwise write _8bit_"),
#         "MAP_TRANS" : ('MAP_TRANS', "_maptrans_", "Write _trans_ or custom if map uses transparent background. If doesn't use then do not write anything"),
#         "MAP_SSAA" : ('MAP_SSAA', "_mapssaa_", "Write SSAA value (e.g. 4x4) used for the map. If no SSAA used then do not write anything"),
#         "MAP_SAMPLES" : ('MAP_SAMPLES', "_mapsamples_", "Write number of map bake samples. If map uses Adaptive Sampling, write max samples value"),
#         "MAP_DENOISE" : ('MAP_DENOISE', "_mapdenoise_", "Write _denoised_ or custom if map was denoised. If wasn't denoised then do not write anything"),
#         "MAP_NORMAL" : ('MAP_NORMAL', "_mapnormal_", "For Normal map, write preset type. For example, _blender_, _unity_, _directX_, _custom_"),
#         "MAP_UV" : ('MAP_UV', "_mapuv_", "Write UV Layer name used for baking map"),
#         "ENGINE" : ('ENGINE', "_engine_", "Write Bake Engine used for baking. _CPU_ or _GPU"),
#         "AUTO_UV" : ('AUTO_UV', "_autouv_", "Write _autouv_ or custom if object was auto uv unwrapped. If not then do not write anything"),
#     }
#     new_items = []
#     used_items = []

#     object = BM_Object_Get(self, context)[0]
#     for index, keyword in enumerate(object.bake_batch_name_table):
#         if index != self.global_keyword_index:
#             used_items.append(keyword.global_keyword_old)

#     for keyword in gen_items:
#         if keyword not in used_items:
#             new_items.append(gen_items.get(keyword))

#     # if len(new_items) == 0:
#     #     new_items.append(('NONE', "None", "All objects are added to Texture Sets"))
#     return new_items

# def BM_BATCHNAMINGKEY_PROPS_global_keyword_Update(self, context):
#     self.global_keword_old = self.global_keyword

# def BM_BATCHNAMINGKEY_PROPS_global_keyword_UpdateOrder(context):
#     object = BM_Object_Get(self, context)[0]
#     for keyword in object.bake_batch_name_table:
#         try:
#             keyword.global_keyword = keyword.global_keyword_old
#         except (TypeError, ValueError):
#             pass

def BM_ITEM_PROPS_bake_batchname_GetPreview(self, context, object=None, map=None, global_active_index=None, decal_texset_tag=""):
    # funcs for data get
    def get_objectname(container):
        if not any([container.nm_is_universal_container, container.nm_is_local_container]):
            return container.global_object_name
        for obj in context.scene.bm_table_of_objects:
            if obj.nm_item_uni_container_master_index == container.nm_master_index and obj.nm_is_local_container is False:
                return obj.global_object_name
    
    def get_containername(container):
        if context.scene.bm_props.global_use_name_matching is False:
            return None
        if container.nm_is_universal_container:
            return container.nm_container_name
        for obj in context.scene.bm_table_of_objects:
            if container.nm_item_uni_container_master_index == obj.nm_master_index and obj.nm_is_universal_container:
                return obj.nm_container_name
    
    def get_packname(container, map):
        for chnlpack in container.chnlp_channelpacking_table:
            chosen_data = {
                'R1G1B' : ['_map_R', '_map_G', '_map_B'],
                'RGB1A' : ['_map_RGB', '_map_A'],
                'R1G1B1A' : ['_map_R', '_map_G', '_map_B', '_map_A'],
            }
            chosen_maps = []
            for prop in chosen_data[chnlpack.global_channelpack_type]:
                chosen_maps.append(getattr(chnlpack, '{}{}'.format(chnlpack.global_channelpack_type, prop)))
            if str(map.global_map_index) in chosen_maps:
                return chnlpack.global_channelpack_name
        return None
    
    def get_texsetname(container):
        if not any([container.nm_is_universal_container, container.nm_is_local_container]):
            container_name = container.global_object_name
        else:
            container_name = container.nm_container_name
        
        for texset in context.scene.bm_props.global_texturesets_table:
            for obj in texset.global_textureset_table_of_objects:
                if obj.global_object_name == container_name:
                    if texset.global_textureset_naming == 'TEXSET_INDEX':
                        return "TextureSet%d" % texset.global_textureset_index
                    elif texset.global_textureset_naming == 'TEXSET_NAME':
                        return texset.global_textureset_name
                    else:
                        return_name = ""
                        for obj1 in texset.global_textureset_table_of_objects:
                            if context.scene.bm_table_of_objects[obj1.global_source_object_index].nm_is_universal_container:
                                for subobj in obj1.global_object_name_subitems:
                                    if subobj.global_object_include_in_texset:
                                        return_name += "%s_" % subobj.global_object_name
                            else:
                                return_name += "%s_" % obj1.global_object_name
                        return return_name[:-1]
                for subobject in obj.global_object_name_subitems:
                    if subobject.global_object_name == container_name:
                        if texset.global_textureset_naming == 'TEXSET_INDEX':
                            return "TextureSet%d" % texset.global_textureset_index
                        elif texset.global_textureset_naming == 'TEXSET_NAME':
                            return texset.global_textureset_name
                        else:
                            return_name = ""
                            for obj1 in texset.global_textureset_table_of_objects:
                                if context.scene.bm_table_of_objects[obj1.global_source_object_index].nm_is_universal_container:
                                    for subobj in obj1.global_object_name_subitems:
                                        if subobj.global_object_include_in_texset:
                                            return_name += "%s_" % subobj.global_object_name
                                else:
                                    return_name += "%s_" % obj1.global_object_name
                            return return_name[:-1]
            return None

    def get_mapres(map_pass):
        if map_pass.out_res == 'CUSTOM':
            return str(map_pass.out_res_height) + "x" + str(map_pass.out_res_width)
        else:
            return map_pass.out_res
    
    def get_mapnormal(map_pass):
        if map.global_map_type != 'NORMAL':
            return None
        if map.map_normal_preset != 'CUSTOM':
            return map.map_normal_preset
        else:
            return map.map_normal_custom_preset
    
    if object is None:
        object = BM_Object_Get(self, context)[0]
        if len(object.global_maps) == 0:
            # self.bake_batchname_preview = "*Object has no Maps*"
            return "*Object has no Maps*"
        map = object.global_maps[object.global_maps_active_index]
        global_active_index = context.scene.bm_props.global_active_index
     
    gen_keywords_values = {
        "$objectindex" : global_active_index,
        "$objectname" : get_objectname(object),
        "$containername" : get_containername(self),
        "$packname" : get_packname(self, map),
        "$texsetname" : get_texsetname(self),
        "$mapindex" : map.global_map_index,
        "$mapname" : getattr(map, 'map_{}_prefix'.format(map.global_map_type)),
        "$mapres" : get_mapres(map),
        "$mapbit" : "32bit" if map.out_use_32bit else "8bit",
        "$maptrans" : "transbg" if map.out_use_transbg else "",
        "$mapssaa" : map.out_super_sampling_aa,
        "$mapsamples" : map.out_samples,
        "$mapdenoise" : "denoised" if map.out_use_denoise else "",
        "$mapnormal" : get_mapnormal(map),
        "$mapuv" : map.uv_active_layer,
        "$engine" : self.bake_device,
        "$autouv" : "autouv" if self.uv_use_auto_unwrap else "",
    }

    preview = ""
    temp_preview = ""
    finding_keyword = False
    for index, char in enumerate(self.bake_batchname):
        # adding chars until $ found - means that we need to insert keyword
        if finding_keyword is False:
            if char == '$':
                finding_keyword = True
                temp_preview = "$"
            else:
                preview += char
        # trying to find keyword value, if can't continue adding chars to temp_preview
        else:
            # no keyword found but found $, aborting finding keyword and adding temp_preview to preview
            if char == '$':
                preview += temp_preview
                temp_preview = '$'
                continue

            temp_preview += char
            try:
                gen_keywords_values[temp_preview.lower()]
            except KeyError:
                if index == len(self.bake_batchname) - 1:
                    preview += temp_preview
            else:
                # keyword found, add its value to preview
                if gen_keywords_values[temp_preview.lower()] is None:
                    finding_keyword = False
                    continue
                if self.bake_batchname_use_caps:
                    preview += str(gen_keywords_values[temp_preview.lower()]).upper()
                else:
                    preview += str(gen_keywords_values[temp_preview.lower()])
                finding_keyword = False

    # self.bake_batchname_preview = preview

    # limit to max 63 characters
    # take decal prefix into account
    len_crop = len(preview + decal_texset_tag) - 63
    if len_crop > 0:
        preview = preview[:-len_crop]

    # add decal_texset_tag
    preview += decal_texset_tag.upper() if object.bake_batchname_use_caps else decal_texset_tag

    # translate
    trans = str.maketrans({char: "_" for char in " |!@#$%^&*(){}:\";'[]<>,.\\/?"})
    preview = preview.translate(trans).strip("_")

    return preview

def BM_ITEM_PROPS_bake_batchname_use_caps_Update(self, context):
    BM_LastEditedProp_Write(context, "Object Bake Output: Batch name use caps", "bake_batchname_use_caps", getattr(self, "bake_batchname_use_caps"), False)
    # upper-case batch name if true else lower-case
    self.bake_batchname = self.bake_batchname.upper() if self.bake_batchname_use_caps else self.bake_batchname.lower()

###############################################################
### BM Table of Objects Funcs ###
###############################################################
def BM_ActiveIndexUpdate(self, context):
    # if context.scene.bm_props.global_bake_available is False:
        # return
    if len(context.scene.bm_table_of_objects):
        source_object = BM_Object_Get(None, context)
        if source_object[1]:
            source_object = context.scene.objects[source_object[0].global_object_name]
            
            if not source_object.visible_get():
                return

            for ob in context.scene.objects:
                ob.select_set(False)

            source_object.select_set(True)
            context.view_layer.objects.active = source_object

def BM_LastEditedProp_Write(context, name: str, prop: str, value: any, is_map: bool):
    context.scene.bm_props.global_last_edited_prop = prop
    context.scene.bm_props.global_last_edited_prop_name = name
    context.scene.bm_props.global_last_edited_prop_is_map = is_map
    context.scene.bm_props.global_last_edited_prop_value = str(value)
    if type(value) == int:
        context.scene.bm_props.global_last_edited_prop_type = "int"
    elif type(value) == float:
        context.scene.bm_props.global_last_edited_prop_type = "float"
    elif type(value) == str:
        context.scene.bm_props.global_last_edited_prop_type = "str"
    elif type(value) == bool:
        if value:
            context.scene.bm_props.global_last_edited_prop_value = '1'
        else:
            context.scene.bm_props.global_last_edited_prop_value = '0'

        context.scene.bm_props.global_last_edited_prop_type = "bool"
    elif type(value) == tuple:
        real_value = ""
        for x in value:
            real_value += str(x)
        context.scene.bm_props.global_last_edited_prop_value = real_value


def BM_Table_of_Objects_GetFTL(context, items, bitflag_filter_item):
        # default return values
        ftl_flags = []
        ftl_neworder = []

        # initialize with all items visible
        if context.scene.bm_props.global_use_name_matching is False:
            ftl_flags = [bitflag_filter_item] * len(items)
            ftl_neworder = [index for index, _ in enumerate(items)]
            
        # initialize with items unvisible if items' parent container nm_is_expanded is False
        else:
            ftl_flags = [bitflag_filter_item] * len(items)
            for global_index, global_object in enumerate(items):
                # visible universal container, all its items unvisible
                if global_object.nm_is_universal_container and global_object.nm_is_expanded is False:
                    ftl_neworder.append(global_index)
                    for local_index, local_object in enumerate(items):
                        if local_object.nm_item_uni_container_master_index == global_object.nm_master_index:
                            ftl_flags[local_index] &= ~bitflag_filter_item
                # visible local container, all its items unvisible
                elif global_object.nm_is_local_container and global_object.nm_is_expanded is False:
                    ftl_neworder.append(global_index)
                    for local_index, local_object in enumerate(items):
                        if local_object.nm_item_uni_container_master_index == global_object.nm_item_uni_container_master_index and local_object.nm_item_local_container_master_index == global_object.nm_master_index:
                            ftl_flags[local_index] &= ~bitflag_filter_item
            ftl_neworder = sorted([index for index, item in enumerate(items) if ftl_flags[index] == ~bitflag_filter_item])

        return ftl_flags, ftl_neworder

def BM_GetObject_from_prop_update(self, context):
    try:
        context.scene.bm_table_of_objects[context.scene.bm_props.global_active_index]
    except IndexError:
        if hasattr(self, "global_map_object_index"):
            return context.scene.bm_table_of_objects[self.global_map_object_index]
        else:
            return self
    else:
        return BM_Object_Get(None, context)[0]

###############################################################
### decal Props Funcs ###
###############################################################
def BM_ITEM_PROPS_decal_is_decal_Update(self, context):
    BM_LastEditedProp_Write(context, "Object Decal: Is Decal", "decal_is_decal", getattr(self, "decal_is_decal"), False)
    if self.decal_is_decal:
        self.hl_use_cage = False
        self.hl_use_unique_per_map = False
        BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(self, self, context)

###############################################################
### hl Props Funcs ###
###############################################################
def BM_ITEM_PROPS_hl_use_unique_per_map_Update(self, context):
    BM_LastEditedProp_Write(context, "Object High to Lowpoly: Unique per map", "hl_use_unique_per_map", getattr(self, "hl_use_unique_per_map"), False)
    object = self
    if object.hl_use_unique_per_map:
        data = {
            'hl_cage_type' : object.hl_cage_type,
            'hl_cage_extrusion' : object.hl_cage_extrusion,
            'hl_max_ray_distance' : object.hl_max_ray_distance,
            'hl_use_cage' : object.hl_use_cage,
            'hl_cage' : object.hl_cage,
        }
        object.hl_use_cage = False
        set_highpoly = False
        highpoly_data = []
        
        for highpoly in object.hl_highpoly_table:
            highpoly_data.append(highpoly.global_object_name)

        if len(object.hl_highpoly_table):
            set_highpoly = True
            BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(object, object, context)

        for map_index, map in enumerate(object.global_maps):
            object.global_maps_active_index = map_index
            for key in data:
                if key == 'hl_cage' and map.hl_use_cage is False:
                    continue
                setattr(map, key, data[key])

            if set_highpoly:
                for index, key in enumerate(highpoly_data):
                    new_highpoly = map.hl_highpoly_table.add()
                    new_highpoly.global_item_index = index + 1
                    new_highpoly.global_holder_index = context.scene.bm_props.global_active_index
                    BM_ITEM_PROPS_hl_add_highpoly_Update(new_highpoly, context)
                    new_highpoly.global_object_name = key
                    map.hl_highpoly_table_active_index = len(map.hl_highpoly_table) - 1
                    object.hl_is_lowpoly = True
    
    else:
        for map in object.global_maps:
            BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(map, object, context)

def BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(container, object, context):
    to_remove = []
    for index, _ in enumerate(container.hl_highpoly_table):
        to_remove.append(index)
    for index in sorted(to_remove, reverse=True):
        context.scene.bm_table_of_objects[container.hl_highpoly_table[index].global_highpoly_object_index].hl_is_highpoly = False
        container.hl_highpoly_table.remove(index)
    container.hl_highpoly_table_active_index = 0
    object.hl_is_lowpoly = False

def BM_ITEM_PROPS_hl_cage_Items(self, context):
    items = []
    # if was chosen None, append it to items
    if self.hl_cage_object_include == 'NONE' and self.hl_cage_object_index == -1:
        items.append(('NONE', "None", "No cage available within the Table of Objects"))

    # active_object = BM_GetObject_from_prop_update(self, context)
    active_object = BM_Object_Get(self, context)[0]
    active_index = context.scene.bm_props.global_active_index
    use_nm = context.scene.bm_props.global_use_name_matching
    cage_container_master_index = -1
    include = []
    if active_object.hl_use_unique_per_map and len(active_object.global_maps):
        active_map = BM_Map_Get(self, active_object)
        for map in active_object.global_maps:
            if map.global_map_index == active_map.global_map_index:
                continue
            if map.hl_use_cage and map.hl_cage_object_index != -1 and map.hl_cage_name_old not in include:
                include.append(map.hl_cage_name_old)
    added = []

    for index, object in enumerate(context.scene.bm_table_of_objects):
        # add current chosen cage
        if (index == self.hl_cage_object_index and object.global_object_name not in added) or (object.global_object_name in include and object.global_object_name not in added):
            items.append((str(object.global_object_name), object.global_object_name, "Object to use as Cage"))
            added.append(object.global_object_name)
            continue
        # skip the item itself and all cages, lows, high already
        if any([object.hl_is_cage, object.hl_is_lowpoly, object.hl_is_highpoly]) or index in [self.hl_cage_object_index, active_index]:#object.global_object_name == active_object.global_object_name:
            continue
        if use_nm:
            if active_object.nm_is_detached:
                if object.nm_is_detached:
                    items.append((str(object.global_object_name), object.global_object_name, "Object to use as Cage"))
                    added.append(object.global_object_name)
            else:
                if all([object.nm_is_local_container, object.nm_is_cage_container, object.nm_item_uni_container_master_index == active_object.nm_item_uni_container_master_index, cage_container_master_index == -1]):
                    cage_container_master_index = object.nm_master_index
                if cage_container_master_index != -1 and object.nm_item_local_container_master_index == cage_container_master_index and object.nm_item_uni_container_master_index == active_object.nm_item_uni_container_master_index:
                    items.append((str(object.global_object_name), object.global_object_name, "Object to use as Cage"))
                    added.append(object.global_object_name)
        else:
            items.append((str(object.global_object_name), object.global_object_name, "Object to use as Cage"))
            added.append(object.global_object_name)

    if len(items) == 0:
        items.append(('NONE', "None", "No cage available within the Table of Objects"))
    return items

def BM_ITEM_PROPS_hl_cage_Update(self, context):
    if self.hl_cage != self.hl_cage_name_old:
        update_name = False
        if self.hl_cage_name_old == 'NONE':
            update_name = True
        self.hl_cage_name_old = self.hl_cage
        try:
            context.scene.bm_table_of_objects[self.hl_cage_object_index].hl_is_cage = False
        except IndexError:
            pass
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if object.global_object_name == self.hl_cage_name_old and not any([object.nm_is_local_container, object.nm_is_universal_container]):
                self.hl_cage_object_index = index
                break
        if self.hl_cage_object_index != -1:
            context.scene.bm_table_of_objects[self.hl_cage_object_index].hl_is_cage = True
        if update_name:
            self.hl_cage = self.hl_cage_name_old
        self.hl_cage_object_include = self.hl_cage
        try:
            self.global_map_type
        except AttributeError:
            return
        else:
            object = BM_Object_Get(self, context)[0]
            if object.hl_use_unique_per_map:
                for map in object.global_maps:
                    if map.hl_use_cage and map.hl_cage_object_index != -1:
                        context.scene.bm_table_of_objects[map.hl_cage_object_index].hl_is_cage = True

def BM_ITEM_PROPS_hl_use_cage_Update(self, context):
    if self.hl_use_cage:
        # explicit abort for setting cage for uni_c 
        # in its is_global update, use_cage set to True
        # random object is getting set as cage, which is bad
        # added check to abort all this for containers
        # including the occasion if self == map
        if hasattr(self, "nm_is_universal_container"):
            if any([self.nm_is_universal_container, self.nm_is_local_container]):
                self.hl_cage_name_old = ""
                self.hl_cage_object_index = -1
                self.hl_cage_object_include = ""
                return

        update_name = False
        if self.hl_cage_name_old == 'NONE':
            update_name = True
        self.hl_cage_name_old = self.hl_cage
        try:
            context.scene.bm_table_of_objects[self.hl_cage_object_index].hl_is_cage = False
        except IndexError:
            pass
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if object.global_object_name == self.hl_cage_name_old and not any([object.nm_is_local_container, object.nm_is_universal_container]):
                self.hl_cage_object_index = index
                break
        if self.hl_cage_object_index != -1:
            context.scene.bm_table_of_objects[self.hl_cage_object_index].hl_is_cage = True
        if update_name:
            self.hl_cage = self.hl_cage_name_old
        self.hl_cage_object_include = self.hl_cage
    else:
        self.hl_cage_name_old = ""
        try:
            context.scene.bm_table_of_objects[self.hl_cage_object_index].hl_is_cage = False
        except IndexError:
            pass
        self.hl_cage_object_index = -1
        self.hl_cage_object_include = ""

def BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, index, type):
    if type == 'OBJECT':
        object = context.scene.bm_table_of_objects[index]
        if object.hl_use_unique_per_map:
            for map in object.global_maps:
                if map.hl_use_cage:
                    map.hl_use_cage = False
        else:
            if object.hl_use_cage:
                object.hl_use_cage = False
            elif object.hl_is_cage:
                for object1 in context.scene.bm_table_of_objects:
                    if object1.hl_use_unique_per_map:
                        for map in object1.global_maps:
                            if map.hl_use_cage and map.hl_cage_object_index == index:
                                map.hl_use_cage = False
                    elif object1.hl_cage_object_index == index:
                        object1.hl_use_cage = False
    elif type == 'MAP':
        object = BM_Object_Get(None, context)[0]
        map = object.global_maps[index]
        if map.hl_use_cage:
            map.hl_use_cage = False
            for map1 in object.global_maps:
                if map1.hl_use_cage and map1.hl_cage_object_index != -1:
                    context.scene.bm_table_of_objects[map1.hl_cage_object_index].hl_is_cage = True

def BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context):
    for object in context.scene.bm_table_of_objects:
        if object.hl_use_unique_per_map:
            for map in object.global_maps:
                if map.hl_use_cage and map.hl_cage_object_index == -1:
                    map.hl_use_cage = False
        elif object.hl_use_cage and object.hl_cage_object_index == -1:
            object.hl_use_cage = False

def BM_ITEM_PROPS_hl_cage_UpdateOrder(context):
    for object in context.scene.bm_table_of_objects:
        if object.hl_use_unique_per_map:
            for map in object.global_maps:
                if map.hl_use_cage and map.hl_cage_object_index != -1:
                    try:
                        for index, object1 in enumerate(context.scene.bm_table_of_objects):
                            if object1.global_object_name == map.hl_cage_object_include and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                                map.hl_cage_object_index = index
                                break
                        map.hl_cage_name_old = map.hl_cage_object_include
                        map.hl_cage = map.hl_cage_object_include
                    except (ValueError, TypeError):
                        pass
        elif object.hl_use_cage and object.hl_cage_object_index != -1:
            try:
                for index, object1 in enumerate(context.scene.bm_table_of_objects):
                    if object1.global_object_name == object.hl_cage_object_include and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                        object.hl_cage_object_index = index
                        break
                object.hl_cage_name_old = object.hl_cage_object_include
                object.hl_cage = object.hl_cage_object_include
            except (ValueError, TypeError):
                pass
 
def BM_ITEM_PROPS_hl_highpoly_Items(self, context):
    try:
        context.scene.bm_table_of_objects[context.scene.bm_props.global_active_index]
    except IndexError:
        return []
    items = []
    # if was chosen None, append it to items
    if self.global_highpoly_object_include == 'NONE' and self.global_highpoly_object_index == -1:
        items.append(('NONE', "None", "No cage available within the Table of Objects"))

    # active_object = BM_GetObject_from_prop_update(self, context)
    active_object = context.scene.bm_table_of_objects[self.global_holder_index]
    active_index = context.scene.bm_props.global_active_index
    use_nm = context.scene.bm_props.global_use_name_matching
    high_container_master_index = -1
    include = []
    skip_include = []
    if active_object.hl_use_unique_per_map and len(active_object.global_maps):
        active_map = BM_Map_Get(self, active_object)
        for index, highpoly in enumerate(active_map.hl_highpoly_table):
            if highpoly.global_highpoly_object_index != -1:
                skip_include.append(highpoly.global_highpoly_name_old)
        for map in active_object.global_maps:
            if map.global_map_index == active_map.global_map_index:
                continue
            for highpoly in map.hl_highpoly_table:
                if highpoly.global_highpoly_object_index != -1 and all([highpoly.global_highpoly_name_old not in include, highpoly.global_highpoly_name_old not in skip_include]):
                    include.append(highpoly.global_highpoly_name_old)
    added = []

    for index, object in enumerate(context.scene.bm_table_of_objects):
        # add current chosen high
        if (index == self.global_highpoly_object_index and object.global_object_name not in added) or (object.global_object_name in include and object.global_object_name not in added):
            items.append((str(object.global_object_name), object.global_object_name, "Object to use as Highpoly"))
            added.append(object.global_object_name)
            continue
        # skip the item itself and all cages, lows, high already
        if any([object.hl_is_cage, object.hl_is_lowpoly, object.hl_is_highpoly]) or index in [self.global_highpoly_object_index, active_index]:
            continue
        if use_nm:
            if active_object.nm_is_detached:
                if object.nm_is_detached:
                    items.append((str(object.global_object_name), object.global_object_name, "Object to use as Highpoly"))
                    added.append(object.global_object_name)
            else:
                if all([object.nm_is_local_container, object.nm_is_highpoly_container, object.nm_item_uni_container_master_index == active_object.nm_item_uni_container_master_index, high_container_master_index == -1]):
                    high_container_master_index = object.nm_master_index
                if high_container_master_index != -1 and object.nm_item_local_container_master_index == high_container_master_index and object.nm_item_uni_container_master_index == active_object.nm_item_uni_container_master_index:
                    items.append((str(object.global_object_name), object.global_object_name, "Object to use as Highpoly"))
                    added.append(object.global_object_name)
        else:
            items.append((str(object.global_object_name), object.global_object_name, "Object to use as Highpoly"))
            added.append(object.global_object_name)

    if len(items) == 0:
        items.append(('NONE', "None", "No highpoly available within the Table of Objects"))
    return items

def BM_ITEM_PROPS_hl_highpoly_Update(self, context):
    if self.global_object_name != self.global_highpoly_name_old:
        update_name = False
        if self.global_highpoly_name_old == 'NONE':
            update_name = True
        self.global_highpoly_name_old = self.global_object_name
        try:
            context.scene.bm_table_of_objects[self.global_highpoly_object_index].hl_is_highpoly = False
        except IndexError:
            pass
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if object.global_object_name == self.global_highpoly_name_old and not any([object.nm_is_local_container, object.nm_is_universal_container]):
                self.global_highpoly_object_index = index
                break
        if self.global_highpoly_object_index != -1:
            context.scene.bm_table_of_objects[self.global_highpoly_object_index].hl_is_highpoly = True
        self.global_highpoly_object_include = self.global_object_name
        if update_name:
            self.global_object_name = self.global_highpoly_name_old
        BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)

def BM_ITEM_PROPS_hl_add_highpoly_Update(self, context):
    self.global_highpoly_name_old = self.global_object_name
    try:
        context.scene.bm_table_of_objects[self.global_highpoly_object_index].hl_is_highpoly = False
    except IndexError:
        pass
    for index, object in enumerate(context.scene.bm_table_of_objects):
        if object.global_object_name == self.global_highpoly_name_old and not any([object.nm_is_local_container, object.nm_is_universal_container]):
            self.global_highpoly_object_index = index
            break
    if self.global_highpoly_object_index != -1:
        context.scene.bm_table_of_objects[self.global_highpoly_object_index].hl_is_highpoly = True
    self.global_highpoly_object_include = self.global_object_name
    BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)
    BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)

def BM_ITEM_PROPS_hl_remove_highpoly_Update(self, context):
    try: 
        context.scene.bm_table_of_objects[self.global_highpoly_object_index].hl_is_highpoly = False
    except IndexError:
        pass
    BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)

def BM_ITEM_PROPS_hl_highpoly_UpdateNames(context):
    for object in context.scene.bm_table_of_objects:
        if object.hl_use_unique_per_map:
            for map in object.global_maps:
                for highpoly in map.hl_highpoly_table:
                    if highpoly.global_highpoly_object_index != -1:
                        context.scene.bm_table_of_objects[highpoly.global_highpoly_object_index].hl_is_highpoly = True
        else:
            for highpoly in object.hl_highpoly_table:
                if highpoly.global_highpoly_object_index != -1:
                    context.scene.bm_table_of_objects[highpoly.global_highpoly_object_index].hl_is_highpoly = True

def BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_RemoveHighpoly(context, container, index):
    for highpoly_index, highpoly in enumerate(container.hl_highpoly_table):
        if highpoly.global_highpoly_object_index == index:
            # default remove highpoly
            for item in container.hl_highpoly_table:
                if item.global_item_index > highpoly.global_item_index:
                    item.global_item_index -= 1
            # set hl_is_highpoly to False for chosen highpoly on remove
            BM_ITEM_PROPS_hl_remove_highpoly_Update(highpoly, context)
            container.hl_highpoly_table.remove(highpoly_index)
            if container.hl_highpoly_table_active_index > 0:
                container.hl_highpoly_table_active_index -= 1
            # update highpolies order
            BM_ITEM_PROPS_hl_highpoly_UpdateOrder(context)
            break

def BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, container):
    if container.hl_use_unique_per_map:
        for map in container.global_maps:
            for highpoly in map.hl_highpoly_table:
                if highpoly.global_highpoly_object_index != -1:
                    BM_ITEM_PROPS_hl_remove_highpoly_Update(highpoly, context)
    else:
        for highpoly in container.hl_highpoly_table:
            if highpoly.global_highpoly_object_index != -1:
                BM_ITEM_PROPS_hl_remove_highpoly_Update(highpoly, context)

def BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, index, type, removed_was_highpoly):
    if type == 'OBJECT':
        if removed_was_highpoly:
            for object1 in context.scene.bm_table_of_objects:
                if object1.hl_use_unique_per_map:
                    len_of_highpolies = 0
                    for map in object1.global_maps:
                        BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_RemoveHighpoly(context, map, index)
                        len_of_highpolies += len(map.hl_highpoly_table)
                    if len_of_highpolies == 0:
                        object1.hl_is_lowpoly = False
                else:
                    BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_RemoveHighpoly(context, object1, index)
                    if len(object1.hl_highpoly_table) == 0:
                        object1.hl_is_lowpoly = False

    elif type == 'MAP':
        object = BM_Object_Get(None, context)[0]
        map = object.global_maps[index]
        for highpoly in map.hl_highpoly_table:
            if highpoly.global_highpoly_object_index != -1:
                BM_ITEM_PROPS_hl_remove_highpoly_Update(highpoly, context)

def BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, container):
    to_remove = []
    for highpoly_index, highpoly in enumerate(container.hl_highpoly_table):
        if highpoly.global_highpoly_object_index == -1:
            to_remove.append(highpoly_index)
    for index in sorted(to_remove, reverse=True):
        container.hl_highpoly_table.remove(index)
    for highpoly_index, highpoly in enumerate(container.hl_highpoly_table):
        highpoly.global_item_index = highpoly_index + 1
    if container.hl_highpoly_table_active_index > 0:
        container.hl_highpoly_table_active_index -= 1

def BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context):
    for object in context.scene.bm_table_of_objects:
        if object.hl_use_unique_per_map:
            len_of_highpolies = 0
            for map in object.global_maps:
                BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, map)
                len_of_highpolies += len(map.hl_highpoly_table)
            if len_of_highpolies == 0:
                object.hl_is_lowpoly = False
        else:
            BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, object)
            if len(object.hl_highpoly_table) == 0:
                 object.hl_is_lowpoly = False

def BM_ITEM_PROPS_hl_highpoly_UpdateOrder(context):
    for object in context.scene.bm_table_of_objects:
        if object.hl_use_unique_per_map:
            for map in object.global_maps:
                for highpoly in map.hl_highpoly_table:
                    for index, object1 in enumerate(context.scene.bm_table_of_objects):
                        if object1.global_object_name == highpoly.global_highpoly_name_old and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                            highpoly.global_highpoly_object_index = index
                            break
                    if highpoly.global_highpoly_object_index != -1:
                        context.scene.bm_table_of_objects[highpoly.global_highpoly_object_index].hl_is_highpoly = True
        else:
            for highpoly in object.hl_highpoly_table:
                for index, object1 in enumerate(context.scene.bm_table_of_objects):
                    if object1.global_object_name == highpoly.global_highpoly_name_old and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                        highpoly.global_highpoly_object_index = index
                        break
                if highpoly.global_highpoly_object_index != -1:
                    context.scene.bm_table_of_objects[highpoly.global_highpoly_object_index].hl_is_highpoly = True

def BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context):
    for object in context.scene.bm_table_of_objects:
        if object.hl_use_unique_per_map:
            for map in object.global_maps:
                for highpoly in map.hl_highpoly_table:
                    if highpoly.global_highpoly_object_index == -1:
                        continue
                    for index, object1 in enumerate(context.scene.bm_table_of_objects):
                        if object1.global_object_name == highpoly.global_highpoly_object_include and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                            highpoly.global_highpoly_object_index = index
                            break
                    try:
                        highpoly.global_highpoly_name_old = highpoly.global_highpoly_object_include
                        highpoly.global_object_name = highpoly.global_highpoly_object_include
                    except TypeError:
                        pass
        else:
            for highpoly in object.hl_highpoly_table:
                if highpoly.global_highpoly_object_index == -1:
                    continue
                for index, object1 in enumerate(context.scene.bm_table_of_objects):
                    if object1.global_object_name == highpoly.global_highpoly_object_include and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                        highpoly.global_highpoly_object_index = index
                        break
                try:
                    highpoly.global_highpoly_name_old = highpoly.global_highpoly_object_include
                    highpoly.global_object_name = highpoly.global_highpoly_object_include
                except TypeError:
                    pass

###############################################################
### uv Props Funcs ###
###############################################################
def BM_ITEM_PROPS_uv_use_unique_per_map_Update(self, context):
    BM_LastEditedProp_Write(context, "Object UVs & Layers: Unique per map", "uv_use_unique_per_map", getattr(self, "uv_use_unique_per_map"), False)
    object = self
    if object.uv_use_unique_per_map:
        data = {
            'uv_bake_data' : object.uv_bake_data,
            'uv_bake_target' : object.uv_bake_target,
            'uv_active_layer' : object.uv_active_layer,
            'uv_type' : object.uv_type,
            'uv_snap_islands_to_pixels' : object.uv_snap_islands_to_pixels,
            'uv_use_auto_unwrap' : object.uv_use_auto_unwrap,
            'uv_auto_unwrap_angle_limit' : object.uv_auto_unwrap_angle_limit,
            'uv_auto_unwrap_island_margin' : object.uv_auto_unwrap_island_margin,
            'uv_auto_unwrap_use_scale_to_bounds' : object.uv_auto_unwrap_use_scale_to_bounds,
        }
    
        for map in object.global_maps:
            for key in data:
                setattr(map, key, data[key])

def BM_ITEM_PROPS_uv_active_layer_Items(self, context):
    object = BM_Object_Get(self, context)
    if object[0].nm_is_universal_container and object[0].nm_uni_container_is_global:
        return [('CONTAINER_AUTO', "Automatic", "UV Map is set automatically because Contaniner configures all its object settings")]
    if object[1] is False:
        return [('NONE', "None", "Current Object doesn't support UV Layers")]
    source_object = context.scene.objects[object[0].global_object_name].data
    uv_layers_bake = []
    uv_layers_other = []

    if len(source_object.uv_layers):
        for uv_layer in source_object.uv_layers:
            if context.scene.bm_props.global_bake_uv_layer_tag in uv_layer.name:
                uv_layers_bake.append((str(uv_layer.name), uv_layer.name, "UV Layer to use for baking current Object's maps"))
            else:
                uv_layers_other.append((str(uv_layer.name), uv_layer.name, "UV Layer to use for baking current Object's maps"))
    else:
        uv_layers_other.append(('NONE_AUTO_CREATE', "Auto Unwrap", "Object has got no UV Layers, Auto UV Unwrap will be proceeded"))
    return uv_layers_bake + uv_layers_other

def BM_ITEM_PROPS_uv_type_Items(self, context):
    items = [('SINGLE', "Single (single tile)", "Regular single-tiled UV layer")]
    if bpy.app.version >= (3, 2, 0):
        items.append(('TILED', "Tiled (UDIMs)", "Tiled UV Layer, UDIM tiles"))
        items.append(('AUTO', "Automatic", "Automatically detect UVMap type. If UDIMs detected, UDIM tiles range will be set automatically for each map"))
    
    return items

def BM_ITEM_PROPS_uv_bake_target_Items(self, context):
    if bpy.app.version >= (2, 92, 0):
        items = [('IMAGE_TEXTURES', "Image Textures", "Bake to image texture files (image files)"),
                 ('VERTEX_COLORS', "Vertex Colors", "Bake to vertex color layers (color attributes, no need for UVs")]
    else:
        items = [('IMAGE_TEXTURES', "Image Textures", "Bake to image texture files (image files)")]
    
    return items

###############################################################
### out Props Funcs ###
###############################################################
def BM_ITEM_PROPS_out_use_unique_per_map_Update(self, context):
    BM_LastEditedProp_Write(context, "Object Format: Unique per map", "out_use_unique_per_map", getattr(self, "out_use_unique_per_map"), False)
    object = self
    if object.out_use_unique_per_map:
        data = {
            'out_file_format' : object.out_file_format,
            'out_compression' : object.out_compression,
            'out_exr_codec' : object.out_exr_codec,
            'out_res' : object.out_res,
            'out_res_height' : object.out_res_height,
            'out_res_width' : object.out_res_width,
            'out_margin' : object.out_margin,
            'out_use_32bit' : object.out_use_32bit,
            'out_use_alpha' : object.out_use_alpha,
            'out_use_transbg' : object.out_use_transbg,
            'out_udim_start_tile' : object.out_udim_start_tile,
            'out_udim_end_tile' : object.out_udim_end_tile,
            'out_super_sampling_aa' : object.out_super_sampling_aa,
            'out_use_adaptive_sampling' : object.out_use_adaptive_sampling,
            'out_adaptive_treshold' : object.out_adaptive_threshold,
            'out_samples' : object.out_samples,
            'out_min_samples' : object.out_min_samples,
            'out_use_denoise' : object.out_use_denoise,
        }

        for map in object.global_maps:
            for key in data:
                setattr(map, key, data[key])

###############################################################
### Map Props Funcs ###
###############################################################
def BM_MAP_PROPS_map_type_Items(self, context):
    # if self.uv_bake_data == 'VERTEX_COLORS':
    #     return [('VERTEX_COLOR_LAYER', "VertexColor Layer", "Bake VertexColor Layer")]

    items = [
        ('', "PBR-Metallic", "PBR maps to bake from existing object materials data"),
        ('ALBEDO', "AlbedoM", "PBR-Metallic. Color image texture containing color without shadows and highlights"),
        ('METALNESS', "Metalness", "PBR-Metallic. Image texture for determining metal and non-metal parts of the object"),
        ('ROUGHNESS', "Roughness", "PBR-Metallic. Image texture for determining roughness across the surface of the object"),
        ('', "PBR-Specular", ""),
        ('DIFFUSE', "AlbedoS", "PBR-Specular. Color image texture containing color without shadows and highlights"),
        ('SPECULAR', "Specular", "PBR-Specular. Image texture for determining specularity across the surface of the object"),
        ('GLOSSINESS', "Glossiness", "PBR-Specular. Image texture for determining glossiness across the surface of the object"),
        ('', "PBR-based", ""),
        ('OPACITY', "Opacity", "Image texture for determining transparent and opaque parts of the object"),
        ('EMISSION', "Emission/Lightmap", "Image texture for determining emissive parts of the object"),

        ('', "Object-based", "PBR and Mask maps to bake from object mesh data"),
        ('NORMAL', "Normal", "Image texture for simulating high details without changing the number of polygons"),
        ('DISPLACEMENT', "Displacement", "Height map used for displacing mesh polygons"),
        ('VECTOR_DISPLACEMENT', "Vector Displacement", "Displacement map where each pixel stores RGB as XYZ displacement data"),
        ('POSITION', "Position", "Indicates object parts location in the UV space"),
        ('DECAL', "Decal Pass", "Bake common passes for Decal Object. For external bake only"),
        ('', "Masks and Details", ""),
        ('AO', "AO", "Ambient Occlusion map contains lightning data"),
        ('CAVITY', "Cavity", "Image texture map for crevice details"),
        ('CURVATURE', "Curvature", "Image texture map for convexity/concavity"),
        ('THICKNESS', "Thickness", "Thick parts of the mesh. Ambient Occlusion map that casts rays from the surface to the inside. Often used for SSS or masking"),
        ('ID', "ID", "Mask out different parts of the mesh with different colors"),
        ('MASK', "Mask", "Black and white mask for masking mesh parts"),
        ('XYZMASK', "XYZ Mask", "Contains data of rays casted from particular axis"),
        ('GRADIENT', "Gradient Mask", "Black and white gradient mask for masking"),
        ('EDGE', "Edge Mask", "Image texture for masking out mesh edges"),
        ('WIREFRAME', "Wireframe Mask", "Black and white mesh wireframe mask"),

        ('', "Passes and Cycles Default", "Bake Cycles default maps and object data and materials passes"),
        ('PASS', "BSDF Pass", "Choose and bake BSDF pass to image texture"),
        ('VERTEX_COLOR_LAYER', "VertexColor Layer", "Bake VertexColor Layer"),
        ('C_COMBINED', "Combined", "Bakes all materials, textures, and lighting contribution except specularity"),
        ('C_AO', "Ambient Occlusion", "Ambient Occlusion map contains lightning data"),
        ('C_SHADOW', "Shadow", "Bakes shadows and lighting"),
        ('C_NORMAL', "Normal", "Bakes normals to an RGB image"),
        ('C_UV', "UV", "Mapped UV coordinates, used to represent where on a mesh a texture gets mapped too"),
        ('C_ROUGHNESS', "Roughness", "Bakes the roughness pass of a material"),
        ('C_EMIT', "Emit", "Bakes Emission, or the Glow color of a material"),
        ('C_ENVIRONMENT', "Environment", "Bakes the environment (i.e. the world surface shader defined for the scene) onto the selected object(s) as seen by rays cast from the world origin."),
        ('C_DIFFUSE', "Diffuse", "Bakes the diffuse pass of a material"),
        ('C_GLOSSY', "Glossy", "Bakes the glossiness pass of a material"),
        ('C_TRANSMISSION', "Transmission", "Bakes the transmission pass of a material")
    ]
    if bpy.app.version >= (3, 0, 0):
        items.append(('C_POSITION', "Position", "Indicates object parts location in the UV space"))
    return items

def BM_MAP_PROPS_map_vertexcolor_layer_Items(self, context):
    object = BM_Object_Get(self, context)
    if object[1] is False:
        return [('NONE', "None", "Current Object doesn't support VertexColor Layers")]
    source_object = context.scene.objects[object[0].global_object_name]
    items = []
    if bpy.app.version < (3, 2, 0):
        for layer in source_object.data.vertex_colors:
            items.append((str(layer.name), layer.name, "VertexColor Layer to bake"))
    else:
        for layer in source_object.data.color_attributes:
            items.append((str(layer.name), layer.name, "VertexColor Layer to bake"))
    if len(items) == 0:
        return [('NONE', "None", "No VertexColor Layers to bake")]
    return items

def BM_MAP_PROPS_map_normal_data_Items(self, context):
    object = BM_Object_Get(self, context)[0]
    if object.hl_use_unique_per_map:
        has_highpolies = any(True for highpoly in BM_Map_Get(self, object).hl_highpoly_table if highpoly.global_highpoly_object_index != -1)
    else:
        has_highpolies = any(True for highpoly in object.hl_highpoly_table if highpoly.global_highpoly_object_index != -1)
    if object.nm_is_universal_container and object.nm_uni_container_is_global:
        has_highpolies = True
    if has_highpolies:
        items = [('HIGHPOLY', "Highpoly", "Bake normals from highpoly object data to lowpoly"),
                 ('MULTIRES', "Multires Modifier", "Bake normals from existing Multires modifier"),
                 ('MATERIAL', "Object/Materials", "Bake normals from object data")]
    else:
        items = [('MULTIRES', "Multires Modifier", "Bake normals from existing Multires modifier"),
                 ('MATERIAL', "Object/Materials", "Bake normals from object data")]
    if object.decal_is_decal:
        items = [('MATERIAL', "Object/Materials", "Bake normals from object data")]
    # above unused
    items = [('HIGHPOLY', "Highpoly", "Bake normals from highpoly object data to lowpoly"),
             ('MULTIRES', "Multires Modifier", "Bake normals from existing Multires modifier"),
             ('MATERIAL', "Object/Materials", "Bake normals from object data")]
    return items 

def BM_MAP_PROPS_map_displacement_data_Items(self, context):
    object = BM_Object_Get(self, context)[0]
    if object.hl_use_unique_per_map:
        has_highpolies = any(True for highpoly in BM_Map_Get(self, object).hl_highpoly_table if highpoly.global_highpoly_object_index != -1)
    else:
        has_highpolies = any(True for highpoly in object.hl_highpoly_table if highpoly.global_highpoly_object_index != -1)
    if object.nm_is_universal_container and object.nm_uni_container_is_global:
        has_highpolies = True
    if has_highpolies:
        items = [('HIGHPOLY', "Highpoly", "Bake displacement from highpoly object data to lowpoly"),
                 ('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
                 ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    else:
        items = [('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
                 ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    if object.decal_is_decal:
        items = [('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    # above unused
    items = [('HIGHPOLY', "Highpoly", "Bake displacement from highpoly object data to lowpoly"),
             ('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
             ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    return items

# Map Preview Funcs
def BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, map_tag):
    pass

def BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, map_tag):
    pass

    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, map_tag)

def BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, map_tag):
    pass

def BM_IterableData_GetNewUniqueName_Simple(data, name_starter):
    index = 0
    for d in data:
        if d.name.find(name_starter) != -1:
            index += 1
    return "%s.%d" % (name_starter, index)

def BM_MAP_PROPS_MapPreview_ReassignMaterials_Prepare(self, context, map_tag):
    pass

def BM_MAP_PROPS_MapPreview_ReassignMaterials_Restore(self, context):
    pass

def BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context):
    pass

# the same, no attention to bm mats removal, because they are not added anyway
BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove = BM_MAP_PROPS_MapPreview_CustomNodes_Remove

def BM_MAP_PROPS_MapPreview_Unset(self, context):
    # unset all previews
    for obj_index, object in enumerate(context.scene.bm_table_of_objects):
        # context.scene.bm_props.global_active_index = obj_index
        for map_index, map in enumerate(object.global_maps):
            # object.global_maps_active_index = map_index

            maps_tags = {
                'AO',
                'CAVITY',
                'CURVATURE',
                'THICKNESS',
                'XYZMASK',
                'GRADIENT',
                'EDGE',
                'WIREFRAME',
                'POSITION',
                'VERTEX_COLOR_LAYER',
                'VECTOR_DISPLACEMENT',
                'ALBEDO',
                'METALNESS',
                'ROUGHNESS',
                'DIFFUSE',
                'SPECULAR',
                'GLOSSINESS',
                'OPACITY',
                'EMISSION',
                'PASS',
                'DECAL',
                'NORMAL',
                'DISPLACEMENT',
                'ID',
                'MASK',
            }
            for key in maps_tags:
                # skip current map
                if self is not None and map_index + 1 == self.global_map_index and obj_index == self.global_map_object_index:
                    continue
                # if all([skip_current_map, obj_index == obj_index_init, map_index == map_index_init, key == map_tag]):
                    # continue

                if getattr(map, "map_%s_use_preview" % key):
                    setattr(map, "map_%s_use_preview" % key, False)

    # return indexes back
    # if any([obj_index_init is None, map_index_init is None]):
        # return
    # context.scene.bm_props.global_active_index = obj_index_init
    # BM_Object_Get(None, context)[0].global_maps_active_index = map_index_init

# Map previews with custom nodes
def BM_MAP_PROPS_map_AO_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_AO_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'AO')
def BM_MAP_PROPS_map_CAVITY_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_CAVITY_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'CAVITY')
def BM_MAP_PROPS_map_CURVATURE_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_CURVATURE_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_THICKNESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_THICKNESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_XYZMASK_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_XYZMASK_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_GRADIENT_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_GRADIENT_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_EDGE_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_EDGE_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'EDGE')
def BM_MAP_PROPS_map_WIREFRAME_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_WIREFRAME_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'WIREFRAME')
def BM_MAP_PROPS_map_POSITION_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_POSITION_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'POSITION')
def BM_MAP_PROPS_map_VERTEX_COLOR_LAYER_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_VERTEX_COLOR_LAYER_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'VERTEX_COLOR_LAYER')
def BM_MAP_PROPS_map_VECTOR_DISPLACEMENT_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_VECTOR_DISPLACEMENT_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'VECTOR_DISPLACEMENT')
def BM_MAP_PROPS_map_DECAL_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_DECAL_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'DECAL')

# Map Previews with Material Relinking
def BM_MAP_PROPS_map_ALBEDO_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_ALBEDO_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'ALBEDO')
def BM_MAP_PROPS_map_METALNESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_METALNESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'METALNESS')
def BM_MAP_PROPS_map_ROUGHNESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_ROUGHNESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'ROUGHNESS')
def BM_MAP_PROPS_map_DIFFUSE_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_DIFFUSE_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'DIFFUSE')
def BM_MAP_PROPS_map_SPECULAR_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_SPECULAR_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'SPECULAR')
def BM_MAP_PROPS_map_GLOSSINESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_GLOSSINESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'GLOSSINESS')
def BM_MAP_PROPS_map_OPACITY_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_OPACITY_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'OPACITY')
def BM_MAP_PROPS_map_EMISSION_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_EMISSION_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'EMISSION')
def BM_MAP_PROPS_map_PASS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_PASS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'PASS')
def BM_MAP_PROPS_map_NORMAL_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_NORMAL_use_preview and self.map_normal_data == 'MATERIAL':
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'NORMAL')
def BM_MAP_PROPS_map_DISPLACEMENT_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(self, context)
    if self.map_DISPLACEMENT_use_preview and self.map_displacement_data == 'MATERIAL':
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'DISPLACEMENT')

# Map Previews with Material Reassign
def BM_MAP_PROPS_map_ID_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_ReassignMaterials_Restore(self, context)
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_ID_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_ReassignMaterials_Prepare(self, context, 'ID')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'ID')
def BM_MAP_PROPS_map_MASK_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_ReassignMaterials_Restore(self, context)
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(self, context)
    if self.map_MASK_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(self, context)
        BM_MAP_PROPS_MapPreview_ReassignMaterials_Prepare(self, context, 'MASK')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'MASK')

###############################################################
### Update Funcs for global_last_edited_prop ###
###############################################################
def BM_MAP_PROPS_global_use_bake_Update(self, context):
    name = "Map: Use in bake"
    BM_LastEditedProp_Write(context, name, "global_use_bake", getattr(self, "global_use_bake"), True)
def BM_MAP_PROPS_global_map_type_Update(self, context):
    name = "Map: Map type"
    BM_LastEditedProp_Write(context, name, "global_map_type", getattr(self, "global_map_type"), True)
def BM_MAP_PROPS_global_affect_by_hl_Update(self, context):
    name = "Map: Affect by Highpoly"
    BM_LastEditedProp_Write(context, name, "global_affect_by_hl", getattr(self, "global_affect_by_hl"), True)
def BM_MAP_PROPS_hl_cage_type_Update(self, context):
    name = "Map High to Lowpoly: Cage type"
    BM_LastEditedProp_Write(context, name, "hl_cage_type", getattr(self, "hl_cage_type"), True)
def BM_MAP_PROPS_hl_cage_extrusion_Update(self, context):
    name = "Map High to Lowpoly: Cage extrusion"
    BM_LastEditedProp_Write(context, name, "hl_cage_extrusion", getattr(self, "hl_cage_extrusion"), True)
def BM_MAP_PROPS_hl_max_ray_distance_Update(self, context):
    name = "Map High to Lowpoly: Max ray distance"
    BM_LastEditedProp_Write(context, name, "hl_max_ray_distance", getattr(self, "hl_max_ray_distance"), True)
def BM_MAP_PROPS_uv_bake_data_Update(self, context):
    name = "Map UVs & Layers: Bake Data"
    BM_LastEditedProp_Write(context, name, "uv_bake_data", getattr(self, "uv_bake_data"), True)
def BM_MAP_PROPS_uv_bake_target_Update(self, context):
    name = "Map UVs & Layers: Bake Target"
    BM_LastEditedProp_Write(context, name, "uv_bake_target", getattr(self, "uv_bake_target"), True)
def BM_MAP_PROPS_uv_type_Update(self, context):
    name = "Map UVs & Layers: UV type"
    BM_LastEditedProp_Write(context, name, "uv_type", getattr(self, "uv_type"), True)
def BM_MAP_PROPS_uv_snap_islands_to_pixels_Update(self, context):
    name = "Map UVs & Layers: Snap UV islands to pixels"
    BM_LastEditedProp_Write(context, name, "uv_snap_islands_to_pixels", getattr(self, "uv_snap_islands_to_pixels"), True)
def BM_MAP_PROPS_out_use_denoise_Update(self, context):
    name = "Map Format: Denoise"
    BM_LastEditedProp_Write(context, name, "out_use_denoise", getattr(self, "out_use_denoise"), True)
def BM_MAP_PROPS_out_file_format_Update(self, context):
    name = "Map Format: File Format"
    BM_LastEditedProp_Write(context, name, "out_file_format", getattr(self, "out_file_format"), True)
def BM_MAP_PROPS_out_exr_codec_Update(self, context):
    name = "Map Format: Exr codec"
    BM_LastEditedProp_Write(context, name, "out_exr_codec", getattr(self, "out_exr_codec"), True)
def BM_MAP_PROPS_out_compression_Update(self, context):
    name = "Map Format: Compression"
    BM_LastEditedProp_Write(context, name, "out_compression", getattr(self, "out_compression"), True)
def BM_MAP_PROPS_out_res_Update(self, context):
    name = "Map Format: Resolution"
    BM_LastEditedProp_Write(context, name, "out_res", getattr(self, "out_res"), True)
def BM_MAP_PROPS_out_res_height_Update(self, context):
    name = "Map Format: Custom Height"
    BM_LastEditedProp_Write(context, name, "out_res_height", getattr(self, "out_res_height"), True)
def BM_MAP_PROPS_out_res_width_Update(self, context):
    name = "Map Format: Custom Width"
    BM_LastEditedProp_Write(context, name, "out_res_width", getattr(self, "out_res_width"), True)
def BM_MAP_PROPS_out_margin_Update(self, context):
    name = "Map Format: Margin"
    BM_LastEditedProp_Write(context, name, "out_margin", getattr(self, "out_margin"), True)
def BM_MAP_PROPS_out_margin_type_Update(self, context):
    name = "Map Format: Margin type"
    BM_LastEditedProp_Write(context, name, "out_margin_type", getattr(self, "out_margin_type"), True)
def BM_MAP_PROPS_out_use_32bit_Update(self, context):
    name = "Map Format: 32bit Float"
    BM_LastEditedProp_Write(context, name, "out_use_32bit", getattr(self, "out_use_32bit"), True)
def BM_MAP_PROPS_out_use_alpha_Update(self, context):
    name = "Map Format: Alpha"
    BM_LastEditedProp_Write(context, name, "out_use_alpha", getattr(self, "out_use_alpha"), True)
def BM_MAP_PROPS_out_use_transbg_Update(self, context):
    name = "Map Format: Transparent bg"
    BM_LastEditedProp_Write(context, name, "out_use_transbg", getattr(self, "out_use_transbg"), True)
def BM_MAP_PROPS_out_udim_start_tile_Update(self, context):
    name = "Map Format: UDIM start tile"
    BM_LastEditedProp_Write(context, name, "out_udim_start_tile", getattr(self, "out_udim_start_tile"), True)
def BM_MAP_PROPS_out_udim_end_tile_Update(self, context):
    name = "Map Format: UDIM end tile"
    BM_LastEditedProp_Write(context, name, "out_udim_end_tile", getattr(self, "out_udim_end_tile"), True)
def BM_MAP_PROPS_out_super_sampling_aa_Update(self, context):
    name = "Map Format: SuperSampling AA"
    BM_LastEditedProp_Write(context, name, "out_super_sampling_aa", getattr(self, "out_super_sampling_aa"), True)
def BM_MAP_PROPS_out_samples_Update(self, context):
    name = "Map Format: Bake Samples"
    BM_LastEditedProp_Write(context, name, "out_samples", getattr(self, "out_samples"), True)
def BM_MAP_PROPS_out_use_adaptive_sampling_Update(self, context):
    name = "Map Format: Adaptive Sampling"
    BM_LastEditedProp_Write(context, name, "out_use_adaptive_sampling", getattr(self, "out_use_adaptive_sampling"), True)
def BM_MAP_PROPS_out_adaptive_threshold_Update(self, context):
    name = "Map Format: Adaptive Threshold"
    BM_LastEditedProp_Write(context, name, "out_adaptive_threshold", getattr(self, "out_adaptive_threshold"), True)
def BM_MAP_PROPS_out_min_samples_Update(self, context):
    name = "Map Format: Min Bake Samples"
    BM_LastEditedProp_Write(context, name, "out_min_samples", getattr(self, "out_min_samples"), True)
def BM_MAP_PROPS_map_ALBEDO_prefix_Update(self, context):
    name = "Map: AlbedoM prefix"
    BM_LastEditedProp_Write(context, name, "map_ALBEDO_prefix", getattr(self, "map_ALBEDO_prefix"), True)
def BM_MAP_PROPS_map_METALNESS_prefix_Update(self, context):
    name = "Map: Metalness prefix"
    BM_LastEditedProp_Write(context, name, "map_METALNESS_prefix", getattr(self, "map_METALNESS_prefix"), True)
def BM_MAP_PROPS_map_ROUGHNESS_prefix_Update(self, context):
    name = "Map: Roughness prefix"
    BM_LastEditedProp_Write(context, name, "map_ROUGHNESS_prefix", getattr(self, "map_ROUGHNESS_prefix"), True)
def BM_MAP_PROPS_map_DIFFUSE_prefix_Update(self, context):
    name = "Map: AlbedoS prefix"
    BM_LastEditedProp_Write(context, name, "map_DIFFUSE_prefix", getattr(self, "map_DIFFUSE_prefix"), True)
def BM_MAP_PROPS_map_SPECULAR_prefix_Update(self, context):
    name = "Map: Specular prefix"
    BM_LastEditedProp_Write(context, name, "map_SPECULAR_prefix", getattr(self, "map_SPECULAR_prefix"), True)
def BM_MAP_PROPS_map_GLOSSINESS_prefix_Update(self, context):
    name = "Map: Glossiness prefix"
    BM_LastEditedProp_Write(context, name, "map_GLOSSINESS_prefix", getattr(self, "map_GLOSSINESS_prefix"), True)
def BM_MAP_PROPS_map_OPACITY_prefix_Update(self, context):
    name = "Map: Opacity prefix"
    BM_LastEditedProp_Write(context, name, "map_OPACITY_prefix", getattr(self, "map_OPACITY_prefix"), True)
def BM_MAP_PROPS_map_EMISSION_prefix_Update(self, context):
    name = "Map: Emission prefix"
    BM_LastEditedProp_Write(context, name, "map_EMISSION_prefix", getattr(self, "map_EMISSION_prefix"), True)
def BM_MAP_PROPS_map_PASS_prefix_Update(self, context):
    name = "Map: BSDF Pass prefix"
    BM_LastEditedProp_Write(context, name, "map_PASS_prefix", getattr(self, "map_PASS_prefix"), True)
def BM_MAP_PROPS_map_pass_type_Update(self, context):
    name = "Map: BSDF Pass type"
    BM_LastEditedProp_Write(context, name, "map_pass_type", getattr(self, "map_pass_type"), True)
    if self.map_PASS_use_preview:
        self.map_PASS_use_preview = False
        self.map_PASS_use_preview = True
def BM_MAP_PROPS_map_DECAL_prefix_Update(self, context):
    name = "Map: Decal Pass prefix"
    BM_LastEditedProp_Write(context, name, "map_DECAL_prefix", getattr(self, "map_DECAL_prefix"), True)
def BM_MAP_PROPS_map_decal_pass_type_Update(self, context):
    name = "Map: Decal Pass type"
    BM_LastEditedProp_Write(context, name, "map_decal_pass_type", getattr(self, "map_decal_pass_type"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'DECAL')
def BM_MAP_PROPS_map_decal_height_opacity_invert_Update(self, context):
    name = "Map: Decal Pass invert"
    BM_LastEditedProp_Write(context, name, "map_decal_height_opacity_invert", getattr(self, "map_decal_height_opacity_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'DECAL')
def BM_MAP_PROPS_map_decal_normal_preset_Update(self, context):
    name = "Map: Decal Pass preset"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_preset", getattr(self, "map_decal_normal_preset"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'DECAL')
def BM_MAP_PROPS_map_decal_normal_custom_preset_Update(self, context):
    name = "Map: Decal Pass custom preset"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_custom_preset", getattr(self, "map_decal_normal_custom_preset"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'DECAL')
def BM_MAP_PROPS_map_decal_normal_r_Update(self, context):
    name = "Map: Decal Pass Swizzle R"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_r", getattr(self, "map_decal_normal_r"), True)
def BM_MAP_PROPS_map_decal_normal_g_Update(self, context):
    name = "Map: Decal Pass G"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_g", getattr(self, "map_decal_normal_g"), True)
def BM_MAP_PROPS_map_decal_normal_b_Update(self, context):
    name = "Map: Decal Pass B"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_b", getattr(self, "map_decal_normal_b"), True)
def BM_MAP_PROPS_map_VERTEX_COLOR_LAYER_prefix_Update(self, context):
    name = "Map: VertexColor Layer prefix"
    BM_LastEditedProp_Write(context, name, "map_VERTEX_COLOR_LAYER_prefix", getattr(self, "map_VERTEX_COLOR_LAYER_prefix"), True)
def BM_MAP_PROPS_map_vertexcolor_layer_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'VERTEX_COLOR_LAYER')
def BM_MAP_PROPS_map_C_COMBINED_prefix_Update(self, context):
    name = "Map: Cycles Combined prefix"
    BM_LastEditedProp_Write(context, name, "map_C_COMBINED_prefix", getattr(self, "map_C_COMBINED_prefix"), True)
def BM_MAP_PROPS_map_C_AO_prefix_Update(self, context):
    name = "Map: Cycles AO prefix"
    BM_LastEditedProp_Write(context, name, "map_C_AO_prefix", getattr(self, "map_C_AO_prefix"), True)
def BM_MAP_PROPS_map_C_SHADOW_prefix_Update(self, context):
    name = "Map: Cycles Shadown prefix "
    BM_LastEditedProp_Write(context, name, "map_C_SHADOW_prefix", getattr(self, "map_C_SHADOW_prefix"), True)
def BM_MAP_PROPS_map_C_POSITION_prefix_Update(self, context):
    name = "Map: Cycles Position prefix "
    BM_LastEditedProp_Write(context, name, "map_C_POSITION_prefix", getattr(self, "map_C_POSITION_prefix"), True)
def BM_MAP_PROPS_map_C_NORMAL_prefix_Update(self, context):
    name = "Map: Cycles Normal prefix"
    BM_LastEditedProp_Write(context, name, "map_C_NORMAL_prefix", getattr(self, "map_C_NORMAL_prefix"), True)
def BM_MAP_PROPS_map_C_UV_prefix_Update(self, context):
    name = "Map: Cycles UV prefix"
    BM_LastEditedProp_Write(context, name, "map_C_UV_prefix", getattr(self, "map_C_UV_prefix"), True)
def BM_MAP_PROPS_map_C_ROUGHNESS_prefix_Update(self, context):
    name = "Map: Cycles Roughness prefix"
    BM_LastEditedProp_Write(context, name, "map_C_ROUGHNESS_prefix", getattr(self, "map_C_ROUGHNESS_prefix"), True)
def BM_MAP_PROPS_map_C_EMIT_prefix_Update(self, context):
    name = "Map: Cycles Emit prefix"
    BM_LastEditedProp_Write(context, name, "map_C_EMIT_prefix", getattr(self, "map_C_EMIT_prefix"), True)
def BM_MAP_PROPS_map_C_ENVIRONMENT_prefix_Update(self, context):
    name = "Map: Cycles Environment prefix"
    BM_LastEditedProp_Write(context, name, "map_C_ENVIRONMENT_prefix", getattr(self, "map_C_ENVIRONMENT_prefix"), True)
def BM_MAP_PROPS_map_C_DIFFUSE_prefix_Update(self, context):
    name = "Map: Cycles Diffuse prefix"
    BM_LastEditedProp_Write(context, name, "map_C_DIFFUSE_prefix", getattr(self, "map_C_DIFFUSE_prefix"), True)
def BM_MAP_PROPS_map_C_GLOSSY_prefix_Update(self, context):
    name = "Map: Cycles Glossy prefix"
    BM_LastEditedProp_Write(context, name, "map_C_GLOSSY_prefix", getattr(self, "map_C_GLOSSY_prefix"), True)
def BM_MAP_PROPS_map_C_TRANSMISSION_prefix_Update(self, context):
    name = "Map: Cycles Transmission prefix"
    BM_LastEditedProp_Write(context, name, "map_C_TRANSMISSION_prefix", getattr(self, "map_C_TRANSMISSION_prefix"), True)
def BM_MAP_PROPS_map_cycles_use_pass_direct_Update(self, context):
    name = "Map: Cycles use direct"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_direct", getattr(self, "map_cycles_use_pass_direct"), True)
def BM_MAP_PROPS_map_cycles_use_pass_indirect_Update(self, context):
    name = "Map: Cycles use indirect"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_indirect", getattr(self, "map_cycles_use_pass_indirect"), True)
def BM_MAP_PROPS_map_cycles_use_pass_color_Update(self, context):
    name = "Map: Cycles use color pass"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_color", getattr(self, "map_cycles_use_pass_color"), True)
def BM_MAP_PROPS_map_cycles_use_pass_diffuse_Update(self, context):
    name = "Map: Cycles use diffuse pass"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_diffuse", getattr(self, "map_cycles_use_pass_diffuse"), True)
def BM_MAP_PROPS_map_cycles_use_pass_glossy_Update(self, context):
    name = "Map: Cycles use glossy pass"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_glossy", getattr(self, "map_cycles_use_pass_glossy"), True)
def BM_MAP_PROPS_map_cycles_use_pass_transmission_Update(self, context):
    name = "Map: Cycles use transmission pass"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_transmission", getattr(self, "map_cycles_use_pass_transmission"), True)
def BM_MAP_PROPS_map_cycles_use_pass_ambient_occlusion_Update(self, context):
    name = "Map: Cycles use ao pass"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_ambient_occlusion", getattr(self, "map_cycles_use_pass_ambient_occlusion"), True)
def BM_MAP_PROPS_map_cycles_use_pass_emit_Update(self, context):
    name = "Map: Cycles use emit pass"
    BM_LastEditedProp_Write(context, name, "map_cycles_use_pass_emit", getattr(self, "map_cycles_use_pass_emit"), True)
def BM_MAP_PROPS_map_NORMAL_prefix_Update(self, context):
    name = "Map: Normal prefix"
    BM_LastEditedProp_Write(context, name, "map_NORMAL_prefix", getattr(self, "map_NORMAL_prefix"), True)
def BM_MAP_PROPS_map_normal_data_Update(self, context):
    name = "Map: Normal data"
    BM_LastEditedProp_Write(context, name, "map_normal_data", getattr(self, "map_normal_data"), True)
    setattr(self, "map_NORMAL_use_preview", False)
def BM_MAP_PROPS_map_normal_space_Update(self, context):
    name = "Map: Normal space"
    BM_LastEditedProp_Write(context, name, "map_normal_space", getattr(self, "map_normal_space"), True)
def BM_MAP_PROPS_map_normal_preset_Update(self, context):
    name = "Map: Normal preset"
    BM_LastEditedProp_Write(context, name, "map_normal_preset", getattr(self, "map_normal_preset"), True)
def BM_MAP_PROPS_map_normal_custom_preset_Update(self, context):
    name = "Map: Normal custom preset"
    BM_LastEditedProp_Write(context, name, "map_normal_custom_preset", getattr(self, "map_normal_custom_preset"), True)
def BM_MAP_PROPS_map_normal_r_Update(self, context):
    name = "Map: Normal Swizzle R"
    BM_LastEditedProp_Write(context, name, "map_normal_r", getattr(self, "map_normal_r"), True)
def BM_MAP_PROPS_map_normal_g_Update(self, context):
    name = "Map: Normal G"
    BM_LastEditedProp_Write(context, name, "map_normal_g", getattr(self, "map_normal_g"), True)
def BM_MAP_PROPS_map_normal_b_Update(self, context):
    name = "Map: Normal B"
    BM_LastEditedProp_Write(context, name, "map_normal_b", getattr(self, "map_normal_b"), True)
def BM_MAP_PROPS_map_DISPLACEMENT_prefix_Update(self, context):
    name = "Map: Displacement prefix"
    BM_LastEditedProp_Write(context, name, "map_DISPLACEMENT_prefix", getattr(self, "map_DISPLACEMENT_prefix"), True)
def BM_MAP_PROPS_map_displacement_data_Update(self, context):
    name = "Map: Displacement data"
    BM_LastEditedProp_Write(context, name, "map_displacement_data", getattr(self, "map_displacement_data"), True)
    setattr(self, "map_DISPLACEMENT_use_preview", False)
def BM_MAP_PROPS_map_displacement_result_Update(self, context):
    name = "Map: Displacement result"
    BM_LastEditedProp_Write(context, name, "map_displacement_result", getattr(self, "map_displacement_result"), True)
def BM_MAP_PROPS_map_displacement_subdiv_levels_Update(self, context):
    name = "Map: Displacement subdiv levels"
    BM_LastEditedProp_Write(context, name, "map_displacement_subdiv_levels", getattr(self, "map_displacement_subdiv_levels"), True)
def BM_MAP_PROPS_map_VECTOR_DISPLACEMENT_prefix_Update(self, context):
    name = "Map: Vector Displacement prefix"
    BM_LastEditedProp_Write(context, name, "map_VECTOR_DISPLACEMENT_prefix", getattr(self, "map_VECTOR_DISPLACEMENT_prefix"), True)
def BM_MAP_PROPS_map_vector_displacement_use_negative_Update(self, context):
    name = "Map: Vector Displacement include negative"
    BM_LastEditedProp_Write(context, name, "map_vector_displacement_use_negative", getattr(self, "map_vector_displacement_use_negative"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'VECTOR_DISPLACEMENT')
def BM_MAP_PROPS_map_vector_displacement_result_Update(self, context):
    name = "Map: Vector Displacement result"
    BM_LastEditedProp_Write(context, name, "map_vector_displacement_result", getattr(self, "map_vector_displacement_result"), True)
def BM_MAP_PROPS_map_vector_displacement_subdiv_levels_Update(self, context):
    name = "Map: Vector Displacement subdiv levels"
    BM_LastEditedProp_Write(context, name, "map_vector_displacement_subdiv_levels", getattr(self, "map_vector_displacement_subdiv_levels"), True)
def BM_MAP_PROPS_map_POSITION_prefix_Update(self, context):
    name = "Map: Position prefix"
    BM_LastEditedProp_Write(context, name, "map_POSITION_prefix", getattr(self, "map_POSITION_prefix"), True)
def BM_MAP_PROPS_map_AO_prefix_Update(self, context):
    name = "Map: AO prefix"
    BM_LastEditedProp_Write(context, name, "map_AO_prefix", getattr(self, "map_AO_prefix"), True)
def BM_MAP_PROPS_map_AO_use_default_Update(self, context):
    name = "Map: AO default"
    BM_LastEditedProp_Write(context, name, "map_AO_use_default", getattr(self, "map_AO_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_samples_Update(self, context):
    name = "Map: AO samples"
    BM_LastEditedProp_Write(context, name, "map_ao_samples", getattr(self, "map_ao_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_distance_Update(self, context):
    name = "Map: AO distance"
    BM_LastEditedProp_Write(context, name, "map_ao_distance", getattr(self, "map_ao_distance"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_black_point_Update(self, context):
    name = "Map: AO black point"
    BM_LastEditedProp_Write(context, name, "map_ao_black_point", getattr(self, "map_ao_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_white_point_Update(self, context):
    name = "Map: AO white point"
    BM_LastEditedProp_Write(context, name, "map_ao_white_point", getattr(self, "map_ao_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_brightness_Update(self, context):
    name = "Map: AO brightness"
    BM_LastEditedProp_Write(context, name, "map_ao_brightness", getattr(self, "map_ao_brightness"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_contrast_Update(self, context):
    name = "Map: AO contrast"
    BM_LastEditedProp_Write(context, name, "map_ao_contrast", getattr(self, "map_ao_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_opacity_Update(self, context):
    name = "Map: AO opacity"
    BM_LastEditedProp_Write(context, name, "map_ao_opacity", getattr(self, "map_ao_opacity"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_use_local_Update(self, context):
    name = "Map: AO only local"
    BM_LastEditedProp_Write(context, name, "map_ao_use_local", getattr(self, "map_ao_use_local"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_ao_use_invert_Update(self, context):
    name = "Map: AO invert"
    BM_LastEditedProp_Write(context, name, "map_ao_use_invert", getattr(self, "map_ao_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'AO')
def BM_MAP_PROPS_map_CAVITY_prefix_Update(self, context):
    name = "Map: Cavity prefix"
    BM_LastEditedProp_Write(context, name, "map_CAVITY_prefix", getattr(self, "map_CAVITY_prefix"), True)
def BM_MAP_PROPS_map_CAVITY_use_default_Update(self, context):
    name = "Map: Cavity default"
    BM_LastEditedProp_Write(context, name, "map_CAVITY_use_default", getattr(self, "map_CAVITY_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_black_point_Update(self, context):
    name = "Map: Cavity black point"
    BM_LastEditedProp_Write(context, name, "map_cavity_black_point", getattr(self, "map_cavity_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_white_point_Update(self, context):
    name = "Map: Cavity white point"
    BM_LastEditedProp_Write(context, name, "map_cavity_white_point", getattr(self, "map_cavity_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_power_Update(self, context):
    name = "Map: Cavity power"
    BM_LastEditedProp_Write(context, name, "map_cavity_power", getattr(self, "map_cavity_power"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_use_invert_Update(self, context):
    name = "Map: Cavity invert"
    BM_LastEditedProp_Write(context, name, "map_cavity_use_invert", getattr(self, "map_cavity_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CAVITY')
def BM_MAP_PROPS_map_CURVATURE_prefix_Update(self, context):
    name = "Map: Curvature prefix"
    BM_LastEditedProp_Write(context, name, "map_CURVATURE_prefix", getattr(self, "map_CURVATURE_prefix"), True)
def BM_MAP_PROPS_map_CURVATURE_use_default_Update(self, context):
    name = "Map: Curvature default"
    BM_LastEditedProp_Write(context, name, "map_CURVATURE_use_default", getattr(self, "map_CURVATURE_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_samples_Update(self, context):
    name = "Map: Curvature samples"
    BM_LastEditedProp_Write(context, name, "map_curv_samples", getattr(self, "map_curv_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_radius_Update(self, context):
    name = "Map: Curvature radius"
    BM_LastEditedProp_Write(context, name, "map_curv_radius", getattr(self, "map_curv_radius"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_black_point_Update(self, context):
    name = "Map: Curvature black point"
    BM_LastEditedProp_Write(context, name, "map_curv_black_point", getattr(self, "map_curv_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_mid_point_Update(self, context):
    name = "Map: Curvature mid point"
    BM_LastEditedProp_Write(context, name, "map_curv_mid_point", getattr(self, "map_curv_mid_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_white_point_Update(self, context):
    name = "Map: Curvature white point"
    BM_LastEditedProp_Write(context, name, "map_curv_white_point", getattr(self, "map_curv_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_body_gamma_Update(self, context):
    name = "Map: Curvature body gamma"
    BM_LastEditedProp_Write(context, name, "map_curv_body_gamma", getattr(self, "map_curv_body_gamma"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_THICKNESS_prefix_Update(self, context):
    name = "Map: Thickness prefix"
    BM_LastEditedProp_Write(context, name, "map_THICKNESS_prefix", getattr(self, "map_THICKNESS_prefix"), True)
def BM_MAP_PROPS_map_THICKNESS_use_default_Update(self, context):
    name = "Map: Thickness default"
    BM_LastEditedProp_Write(context, name, "map_THICKNESS_use_default", getattr(self, "map_THICKNESS_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_samples_Update(self, context):
    name = "Map: Thickness samples"
    BM_LastEditedProp_Write(context, name, "map_thick_samples", getattr(self, "map_thick_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_distance_Update(self, context):
    name = "Map: Thickness distance"
    BM_LastEditedProp_Write(context, name, "map_thick_distance", getattr(self, "map_thick_distance"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_black_point_Update(self, context):
    name = "Map: Thickness black point"
    BM_LastEditedProp_Write(context, name, "map_thick_black_point", getattr(self, "map_thick_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_white_point_Update(self, context):
    name = "Map: Thickness white point"
    BM_LastEditedProp_Write(context, name, "map_thick_white_point", getattr(self, "map_thick_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_brightness_Update(self, context):
    name = "Map: Thickness brightness"
    BM_LastEditedProp_Write(context, name, "map_thick_brightness", getattr(self, "map_thick_brightness"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_contrast_Update(self, context):
    name = "Map: Thickness contrast"
    BM_LastEditedProp_Write(context, name, "map_thick_contrast", getattr(self, "map_thick_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_use_invert_Update(self, context):
    name = "Map: Thickness invert"
    BM_LastEditedProp_Write(context, name, "map_thick_use_invert", getattr(self, "map_thick_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_ID_prefix_Update(self, context):
    name = "Map: ID prefix"
    BM_LastEditedProp_Write(context, name, "map_ID_prefix", getattr(self, "map_ID_prefix"), True)
def BM_MAP_PROPS_map_matid_data_Update(self, context):
    name = "Map: ID data"
    BM_LastEditedProp_Write(context, name, "map_matid_data", getattr(self, "map_matid_data"), True)
    if self.map_ID_use_preview:
        self.map_ID_use_preview = False
        self.map_ID_use_preview = True
def BM_MAP_PROPS_map_matid_vertex_groups_name_contains_Update(self, context):
    name = "Map: ID vertex groups name contains"
    BM_LastEditedProp_Write(context, name, "map_matid_vertex_groups_name_contains", getattr(self, "map_matid_vertex_groups_name_contains"), True)
    if self.map_ID_use_preview:
        self.map_ID_use_preview = False
        self.map_ID_use_preview = True
def BM_MAP_PROPS_map_matid_algorithm_Update(self, context):
    name = "Map: ID algorithm"
    BM_LastEditedProp_Write(context, name, "map_matid_algorithm", getattr(self, "map_matid_algorithm"), True)
    if self.map_ID_use_preview:
        self.map_ID_use_preview = False
        self.map_ID_use_preview = True
def BM_MAP_PROPS_map_matid_jilter_Update(self, context):
    name = "Map: ID algorithm"
    BM_LastEditedProp_Write(context, name, "map_matid_algorithm", getattr(self, "map_matid_algorithm"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'ID')
def BM_MAP_PROPS_map_MASK_prefix_Update(self, context):
    name = "Map: Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_MASK_prefix", getattr(self, "map_MASK_prefix"), True)
def BM_MAP_PROPS_map_mask_data_Update(self, context):
    name = "Map: Mask data"
    BM_LastEditedProp_Write(context, name, "map_mask_data", getattr(self, "map_mask_data"), True)
    if self.map_MASK_use_preview:
        self.map_MASK_use_preview = False
        self.map_MASK_use_preview = True
def BM_MAP_PROPS_map_mask_vertex_groups_name_contains_Update(self, context):
    name = "Map: Mask vertex groups name contains"
    BM_LastEditedProp_Write(context, name, "map_mask_vertex_groups_name_contains", getattr(self, "map_mask_vertex_groups_name_contains"), True)
    if self.map_MASK_use_preview:
        self.map_MASK_use_preview = False
        self.map_MASK_use_preview = True
def BM_MAP_PROPS_map_mask_materials_name_contains_Update(self, context):
    name = "Map: Mask materials name contains"
    BM_LastEditedProp_Write(context, name, "map_mask_materials_name_contains", getattr(self, "map_mask_materials_name_contains"), True)
    if self.map_MASK_use_preview:
        self.map_MASK_use_preview = False
        self.map_MASK_use_preview = True
def BM_MAP_PROPS_map_mask_color1_Update(self, context):
    name = "Map: Mask color1"
    BM_LastEditedProp_Write(context, name, "map_mask_color1", getattr(self, "map_mask_color1"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'MASK')
def BM_MAP_PROPS_map_mask_color2_Update(self, context):
    name = "Map: Mask color2"
    BM_LastEditedProp_Write(context, name, "map_mask_color2", getattr(self, "map_mask_color2"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'MASK')
def BM_MAP_PROPS_map_mask_use_invert_Update(self, context):
    name = "Map: Mask invert"
    BM_LastEditedProp_Write(context, name, "map_mask_use_invert", getattr(self, "map_mask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'MASK')
def BM_MAP_PROPS_map_XYZMASK_prefix_Update(self, context):
    name = "Map: XYZ Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_XYZMASK_prefix", getattr(self, "map_XYZMASK_prefix"), True)
def BM_MAP_PROPS_map_XYZMASK_use_default_Update(self, context):
    name = "Map: XYZ Mask default"
    BM_LastEditedProp_Write(context, name, "map_XYZMASK_use_default", getattr(self, "map_XYZMASK_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_x_Update(self, context):
    name = "Map: XYZ Mask X"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_x", getattr(self, "map_xyzmask_use_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_y_Update(self, context):
    name = "Map: XYZ Mask Y"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_y", getattr(self, "map_xyzmask_use_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_z_Update(self, context):
    name = "Map: XYZ Mask Z"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_z", getattr(self, "map_xyzmask_use_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_coverage_Update(self, context):
    name = "Map: XYZ Mask coverage"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_coverage", getattr(self, "map_xyzmask_coverage"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_saturation_Update(self, context):
    name = "Map: XYZ Mask saturation"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_saturation", getattr(self, "map_xyzmask_saturation"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_opacity_Update(self, context):
    name = "Map: XYZ Mask opacity"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_opacity", getattr(self, "map_xyzmask_opacity"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_invert_Update(self, context):
    name = "Map: XYZ Mask invert"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_invert", getattr(self, "map_xyzmask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_GRADIENT_prefix_Update(self, context):
    name = "Map: Gradient Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_GRADIENT_prefix", getattr(self, "map_GRADIENT_prefix"), True)
def BM_MAP_PROPS_map_GRADIENT_use_default_Update(self, context):
    name = "Map: Gradient Mask default"
    BM_LastEditedProp_Write(context, name, "map_GRADIENT_use_default", getattr(self, "map_GRADIENT_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_type_Update(self, context):
    name = "Map: Gradient Mask type"
    BM_LastEditedProp_Write(context, name, "map_gmask_type", getattr(self, "map_gmask_type"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_location_x_Update(self, context):
    name = "Map: Gradient Mask location x"
    BM_LastEditedProp_Write(context, name, "map_gmask_location_x", getattr(self, "map_gmask_location_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_location_y_Update(self, context):
    name = "Map: Gradient Mask location y"
    BM_LastEditedProp_Write(context, name, "map_gmask_location_y", getattr(self, "map_gmask_location_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_location_z_Update(self, context):
    name = "Map: Gradient Mask location z"
    BM_LastEditedProp_Write(context, name, "map_gmask_location_z", getattr(self, "map_gmask_location_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_rotation_x_Update(self, context):
    name = "Map: Gradient Mask rotation x"
    BM_LastEditedProp_Write(context, name, "map_gmask_rotation_x", getattr(self, "map_gmask_rotation_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_rotation_y_Update(self, context):
    name = "Map: Gradient Mask rotation y"
    BM_LastEditedProp_Write(context, name, "map_gmask_rotation_y", getattr(self, "map_gmask_rotation_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_rotation_z_Update(self, context):
    name = "Map: Gradient Mask rotation z"
    BM_LastEditedProp_Write(context, name, "map_gmask_rotation_z", getattr(self, "map_gmask_rotation_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_scale_x_Update(self, context):
    name = "Map: Gradient Mask scale x"
    BM_LastEditedProp_Write(context, name, "map_gmask_scale_x", getattr(self, "map_gmask_scale_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_scale_y_Update(self, context):
    name = "Map: Gradient Mask scale y"
    BM_LastEditedProp_Write(context, name, "map_gmask_scale_y", getattr(self, "map_gmask_scale_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_scale_z_Update(self, context):
    name = "Map: Gradient Mask scale z"
    BM_LastEditedProp_Write(context, name, "map_gmask_scale_z", getattr(self, "map_gmask_scale_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_coverage_Update(self, context):
    name = "Map: Gradient Mask coverage"
    BM_LastEditedProp_Write(context, name, "map_gmask_coverage", getattr(self, "map_gmask_coverage"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_contrast_Update(self, context):
    name = "Map: Gradient Mask contrast"
    BM_LastEditedProp_Write(context, name, "map_gmask_contrast", getattr(self, "map_gmask_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_saturation_Update(self, context):
    name = "Map: Gradient Mask saturation"
    BM_LastEditedProp_Write(context, name, "map_gmask_saturation", getattr(self, "map_gmask_saturation"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_opacity_Update(self, context):
    name = "Map: Gradient Mask opacity"
    BM_LastEditedProp_Write(context, name, "map_gmask_opacity", getattr(self, "map_gmask_opacity"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_use_invert_Update(self, context):
    name = "Map: Gradient Mask invert"
    BM_LastEditedProp_Write(context, name, "map_gmask_use_invert", getattr(self, "map_gmask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_EDGE_prefix_Update(self, context):
    name = "Map: Edge Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_EDGE_prefix", getattr(self, "map_EDGE_prefix"), True)
def BM_MAP_PROPS_map_EDGE_use_default_Update(self, context):
    name = "Map: Edge Mask default"
    BM_LastEditedProp_Write(context, name, "map_EDGE_use_default", getattr(self, "map_EDGE_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_samples_Update(self, context):
    name = "Map: Edge Mask samples"
    BM_LastEditedProp_Write(context, name, "map_edgemask_samples", getattr(self, "map_edgemask_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_radius_Update(self, context):
    name = "Map: Edge Mask radius"
    BM_LastEditedProp_Write(context, name, "map_edgemask_radius", getattr(self, "map_edgemask_radius"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_edge_contrast_Update(self, context):
    name = "Map: Edge Mask edge contrast"
    BM_LastEditedProp_Write(context, name, "map_edgemask_edge_contrast", getattr(self, "map_edgemask_edge_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_body_contrast_Update(self, context):
    name = "Map: Edge Mask body contrast"
    BM_LastEditedProp_Write(context, name, "map_edgemask_body_contrast", getattr(self, "map_edgemask_body_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_use_invert_Update(self, context):
    name = "Map: Edge Mask invert"
    BM_LastEditedProp_Write(context, name, "map_edgemask_use_invert", getattr(self, "map_edgemask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'EDGE')
def BM_MAP_PROPS_map_WIREFRAME_prefix_Update(self, context):
    name = "Map: Wireframe prefix"
    BM_LastEditedProp_Write(context, name, "map_WIREFRAME_prefix", getattr(self, "map_WIREFRAME_prefix"), True)
def BM_MAP_PROPS_map_wireframemask_line_thickness_Update(self, context):
    name = "Map: Wireframe Mask line thickness"
    BM_LastEditedProp_Write(context, name, "map_wireframemask_line_thickness", getattr(self, "map_wireframemask_line_thickness"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'WIREFRAME')
def BM_MAP_PROPS_map_wireframemask_use_invert_Update(self, context):
    name = "Map: Wireframe Mask invert"
    BM_LastEditedProp_Write(context, name, "map_wireframemask_use_invert", getattr(self, "map_wireframemask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(self, context, 'WIREFRAME')

def BM_ITEM_PROPS_global_use_bake_Update(self, context):
    name = "Object: Use in bake"
    BM_LastEditedProp_Write(context, name, "global_use_bake", getattr(self, "global_use_bake"), False)
def BM_ITEM_PROPS_decal_use_custom_camera_Update(self, context):
    name = "Object Decal: Use custom camera"
    BM_LastEditedProp_Write(context, name, "decal_use_custom_camera", getattr(self, "decal_use_custom_camera"), False)
def BM_ITEM_PROPS_decal_custom_camera_Update(self, context):
    name = "Object Decal: Custom camera"
    BM_LastEditedProp_Write(context, name, "decal_custom_camera", getattr(self, "decal_custom_camera"), False)
def BM_ITEM_PROPS_decal_upper_coordinate_Update(self, context):
    name = "Object Decal: Upper coordinate"
    BM_LastEditedProp_Write(context, name, "decal_upper_coordinate", getattr(self, "decal_upper_coordinate"), False)
def BM_ITEM_PROPS_decal_boundary_offset_Update(self, context):
    name = "Object Decal: Boundary offset"
    BM_LastEditedProp_Write(context, name, "decal_boundary_offset", getattr(self, "decal_boundary_offset"), False)
def BM_ITEM_PROPS_hl_decals_use_separate_texset_Update(self, context):
    name = "Object High to Lowpoly: Use separate texset for decals"
    BM_LastEditedProp_Write(context, name, "hl_decals_use_separate_texset", getattr(self, "hl_decals_use_separate_texset"), False)
def BM_ITEM_PROPS_hl_decals_separate_texset_prefix_Update(self, context):
    name = "Object High to Lowpoly: Decals TexSet prefix"
    BM_LastEditedProp_Write(context, name, "hl_decals_separate_texset_prefix", getattr(self, "hl_decals_separate_texset_prefix"), False)
def BM_ITEM_PROPS_hl_cage_type_Update(self, context):
    name = "Object High to Lowpoly: Cage type"
    BM_LastEditedProp_Write(context, name, "hl_cage_type", getattr(self, "hl_cage_type"), False)
def BM_ITEM_PROPS_hl_cage_extrusion_Update(self, context):
    name = "Object High to Lowpoly: Cage extrusion"
    BM_LastEditedProp_Write(context, name, "hl_cage_extrusion", getattr(self, "hl_cage_extrusion"), False)
def BM_ITEM_PROPS_hl_max_ray_distance(self, context):
    name = "Object High to Lowpoly: Max ray distance"
    BM_LastEditedProp_Write(context, name, "hl_max_ray_distance", getattr(self, "hl_max_ray_distance"), False)
def BM_ITEM_PROPS_uv_bake_data_Update(self, context):
    name = "Object UVs & Layers: Bake data"
    BM_LastEditedProp_Write(context, name, "uv_bake_data", getattr(self, "uv_bake_data"), False)
def BM_ITEM_PROPS_uv_bake_target_Update(self, context):
    name = "Object UVs & Layers: Bake target"
    BM_LastEditedProp_Write(context, name, "uv_bake_target", getattr(self, "uv_bake_target"), False)
def BM_ITEM_PROPS_uv_type_Update(self, context):
    name = "Object UVs & Layers: UV type"
    BM_LastEditedProp_Write(context, name, "uv_type", getattr(self, "uv_type"), False)
def BM_ITEM_PROPS_uv_snap_islands_to_pixels_Update(self, context):
    name = "Object UVs & Layers: Snap UV islands to pixels"
    BM_LastEditedProp_Write(context, name, "uv_snap_islands_to_pixels", getattr(self, "uv_snap_islands_to_pixels"), False)
def BM_ITEM_PROPS_uv_use_auto_unwrap_Update(self, context):
    name = "Object UVs & Layers: Auto unwrap"
    BM_LastEditedProp_Write(context, name, "uv_use_auto_unwrap", getattr(self, "uv_use_auto_unwrap"), False)
def BM_ITEM_PROPS_uv_auto_unwrap_angle_limit_Update(self, context):
    name = "Object UVs & Layers: Auto unwrap angle limit"
    BM_LastEditedProp_Write(context, name, "uv_auto_unwrap_angle_limit", getattr(self, "uv_auto_unwrap_angle_limit"), False)
def BM_ITEM_PROPS_uv_auto_unwrap_island_margin_Update(self, context):
    name = "Object UVs & Layers: Auto unwrap islands margin"
    BM_LastEditedProp_Write(context, name, "uv_auto_unwrap_island_margin", getattr(self, "uv_auto_unwrap_island_margin"), False)
def BM_ITEM_PROPS_uv_auto_unwrap_use_scale_to_bounds_Update(self, context):
    name = "Object UVs & Layers: Auto unwrap scale to bounds"
    BM_LastEditedProp_Write(context, name, "uv_auto_unwrap_use_scale_to_bounds", getattr(self, "uv_auto_unwrap_use_scale_to_bounds"), False)
def BM_ITEM_PROPS_out_use_denoise_Update(self, context):
    name = "Object Format: Denoise"
    BM_LastEditedProp_Write(context, name, "out_use_denoise", getattr(self, "out_use_denoise"), False)
def BM_ITEM_PROPS_out_file_format_Update(self, context):
    name = "Object Format: File Format"
    BM_LastEditedProp_Write(context, name, "out_file_format", getattr(self, "out_file_format"), False)
def BM_ITEM_PROPS_out_exr_codec_Update(self, context):
    name = "Object Format: Exr codec"
    BM_LastEditedProp_Write(context, name, "out_exr_codec", getattr(self, "out_exr_codec"), False)
def BM_ITEM_PROPS_out_compression_Update(self, context):
    name = "Object Format: Compression"
    BM_LastEditedProp_Write(context, name, "out_compression", getattr(self, "out_compression"), False)
def BM_ITEM_PROPS_out_res_Update(self, context):
    name = "Object Format: Resolution"
    BM_LastEditedProp_Write(context, name, "out_res", getattr(self, "out_res"), False)
def BM_ITEM_PROPS_out_res_height_Update(self, context):
    name = "Object Format: Custom height"
    BM_LastEditedProp_Write(context, name, "out_res_height", getattr(self, "out_res_height"), False)
def BM_ITEM_PROPS_out_res_width_Update(self, context):
    name = "Object Format: Custom width"
    BM_LastEditedProp_Write(context, name, "out_res_width", getattr(self, "out_res_width"), False)
def BM_ITEM_PROPS_out_margin_Update(self, context):
    name = "Object Format: Margin"
    BM_LastEditedProp_Write(context, name, "out_margin", getattr(self, "out_margin"), False)
def BM_ITEM_PROPS_out_margin_type_Update(self, context):
    name = "Object Format: Margin type"
    BM_LastEditedProp_Write(context, name, "out_margin_type", getattr(self, "out_margin_type"), False)
def BM_ITEM_PROPS_out_use_32bit_Update(self, context):
    name = "Object Format: 32bit float"
    BM_LastEditedProp_Write(context, name, "out_use_32bit", getattr(self, "out_use_32bit"), False)
def BM_ITEM_PROPS_out_use_alpha_Update(self, context):
    name = "Object Format: Alpha"
    BM_LastEditedProp_Write(context, name, "out_use_alpha", getattr(self, "out_use_alpha"), False)
def BM_ITEM_PROPS_out_use_transbg_Update(self, context):
    name = "Object Format: Transparent bg"
    BM_LastEditedProp_Write(context, name, "out_use_transbg", getattr(self, "out_use_transbg"), False)
def BM_ITEM_PROPS_out_udim_start_tile_Update(self, context):
    name = "Object Format: UDIM start tile"
    BM_LastEditedProp_Write(context, name, "out_udim_start_tile", getattr(self, "out_udim_start_tile"), False)
def BM_ITEM_PROPS_out_udim_end_tile_Update(self, context):
    name = "Object Format: UDIM end tile"
    BM_LastEditedProp_Write(context, name, "out_udim_end_tile", getattr(self, "out_udim_end_tile"), False)
def BM_ITEM_PROPS_out_super_sampling_aa_Update(self, context):
    name = "Object Format: SuperSampling AA"
    BM_LastEditedProp_Write(context, name, "out_super_sampling_aa", getattr(self, "out_super_sampling_aa"), False)
def BM_ITEM_PROPS_out_samples(self, context):
    name = "Object Format: Bake samples"
    BM_LastEditedProp_Write(context, name, "out_samples", getattr(self, "out_samples"), False)
def BM_ITEM_PROPS_out_use_adaptive_sampling_Update(self, context):
    name = "Object Format: Adaptive sampling"
    BM_LastEditedProp_Write(context, name, "out_use_adaptive_sampling", getattr(self, "out_use_adaptive_sampling"), False)
def BM_ITEM_PROPS_out_adaptive_threshold_Update(self, context):
    name = "Object Format: Adaptive threshold"
    BM_LastEditedProp_Write(context, name, "out_adaptive_threshold", getattr(self, "out_adaptive_threshold"), False)
def BM_ITEM_PROPS_out_min_samples_Update(self, context):
    name = "Object Format: Bake min samples"
    BM_LastEditedProp_Write(context, name, "out_min_samples", getattr(self, "out_min_samples"), False)
def BM_ITEM_PROPS_csh_use_triangulate_lowpoly_Update(self, context):
    name = "Object Shading: Triangulate lowpoly"
    BM_LastEditedProp_Write(context, name, "csh_use_triangulate_lowpoly", getattr(self, "csh_use_triangulate_lowpoly"), False)
def BM_ITEM_PROPS_csh_use_lowpoly_recalc_normals_Update(self, context):
    name = "Object Shading: Recalculate Lowpoly Normals Outside"
    BM_LastEditedProp_Write(context, name, "csh_use_lowpoly_recalc_normals", getattr(self, "csh_use_lowpoly_recalc_normals"), False)
def BM_ITEM_PROPS_csh_lowpoly_use_smooth_Update(self, context):
    name = "Object Shading: Smooth lowpoly"
    BM_LastEditedProp_Write(context, name, "csh_lowpoly_use_smooth", getattr(self, "csh_lowpoly_use_smooth"), False)
def BM_ITEM_PROPS_csh_lowpoly_smoothing_groups_enum_Update(self, context):
    name = "Object Shading: Lowpoly smoothing type"
    BM_LastEditedProp_Write(context, name, "csh_lowpoly_smoothing_groups_enum", getattr(self, "csh_lowpoly_smoothing_groups_enum"), False)
def BM_ITEM_PROPS_csh_lowpoly_smoothing_groups_angle_Update(self, context):
    name = "Object Shading: Lowpoly auto smooth angle"
    BM_LastEditedProp_Write(context, name, "csh_lowpoly_smoothing_groups_angle", getattr(self, "csh_lowpoly_smoothing_groups_angle"), False)
def BM_ITEM_PROPS_csh_lowpoly_smoothing_groups_name_contains_Update(self, context):
    name = "Object Shading: Lowpoly vertex groups name contains"
    BM_LastEditedProp_Write(context, name, "csh_lowpoly_smoothing_groups_name_contains", getattr(self, "csh_lowpoly_smoothing_groups_name_contains"), False)
def BM_ITEM_PROPS_csh_use_highpoly_recalc_normals_Update(self, context):
    name = "Object Shading: Recalculate Highpoly Normals Outside"
    BM_LastEditedProp_Write(context, name, "csh_use_highpoly_recalc_normals", getattr(self, "csh_use_highpoly_recalc_normals"), False)
def BM_ITEM_PROPS_csh_highpoly_use_smooth_Update(self, context):
    name = "Object Shading: Smooth highpoly"
    BM_LastEditedProp_Write(context, name, "csh_highpoly_use_smooth", getattr(self, "csh_highpoly_use_smooth"), False)
def BM_ITEM_PROPS_csh_highpoly_smoothing_groups_enum_Update(self, context):
    name = "Object Shading: Highpoly smoothing type"
    BM_LastEditedProp_Write(context, name, "csh_highpoly_smoothing_groups_enum", getattr(self, "csh_highpoly_smoothing_groups_enum"), False)
def BM_ITEM_PROPS_csh_highpoly_smoothing_groups_angle_Update(self, context):
    name = "Object Shading: Highpoly auto smooth angle"
    BM_LastEditedProp_Write(context, name, "csh_highpoly_smoothing_groups_angle", getattr(self, "csh_highpoly_smoothing_groups_angle"), False)
def BM_ITEM_PROPS_csh_highpoly_smoothing_groups_name_contains_Update(self, context):
    name = "Object Shading: Highpoly vertex groups name contains"
    BM_LastEditedProp_Write(context, name, "csh_highpoly_smoothing_groups_name_contains", getattr(self, "csh_highpoly_smoothing_groups_name_contains"), False)
def BM_ITEM_PROPS_bake_save_internal_Update(self, context):
    name = "Object Bake Output: Save internally"
    BM_LastEditedProp_Write(context, name, "bake_save_internal", getattr(self, "bake_save_internal"), False)
def BM_ITEM_PROPS_bake_output_filepath_Update(self, context):
    name = "Object Bake Output: Filepath"
    BM_LastEditedProp_Write(context, name, "bake_output_filepath", getattr(self, "bake_output_filepath"), False)
def BM_ITEM_PROPS_bake_create_subfolder_Update(self, context):
    name = "Object Bake Output: Create subfolder"
    BM_LastEditedProp_Write(context, name, "bake_create_subfolder", getattr(self, "bake_create_subfolder"), False)
def BM_ITEM_PROPS_bake_subfolder_name_Update(self, context):
    name = "Object Bake Output: Subfolder name"
    BM_LastEditedProp_Write(context, name, "bake_subfolder_name", getattr(self, "bake_subfolder_name"), False)
def BM_ITEM_PROPS_bake_batchname_Update(self, context):
    name = "Object Bake Output: Batch name"
    BM_LastEditedProp_Write(context, name, "bake_batchname", getattr(self, "bake_batchname"), False)
def BM_ITEM_PROPS_bake_create_material_Update(self, context):
    name = "Object Bake Output: Create material"
    BM_LastEditedProp_Write(context, name, "bake_create_material", getattr(self, "bake_create_material"), False)
def BM_ITEM_PROPS_bake_assign_modifiers_Update(self, context):
    name = "Object Bake Output: Assign Modifiers"
    BM_LastEditedProp_Write(context, name, "bake_assign_modifiers", getattr(self, "bake_assign_modifiers"), False)
def BM_ITEM_PROPS_bake_device_Update(self, context):
    name = "Object Bake Output: Device"
    BM_LastEditedProp_Write(context, name, "bake_device", getattr(self, "bake_device"), False)
def BM_ITEM_PROPS_bake_hide_when_inactive_Update(self, context):
    name = "Object Bake Output: Hide when Inactive"
    BM_LastEditedProp_Write(context, name, "bake_hide_when_inactive", getattr(self, "bake_hide_when_inactive"), False)
def BM_ITEM_PROPS_bake_vg_index_Update(self, context):
    name = "Object Bake Output: VG Index"
    BM_LastEditedProp_Write(context, name, "bake_vg_index", getattr(self, "bake_vg_index"), False)

###############################################################
### Update Funcs for global_cauc_objects object ###
###############################################################
def BM_CAUC_Object_UnsetBoolsUpdate(self, props):
    for prop in props:
        setattr(self, prop, False)

def BM_CAUC_Object_use_include_Update(self, context):
    if self.use_include:
        BM_CAUC_Object_UnsetBoolsUpdate(self, ["is_highpoly", "is_cage"])
def BM_CAUC_Object_is_highpoly_Update(self, context):
    if self.is_highpoly:
        BM_CAUC_Object_UnsetBoolsUpdate(self, ["use_include", "is_cage"])
def BM_CAUC_Object_is_cage_Update(self, context):
    if self.is_cage:
        BM_CAUC_Object_UnsetBoolsUpdate(self, ["use_include", "is_highpoly"])
