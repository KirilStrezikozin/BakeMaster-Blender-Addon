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

def BM_Table_of_Objects_NameMatching_GetNameChunks(chunks: list, combine_type: str):
    lowpoly_prefix_raw = "low"
    highpoly_prefix_raw = "high"
    cage_prefix_raw = "cage"
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
    NameChunks = BM_Table_of_Objects_NameMatching_GenerateNameChunks
    GetChunks = BM_Table_of_Objects_NameMatching_GetNameChunks
    Intersaction = BM_Table_of_Objects_NameMatching_IndexesIntersaction
    CombineToRaw = BM_Table_of_Objects_NameMatching_CombineToRaw
    CombineGroups = BM_Table_of_Objects_NameMatching_CombineGroups
    lowpoly_prefix_raw = "low"
    highpoly_prefix_raw = "high"
    cage_prefix_raw = "cage"
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
            root_name = GetChunks(object_name_chunked, 'ROOT')
            tale_name = GetChunks(object_name_chunked, 'TALE')

            # find any objects in the input_objects with the same root_name and tale_name
            pairs = [object_name]
            for object_name_pair in objects_names_input:
                if object_name_pair in used_obj_names:
                    continue
                pair_name_chunked = NameChunks(object_name_pair)
                pair_root = GetChunks(pair_name_chunked, 'ROOT')
                pair_tale = GetChunks(pair_name_chunked, 'TALE')
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
                root_name = GetChunks(object_name_chunked, 'ROOT')

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
    lowpoly_prefix_raw = "low"
    highpoly_prefix_raw = "high"
    cage_prefix_raw = "cage"

    # trash texsets
    to_remove = []
    for index, item in enumerate(context.scene.bm_props.global_texturesets_table):
        to_remove.append(index)
    for index in to_remove[::-1]:
        context.scene.bm_props.global_texturesets_table.remove(index)

    if self.global_use_name_matching is True:
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
            for index, subitem in enumerate(context.scene.bm_table_of_objects):
                if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.hl_is_lowpoly:
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

def BM_ITEM_PROPS_bake_batchname_Update(self, context):
    # DEMO: no refresh on add maps, maps props update, no refresh on obj add,
    # TODO: blender preferences to set what to write for some batch name args
    # update batchname preview
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
            for map_index, map_pass in enumerate(container.global_maps):
                # DEMO
                if any([chnlpack.global_r_map == str(map_index), chnlpack.global_g_map == str(map_index), chnlpack.global_b_map == str(map_index), chnlpack.global_a_map == str(map_index)]):
                    return chnlpack.global_channelpack_name
        return None
    
    def get_texsetname(container):
        if not any([container.nm_is_universal_container, container.nm_is_local_container, context.scene.bm_props.global_use_name_matching]):
            container_name = container.global_object_name
        else:
            container_name = container.nm_container_name
        
        if container.global_is_included_in_texset:
            return None
        for texset in context.scene.global_texturesets_table:
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
        elif map_pass.out_res == 'TEXEL':
            # DEMO
            return "1891"
        else:
            return map_pass.out_res
    
    def get_mapnormal(map_pass):
        if map.map_normal_preset != 'CUSTOM':
            return map.map_normal_preset
        else:
            return map.map_normal_custom_preset
    
    object = BM_Object_Get(context)[0]
    if len(object.global_maps) == 0:
        self.bake_batchname_preview = "*Object has no Maps*"
        return
    map = object.global_maps[object.global_maps_active_index]

    gen_keywords_values = {
        "$objectindex" : context.scene.bm_props.global_active_index,
        "$objectname" : get_objectname(object),
        "$containername" : get_containername(object),
        "$packname" : get_packname(object),
        "$texsetname" : get_texsetname(object),
        "$mapindex" : map.global_map_index,
        "$mapname" : map.global_map_prefix, # DEMO
        "$mapres" : get_mapres(map),
        "$mapbit" : "32bit" if map.out_use_32bit else "8bit", # DEMO
        "$maptrans" : "transbg" if map.out_use_transbg else "", # DEMO
        "$mapssaa" : map.out_super_sampling_aa,
        "$mapsamples" : map.out_samples,
        "$mapdenoise" : "denoised" if map.out_use_denoise else "", # DEMO
        "$mapnormal" : get_mapnormal(map),
        "$mapuv" : map.uv_active_layer,
        "$engine" : object.bake_device,
        "$autouv" : "autouv" if map.uv_use_auto_unwrap else "" # DEMO
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
            # no keyword found but found $, aborting finding keyword and addin temp_preview to preview
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

    self.bake_batchname_preview = preview

def BM_ITEM_PROPS_bake_batchname_use_caps_Update(self, context):
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
### hl Props Funcs ###
###############################################################
def BM_ITEM_PROPS_hl_use_unique_per_map_Update(self, context):
    object = BM_Object_Get(context)[0]
    if object.hl_use_unique_per_map and len(object.global_maps):
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
        
        if len(object.hl_highpoly_table):
            set_highpoly = True
            BM_ITEM_PROPS_hl_use_unique_per_map_Update_TrashHighpolies(object, object, context)

        for map_index, map in enumerate(object.global_maps):
            object.global_maps_active_index = map_index
            for key in data:
                setattr(map, key, data[key])

            if set_highpoly:
                for index, key in enumerate(highpoly_data):
                    new_highpoly = map.hl_highpoly_table.add()
                    new_highpoly.global_item_index = index + 1
                    BM_ITEM_PROPS_hl_add_highpoly_Update(new_highpoly, context)
                    new_highpoly.global_object_name = key
                    map.hl_highpoly_table_active_index = len(map.hl_highpoly_table) - 1
    
    elif object.hl_use_unique_per_map is False:
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
    active_object = BM_Object_Get(context)[0]
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
        if any([object.hl_is_cage, object.hl_is_lowpoly, object.hl_is_highpoly]) or index == self.hl_cage_object_index:#object.global_object_name == active_object.global_object_name:
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
    active_object = BM_Object_Get(context)[0]
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
        if any([object.hl_is_cage, object.hl_is_lowpoly, object.hl_is_highpoly]) or index == self.global_highpoly_object_index:
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

def BM_ITEM_PROPS_hl_remove_highpoly_Update(self, context):
    try: 
        context.scene.bm_table_of_objects[self.global_highpoly_object_index].hl_is_highpoly = False
    except IndexError:
        pass

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
                    for map in object1.global_maps:
                        BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_RemoveHighpoly(context, map, index)
                else:
                    BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_RemoveHighpoly(context, object1, index)

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
            for map in object.global_maps:
                BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, map)
        else:
            BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, object)

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
                    highpoly.global_highpoly_name_old = highpoly.global_highpoly_object_include
                    highpoly.global_object_name = highpoly.global_highpoly_object_include
        else:
            for highpoly in object.hl_highpoly_table:
                if highpoly.global_highpoly_object_index == -1:
                    continue
                for index, object1 in enumerate(context.scene.bm_table_of_objects):
                    if object1.global_object_name == highpoly.global_highpoly_object_include and not any([object1.nm_is_local_container, object1.nm_is_universal_container]):
                        highpoly.global_highpoly_object_index = index
                        break
                highpoly.global_highpoly_name_old = highpoly.global_highpoly_object_include
                highpoly.global_object_name = highpoly.global_highpoly_object_include

