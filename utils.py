# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on
# Copyright (C) 2022 Kiril Strezikozin aka kemplerart
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
def BM_Object_Get(context):
    object = [context.scene.bm_table_of_objects[context.scene.bm_props.global_active_index], True] 
    try:
        context.scene.objects[object[0].global_object_name]
    except (KeyError, AttributeError, UnboundLocalError):
        object[1] = False
    return object

def BM_Map_Get(object):
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
                new_highpoly.global_item_index = highpoly_index + 1
                try:
                    BM_ITEM_PROPS_hl_add_highpoly_Update(new_highpoly, context)
                    new_highpoly.global_object_name = highpoly
                    lowpoly_object.hl_highpoly_table_active_index = len(lowpoly_object.hl_highpoly_table) - 1
                    lowpoly_object.hl_is_lowpoly = True
                except TypeError:
                    # lowpoly_object.hl_highpoly_table.remove(highpoly_index)
                    pass

                # mark highpoly source object as decal if decal tag had been found previously
                if marked_decals[highpoly_index] == 1 and new_highpoly.global_highpoly_object_index != -1: 
                    context.scene.bm_table_of_objects[new_highpoly.global_highpoly_object_index].hl_is_decal = True

            # set cage
            if cage != "NONE":
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
            'out_udim_start_tile' : self.out_udim_start_tile,
            'out_udim_end_tile' : self.out_udim_end_tile,
            'out_super_sampling_aa' : self.out_super_sampling_aa,
            'out_samples' : self.out_samples,
            'out_use_adaptive_sampling' : self.out_use_adaptive_sampling,
            'out_adaptive_threshold' : self.out_adaptive_threshold,
            'out_min_samples' : self.out_min_samples,
            'out_use_unique_per_map' : self.out_use_unique_per_map,
            'csh_use_triangulate_lowpoly' : self.csh_use_triangulate_lowpoly,
            'csh_use_lowpoly_reset_normals' : self.csh_use_lowpoly_reset_normals,
            'csh_lowpoly_use_smooth' : self.csh_lowpoly_use_smooth,
            'csh_lowpoly_smoothing_groups_enum' : self.csh_lowpoly_smoothing_groups_enum,
            'csh_lowpoly_smoothing_groups_angle' : self.csh_lowpoly_smoothing_groups_angle,
            'csh_lowpoly_smoothing_groups_name_contains' : self.csh_lowpoly_smoothing_groups_name_contains,
            'csh_use_highpoly_reset_normals' : self.csh_use_highpoly_reset_normals,
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
            'bake_device' : self.bake_device,
        }

        # apply props values to all container objects
        local_c_master_index = -1
        for object in context.scene.bm_table_of_objects:
            if object.nm_item_uni_container_master_index == self.nm_master_index and object.nm_is_lowpoly_container:
                local_c_master_index = object.nm_master_index

            if object.nm_item_uni_container_master_index == self.nm_master_index and object.nm_is_local_container is False and object.nm_item_local_container_master_index == local_c_master_index: 
                # maps
                # trash
                BM_ITEM_RemoveLocalPreviews(object, context)
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
                        'out_udim_start_tile' : map.out_udim_start_tile,
                        'out_udim_end_tile' : map.out_udim_end_tile,
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
                        'map_vertexcolor_layer' : map.map_vertexcolor_layer,

                        'map_C_COMBINED_prefix' : map.map_C_COMBINED_prefix,

                        'map_C_AO_prefix' : map.map_C_AO_prefix,

                        'map_C_SHADOW_prefix' : map.map_C_SHADOW_prefix,

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

        BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

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
                break

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
    object = BM_Object_Get(context)[0]
    maps_names = {
        'ALBEDO' : "Albedo",
        'METALNESS' : "Metalness",
        'ROUGHNESS' : "Roughness",
        'DIFFUSE' : "Diffuse",
        'SPECULAR' : "Specular",
        'GLOSSINESS' : "Glossiness",
        'OPACITY' : "Opacity",
        'EMISSION' : "Emission/Lightmap",

        'NORMAL' : "Normal",
        'DISPLACEMENT' : "Displacement",
        'VECTOR_DISPLACEMENT' : "Vector Displacement",
        'POSITION' : "Position",
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

#     object = BM_Object_Get(context)[0]
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
#     object = BM_Object_Get(context)[0]
#     for keyword in object.bake_batch_name_table:
#         try:
#             keyword.global_keyword = keyword.global_keyword_old
#         except (TypeError, ValueError):
#             pass

def BM_ITEM_PROPS_bake_batchname_GetPreview(self, context):
    # funcs for data get
    def get_objectname(container):
        if not any([container.nm_is_universal_container, container.nm_is_local_container, context.scene.bm_props.global_use_name_matching]):
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
    
    def get_packname(container):
        for chnlpack in container.chnlp_channelpacking_table:
            chosen_data = {
                'R1G1B' : ['_map_R', '_map_G', '_map_B'],
                'RGB1A' : ['_map_RGB', '_map_A'],
                'R1G1B1A' : ['_map_R', '_map_G', '_map_B', '_map_A'],
            }
            chosen_maps = []
            for prop in chosen_data[chnlpack.global_channelpack_type]:
                chosen_maps.append(getattr(chnlpack, '{}{}'.format(chnlpack.global_channelpack_type, prop)))
            for map_pass in container.global_maps:
                if str(map_pass.global_map_index) in chosen_maps:
                    return chnlpack.global_channelpack_name
        return None
    
    def get_texsetname(container):
        if not any([container.nm_is_universal_container, container.nm_is_local_container, context.scene.bm_props.global_use_name_matching]):
            container_name = container.global_object_name
        else:
            container_name = container.nm_container_name
        
        if container.global_is_included_in_texset:
            return None
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
                            if context.scene.bm_table_of_objects[obj1.global_source_object_index].nm_is_universal_container and context.scene.bm_props.global_use_name_matching:
                                for subobj in obj1.global_object_name_subitems:
                                    if subobj.global_object_include_in_texset:
                                        return_name += "%s_" % subobj.global_object_name
                            else:
                                return_name += "%s_" % obj1.global_object_name
                        return return_name[:-1]

    def get_mapres(map_pass):
        if map_pass.out_res == 'CUSTOM':
            return map_pass.out_res_height + "x" + map_pass.out_res_width
        else:
            return map_pass.out_res
    
    def get_mapnormal(map_pass):
        if map.map_normal_preset != 'CUSTOM':
            return map.map_normal_preset
        else:
            return map.map_normal_custom_preset
    
    object = BM_Object_Get(context)[0]
    if len(object.global_maps) == 0:
        # self.bake_batchname_preview = "*Object has no Maps*"
        return "*Object has no Maps*"
    map = object.global_maps[object.global_maps_active_index]

    gen_keywords_values = {
        "$objectindex" : context.scene.bm_props.global_active_index,
        "$objectname" : get_objectname(object),
        "$containername" : get_containername(object),
        "$packname" : get_packname(object),
        "$texsetname" : get_texsetname(object),
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
        "$engine" : object.bake_device,
        "$autouv" : "autouv" if object.uv_use_auto_unwrap else "",
    }

    preview = ""
    temp_preview = ""
    finding_keyword = False
    for index, char in enumerate(object.bake_batchname):
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
                if index == len(object.bake_batchname) - 1:
                    preview += temp_preview
            else:
                # keyword found, add its value to preview
                if gen_keywords_values[temp_preview.lower()] is None:
                    finding_keyword = False
                    continue
                if object.bake_batchname_use_caps:
                    preview += str(gen_keywords_values[temp_preview.lower()]).upper()
                else:
                    preview += str(gen_keywords_values[temp_preview.lower()])
                finding_keyword = False

    # self.bake_batchname_preview = preview
    return preview

def BM_ITEM_PROPS_bake_batchname_use_caps_Update(self, context):
    BM_LastEditedProp_Write(context, "Object Bake Output: Batch name use caps", "bake_batchname_use_caps", getattr(self, "bake_batchname_use_caps"), False)
    # upper-case batch name if true else lower-case
    self.bake_batchname = self.bake_batchname.upper() if self.bake_batchname_use_caps else self.bake_batchname.lower()

###############################################################
### BM Table of Objects Funcs ###
###############################################################
def BM_ActiveIndexUpdate(self, context):
    if len(context.scene.bm_table_of_objects):
        source_object = BM_Object_Get(context)
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

    active_object = BM_Object_Get(context)[0]
    active_index = context.scene.bm_props.global_active_index
    use_nm = context.scene.bm_props.global_use_name_matching
    cage_container_master_index = -1
    include = []
    if active_object.hl_use_unique_per_map and len(active_object.global_maps):
        active_map = BM_Map_Get(active_object)
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
            object = BM_Object_Get(context)[0]
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
        # not including the occasion if self == map, because for uni_c hl_unique_per_map is always false
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
        object = BM_Object_Get(context)[0]
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
    items = []
    # if was chosen None, append it to items
    if self.global_highpoly_object_include == 'NONE' and self.global_highpoly_object_index == -1:
        items.append(('NONE', "None", "No cage available within the Table of Objects"))

    active_object = BM_Object_Get(context)[0]
    active_index = context.scene.bm_props.global_active_index
    use_nm = context.scene.bm_props.global_use_name_matching
    high_container_master_index = -1
    include = []
    skip_include = []
    if active_object.hl_use_unique_per_map and len(active_object.global_maps):
        active_map = BM_Map_Get(active_object)
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
        object = BM_Object_Get(context)[0]
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
    object = BM_Object_Get(context)
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
    items = [('AUTO', "Automatic", "Automatically detect UVMap type. If UDIMs detected, UDIM tiles range will be set automatically for each map"),
             ('SINGLE', "Single (single tile)", "Regular single-tiled UV layer")]
    if bpy.app.version >= (3, 2, 0):
        items.append(('TILED', "Tiled (UDIMs)", "Tiled UV Layer, UDIM tiles"))
    
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
        ('ALBEDO', "Albedo", "PBR-Metallic. Color image texture containing color without shadows and highlights"),
        ('METALNESS', "Metalness", "PBR-Metallic. Image texture for determining metal and non-metal parts of the object"),
        ('ROUGHNESS', "Roughness", "PBR-Metallic. Image texture for determining roughness across the surface of the object"),
        ('', "PBR-Specular", ""),
        ('DIFFUSE', "Albedo", "PBR-Specular. Color image texture containing color without shadows and highlights"),
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
        ('DECAL', "Decal Pass", "Bake common passes for Decal Object"),
        ('', "Masks and Details", ""),
        ('AO', "AO", "Ambient Occlusion map contains lightning data"),
        ('CAVITY', "Cavity", "Image texture map for crevice details"),
        ('CURVATURE', "Curvature", "Image texture map for convexity/concavity"),
        ('THICKNESS', "Thickness", "Thick parts of the mesh. Ambient Occlusion map that casts rays from the surface to the inside. Often used for SSS or masking"),
        ('ID', "Material ID", "Mask out different parts of the mesh with different colors"),
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
    return items

def BM_MAP_PROPS_map_vertexcolor_layer_Items(self, context):
    def object_get_vertexcolor_layers(data):
        items = []
        if len(data):
            for layer in data:
                items.append((str(layer.name), layer.name, "VertexColor Layer to bake"))
            return items
        else:
            return [('NONE', "None", "No VertexColor Layers to bake")]

    object = BM_Object_Get(context)
    if object[1] is False:
        return [('NONE', "None", "Current Object doesn't support VertexColor Layers")]
    source_object = context.scene.objects[object[0].global_object_name]
    if bpy.app.version < (3, 2, 0):
        return object_get_vertexcolor_layers(source_object.data.vertex_colors)
    else:
        return object_get_vertexcolor_layers(source_object.data.color_attributes)

def BM_MAP_PROPS_map_normal_data_Items(self, context):
    object = BM_Object_Get(context)[0]
    if object.hl_use_unique_per_map:
        len_of_highpolies = len(BM_Map_Get(object).hl_highpoly_table)
    else:
        len_of_highpolies = len(object.hl_highpoly_table)
    if len_of_highpolies > 0:
        items = [('HIGHPOLY', "Highpoly", "Bake normals from highpoly object data to lowpoly"),
                 ('MULTIRES', "Multires Modifier", "Bake normals from existing Multires modifier"),
                 ('MATERIAL', "Object/Materials", "Bake normals from object data")]
    else:
        items = [('MULTIRES', "Multires Modifier", "Bake normals from existing Multires modifier"),
                 ('MATERIAL', "Object/Materials", "Bake normals from object data")]
    if object.decal_is_decal:
        items = [('MATERIAL', "Object/Materials", "Bake normals from object data")]
    return items 

def BM_MAP_PROPS_map_displacement_data_Items(self, context):
    object = BM_Object_Get(context)[0]
    if object.hl_use_unique_per_map:
        len_of_highpolies = len(BM_Map_Get(object).hl_highpoly_table)
    else:
        len_of_highpolies = len(object.hl_highpoly_table)
    if len_of_highpolies > 0:
        items = [('HIGHPOLY', "Highpoly", "Bake displacement from highpoly object data to lowpoly"),
                 ('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
                 ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    else:
        items = [('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
                 ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    if object.decal_is_decal:
        items = [('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    return items

# Map Preview Funcs
def BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, map_tag):
    object_item_full = BM_Object_Get(context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    if getattr(BM_Map_Get(object_item), "map_%s_use_preview" % map_tag) is False:
        return

    # collecting objects for which update bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return

    highpolies = object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])

    # which bm_nodes' values will change
    nodes_names_data = {
        'AO' : [
            'BM_AmbientOcclusion',
            'BM_ValToRGB',
            'BM_MixRGB',
            'BM_BrightContrast',
            'BM_Invert',
        ],
        'CAVITY' : [
            'BM_ValToRGB',
            'BM_Math',
            'BM_Invert',
        ],
        'CURVATURE' : [
            'BM_Value',
            'BM_AmbientOcclusion',
            'BM_AmbientOcclusion.001',
            'BM_ValToRGB',
            'BM_Gamma',
        ],
        'THICKNESS' : [
            'BM_AmbientOcclusion',
            'BM_MapRange',
            'BM_ValToRGB',
            'BM_Invert',
        ],
        'XYZMASK' : [
            'BM_SeparateXYZ',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_VectorMath.002',
            'BM_MapRange',
            'BM_MixRGB',
        ],
        'GRADIENT' : [
            'BM_Mapping',
            'BM_TexGradient',
            'BM_MapRange',
            'BM_MixRGB',
            'BM_HueSaturation',
            'BM_Invert',
        ],
        'EDGE' : [
            'BM_Bevel',
            'BM_MapRange',
            'BM_Invert',
        ],
        'WIREFRAME' : [
            'BM_Value',
            'BM_Invert',
        ],
        'POSITION' : [
        ],
        'VERTEX_COLOR_LAYER' : [
            'BM_Attribute',
        ],
        'VECTOR_DISPLACEMENT' : [
            'BM_Value',
        ],
        'DECAL' : [
            'BM_VectorMath.001',
            'BM_Invert',
            'BM_Invert.001',
            'BM_Emission',
        ],
    }
    
    map = BM_Map_Get(object_item)
    # looping through materials
    for object in objects:
        for material in object.data.materials:
            if material is None:
                continue

            material.use_nodes = True
            bm_nodes = str([node.name for node in material.node_tree.nodes])
            if bm_nodes.find('BM_') == -1:
                continue
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            map_nodes = nodes_names_data[map_tag]
            # updating nodes inputs and properties
            if map_tag == "AO":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    distance = 1
                    only_local = False
                    black_point = 0
                    white_point = 0.8
                    opacity = 0.67
                    brightness = -0.3
                    contrast = 0.3
                    invert = 0        
                else:
                    samples = map.map_ao_samples
                    distance = map.map_ao_distance
                    only_local = map.map_ao_use_local
                    black_point = map.map_ao_black_point
                    white_point = map.map_ao_white_point
                    opacity = map.map_ao_opacity
                    brightness = map.map_ao_brightness
                    contrast = map.map_ao_contrast
                    invert = map.map_ao_use_invert

                nodes[map_nodes[0]].samples = samples
                nodes[map_nodes[0]].inputs[1].default_value = distance
                nodes[map_nodes[0]].only_local = only_local
                nodes[map_nodes[1]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[1]].color_ramp.elements[1].position = white_point
                nodes[map_nodes[2]].inputs[0].default_value = opacity
                nodes[map_nodes[3]].inputs[1].default_value = brightness
                nodes[map_nodes[3]].inputs[2].default_value = contrast
                nodes[map_nodes[4]].inputs[0].default_value = invert

            if map_tag == "CAVITY":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    black_point = 0
                    white_point = 1
                    power = 2.5
                    invert = 0
                else:
                    black_point = map.map_cavity_black_point
                    white_point = map.map_cavity_white_point
                    power = map.map_cavity_power
                    invert = map.map_cavity_use_invert

                nodes[map_nodes[0]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[0]].color_ramp.elements[1].position = white_point
                nodes[map_nodes[1]].inputs[1].default_value = power
                nodes[map_nodes[2]].inputs[0].default_value = invert

            if map_tag == "CURVATURE":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    radius = 2.2
                    black_point = 0.4
                    mid_point = 0.5
                    white_point = 0.6
                    gamma = 2.2
                else:
                    samples = map.map_curv_samples
                    radius = map.map_curv_radius
                    black_point = map.map_curv_black_point
                    mid_point = map.map_curv_mid_point
                    white_point = map.map_curv_white_point
                    gamma = map.map_curv_body_gamma
                
                nodes[map_nodes[0]].outputs[0].default_value = radius
                nodes[map_nodes[1]].samples = samples
                nodes[map_nodes[2]].samples = samples
                nodes[map_nodes[3]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[3]].color_ramp.elements[1].position = mid_point
                nodes[map_nodes[3]].color_ramp.elements[2].position = white_point
                nodes[map_nodes[4]].inputs[1].default_value = gamma

            if map_tag == "THICKNESS":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    distance = 1
                    black_point = 0
                    white_point = 1
                    brightness = 1
                    contrast = 0
                    invert = 0
                else:
                    samples = map.map_thick_samples
                    distance = map.map_thick_distance
                    black_point = map.map_thick_black_point
                    white_point = map.map_thick_white_point
                    brightness = map.map_thick_brightness
                    contrast = map.map_thick_contrast
                    invert = map.map_thick_use_invert

                nodes[map_nodes[0]].samples = samples
                nodes[map_nodes[0]].inputs[1].default_value = distance
                nodes[map_nodes[1]].inputs[1].default_value = contrast
                nodes[map_nodes[1]].inputs[4].default_value = brightness
                nodes[map_nodes[2]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[2]].color_ramp.elements[1].position = white_point
                nodes[map_nodes[3]].inputs[0].default_value = invert

            if map_tag == "XYZMASK":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    coverage = 0
                    saturation = 1
                    opacity = 1
                    invert = 1
                else:
                    coverage = map.map_xyzmask_coverage
                    saturation = map.map_xyzmask_saturation
                    opacity = map.map_xyzmask_opacity
                    invert = map.map_xyzmask_use_invert

                for i in range(3):
                    nodes[map_nodes[3]].inputs[1].default_value[i] = invert

                nodes[map_nodes[4]].inputs[1].default_value = coverage
                nodes[map_nodes[4]].inputs[4].default_value = saturation
                nodes[map_nodes[5]].inputs[0].default_value = opacity

                if map.map_xyzmask_use_x:
                    links.new(nodes[map_nodes[0]].outputs[0], nodes[map_nodes[1]].inputs[0])
                elif len(nodes[map_nodes[0]].outputs[0].links):
                    links.remove(nodes[map_nodes[0]].outputs[0].links[0])
                if map.map_xyzmask_use_y:
                    links.new(nodes[map_nodes[0]].outputs[1], nodes[map_nodes[1]].inputs[1])
                elif len(nodes[map_nodes[0]].outputs[1].links):
                    links.remove(nodes[map_nodes[0]].outputs[1].links[0])
                if map.map_xyzmask_use_z:
                    links.new(nodes[map_nodes[0]].outputs[2], nodes[map_nodes[2]].inputs[1])
                elif len(nodes[map_nodes[0]].outputs[2].links):
                    links.remove(nodes[map_nodes[0]].outputs[2].links[0])

            if map_tag == "GRADIENT":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    #mapping = [[0, 0, 0], [0, 0, 0], [1, 1, 1]]
                    coverage = 0
                    contrast = 1
                    saturation = 1
                    opacity = 1
                    invert = 0
                else:
                    coverage = map.map_gmask_coverage
                    contrast = map.map_gmask_contrast
                    saturation = map.map_gmask_saturation
                    opacity = map.map_gmask_opacity
                    invert = map.map_gmask_use_invert
                g_type = map.map_gmask_type

                # mapping can be changed no matter the use_default state
                mapping = [
                    [map.map_gmask_location_x, map.map_gmask_location_y, map.map_gmask_location_z],
                    [map.map_gmask_rotation_x, map.map_gmask_rotation_y, map.map_gmask_rotation_z],
                    [map.map_gmask_scale_x, map.map_gmask_scale_y, map.map_gmask_scale_z],
                ]
                for i in range(1, 4):
                    for j in range(3):
                        nodes[map_nodes[0]].inputs[i].default_value[j] = mapping[i - 1][j]

                nodes[map_nodes[1]].gradient_type = g_type
                nodes[map_nodes[2]].inputs[1].default_value = coverage
                nodes[map_nodes[2]].inputs[4].default_value = contrast
                nodes[map_nodes[3]].inputs[0].default_value = opacity
                nodes[map_nodes[4]].inputs[2].default_value = saturation
                nodes[map_nodes[5]].inputs[0].default_value = invert

            if map_tag == "EDGE":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    radius = 0.02
                    edge_contrast = 0
                    body_contrast = 1
                    invert = 1
                else:
                    samples = map.map_edgemask_samples
                    radius = map.map_edgemask_radius
                    edge_contrast = map.map_edgemask_edge_contrast
                    body_contrast = map.map_edgemask_body_contrast
                    invert = map.map_edgemask_use_invert

                nodes[map_nodes[0]].samples = samples
                nodes[map_nodes[0]].inputs[0].default_value = radius
                nodes[map_nodes[1]].inputs[1].default_value = edge_contrast
                nodes[map_nodes[1]].inputs[4].default_value = body_contrast
                nodes[map_nodes[2]].inputs[0].default_value = invert

            if map_tag == "WIREFRAME":
                radius = map.map_wireframemask_line_thickness
                invert = map.map_wireframemask_use_invert

                nodes[map_nodes[0]].outputs[0].default_value = radius
                nodes[map_nodes[1]].inputs[0].default_value = invert
                
            # if map_tag == "POSITION":
                
            if map_tag == "VERTEX_COLOR_LAYER":
                layer = map.map_vertexcolor_layer

                nodes[map_nodes[0]].attribute_name = layer

            if map_tag == "VECTOR_DISPLACEMENT":
                value = int(not map.map_vector_displacement_use_negative) - 1

                nodes[map_nodes[0]].outputs[0].default_value = value
            
            if map_tag == "DECAL":
                nodes[map_nodes[1]].inputs[0].default_value = bool(map.map_decal_height_opacity_invert)
                nodes[map_nodes[2]].inputs[0].default_value = bool(map.map_decal_height_opacity_invert)

                link_from = {
                    'NORMAL' : 0,
                    'HEIGHT' : 1,
                    'OPACITY' : 2,
                }
                index = link_from[map.map_decal_pass_type]
                links.new(nodes[map_nodes[index]].outputs[0], nodes[map_nodes[3]].inputs[0])

def BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, map_tag):
    object_item_full = BM_Object_Get(context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    if getattr(BM_Map_Get(object_item), "map_%s_use_preview" % map_tag) is False:
        return

    # collecting objects for which add bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return
    highpolies = object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])

    # nodes data
    nodes_data = {
        'AO' : [
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeValToRGB',
            'ShaderNodeMixRGB',
            'ShaderNodeBrightContrast',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'CAVITY' : [
            'ShaderNodeNewGeometry',
            'ShaderNodeValToRGB',
            'ShaderNodeMath',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'CURVATURE' : [
            'ShaderNodeValue',
            'ShaderNodeMath',
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeInvert',
            'ShaderNodeMixRGB',
            'ShaderNodeValToRGB',
            'ShaderNodeGamma',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'THICKNESS' : [
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeMapRange',
            'ShaderNodeValToRGB',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'XYZMASK' : [
            'ShaderNodeNewGeometry',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeMapRange',
            'ShaderNodeMixRGB',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'GRADIENT' : [
            'ShaderNodeTexCoord',
            'ShaderNodeMapping',
            'ShaderNodeTexGradient',
            'ShaderNodeMapRange',
            'ShaderNodeMixRGB',
            'ShaderNodeHueSaturation',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'EDGE' : [
            'ShaderNodeBevel',
            'ShaderNodeNewGeometry',
            'ShaderNodeVectorMath',
            'ShaderNodeMapRange',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'WIREFRAME' : [
            'ShaderNodeValue',
            'ShaderNodeMath',
            'ShaderNodeWireframe',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'POSITION' : [
            'ShaderNodeTexCoord',
            'ShaderNodeSeparateRGB',
            'ShaderNodeInvert',
            'ShaderNodeCombineRGB',
            'ShaderNodeGamma',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'VERTEX_COLOR_LAYER' : [
            'ShaderNodeAttribute',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'VECTOR_DISPLACEMENT' : [
            'ShaderNodeTexCoord',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeValue',
            'ShaderNodeMapRange',
            'ShaderNodeMapRange',
            'ShaderNodeMapRange',
            'ShaderNodeCombineXYZ',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'DECAL' : [
            'ShaderNodeTexCoord',
            'ShaderNodeVectorTransform',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeInvert',
            'ShaderNodeInvert',
            'ShaderNodeRGB',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
    }

    nodes_names_data = {
        'AO' : [
            'BM_AmbientOcclusion',
            'BM_ValToRGB',
            'BM_MixRGB',
            'BM_BrightContrast',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'CAVITY' : [
            'BM_NewGeometry',
            'BM_ValToRGB',
            'BM_Math',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'CURVATURE' : [
            'BM_Value',
            'BM_Math',
            'BM_AmbientOcclusion',
            'BM_AmbientOcclusion.001',
            'BM_Invert',
            'BM_MixRGB',
            'BM_ValToRGB',
            'BM_Gamma',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'THICKNESS' : [
            'BM_AmbientOcclusion',
            'BM_MapRange',
            'BM_ValToRGB',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'XYZMASK' : [
            'BM_NewGeometry',
            'BM_SeparateXYZ',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_VectorMath.002',
            'BM_MapRange',
            'BM_MixRGB',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'GRADIENT' : [
            'BM_TexCoord',
            'BM_Mapping',
            'BM_TexGradient',
            'BM_MapRange',
            'BM_MixRGB',
            'BM_HueSaturation',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'EDGE' : [
            'BM_Bevel',
            'BM_NewGeometry',
            'BM_VectorMath',
            'BM_MapRange',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'WIREFRAME' : [
            'BM_Value',
            'BM_Math',
            'BM_Wireframe',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'POSITION' : [
            'BM_TexCoord',
            'BM_SeparateRGB',
            'BM_Invert',
            'BM_CombineRGB',
            'BM_Gamma',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'VERTEX_COLOR_LAYER' : [
            'BM_Attribute',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'VECTOR_DISPLACEMENT' : [
            'BM_TexCoord',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_VectorMath.002',
            'BM_SeparateXYZ',
            'BM_SeparateXYZ.001',
            'BM_Value',
            'BM_MapRange',
            'BM_MapRange.001',
            'BM_MapRange.002',
            'BM_CombineXYZ',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'DECAL' : [
            'BM_TexCoord',
            'BM_VectorTransform',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_SeparateXYZ',
            'BM_Invert',
            'BM_Invert.001',
            'BM_RGB',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
    }

    # adding materials if needed
    for object in objects:
        len_of_mats = len(object.data.materials)
        if len_of_mats == 0 or len([material for material in object.data.materials if material is None]) == len_of_mats:
            new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s" % (object.name, map_tag))
            object.data.materials.append(new_mat)
    
    # adding nodes to object's materials
    for object in objects:
        for material in object.data.materials:
            if material is None:
                continue

            material.use_nodes = True
            location_x = 0
            for index, node_type in enumerate(nodes_data[map_tag]):
                new_node = material.node_tree.nodes.new(node_type)
                new_node.name = nodes_names_data[map_tag][index]
                new_node.location = (location_x, 0)
                location_x += 300

            # setting up added nodes defaults
            nodes = material.node_tree.nodes
            # AO
            if map_tag == "AO":
                nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
                nodes['BM_MixRGB'].inputs[1].default_value = (1, 1, 1, 1)
        
            # CAVITY
            if map_tag == "CAVITY":
                nodes['BM_Math'].operation = 'POWER'
                nodes['BM_OutputMaterial'].target = 'CYCLES'

            # CURVATURE
            if map_tag == "CURVATURE":
                nodes['BM_Math'].operation = 'MULTIPLY'
                nodes['BM_Math'].inputs[1].default_value = 0.01
                nodes['BM_AmbientOcclusion'].inside = True
                nodes['BM_AmbientOcclusion.001'].inside = False
                nodes['BM_AmbientOcclusion.001'].inputs[0].default_value = (0, 0, 0, 1)
                nodes['BM_ValToRGB'].color_ramp.elements[0].color = (0, 0, 0, 1)
                nodes['BM_ValToRGB'].color_ramp.elements[1].color = (1, 1, 1, 1)
                new_element = nodes['BM_ValToRGB'].color_ramp.elements.new(0.5)
                new_element.color = (0.5, 0.5, 0.5, 1)
            
            # THICKNESS
            if map_tag == "THICKNESS":
                nodes['BM_AmbientOcclusion'].inside = True

            # XYZMASK
            if map_tag == "XYZMASK":
                nodes['BM_VectorMath.002'].operation = 'MULTIPLY'
                nodes['BM_MixRGB'].inputs[1].default_value = (0, 0, 0, 0)

            # GRADIENT
            if map_tag == "GRADIENT":
                nodes['BM_MixRGB'].inputs[1].default_value = (0, 0, 0, 0)

            # EDGE
            if map_tag == "EDGE":
                nodes['BM_VectorMath'].operation = 'DOT_PRODUCT'

            # WIREFRAME
            if map_tag == "WIREFRAME":
                nodes['BM_Math'].operation = 'MULTIPLY'
                nodes['BM_Math'].inputs[1].default_value = 0.01

            # POSITION
            if map_tag == "POSITION":
                nodes['BM_Gamma'].inputs[1].default_value = 2.2

            # VERTEX_COLOR_LAYER
            if map_tag == "VERTEX_COLOR_LAYER":
                pass
            
            # VECTOR_DISPLACEMENT
            if map_tag == "VECTOR_DISPLACEMENT":
                nodes['BM_VectorMath'].inputs[1].default_value[0] = -0.5
                nodes['BM_VectorMath'].inputs[1].default_value[1] = -0.5
                nodes['BM_VectorMath'].inputs[1].default_value[2] = -0.5
                nodes['BM_VectorMath.001'].operation = 'MULTIPLY'
                nodes['BM_VectorMath.001'].inputs[1].default_value[0] = 2
                nodes['BM_VectorMath.001'].inputs[1].default_value[1] = 2
                nodes['BM_VectorMath.001'].inputs[1].default_value[2] = 2
                nodes['BM_VectorMath.002'].operation = 'SUBTRACT'
                nodes['BM_MapRange'].clamp = False
                nodes['BM_MapRange.001'].clamp = False
                nodes['BM_MapRange.002'].clamp = False
            
            # DECAL
            if map_tag == "DECAL":
                nodes['BM_VectorTransform'].convert_to = 'CAMERA'
                nodes['BM_VectorMath'].operation = 'MULTIPLY'
                nodes['BM_VectorMath'].inputs[1].default_value = (0.5, 0.5, -0.5)
                nodes['BM_VectorMath.001'].inputs[1].default_value = (0.5, 0.5, 0.5)
                nodes['BM_RGB'].outputs[0].default_value = (1, 1, 1, 1)

            nodes['BM_OutputMaterial'].target = 'CYCLES'

            # linking added nodes
            # shell - [node_from, node_to, out_socket, in_socket]
            links_data = {
                'AO' : [
                    [0, 1, 1, 0],
                    [1, 2, 0, 2],
                    [2, 3, 0, 0],
                    [3, 4, 0, 1],
                    [4, 5, 0, 0],
                    [5, 6, 0, 0],
                ],
                'CAVITY' : [
                    [0, 1, 7, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                ],
                'CURVATURE' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 1],
                    [1, 3, 0, 1],
                    [2, 4, 1, 1],
                    [4, 5, 0, 1],
                    [3, 5, 1, 2],
                    [5, 6, 0, 0],
                    [6, 7, 0, 0],
                    [7, 8, 0, 0],
                    [8, 9, 0, 0],
                ],
                'THICKNESS' : [
                    [0, 1, 1, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                ],
                'XYZMASK' : [
                    [0, 1, 1, 0],
                    [2, 3, 0, 0],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                    [5, 6, 0, 2],
                    [6, 7, 0, 0],
                    [7, 8, 0, 0],
                ],
                'GRADIENT' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 0],
                    [3, 4, 0, 2],
                    [4, 5, 0, 4],
                    [5, 6, 0, 1],
                    [6, 7, 0, 0],
                    [7, 8, 0, 0],
                ],
                'EDGE' : [
                    [0, 2, 0, 0],
                    [1, 2, 1, 1],
                    [2, 3, 1, 0],
                    [3, 4, 0, 1],
                    [4, 5, 0, 0],
                    [5, 6, 0, 0],
                ],
                'WIREFRAME' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                ],
                'POSITION' : [
                    [0, 1, 0, 0],
                    [1, 3, 0, 0],
                    [1, 3, 2, 1],
                    [1, 2, 1, 1],
                    [2, 3, 0, 2],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                    [5, 6, 0, 0],
                ],
                'VERTEX_COLOR_LAYER' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 0],
                ],
                'VECTOR_DISPLACEMENT' : [
                    [0, 1, 2, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [0, 3, 3, 0],
                    [3, 4, 0, 0],
                    [0, 5, 3, 0],
                    [6, 7, 0, 1],
                    [6, 8, 0, 1],
                    [6, 9, 0, 1],
                    [4, 7, 0, 0],
                    [4, 8, 1, 0],
                    [5, 9, 2, 0],
                    [7, 10, 0, 0],
                    [8, 10, 0, 1],
                    [9, 10, 0, 2],
                    [10, 11, 0, 0],
                    [11, 12, 0, 0],
                ],
                'DECAL' : [
                    [0, 1, 1, 0],
                    [0, 4, 0, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 0],
                    [4, 5, 2, 1],
                    [7, 6, 0, 1],
                    [8, 9, 0, 0],
                ],
            }

            # linking
            map_nodes = nodes_names_data[map_tag]
            for link in links_data[map_tag]:
                out_socket = material.node_tree.nodes[map_nodes[link[0]]].outputs[link[2]]
                in_socket = material.node_tree.nodes[map_nodes[link[1]]].inputs[link[3]]
                material.node_tree.links.new(out_socket, in_socket)
            
            if context.scene.render.engine != 'CYCLES':
                bpy.ops.bakemaster.report_message(message_type='INFO', message=BM_Labels.INFO_MAP_PREVIEWNOTCYCLES)

            material.node_tree.nodes['BM_OutputMaterial'].select = True
            material.node_tree.nodes.active = nodes['BM_OutputMaterial']

    #       for node in nodes:
    #           if node.type == 'OUTPUT_MATERIAL' and node.name.find('BM_') == -1:
    #               node.target = 'ALL'

    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, map_tag)

def BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, map_tag):
    object_item_full = BM_Object_Get(context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    map = BM_Map_Get(object_item)
    if getattr(map, "map_%s_use_preview" % map_tag) is False:
        return

    # collecting objects for which add bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return
    highpolies = object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])

    map_type_origin = map_tag
    if map_tag == 'PASS':
        map_tag = map.map_pass_type

    # each shaders supports grabbing specified passes,
    # passes keys' values are sockets names
    # passes names and grabbing algo may differ for each map type
    node_getable_data = {
        'ALBEDO' : ['Color', 'Base Color'],
        'METALNESS' : ['Metallic'],
        'ROUGHNESS' : ['Roughness'],
        'DIFFUSE' : ['Color', 'Base Color'],
        'SPECULAR' : ['Specular'],
        'GLOSSINESS' : ['Roughness'],
        'OPACITY' : ['Alpha', 'Opacity'],
        'BASE_COLOR' : ['Base Color'],
        'SS_COLOR' : ['Subsurface Color', 'Color'],
        'METALLIC' : ['Metallic'],
        'ANISOTROPIC' : ['Anisotropic'],
        'SHEEN' : ['Sheen'],
        'CLEARCOAT' : ['Clearcoat'],
        'IOR' : ['IOR'],
        'TRANSMISSION' : ['Transmission'],
        'EMISSION' : ['Emission'],
        'ALPHA' : ['Alpha'],
        'NORMAL' : ['Normal'],
        'DISPLACEMENT' : ['Displacement'],
    }

    def get_socket_default_color_value(socket, socket_name):  
        default_color_data = {
            'Color' : getattr(socket, "default_value"),
            'Base Color' : getattr(socket, "default_value"),
            'Metallic' : [getattr(socket, "default_value")]*3,
            'Roughness' : [getattr(socket, "default_value")]*3,
            'Specular' : [getattr(socket, "default_value")]*3,
            'Alpha' : [getattr(socket, "default_value")]*3,
            'Subsurface Color' : getattr(socket, "default_value"),
            'Anisotropic' : [getattr(socket, "default_value")]*3,
            'Sheen' : [getattr(socket, "default_value")]*3,
            'Clearcoat' : [getattr(socket, "default_value")]*3,
            'IOR' : [getattr(socket, "default_value")]*3,
            'Transmission' : [getattr(socket, "default_value")]*3,
            'Emission' : getattr(socket, "default_value"),
            'Normal' : [0.5, 0.5, 1],
            'Displacement' : [0.0]*3,
        }
        data = list(default_color_data[socket_name])
        if len(data) != 4:
            data.append(1)
        return tuple(data)
    
    ad_map_tag = ""
    map_tag_origin = map_tag
    if map_tag in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
        ad_map_tag = 'METALNESS'
        map_tag = 'DIFFUSE'

    for object in objects:
        if len(object.data.materials) == 0:
            bpy.ops.bakemaster.report_message(message_type='WARNING', message="%s: No Materials" % object.name)
            continue

        for material in object.data.materials:
            if material is None:
                continue

            material.use_nodes = True
            grab_socket = None
            default_value = None
            grab_ad_socket = None
            default_ad_value = None
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            # grabbing socket to preview
            for node in nodes:
                if node.type != 'OUTPUT_MATERIAL':
                    continue
                
                if map_tag == 'DISPLACEMENT':
                    if len(node.inputs[2].links) == 0:
                        continue
                    grab_socket = node.inputs[2].links[0].from_socket
                    input_node = node.inputs[2].links[0].from_node
                    if input_node.type in ['DISPLACEMENT', 'VECTOR_DISPLACEMENT']:
                            if len(input_node.inputs[0].links) == 0:
                                default_value = tuple([input_node.inputs[0].default_value, input_node.inputs[0].default_value, input_node.inputs[0].default_value, 1])
                                grab_socket = None
                                break
                            grab_socket = input_node.inputs[0].links[0].from_socket
                    break
                
                if len(node.inputs[0].links) == 0:
                        continue
                
                # find socket value to grab
                for input_socket in node.inputs[0].links[0].from_node.inputs:
                    if input_socket.name in node_getable_data[map_tag]:
                        if len(input_socket.links) == 0:
                            default_value = get_socket_default_color_value(input_socket, input_socket.name)
                            break
                        grab_socket = input_socket.links[0].from_socket
                        if input_socket.links[0].from_node.type == 'NORMAL_MAP':
                            if len(input_socket.links[0].from_node.inputs[1].links) == 0:
                                default_value = tuple(input_socket.links[0].from_node.inputs[1].default_value)
                                grab_socket = None
                                break
                            grab_socket = input_socket.links[0].from_node.inputs[1].links[0].from_socket
                        break

                if any([grab_socket is not None, default_value is not None]):
                    break

                if ad_map_tag == "":
                    continue
                
                # find additional socket value for pbrs previews
                for input_socket in node.inputs[0].links[0].from_node.inputs:
                    if input_socket.name in node_getable_data[ad_map_tag]:
                        if len(input_socket.links) == 0:
                            default_ad_value = get_socket_default_color_value(input_socket, input_socket.name)
                            break
                        grab_ad_socket = input_socket.links[0].from_socket
                        break
                
                if any([grab_ad_socket is not None, default_ad_value is not None]):
                    break
            
            # add out, emission nodes
            new_nodes = ['ShaderNodeEmission', 'ShaderNodeOutputMaterial']
            rgb_node_name_end = ""
            if grab_socket is None:
                new_nodes.append('ShaderNodeRGB')
            if grab_ad_socket is None and map_tag_origin in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeRGB')
                rgb_node_name_end = ".001" if grab_socket is None else ""

            # pbr specular nodes
            if map_tag_origin in ['GLOSSINESS', 'DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeInvert')
            if map_tag_origin in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeMixRGB')
            if map_tag_origin == 'SPECULAR' and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeValue')
                new_nodes.append('ShaderNodeMixRGB')

            location_x = 0
            for node_type in new_nodes:
                new_node = nodes.new(node_type)
                new_node.name = 'BM_%s' % node_type[10:]
                new_node.location = (location_x, 0)
                location_x += 300

            # nodes values
            default_value = (0, 0, 0, 1) if default_value is None else default_value
            if grab_socket is None:
                nodes['BM_RGB'].outputs[0].default_value = default_value
                value = nodes['BM_RGB'].outputs[0]
            else:
                value = grab_socket

            # additional node values
            default_ad_value = (0, 0, 0, 1) if default_ad_value is None else default_ad_value
            if grab_ad_socket is None and map_tag_origin in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                nodes['BM_RGB%s' % rgb_node_name_end].outputs[0].default_value = default_ad_value
                ad_value = nodes['BM_RGB%s' % rgb_node_name_end].outputs[0]
            elif map_type_origin != 'PASS':
                ad_value = grab_ad_socket

            # link added nodes and link with grabbed socket
            if map_tag_origin == 'GLOSSINESS':
                nodes['BM_Invert'].inputs[0].default_value = 1.0
                links.new(value, nodes['BM_Invert'].inputs[1])
                links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
            elif map_tag_origin == 'DIFFUSE':
                nodes['BM_Invert'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
                links.new(ad_value, nodes['BM_Invert'].inputs[1])
                links.new(nodes['BM_Invert'].outputs[0], nodes['BM_MixRGB'].inputs[2])
                links.new(value, nodes['BM_MixRGB'].inputs[1])
                links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_Emission'].inputs[0])
            elif map_tag_origin == 'SPECULAR' and map_type_origin != 'PASS':
                nodes['BM_Invert'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
                nodes['BM_MixRGB.001'].blend_type = 'ADD'
                nodes['BM_Value'].outputs[0].default_value = 0.04
                links.new(ad_value, nodes['BM_Invert'].inputs[1])
                links.new(ad_value, nodes['BM_MixRGB'].inputs[2])
                links.new(nodes['BM_Invert'].outputs[0], nodes['BM_MixRGB.001'].inputs[0])
                links.new(value, nodes['BM_MixRGB'].inputs[1])
                links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_MixRGB.001'].inputs[1])
                links.new(nodes['BM_Value'].outputs[0], nodes['BM_MixRGB.001'].inputs[2])
                links.new(nodes['BM_MixRGB.001'].outputs[0], nodes['BM_Emission'].inputs[0])
            else:
                if grab_socket is None:
                    links.new(nodes['BM_RGB'].outputs[0], nodes['BM_Emission'].inputs[0])
                else:
                    links.new(grab_socket, nodes['BM_Emission'].inputs[0])
            links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

            if context.scene.render.engine != 'CYCLES':
                bpy.ops.bakemaster.report_message(message_type='INFO', message=BM_Labels.INFO_MAP_PREVIEWNOTCYCLES)

            nodes['BM_OutputMaterial'].target = 'CYCLES'
            nodes['BM_OutputMaterial'].select = True
            nodes.active = nodes['BM_OutputMaterial']

def BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context):
    object_item = BM_Object_Get(context)
    if any([object_item[1] is False, object_item[0].nm_is_universal_container, object_item[0].nm_is_local_container]):
        return

    # collecting objects from which remove bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item[0].global_object_name]
    if len(source_object) == 0:
        return
    objects = [source_object[0]]
    highpolies = object_item[0].hl_highpoly_table
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])

    # removing bm_nodes
    for object in objects:
        mats_to_remove = []
        for mat_index, material in enumerate(object.data.materials):
            if material is None:
                continue
            if material.name.find('BM_CustomMaterial') != -1:
                mats_to_remove.append(mat_index)
                continue

            material.use_nodes = True
            to_remove = []
            for index, node in enumerate(material.node_tree.nodes):
                if node.name.find('BM_') != -1:
                    to_remove.append(index)
            for index in sorted(to_remove, reverse=True):
                material.node_tree.nodes.remove(material.node_tree.nodes[index])
        
        # removing custom bm_materials
        for mat_index in sorted(mats_to_remove, reverse=True):
            object.data.materials.pop(index=mat_index)

# the same, no attention to bm mats removal, because they are not added anyway
BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove = BM_MAP_PROPS_MapPreview_CustomNodes_Remove

def BM_MAP_PROPS_MapPreview_Unset(context, obj_index_init, map_index_init, skip_current_map, map_tag):
    # unset all previews
    for obj_index, object in enumerate(context.scene.bm_table_of_objects):
        context.scene.bm_props.global_active_index = obj_index
        for map_index, map in enumerate(object.global_maps):
            object.global_maps_active_index = map_index

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
                if all([skip_current_map, obj_index == obj_index_init, map_index_init == map_index_init, key == map_tag]):
                    continue

                if getattr(map, "map_%s_use_preview" % key):
                    setattr(map, "map_%s_use_preview" % key, False)

    # return indexes back
    context.scene.bm_props.global_active_index = obj_index_init
    BM_Object_Get(context)[0].global_maps_active_index = map_index_init

# Map previews with custom nodes
def BM_MAP_PROPS_map_AO_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_AO_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'AO')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'AO')
def BM_MAP_PROPS_map_CAVITY_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_CAVITY_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'CAVITY')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'CAVITY')
def BM_MAP_PROPS_map_CURVATURE_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_CURVATURE_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'CURVATURE')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'CURVATURE')
def BM_MAP_PROPS_map_THICKNESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_THICKNESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'THICKNESS')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'THICKNESS')
def BM_MAP_PROPS_map_XYZMASK_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_XYZMASK_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'XYZMASK')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'XYZMASK')
def BM_MAP_PROPS_map_GRADIENT_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_GRADIENT_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'GRADIENT')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'GRADIENT')
def BM_MAP_PROPS_map_EDGE_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_EDGE_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'EDGE')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'EDGE')
def BM_MAP_PROPS_map_WIREFRAME_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_WIREFRAME_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'WIREFRAME')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'WIREFRAME')
def BM_MAP_PROPS_map_POSITION_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_POSITION_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'POSITION')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'POSITION')
def BM_MAP_PROPS_map_VERTEX_COLOR_LAYER_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_VERTEX_COLOR_LAYER_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'VERTEX_COLOR_LAYER')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'VERTEX_COLOR_LAYER')
def BM_MAP_PROPS_map_VECTOR_DISPLACEMENT_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_VECTOR_DISPLACEMENT_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'VECTOR_DISPLACEMENT')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'VECTOR_DISPLACEMENT')
def BM_MAP_PROPS_map_DECAL_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_CustomNodes_Remove(context)
    if self.map_DECAL_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'DECAL')
        BM_MAP_PROPS_MapPreview_CustomNodes_Add(self, context, 'DECAL')