###############################################################
### uv Props Funcs ###
###############################################################
def BM_ITEM_PROPS_uv_use_unique_per_map_Update(self, context):
    pass

def BM_ITEM_PROPS_out_use_unique_per_map_Update(self, context):
    pass

def BM_ITEM_PROPS_uv_active_layer_Items(self, context):
    object = BM_Object_Get(context)
    if object[0].nm_is_universal_container and object[0].nm_uni_container_is_global:
        return [('CONTAINER_AUTO', "Automatic", "UV Map is set automatically because Contaniner configures all its object settings")]
    if object[1] is False:
        return [('NONE', "None", "Current Object doesn't support UV Layers")]
    source_object = context.scene.objects[object[0].global_object_name].data
    uv_layers = []

    if len(source_object.uv_layers):
        for uv_layer in source_object.uv_layers:
            uv_layers.append((str(uv_layer.name), uv_layer.name, "UV Layer to use for baking current Object's maps"))
    else:
        uv_layers.append(('NONE_AUTO_CREATE', "Auto Unwrap", "Object has got no UV Layers, Auto UV Unwrap will be proceeded"))
    return uv_layers

def BM_ITEM_PROPS_uv_type_Items(self, context):
    if bpy.app.version >= (3, 2, 0):
        items = [('SINGLE', "Single (single tile)", "Regular single-tiled UV layer"),
                 ('TILED', "Tiled (UDIMs)", "Tiled UV Layer, UDIM tiles")]
    else:
        items = [('SINGLE', "Single (single tile)", "Regular single-tiled UV layer")]
    
    return items

def BM_ITEM_PROPS_uv_bake_target_Items(self, context):
    if bpy.app.version >= (2, 92, 0):
        items = [('IMAGE_TEXTURES', "Image Textures", "Bake to image texture files (image files)"),
                ('VERTEX_COLORS', "Vertex Colors", "Bake to vertex color layers (color attributes, no need for UVs")]
    else:
        items = [('IMAGE_TEXTURES', "Image Textures", "Bake to image texture files (image files)")]
    
    return items

def BM_ITEM_PROPS_UVSettings_Update(self, context):
    pass

def BM_ITEM_PROPS_HighLowSettings_Update(self, context):
    pass

def BM_ITEM_PROPS_OutputSettings_Update(self, context):
    pass

def BM_MAP_PROPS_map_type_Items(self, context):
    # if self.uv_bake_data == 'VERTEX_COLORS':
    #     return [('VERTEX_COLOR_LAYER', "VertexColor Layer", "Bake VertexColor Layer")]

    items = [
        ('', "PBR-Metallic", "PBR maps to bake from existing object materials data"),
        ('ALBEDO', "Albedo", "PBR-Metallic. Color image texture containing color without shadows and highlights"),
        ('METALNESS', "Metalness", "PBR-Metallic. Image texture for determining metal and non-metal parts of the object"),
        ('ROUGHNESS', "Roughness", "PBR-Metallic. Image texture for determining roughness across the surface of the object"),
        ('', "PBR-Specular", ""),
        ('DIFFUSE', "Diffuse", "PBR-Specular. Color image texture containing color without shadows and highlights"),
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
    if bpy.app.version < (3, 0, 0):
        return object_get_vertexcolor_layers(source_object.data.vertex_colors)
    else:
        return object_get_vertexcolor_layers(source_object.data.color_attributes)

def BM_MAP_PROPS_map_displacement_data_Items(self, context):
    object = BM_Object_Get(context)[0]
    if len(object.hl_highpoly_table):
        items = [('HIGHPOLY', "Highpoly", "Bake displacement from highpoly object data to lowpoly"),
                 ('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
                 ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]
    else:
        items = [('MULTIRES', "Multires Modifier", "Bake displacement from existing Multires modifier"),
                 ('MATERIAL', "Material Displacement", "Bake displacement from object materials displacement socket")]

    return items

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