# Map Previews with Material Relinking
def BM_MAP_PROPS_map_ALBEDO_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_ALBEDO_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'ALBEDO')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'ALBEDO')
def BM_MAP_PROPS_map_METALNESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_METALNESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'METALNESS')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'METALNESS')
def BM_MAP_PROPS_map_ROUGHNESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_ROUGHNESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'ROUGHNESS')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'ROUGHNESS')
def BM_MAP_PROPS_map_DIFFUSE_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_DIFFUSE_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'DIFFUSE')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'DIFFUSE')
def BM_MAP_PROPS_map_SPECULAR_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_SPECULAR_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'SPECULAR')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'SPECULAR')
def BM_MAP_PROPS_map_GLOSSINESS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_GLOSSINESS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'GLOSSINESS')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'GLOSSINESS')
def BM_MAP_PROPS_map_OPACITY_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_OPACITY_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'OPACITY')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'OPACITY')
def BM_MAP_PROPS_map_EMISSION_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_EMISSION_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'EMISSION')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'EMISSION')
def BM_MAP_PROPS_map_PASS_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_PASS_use_preview:
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'PASS')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'PASS')
def BM_MAP_PROPS_map_NORMAL_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_NORMAL_use_preview and self.map_normal_data == 'MATERIAL':
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'NORMAL')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'NORMAL')
def BM_MAP_PROPS_map_DISPLACEMENT_use_preview_Update(self, context):
    BM_MAP_PROPS_MapPreview_RelinkMaterials_Remove(context)
    if self.map_DISPLACEMENT_use_preview and self.map_displacement_data == 'MATERIAL':
        BM_MAP_PROPS_MapPreview_Unset(context, context.scene.bm_props.global_active_index, self.global_map_index - 1, True, 'DISPLACEMENT')
        BM_MAP_PROPS_MapPreview_RelinkMaterials_Add(self, context, 'DISPLACEMENT')

# Map Previews with Material Reassign
def BM_MAP_PROPS_map_ID_use_preview_Update(self, context):
    pass
def BM_MAP_PROPS_map_MASK_use_preview_Update(self, context):
    pass

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
    name = "Map: Albedo prefix"
    BM_LastEditedProp_Write(context, name, "map_ALBEDO_prefix", getattr(self, "map_ALBEDO_prefix"), True)
def BM_MAP_PROPS_map_METALNESS_prefix_Update(self, context):
    name = "Map: Metalness prefix"
    BM_LastEditedProp_Write(context, name, "map_METALNESS_prefix", getattr(self, "map_METALNESS_prefix"), True)
def BM_MAP_PROPS_map_ROUGHNESS_prefix_Update(self, context):
    name = "Map: Roughness prefix"
    BM_LastEditedProp_Write(context, name, "map_ROUGHNESS_prefix", getattr(self, "map_ROUGHNESS_prefix"), True)
def BM_MAP_PROPS_map_DIFFUSE_prefix_Update(self, context):
    name = "Map: Diffuse prefix"
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
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'DECAL')
def BM_MAP_PROPS_map_decal_height_opacity_invert_Update(self, context):
    name = "Map: Decal Pass invert"
    BM_LastEditedProp_Write(context, name, "map_decal_height_opacity_invert", getattr(self, "map_decal_height_opacity_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'DECAL')
def BM_MAP_PROPS_map_decal_normal_preset_Update(self, context):
    name = "Map: Decal Pass preset"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_preset", getattr(self, "map_decal_normal_preset"), True)
def BM_MAP_PROPS_map_decal_normal_custom_preset_Update(self, context):
    name = "Map: Decal Pass custom preset"
    BM_LastEditedProp_Write(context, name, "map_decal_normal_custom_preset", getattr(self, "map_decal_normal_custom_preset"), True)
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
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'VERTEX_COLOR_LAYER')
def BM_MAP_PROPS_map_C_COMBINED_prefix_Update(self, context):
    name = "Map: Cycles Combined prefix"
    BM_LastEditedProp_Write(context, name, "map_C_COMBINED_prefix", getattr(self, "map_C_COMBINED_prefix"), True)
def BM_MAP_PROPS_map_C_AO_prefix_Update(self, context):
    name = "Map: Cycles AO prefix"
    BM_LastEditedProp_Write(context, name, "map_C_AO_prefix", getattr(self, "map_C_AO_prefix"), True)
def BM_MAP_PROPS_map_C_SHADOW_prefix_Update(self, context):
    name = "Map: Cycles Shadown prefix "
    BM_LastEditedProp_Write(context, name, "map_C_SHADOW_prefix", getattr(self, "map_C_SHADOW_prefix"), True)
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
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'VECTOR_DISPLACEMENT')
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
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_samples_Update(self, context):
    name = "Map: AO samples"
    BM_LastEditedProp_Write(context, name, "map_ao_samples", getattr(self, "map_ao_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_distance_Update(self, context):
    name = "Map: AO distance"
    BM_LastEditedProp_Write(context, name, "map_ao_distance", getattr(self, "map_ao_distance"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_black_point_Update(self, context):
    name = "Map: AO black point"
    BM_LastEditedProp_Write(context, name, "map_ao_black_point", getattr(self, "map_ao_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_white_point_Update(self, context):
    name = "Map: AO white point"
    BM_LastEditedProp_Write(context, name, "map_ao_white_point", getattr(self, "map_ao_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_brightness_Update(self, context):
    name = "Map: AO brightness"
    BM_LastEditedProp_Write(context, name, "map_ao_brightness", getattr(self, "map_ao_brightness"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_contrast_Update(self, context):
    name = "Map: AO contrast"
    BM_LastEditedProp_Write(context, name, "map_ao_contrast", getattr(self, "map_ao_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_opacity_Update(self, context):
    name = "Map: AO opacity"
    BM_LastEditedProp_Write(context, name, "map_ao_opacity", getattr(self, "map_ao_opacity"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_use_local_Update(self, context):
    name = "Map: AO only local"
    BM_LastEditedProp_Write(context, name, "map_ao_use_local", getattr(self, "map_ao_use_local"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_ao_use_invert_Update(self, context):
    name = "Map: AO invert"
    BM_LastEditedProp_Write(context, name, "map_ao_use_invert", getattr(self, "map_ao_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'AO')
def BM_MAP_PROPS_map_CAVITY_prefix_Update(self, context):
    name = "Map: Cavity prefix"
    BM_LastEditedProp_Write(context, name, "map_CAVITY_prefix", getattr(self, "map_CAVITY_prefix"), True)
def BM_MAP_PROPS_map_CAVITY_use_default_Update(self, context):
    name = "Map: Cavity default"
    BM_LastEditedProp_Write(context, name, "map_CAVITY_use_default", getattr(self, "map_CAVITY_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_black_point_Update(self, context):
    name = "Map: Cavity black point"
    BM_LastEditedProp_Write(context, name, "map_cavity_black_point", getattr(self, "map_cavity_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_white_point_Update(self, context):
    name = "Map: Cavity white point"
    BM_LastEditedProp_Write(context, name, "map_cavity_white_point", getattr(self, "map_cavity_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_power_Update(self, context):
    name = "Map: Cavity power"
    BM_LastEditedProp_Write(context, name, "map_cavity_power", getattr(self, "map_cavity_power"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CAVITY')
def BM_MAP_PROPS_map_cavity_use_invert_Update(self, context):
    name = "Map: Cavity invert"
    BM_LastEditedProp_Write(context, name, "map_cavity_use_invert", getattr(self, "map_cavity_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CAVITY')
def BM_MAP_PROPS_map_CURVATURE_prefix_Update(self, context):
    name = "Map: Curvature prefix"
    BM_LastEditedProp_Write(context, name, "map_CURVATURE_prefix", getattr(self, "map_CURVATURE_prefix"), True)
def BM_MAP_PROPS_map_CURVATURE_use_default_Update(self, context):
    name = "Map: Curvature default"
    BM_LastEditedProp_Write(context, name, "map_CURVATURE_use_default", getattr(self, "map_CURVATURE_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_samples_Update(self, context):
    name = "Map: Curvature samples"
    BM_LastEditedProp_Write(context, name, "map_curv_samples", getattr(self, "map_curv_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_radius_Update(self, context):
    name = "Map: Curvature radius"
    BM_LastEditedProp_Write(context, name, "map_curv_radius", getattr(self, "map_curv_radius"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_black_point_Update(self, context):
    name = "Map: Curvature black point"
    BM_LastEditedProp_Write(context, name, "map_curv_black_point", getattr(self, "map_curv_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_mid_point_Update(self, context):
    name = "Map: Curvature mid point"
    BM_LastEditedProp_Write(context, name, "map_curv_mid_point", getattr(self, "map_curv_mid_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_white_point_Update(self, context):
    name = "Map: Curvature white point"
    BM_LastEditedProp_Write(context, name, "map_curv_white_point", getattr(self, "map_curv_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_curv_body_gamma_Update(self, context):
    name = "Map: Curvature body gamma"
    BM_LastEditedProp_Write(context, name, "map_curv_body_gamma", getattr(self, "map_curv_body_gamma"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'CURVATURE')
def BM_MAP_PROPS_map_THICKNESS_prefix_Update(self, context):
    name = "Map: Thickness prefix"
    BM_LastEditedProp_Write(context, name, "map_THICKNESS_prefix", getattr(self, "map_THICKNESS_prefix"), True)
def BM_MAP_PROPS_map_THICKNESS_use_default_Update(self, context):
    name = "Map: Thickness default"
    BM_LastEditedProp_Write(context, name, "map_THICKNESS_use_default", getattr(self, "map_THICKNESS_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_samples_Update(self, context):
    name = "Map: Thickness samples"
    BM_LastEditedProp_Write(context, name, "map_thick_samples", getattr(self, "map_thick_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_distance_Update(self, context):
    name = "Map: Thickness distance"
    BM_LastEditedProp_Write(context, name, "map_thick_distance", getattr(self, "map_thick_distance"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_black_point_Update(self, context):
    name = "Map: Thickness black point"
    BM_LastEditedProp_Write(context, name, "map_thick_black_point", getattr(self, "map_thick_black_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_white_point_Update(self, context):
    name = "Map: Thickness white point"
    BM_LastEditedProp_Write(context, name, "map_thick_white_point", getattr(self, "map_thick_white_point"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_brightness_Update(self, context):
    name = "Map: Thickness brightness"
    BM_LastEditedProp_Write(context, name, "map_thick_brightness", getattr(self, "map_thick_brightness"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_contrast_Update(self, context):
    name = "Map: Thickness contrast"
    BM_LastEditedProp_Write(context, name, "map_thick_contrast", getattr(self, "map_thick_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_thick_use_invert_Update(self, context):
    name = "Map: Thickness invert"
    BM_LastEditedProp_Write(context, name, "map_thick_use_invert", getattr(self, "map_thick_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'THICKNESS')
def BM_MAP_PROPS_map_ID_prefix_Update(self, context):
    name = "Map: ID prefix"
    BM_LastEditedProp_Write(context, name, "map_ID_prefix", getattr(self, "map_ID_prefix"), True)
def BM_MAP_PROPS_map_matid_data_Update(self, context):
    name = "Map: ID data"
    BM_LastEditedProp_Write(context, name, "map_matid_data", getattr(self, "map_matid_data"), True)
def BM_MAP_PROPS_map_matid_vertex_groups_name_contains_Update(self, context):
    name = "Map: ID vertex groups name contains"
    BM_LastEditedProp_Write(context, name, "map_matid_vertex_groups_name_contains", getattr(self, "map_matid_vertex_groups_name_contains"), True)
def BM_MAP_PROPS_map_matid_algorithm_Update(self, context):
    name = "Map: ID algorithm"
    BM_LastEditedProp_Write(context, name, "map_matid_algorithm", getattr(self, "map_matid_algorithm"), True)
def BM_MAP_PROPS_map_MASK_prefix_Update(self, context):
    name = "Map: Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_MASK_prefix", getattr(self, "map_MASK_prefix"), True)
def BM_MAP_PROPS_map_mask_data_Update(self, context):
    name = "Map: Mask data"
    BM_LastEditedProp_Write(context, name, "map_mask_data", getattr(self, "map_mask_data"), True)
def BM_MAP_PROPS_map_mask_vertex_groups_name_contains_Update(self, context):
    name = "Map: Mask vertex groups name contains"
    BM_LastEditedProp_Write(context, name, "map_mask_vertex_groups_name_contains", getattr(self, "map_mask_vertex_groups_name_contains"), True)
def BM_MAP_PROPS_map_mask_materials_name_contains_Update(self, context):
    name = "Map: Mask materials name contains"
    BM_LastEditedProp_Write(context, name, "map_mask_materials_name_contains", getattr(self, "map_mask_materials_name_contains"), True)
def BM_MAP_PROPS_map_mask_color1_Update(self, context):
    name = "Map: Mask color1"
    BM_LastEditedProp_Write(context, name, "map_mask_color1", getattr(self, "map_mask_color1"), True)
def BM_MAP_PROPS_map_mask_color2_Update(self, context):
    name = "Map: Mask color2"
    BM_LastEditedProp_Write(context, name, "map_mask_color2", getattr(self, "map_mask_color2"), True)
def BM_MAP_PROPS_map_mask_use_invert_Update(self, context):
    name = "Map: Mask invert"
    BM_LastEditedProp_Write(context, name, "map_mask_use_invert", getattr(self, "map_mask_use_invert"), True)
def BM_MAP_PROPS_map_XYZMASK_prefix_Update(self, context):
    name = "Map: XYZ Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_XYZMASK_prefix", getattr(self, "map_XYZMASK_prefix"), True)
def BM_MAP_PROPS_map_XYZMASK_use_default_Update(self, context):
    name = "Map: XYZ Mask default"
    BM_LastEditedProp_Write(context, name, "map_XYZMASK_use_default", getattr(self, "map_XYZMASK_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_x_Update(self, context):
    name = "Map: XYZ Mask X"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_x", getattr(self, "map_xyzmask_use_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_y_Update(self, context):
    name = "Map: XYZ Mask Y"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_y", getattr(self, "map_xyzmask_use_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_z_Update(self, context):
    name = "Map: XYZ Mask Z"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_z", getattr(self, "map_xyzmask_use_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_coverage_Update(self, context):
    name = "Map: XYZ Mask coverage"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_coverage", getattr(self, "map_xyzmask_coverage"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_saturation_Update(self, context):
    name = "Map: XYZ Mask saturation"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_saturation", getattr(self, "map_xyzmask_saturation"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_opacity_Update(self, context):
    name = "Map: XYZ Mask opacity"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_opacity", getattr(self, "map_xyzmask_opacity"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_xyzmask_use_invert_Update(self, context):
    name = "Map: XYZ Mask invert"
    BM_LastEditedProp_Write(context, name, "map_xyzmask_use_invert", getattr(self, "map_xyzmask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'XYZMASK')
def BM_MAP_PROPS_map_GRADIENT_prefix_Update(self, context):
    name = "Map: Gradient Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_GRADIENT_prefix", getattr(self, "map_GRADIENT_prefix"), True)
def BM_MAP_PROPS_map_GRADIENT_use_default_Update(self, context):
    name = "Map: Gradient Mask default"
    BM_LastEditedProp_Write(context, name, "map_GRADIENT_use_default", getattr(self, "map_GRADIENT_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_type_Update(self, context):
    name = "Map: Gradient Mask type"
    BM_LastEditedProp_Write(context, name, "map_gmask_type", getattr(self, "map_gmask_type"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_location_x_Update(self, context):
    name = "Map: Gradient Mask location x"
    BM_LastEditedProp_Write(context, name, "map_gmask_location_x", getattr(self, "map_gmask_location_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_location_y_Update(self, context):
    name = "Map: Gradient Mask location y"
    BM_LastEditedProp_Write(context, name, "map_gmask_location_y", getattr(self, "map_gmask_location_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_location_z_Update(self, context):
    name = "Map: Gradient Mask location z"
    BM_LastEditedProp_Write(context, name, "map_gmask_location_z", getattr(self, "map_gmask_location_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_rotation_x_Update(self, context):
    name = "Map: Gradient Mask rotation x"
    BM_LastEditedProp_Write(context, name, "map_gmask_rotation_x", getattr(self, "map_gmask_rotation_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_rotation_y_Update(self, context):
    name = "Map: Gradient Mask rotation y"
    BM_LastEditedProp_Write(context, name, "map_gmask_rotation_y", getattr(self, "map_gmask_rotation_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_rotation_z_Update(self, context):
    name = "Map: Gradient Mask rotation z"
    BM_LastEditedProp_Write(context, name, "map_gmask_rotation_z", getattr(self, "map_gmask_rotation_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_scale_x_Update(self, context):
    name = "Map: Gradient Mask scale x"
    BM_LastEditedProp_Write(context, name, "map_gmask_scale_x", getattr(self, "map_gmask_scale_x"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_scale_y_Update(self, context):
    name = "Map: Gradient Mask scale y"
    BM_LastEditedProp_Write(context, name, "map_gmask_scale_y", getattr(self, "map_gmask_scale_y"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_scale_z_Update(self, context):
    name = "Map: Gradient Mask scale z"
    BM_LastEditedProp_Write(context, name, "map_gmask_scale_z", getattr(self, "map_gmask_scale_z"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_coverage_Update(self, context):
    name = "Map: Gradient Mask coverage"
    BM_LastEditedProp_Write(context, name, "map_gmask_coverage", getattr(self, "map_gmask_coverage"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_contrast_Update(self, context):
    name = "Map: Gradient Mask contrast"
    BM_LastEditedProp_Write(context, name, "map_gmask_contrast", getattr(self, "map_gmask_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_saturation_Update(self, context):
    name = "Map: Gradient Mask saturation"
    BM_LastEditedProp_Write(context, name, "map_gmask_saturation", getattr(self, "map_gmask_saturation"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_opacity_Update(self, context):
    name = "Map: Gradient Mask opacity"
    BM_LastEditedProp_Write(context, name, "map_gmask_opacity", getattr(self, "map_gmask_opacity"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_gmask_use_invert_Update(self, context):
    name = "Map: Gradient Mask invert"
    BM_LastEditedProp_Write(context, name, "map_gmask_use_invert", getattr(self, "map_gmask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'GRADIENT')
def BM_MAP_PROPS_map_EDGE_prefix_Update(self, context):
    name = "Map: Edge Mask prefix"
    BM_LastEditedProp_Write(context, name, "map_EDGE_prefix", getattr(self, "map_EDGE_prefix"), True)
def BM_MAP_PROPS_map_EDGE_use_default_Update(self, context):
    name = "Map: Edge Mask default"
    BM_LastEditedProp_Write(context, name, "map_EDGE_use_default", getattr(self, "map_EDGE_use_default"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_samples_Update(self, context):
    name = "Map: Edge Mask samples"
    BM_LastEditedProp_Write(context, name, "map_edgemask_samples", getattr(self, "map_edgemask_samples"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_radius_Update(self, context):
    name = "Map: Edge Mask radius"
    BM_LastEditedProp_Write(context, name, "map_edgemask_radius", getattr(self, "map_edgemask_radius"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_edge_contrast_Update(self, context):
    name = "Map: Edge Mask edge contrast"
    BM_LastEditedProp_Write(context, name, "map_edgemask_edge_contrast", getattr(self, "map_edgemask_edge_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_body_contrast_Update(self, context):
    name = "Map: Edge Mask body contrast"
    BM_LastEditedProp_Write(context, name, "map_edgemask_body_contrast", getattr(self, "map_edgemask_body_contrast"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'EDGE')
def BM_MAP_PROPS_map_edgemask_use_invert_Update(self, context):
    name = "Map: Edge Mask invert"
    BM_LastEditedProp_Write(context, name, "map_edgemask_use_invert", getattr(self, "map_edgemask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'EDGE')
def BM_MAP_PROPS_map_WIREFRAME_prefix_Update(self, context):
    name = "Map: Wireframe prefix"
    BM_LastEditedProp_Write(context, name, "map_WIREFRAME_prefix", getattr(self, "map_WIREFRAME_prefix"), True)
def BM_MAP_PROPS_map_wireframemask_line_thickness_Update(self, context):
    name = "Map: Wireframe Mask line thickness"
    BM_LastEditedProp_Write(context, name, "map_wireframemask_line_thickness", getattr(self, "map_wireframemask_line_thickness"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'WIREFRAME')
def BM_MAP_PROPS_map_wireframemask_use_invert_Update(self, context):
    name = "Map: Wireframe Mask invert"
    BM_LastEditedProp_Write(context, name, "map_wireframemask_use_invert", getattr(self, "map_wireframemask_use_invert"), True)
    BM_MAP_PROPS_MapPreview_CustomNodes_Update(context, 'WIREFRAME')

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
def BM_ITEM_PROPS_csh_use_lowpoly_reset_normals_Update(self, context):
    name = "Object Shading: Reset lowpoly normals"
    BM_LastEditedProp_Write(context, name, "csh_use_lowpoly_reset_normals", getattr(self, "csh_use_lowpoly_reset_normals"), False)
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
def BM_ITEM_PROPS_csh_use_highpoly_reset_normals_Update(self, context):
    name = "Object Shading: Reset highpoly normals"
    BM_LastEditedProp_Write(context, name, "csh_use_highpoly_reset_normals", getattr(self, "csh_use_highpoly_reset_normals"), False)
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

###############################################################
###############################################################

# when removing these funcs, remove all their calls, some of which I saw in operators
def BM_ITEM_UseTargetUpdate(self, context):
    return

    if not self.use_target:
        for index, item in enumerate(context.scene.bm_aol):
            if item.use_source and item.source_name == self.object_pointer.name:
                self.source = 'NONE'
                item.use_source = False
                item.source_name = ""
                break
    else:
        BM_ITEM_PROPS_hl_highpoly_Update(self, context)

    #BM_ITEM_RemoveLocalPreviews(self, context)

def BM_ITEM_OverwriteUpdate(self, context):
    return

    if self.use_overwrite:
        for index, map in enumerate(self.maps):
            map.bake_target = self.overwrite_bake_target
            map.use_denoise = self.overwrite_use_denoise
            map.file_format = self.overwrite_file_format
            map.res_enum = self.overwrite_res_enum
            map.res_height = self.overwrite_res_height
            map.res_weight = self.overwrite_res_width
            map.margin = self.overwrite_margin
            map.margin_type = self.overwrite_margin_type
            map.use_32bit = self.overwrite_use_32bit
            map.use_alpha = self.overwrite_use_alpha
            map.udim_start_tile = self.overwrite_udim_start_tile
            map.udim_end_tile = self.overwrite_udim_end_tile

def BM_ITEM_BatchNameUpdate(self, context):
    try:
        if "item" not in self.batch_name:
            self.batch_name = f"item_{self.batch_name}"

        args = ['index',
                'item',
                'sourcetarget',
                'uvpacked',
                'map',
                'res',
                'float',
                'alpha']

        args_used = [arg for arg in args if arg in self.batch_name]
        args_names_starters = [arg[0] for arg in args_used]
        batch_name_new = ""

        for start_index in range(len(self.batch_name)):

            # if the itered string won't start on any of the symbols in args -> skip it to reduce number of iterations
            if self.batch_name[start_index] not in args_names_starters:
                continue

            # to see how the algo works, type print(self.batch_name[start_index:end_index]) here
            for end_index in range(start_index, len(self.batch_name) + 1): # len() + 1, because we need to check the last symbol

                if self.batch_name[start_index:end_index] in args_used: # if itered srting is an arg -> add it to the batch_name_new
                    batch_name_new += "{}_".format(self.batch_name[start_index:end_index])
                    break

        batch_name_new = batch_name_new[:(len(batch_name_new) - 1)] # remove last '_'

        if self.batch_name != batch_name_new:
            self.batch_name = batch_name_new

    except RecursionError:
        pass

def BM_MAP_MaterialUpdate(self, material, map_index):
    return

    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes_source = [#AO
                    ('BM_AmbientOcclusion',
                     'BM_ValToRGB',
                     'BM_MixRGB',
                     'BM_BrightContrast',
                     'BM_Invert'),
                    #Cavity
                    ('BM_ValToRGB',
                     'BM_Math',
                     'BM_Invert'),
                    #Curvature
                    ('BM_Bevel',
                     'BM_MapRange',
                     'BM_Invert'),
                    #Thickness
                    ('BM_AmbientOcclusion',
                     'BM_MapRange',
                     'BM_ValToRGB',
                     'BM_Invert'),
                    #NormalMask
                    ('BM_SeparateXYZ',
                     'BM_VectorMath',
                     'BM_VectorMath.001',
                     'BM_VectorMath.002',
                     'BM_MapRange',
                     'BM_MixRGB'),
                    #GradientMask
                    ('BM_Mapping',
                     'BM_TexGradient',
                     'BM_MapRange',
                     'BM_MixRGB',
                     'BM_HueSaturation',
                     'BM_Invert')]

    bm_nodes = nodes_source[map_index]
    #AO
    if map_index == 0:
        if self.ao_use_default:
            samples = 16
            distance = 1
            only_local = False
            black_point = 0
            white_point = 0.8
            opacity = 0.67
            brightness = -0.3
            contrast = 0.3
            invert = 0
        else:
            samples = self.ao_samples
            distance = self.ao_distance
            only_local = self.ao_use_local
            black_point = self.ao_black_point
            white_point = self.ao_white_point
            opacity = self.ao_opacity
            brightness = self.ao_brightness
            contrast = self.ao_contrast
            invert = self.ao_use_invert
        nodes[bm_nodes[0]].samples = samples
        nodes[bm_nodes[0]].inputs[1].default_value = distance
        nodes[bm_nodes[0]].only_local = only_local
        nodes[bm_nodes[1]].color_ramp.elements[0].position = black_point
        nodes[bm_nodes[1]].color_ramp.elements[1].position = white_point
        nodes[bm_nodes[2]].inputs[0].default_value = opacity
        nodes[bm_nodes[3]].inputs[1].default_value = brightness
        nodes[bm_nodes[3]].inputs[2].default_value = contrast
        nodes[bm_nodes[4]].inputs[0].default_value = invert

    #Cavity
    if map_index == 1:
        if self.cavity_use_default:
            black_point = 0
            white_point = 1
            power = 2.5
            invert = 0
        else:
            black_point = self.cavity_black_point
            white_point = self.cavity_white_point
            power = self.cavity_power
            invert = self.cavity_use_invert
        nodes[bm_nodes[0]].color_ramp.elements[0].position = black_point
        nodes[bm_nodes[0]].color_ramp.elements[1].position = white_point
        nodes[bm_nodes[1]].inputs[1].default_value = power
        nodes[bm_nodes[2]].inputs[0].default_value = invert

    #Curvature
    if map_index == 2:
        if self.curv_use_default:
            samples = 4
            radius = 0.02
            edge_contrast = 0
            body_contrast = 1
            invert = 1
        else:
            samples = self.curv_samples
            radius = self.curv_radius
            edge_contrast = self.curv_edge_contrast
            body_contrast = self.curv_body_contrast
            invert = self.curv_use_invert
        nodes[bm_nodes[0]].samples = samples
        nodes[bm_nodes[0]].inputs[0].default_value = radius
        nodes[bm_nodes[1]].inputs[1].default_value = edge_contrast
        nodes[bm_nodes[1]].inputs[4].default_value = body_contrast
        nodes[bm_nodes[2]].inputs[0].default_value = invert

    #Thickness
    if map_index == 3:
        if self.thick_use_default:
            samples = 16
            distance = 1
            black_point = 0
            white_point = 1
            brightness = 1
            contrast = 0
            invert = 0
        else:
            samples = self.thick_samples
            distance = self.thick_distance
            black_point = self.thick_black_point
            white_point = self.thick_white_point
            brightness = self.thick_brightness
            contrast = self.thick_contrast
            invert = self.thick_use_invert
        nodes[bm_nodes[0]].samples = samples
        nodes[bm_nodes[0]].inputs[1].default_value = distance
        nodes[bm_nodes[1]].inputs[1].default_value = contrast
        nodes[bm_nodes[1]].inputs[4].default_value = brightness
        nodes[bm_nodes[2]].color_ramp.elements[0].position = black_point
        nodes[bm_nodes[2]].color_ramp.elements[1].position = white_point
        nodes[bm_nodes[3]].inputs[0].default_value = invert
        
    #NormalMask
    if map_index == 4:
        if self.xyzmask_use_default:
            coverage = 0
            saturation = 1
            opacity = 1
            invert = 1
        else:
            coverage = self.xyzmask_coverage
            saturation = self.xyzmask_saturation
            opacity = self.xyzmask_opacity
            invert = self.xyzmask_use_invert
        for i in range(3):
            nodes[bm_nodes[3]].inputs[1].default_value[i] = invert
        nodes[bm_nodes[4]].inputs[1].default_value = coverage
        nodes[bm_nodes[4]].inputs[4].default_value = saturation
        nodes[bm_nodes[5]].inputs[0].default_value = opacity
        if self.xyzmask_use_x:
            links.new(nodes[bm_nodes[0]].outputs[0], nodes[bm_nodes[1]].inputs[0])
        else:
            if len(nodes[bm_nodes[0]].outputs[0].links):
                links.remove(nodes[bm_nodes[0]].outputs[0].links[0])
        if self.xyzmask_use_y:
            links.new(nodes[bm_nodes[0]].outputs[1], nodes[bm_nodes[1]].inputs[1])
        else:
            if len(nodes[bm_nodes[0]].outputs[1].links):
                links.remove(nodes[bm_nodes[0]].outputs[1].links[0])
        if self.xyzmask_use_z:
            links.new(nodes[bm_nodes[0]].outputs[2], nodes[bm_nodes[2]].inputs[1])
        else:
            if len(nodes[bm_nodes[0]].outputs[2].links):
                links.remove(nodes[bm_nodes[0]].outputs[2].links[0])

    #GradientMask
    if map_index == 5:
        if self.gmask_use_default:
            type = 'LINEAR'
            #mapping = [[0, 0, 0], [0, 0, 0], [1, 1, 1]]
            coverage = 0
            contrast = 1
            saturation = 1
            opacity = 1
            invert = 0
        else:
            type = self.gmask_type
            coverage = self.gmask_coverage
            contrast = self.gmask_contrast
            saturation = self.gmask_saturation
            opacity = self.gmask_opacity
            invert = self.gmask_use_invert 
        # mapping can be changed no matter the use_default state
        mapping = [[self.gmask_location_x, self.gmask_location_y, self.gmask_location_z],
                   [self.gmask_rotation_x, self.gmask_rotation_y, self.gmask_rotation_z],
                   [self.gmask_scale_x, self.gmask_scale_y, self.gmask_scale_z]]
        for i in range(1, 4):
            for j in range(3):
                nodes[bm_nodes[0]].inputs[i].default_value[j] = mapping[i - 1][j]
        nodes[bm_nodes[1]].gradient_type = type
        nodes[bm_nodes[2]].inputs[1].default_value = coverage
        nodes[bm_nodes[2]].inputs[4].default_value = contrast
        nodes[bm_nodes[3]].inputs[0].default_value = opacity
        nodes[bm_nodes[4]].inputs[2].default_value = saturation
        nodes[bm_nodes[5]].inputs[0].default_value = invert      

def BM_MAP_Preview_SetNodes(self, context, material, map_index, use_preview):
    return


    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes_source = [#AO
                    ('ShaderNodeAmbientOcclusion',
                     'ShaderNodeValToRGB',
                     'ShaderNodeMixRGB',
                     'ShaderNodeBrightContrast',
                     'ShaderNodeInvert',
                     'ShaderNodeEmission',
                     'ShaderNodeOutputMaterial'),
                    #Cavity
                    ('ShaderNodeNewGeometry',
                     'ShaderNodeValToRGB',
                     'ShaderNodeMath',
                     'ShaderNodeInvert',
                     'ShaderNodeEmission',
                     'ShaderNodeOutputMaterial'),
                    #Curvature
                    ('ShaderNodeBevel',
                     'ShaderNodeNewGeometry',
                     'ShaderNodeVectorMath',
                     'ShaderNodeMapRange',
                     'ShaderNodeInvert',
                     'ShaderNodeEmission',
                     'ShaderNodeOutputMaterial'),
                    #Thickness
                    ('ShaderNodeAmbientOcclusion',
                     'ShaderNodeMapRange',
                     'ShaderNodeValToRGB',
                     'ShaderNodeInvert',
                     'ShaderNodeEmission',
                     'ShaderNodeOutputMaterial'),
                    #NormalMask
                    ('ShaderNodeNewGeometry',
                     'ShaderNodeSeparateXYZ',
                     'ShaderNodeVectorMath',
                     'ShaderNodeVectorMath',
                     'ShaderNodeVectorMath',
                     'ShaderNodeMapRange',
                     'ShaderNodeMixRGB',
                     'ShaderNodeEmission',
                     'ShaderNodeOutputMaterial'),
                    #GradientMask
                    ('ShaderNodeTexCoord',
                     'ShaderNodeMapping',
                     'ShaderNodeTexGradient',
                     'ShaderNodeMapRange',
                     'ShaderNodeMixRGB',
                     'ShaderNodeHueSaturation',
                     'ShaderNodeInvert',
                     'ShaderNodeEmission',
                     'ShaderNodeOutputMaterial')]

    location = 1000000
    for node in nodes_source[map_index]:
        new_node = nodes.new(node)
        new_node.name = "BM_" + node[10:]
        new_node.location = (location, 0)#1000000)
        location += 300

    #AO
    if map_index == 0:
        nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
        nodes['BM_MixRGB'].inputs[1].default_value = (1, 1, 1, 1)
        nodes['BM_OutputMaterial'].target = 'CYCLES'

        links.new(nodes['BM_AmbientOcclusion'].outputs[1], nodes['BM_ValToRGB'].inputs[0])
        links.new(nodes['BM_ValToRGB'].outputs[0], nodes['BM_MixRGB'].inputs[2])
        links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_BrightContrast'].inputs[0])
        links.new(nodes['BM_BrightContrast'].outputs[0], nodes['BM_Invert'].inputs[1])
        links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
        links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

    #Cavity
    if map_index == 1:
        nodes['BM_Math'].operation = 'POWER'
        nodes['BM_OutputMaterial'].target = 'CYCLES'

        links.new(nodes['BM_NewGeometry'].outputs[7], nodes['BM_ValToRGB'].inputs[0])
        links.new(nodes['BM_ValToRGB'].outputs[0], nodes['BM_Math'].inputs[0])
        links.new(nodes['BM_Math'].outputs[0], nodes['BM_Invert'].inputs[1])
        links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
        links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

    #Curvature
    if map_index == 2:
        nodes['BM_VectorMath'].operation = 'DOT_PRODUCT'
        nodes['BM_OutputMaterial'].target = 'CYCLES'

        links.new(nodes['BM_Bevel'].outputs[0], nodes['BM_VectorMath'].inputs[0])
        links.new(nodes['BM_NewGeometry'].outputs[1], nodes['BM_VectorMath'].inputs[1])
        links.new(nodes['BM_VectorMath'].outputs[1], nodes['BM_MapRange'].inputs[0])
        links.new(nodes['BM_MapRange'].outputs[0], nodes['BM_Invert'].inputs[1])
        links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
        links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

    #Thickness
    if map_index == 3:
        nodes['BM_AmbientOcclusion'].inside = True
        nodes['BM_OutputMaterial'].target = 'CYCLES'

        links.new(nodes['BM_AmbientOcclusion'].outputs[1], nodes['BM_MapRange'].inputs[0])
        links.new(nodes['BM_MapRange'].outputs[0], nodes['BM_ValToRGB'].inputs[0])
        links.new(nodes['BM_ValToRGB'].outputs[0], nodes['BM_Invert'].inputs[1])
        links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
        links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

    #NormalMask
    if map_index == 4:
        nodes['BM_VectorMath.002'].operation = 'MULTIPLY'
        nodes['BM_MixRGB'].inputs[1].default_value = (0, 0, 0, 0)
        nodes['BM_OutputMaterial'].target = 'CYCLES'

        links.new(nodes['BM_NewGeometry'].outputs[1], nodes['BM_SeparateXYZ'].inputs[0])
        links.new(nodes['BM_VectorMath'].outputs[0], nodes['BM_VectorMath.001'].inputs[0])
        links.new(nodes['BM_VectorMath.001'].outputs[0], nodes['BM_VectorMath.002'].inputs[0])
        links.new(nodes['BM_VectorMath.002'].outputs[0], nodes['BM_MapRange'].inputs[0])
        links.new(nodes['BM_MapRange'].outputs[0], nodes['BM_MixRGB'].inputs[2])
        links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_Emission'].inputs[0])
        links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

    #GradientMask
    if map_index == 5:
        nodes['BM_MixRGB'].inputs[1].default_value = (0, 0, 0, 0)
        nodes['BM_OutputMaterial'].target = 'CYCLES'
        
        links.new(nodes['BM_TexCoord'].outputs[0], nodes['BM_Mapping'].inputs[0])
        links.new(nodes['BM_Mapping'].outputs[0], nodes['BM_TexGradient'].inputs[0])
        links.new(nodes['BM_TexGradient'].outputs[0], nodes['BM_MapRange'].inputs[0])
        links.new(nodes['BM_MapRange'].outputs[0], nodes['BM_MixRGB'].inputs[2])
        links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_HueSaturation'].inputs[4])
        links.new(nodes['BM_HueSaturation'].outputs[0], nodes['BM_Invert'].inputs[1])
        links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
        links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

    if use_preview:
        if context.scene.render.engine != 'CYCLES':
            self.report({'INFO'}, BM_Labels.INFO_MAP_PREVIEWNOTCYCLES)

        for node in nodes:
            if node.type == 'OUTPUT_MATERIAL' and node.name.find('BM_') == -1:
                node.target = 'ALL'

        nodes['BM_OutputMaterial'].select = True
        nodes.active = nodes['BM_OutputMaterial']

    BM_MAP_MaterialUpdate(self, material, map_index)

def BM_MAP_Preview_SetMaterial(self, context, map_index):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]

    maps = ['BM_AO_Preview', 'BM_Cavity_Preview', 'BM_Curvature_Preview',
            'BM_Thickness_Preview', 'BM_NormalMask_Preview', 'BM_GradientMask_Preview']

    # removing NoneType materials
    for index in range(len(item.object_pointer.data.materials))[::-1]:
        if item.object_pointer.data.materials[index] is None:
            item.object_pointer.data.materials.pop(index = index)

    # set bm preview nodes for each mat
    if len(item.object_pointer.data.materials):
        for mat in item.object_pointer.data.materials:
            BM_MAP_Preview_SetNodes(self, context, mat, map_index, True)
    else:
        new_mat = bpy.data.materials.new(name = maps[map_index])
        item.object_pointer.data.materials.append(new_mat)
        BM_MAP_Preview_SetNodes(self, context, new_mat, map_index, True)

def BM_MAP_Preview_CleanMaterial(context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    
    # remove nodes named with 'BM_' from item materials
    for mat in item.object_pointer.data.materials:
        if mat is None:
            continue

        mat.use_nodes = True
        for node in mat.node_tree.nodes:
            if node.name.find('BM_') != -1:
                mat.node_tree.nodes.remove(node)

    # if item has source, remove the nodes from its mats as well
    # as long as if ther is a source, preview assigns preview to it.
    if item.use_target and item.source != 'NONE':
        source_item = context.scene.bm_aol[int(item.source)]

        for mat in source_item.object_pointer.data.materials:
            if mat is None:
                continue

            mat.use_nodes = True
            for node in mat.node_tree.nodes:
                if node.name.find('BM_') != -1:
                    mat.node_tree.nodes.remove(node)

def BM_MAP_Preview_LocalUpdate(self, context, map_index):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]

    props = ['ao_use_preview', 'cavity_use_preview', 'curv_use_preview',
             'thick_use_preview', 'xyzmask_use_preview', 'gmask_use_preview']
    
    for index, map in enumerate(item.maps):
        for i in range(len(props)):
            if i != map_index:
                setattr(map, props[i], False)

def BM_MAP_Preview_AO(self, context):
    return

    BM_MAP_Preview_CleanMaterial(context)
    if self.ao_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 0) 
        BM_MAP_Preview_SetMaterial(self, context, 0)

def BM_MAP_Preview_Cavity(self, context):
    return

    BM_MAP_Preview_CleanMaterial(context)
    if self.cavity_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 1)
        BM_MAP_Preview_SetMaterial(self, context, 1)

def BM_MAP_Preview_Curvature(self, context):
    return

    BM_MAP_Preview_CleanMaterial(context)
    if self.curv_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 2)
        BM_MAP_Preview_SetMaterial(self, context, 2)

def BM_MAP_Preview_Thickness(self, context):
    return

    BM_MAP_Preview_CleanMaterial(context)
    if self.thick_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 3)
        BM_MAP_Preview_SetMaterial(self, context, 3)

def BM_MAP_Preview_NormalMask(self, context):
    return

    BM_MAP_Preview_CleanMaterial(context)
    if self.xyzmask_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 4)
        BM_MAP_Preview_SetMaterial(self, context, 4)

def BM_MAP_Preview_GradientMask(self, context):
    return

    BM_MAP_Preview_CleanMaterial(context)
    if self.gmask_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 5)
        BM_MAP_Preview_SetMaterial(self, context, 5)

def BM_MAP_AO_MaterialUpdate(self, context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]

    if self.ao_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 0)
            
def BM_MAP_Cavity_MaterialUpdate(self, context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.cavity_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 1)         

def BM_MAP_Curvature_MaterialUpdate(self, context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.curv_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 2)
            
def BM_MAP_Thickness_MaterialUpdate(self, context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.thick_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 3)          

def BM_MAP_XYZMask_MaterialUpdate(self, context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.xyzmask_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 4)       

def BM_MAP_GradientMask_MaterialUpdate(self, context):
    return

    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.gmask_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 5)

def BM_ITEM_RemoveLocalPreviews(self, context):
    return

    props = ['ao_use_preview', 'cavity_use_preview', 'curv_use_preview',
             'thick_use_preview', 'xyzmask_use_preview', 'gmask_use_preview']

    #for item_index, item in enumerate(context.scene.bm_aol):
    item = context.scene.bm_aol[context.scene.bm_props.global_active_index]

    for index, map in enumerate(item.maps):
        for i in range(len(props)):
            setattr(map, props[i], False)

def BM_MAP_AffectBySouce_Update(self, context):
    return 

    props = ['ao_use_preview', 'cavity_use_preview', 'curv_use_preview',
             'thick_use_preview', 'xyzmask_use_preview', 'gmask_use_preview']

    # if there is any preview True in props -> update it (set false, set true)
    try:
        active_preview = [prop for prop in props if getattr(self, prop) is True][0]
    except:
        return

    setattr(self, active_preview, False)
    setattr(self, active_preview, True)

# auto set subdiv_levels -> not implemented
def BM_MAP_AutoSetSubdivLevels(self, context):
    return 

    try:
        item = context.scene.bm_aol[context.scene.bm_props.global_active_index]
        subdiv_levels = 1

        if item.use_target and item.source != 'NONE' and self.use_source_target:
            item_poly_count = len(item.object_pointer.data.polygons)
            source_poly_count = len(context.scene.bm_aol[int(item.source)].object_pointer.data.polygons)

            while subdiv_levels < 10 and (item_poly_count * 4 ** subdiv_levels) < source_poly_count:
                subdiv_levels += 1

        if self.displacement_subdiv_levels != subdiv_levels:
            self.displacement_subdiv_levels = subdiv_levels

    except RecursionError:
        pass
