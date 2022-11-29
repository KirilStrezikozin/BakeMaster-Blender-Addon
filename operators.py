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
import webbrowser
from .utils import *
from .labels import BM_Labels

class BM_OT_Table_of_Objects(bpy.types.Operator):
    bl_idname = 'bakemaster.table_of_objects'
    bl_label = ""
    bl_description = "Move the bake priority of object in the list up and down.\nWhen Name Matching is on, moving Containers bake priority is possible"
    bl_options = {'INTERNAL', 'UNDO'}

    control : bpy.props.EnumProperty(
        items = [('UP', "Up", ""), ('DOWN', "Down", "")])

    def invoke(self, context, event):
        scene = context.scene
        global_active_index = scene.bm_props.global_active_index

        try:
            scene.bm_table_of_objects[global_active_index]
        except IndexError:
            pass
        else:
            item = scene.bm_table_of_objects[global_active_index]
            if self.control == 'UP' and global_active_index > 0:
                # default move for regular objects
                if scene.bm_props.global_use_name_matching is False:
                    scene.bm_table_of_objects.move(global_active_index, global_active_index - 1)
                    # sync texset objs
                    BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                    # update cage and highpolies source objects indexes
                    BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                    BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                    scene.bm_props.global_active_index -= 1
                # move nm items
                else:
                    to_move = []
                    move_to_index = -1
                    # moving universal container
                    if item.nm_is_universal_container:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_master_index:
                                to_move.append(index)
                        # finding where to move to
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_is_universal_container and object.nm_master_index + 1 == item.nm_master_index or object.nm_is_detached and object.nm_master_index + 1 == item.nm_master_index:
                                move_starter_index = index
                                move_to_index = index
                                break
                        to_move.append(global_active_index)
                        if move_starter_index == -1:
                            return {'FINISHED'}
                        # moving each in to_move on the starter_index and index += 1 each move iteration
                        increaser = 0
                        for index in sorted(to_move):
                            scene.bm_table_of_objects.move(index, move_starter_index + increaser)
                            # sync texset objs
                            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                            # update cage and highpolies source objects indexes
                            BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                            increaser += 1
                                
                    # moving local container (cant move out of its uni)
                    elif item.nm_is_local_container:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_master_index:
                                to_move.append(index)
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_is_local_container and object.nm_master_index + 1 == item.nm_master_index:
                                if move_starter_index == -1:
                                    move_starter_index = index
                                    move_to_index = index
                        to_move.append(global_active_index)
                        if move_starter_index == -1:
                            return {'FINISHED'}
                        # moving all items within the same local container 
                        increaser = 0
                        for index in sorted(to_move):
                            scene.bm_table_of_objects.move(index, move_starter_index + increaser)
                            # sync texset objs
                            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                            # update cage and highpolies source objects indexes
                            BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                            increaser += 1
                    
                    # move local item
                    elif item.nm_is_detached is False:
                        move_starter_index = -1
                        len_of_local_items = 0
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_item_local_container_master_index and object.nm_master_index < item.nm_master_index:
                                len_of_local_items += 1
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_item_local_container_master_index and object.nm_master_index + 1 == item.nm_master_index:
                                if move_starter_index == -1:
                                    move_starter_index = index
                                    move_to_index = index
                        # if there are no other local items within the same local container, do not move the item
                        if len_of_local_items < 1:
                            return {'FINISHED'}
                        else:
                            scene.bm_table_of_objects.move(global_active_index, move_starter_index)
                            # sync texset objs
                            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                            # update cage and highpolies source objects indexes
                            BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                    
                    # move detached
                    else:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_is_detached and object.nm_master_index + 1 == item.nm_master_index:
                                move_starter_index = index
                                move_to_index = index
                                break
                            elif object.nm_is_universal_container and object.nm_master_index + 1 == item.nm_master_index:
                                move_starter_index = index
                                move_to_index = index
                                break
                        if move_starter_index == -1:
                            return {'FINISHED'}
                        # moving detached on top of the previous uni_c or before the previous detached
                        scene.bm_table_of_objects.move(global_active_index, move_starter_index)
                        # sync texset objs
                        BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                        # update cage and highpolies source objects indexes
                        BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                        BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)

                    # updating active index
                    if move_to_index != -1:
                        scene.bm_props.global_active_index = move_to_index
                    # updating nm master_indexes
                    BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)
                # update texsets objs because object was moved
                BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

            elif self.control == 'DOWN' and global_active_index < len(scene.bm_table_of_objects) - 1:
                # default move for regular objects
                if scene.bm_props.global_use_name_matching is False:
                    scene.bm_table_of_objects.move(global_active_index, global_active_index + 1)
                    # sync texset objs
                    BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                    # update cage and highpolies source objects indexes
                    BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                    BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                    scene.bm_props.global_active_index += 1
                # move nm items
                else:
                    to_move = []
                    move_to_index = -1
                    len_of_locals = 0
                    len_of_move_to = 0
                    # moving universal container
                    if item.nm_is_universal_container:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_master_index:
                                to_move.append(index)
                                len_of_move_to += 1
                        # finding where to move to
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_is_detached and object.nm_master_index - 1 == item.nm_master_index:
                                move_starter_index = index
                                move_to_index = index - len_of_move_to
                                break
                            elif object.nm_is_universal_container and object.nm_master_index - 1 == item.nm_master_index:
                                move_starter_index = index
                                for object1 in scene.bm_table_of_objects:
                                    if object1.nm_item_uni_container_master_index == object.nm_master_index:
                                        len_of_locals += 1
                                move_to_index = global_active_index + len_of_locals + 1 
                                break
                        to_move.append(global_active_index)
                        if move_starter_index == -1:
                            return {'FINISHED'}
                        # moving each in to_move on the starter_index and index -= 1 each move iteration
                        for index in sorted(to_move):
                            scene.bm_table_of_objects.move(global_active_index, move_starter_index + len_of_locals)
                            # sync texset objs
                            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                            # update cage and highpolies source objects indexes
                            BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                                
                    # moving local container (cant move out of its uni)
                    elif item.nm_is_local_container:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_master_index:
                                to_move.append(index)
                                len_of_move_to += 1
                        # finding where to move to
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_is_local_container and object.nm_master_index - 1 == item.nm_master_index:
                                move_starter_index = index
                                for object1 in scene.bm_table_of_objects:
                                    if object1.nm_item_uni_container_master_index == object.nm_item_uni_container_master_index and object1.nm_item_local_container_master_index == object.nm_master_index:
                                        len_of_locals += 1
                                move_to_index = global_active_index + len_of_locals + 1
                                break
                        to_move.append(global_active_index)
                        if move_starter_index == -1:
                            return {'FINISHED'}
                        # moving all items within the same local container 
                        for index in sorted(to_move):
                            scene.bm_table_of_objects.move(global_active_index, move_starter_index + len_of_locals)
                            # sync texset objs
                            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                            # update cage and highpolies source objects indexes
                            BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                    
                    # move local item
                    elif item.nm_is_detached is False:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_item_local_container_master_index and object.nm_master_index > item.nm_master_index:
                                len_of_locals += 1
                        # finding where to move to
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_item_local_container_master_index and object.nm_master_index - 1 == item.nm_master_index:
                                move_starter_index = index
                                move_to_index = index
                                break
                        # if there are no other local items within the same local container, do not move the item
                        if len_of_locals < 1:
                            return {'FINISHED'}
                        else:
                            scene.bm_table_of_objects.move(global_active_index, move_starter_index)
                            # sync texset objs
                            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                            # update cage and highpolies source objects indexes
                            BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)
                    
                    # move detached
                    else:
                        move_starter_index = -1
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_is_detached and object.nm_master_index - 1 == item.nm_master_index:
                                move_starter_index = index
                                move_to_index = index
                                break
                            elif object.nm_is_universal_container and object.nm_master_index - 1 == item.nm_master_index:
                                for object1 in scene.bm_table_of_objects:
                                    if object1.nm_item_uni_container_master_index == object.nm_master_index:
                                        len_of_locals += 1
                                move_to_index = global_active_index + len_of_locals + 1
                                move_starter_index = index + len_of_locals
                                break
                        if move_starter_index == -1:
                            return {'FINISHED'}
                        # moving detached on top of the previous uni_c or before the previous detached
                        scene.bm_table_of_objects.move(global_active_index, move_starter_index)
                        # sync texset objs
                        BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
                        # update cage and highpolies source objects indexes
                        BM_ITEM_PROPS_hl_cage_UpdateOrder(context)
                        BM_ITEM_PROPS_hl_highpoly_UpdateOnMove(context)

                    # updating active index
                    if move_to_index != -1:
                        scene.bm_props.global_active_index = move_to_index
                    # updating nm master_indexes
                    BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)
                # update texsets objs because object was moved
                BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)
        return {'FINISHED'}

class BM_OT_Table_of_Objects_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.table_of_objects_add'
    bl_label = ""
    bl_description = "Add selected mesh object(s) in the scene to the list below.\nWhen Name Matching is on, added object(s) will be automatically matched"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        is_mesh = True
        exists = False
        objects = []
        objects_data = []
        # get prefixes
        lowpoly_prefix_raw = context.scene.bm_props.global_lowpoly_tag
        highpoly_prefix_raw = context.scene.bm_props.global_highpoly_tag
        cage_prefix_raw = context.scene.bm_props.global_cage_tag
        decal_prefix_raw = context.scene.bm_props.global_decal_tag
        refresh_nm_config = False

        if context.object:
            for object in scene.bm_table_of_objects:
                objects.append(object.global_object_name)
                try:
                    context.scene.objects[object.global_object_name]
                except (KeyError, AttributeError, UnboundLocalError):
                    pass
                else:
                    object_pointer = context.scene.objects[object.global_object_name]
                    objects_data.append(object_pointer.data)
                
        # default add
        if scene.bm_props.global_use_name_matching is False:
            if context.object:
                for object in context.selected_objects:
                    if object.type == 'MESH':

                        if object not in objects and object.data not in objects_data:
                            # remove None all highpolies
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                            # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                            BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                            new_item = scene.bm_table_of_objects.add()
                            new_item.global_object_name = object.name
                            # new_item.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, new_item.bake_batchname)
                            scene.bm_props.global_active_index = len(scene.bm_table_of_objects) - 1
                        else:
                            exists = True
                    else:
                        is_mesh = False

        # adding with name matching
        else:
            if len(scene.bm_table_of_objects) == 0:
                scene.bm_props.global_use_name_matching = False
                refresh_nm_config = True

            if context.object:
                # new config
                insert_data = []
                new_data = []
                all_objs = BM_Table_of_Objects_NameMatching_GetAllObjectNames(context)
                # creating list of all objs to add
                new_objs = []
                for object in context.selected_objects:
                    # checks
                    if object.type != 'MESH':
                        is_mesh = False
                        continue
                    if object in objects or object.data in objects_data:
                        exists = True
                        continue
                    new_objs.append(object.name)
                for object in scene.bm_table_of_objects:
                    if object.nm_is_detached:
                        new_objs.append(object.global_object_name)
                
                # try match some
                for object_name in new_objs:
                    object_name_chunked = BM_Table_of_Objects_NameMatching_GenerateNameChunks(object_name)
                    root_name = BM_Table_of_Objects_NameMatching_GetNameChunks(object_name_chunked, 'ROOT', context)
                    match_found = False
                    for object in scene.bm_table_of_objects:
                        if not any([object.nm_is_universal_container, object.nm_is_local_container, object.nm_is_detached]) and object.global_object_name != object_name:

                            pair_object_name_chunked = BM_Table_of_Objects_NameMatching_GenerateNameChunks(object.global_object_name)
                            pair_root_name = BM_Table_of_Objects_NameMatching_GetNameChunks(pair_object_name_chunked, 'ROOT', context)

                            # check if found match
                            if BM_Table_of_Objects_NameMatching_CombineToRaw(pair_root_name).find(BM_Table_of_Objects_NameMatching_CombineToRaw(root_name)) == 0 or BM_Table_of_Objects_NameMatching_CombineToRaw(root_name).find(BM_Table_of_Objects_NameMatching_CombineToRaw(pair_root_name)) == 0:
                                # add nm_master_indexes to new_data to insert new obj
                                # or a flag to add local_clowpoly
                                # low
                                if lowpoly_prefix_raw in object_name_chunked:
                                    if lowpoly_prefix_raw in pair_object_name_chunked:
                                        insert_data.append([object_name, object.nm_item_uni_container_master_index, object.nm_item_local_container_master_index, None, 'hl_is_lowpoly'])
                                    else:
                                        container_found = False
                                        for object1 in scene.bm_table_of_objects:
                                            if object1.nm_item_uni_container_master_index == object.nm_item_uni_container_master_index and object1.nm_is_local_container and object1.nm_is_lowpoly_container:
                                                container_found = True
                                                insert_data.append([object_name, object1.nm_item_uni_container_master_index, object1.nm_master_index, None, 'hl_is_lowpoly'])
                                        if container_found is False:
                                            insert_data.append([object_name, object.nm_item_uni_container_master_index, None, 0, 'hl_is_lowpoly'])
                                    match_found = True
                                # high
                                if highpoly_prefix_raw in object_name_chunked:
                                    if highpoly_prefix_raw in pair_object_name_chunked:
                                        insert_data.append([object_name, object.nm_item_uni_container_master_index, object.nm_item_local_container_master_index, None, 'hl_is_highpoly'])
                                    else:
                                        container_found = False
                                        for object1 in scene.bm_table_of_objects:
                                            if object1.nm_item_uni_container_master_index == object.nm_item_uni_container_master_index and object1.nm_is_local_container and object1.nm_is_highpoly_container:
                                                container_found = True
                                                insert_data.append([object_name, object1.nm_item_uni_container_master_index, object1.nm_master_index, None, 'hl_is_highpoly'])
                                        if container_found is False:
                                            insert_data.append([object_name, object.nm_item_uni_container_master_index, None, 1, 'hl_is_highpoly'])
                                    match_found = True
                                # cage
                                if cage_prefix_raw in object_name_chunked:
                                    if cage_prefix_raw in pair_object_name_chunked:
                                        insert_data.append([object_name, object.nm_item_uni_container_master_index, object.nm_item_local_container_master_index, None, 'hl_is_cage'])
                                    else:
                                        container_found = False
                                        for object1 in scene.bm_table_of_objects:
                                            if object1.nm_item_uni_container_master_index == object.nm_item_uni_container_master_index and object1.nm_is_local_container and object1.nm_is_cage_container:
                                                container_found = True
                                                insert_data.append([object_name, object1.nm_item_uni_container_master_index, object1.nm_master_index, None, 'hl_is_cage'])
                                        if container_found is False:
                                            insert_data.append([object_name, object.nm_item_uni_container_master_index, None, 2, 'hl_is_cage'])
                                    match_found = True
                                break
                    # add it to construct new data if no match was found
                    if match_found is False:
                        new_data.append(object_name)

                # insert matched data
                container_props = ['nm_is_lowpoly_container', 'nm_is_highpoly_container', 'nm_is_cage_container']
                container_names = ['Lowpolies', 'Highpolies', 'Cages']
                skip_add_container = False
                for shell in insert_data:
                    if shell[0] in BM_Table_of_Objects_NameMatching_GetAllObjectNames(context):
                        continue
                    # adding containers
                    if shell[3] is not None:
                        container_insert_index = 0
                        insert_index = 0
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == shell[1]:
                                container_insert_index = index
                            if object.nm_item_uni_container_master_index == shell[1] and getattr(object, container_props[shell[3]]):
                                skip_add_container = True
                                shell[2] = object.nm_master_index
                        if skip_add_container is False:
                            # remove None all highpolies
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                            # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                            BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                            new_container = scene.bm_table_of_objects.add()
                            new_container.nm_container_name_old = BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, container_names[shell[3]])
                            new_container.nm_container_name = new_container.nm_container_name_old
                            new_container.nm_this_indent = 1
                            new_container.nm_is_local_container = True
                            new_container.nm_is_expanded = True
                            setattr(new_container, container_props[shell[3]], True)
                            # new_container.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, new_container.bake_batchname)
                            # remove None all highpolies
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                            # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                            BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                            new_item = scene.bm_table_of_objects.add()
                            new_item.global_object_name = shell[0]
                            new_item.nm_this_indent = 2
                            new_item.nm_is_expanded = True
                            # setattr(new_item, shell[4], True)
                            # new_item.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, new_item.bake_batchname)
                            # move item to the right place
                            scene.bm_table_of_objects.move(len(scene.bm_table_of_objects) - 2, container_insert_index + 1)
                            scene.bm_table_of_objects.move(len(scene.bm_table_of_objects) - 1, container_insert_index + 2)
                            # update master indexes
                            BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)
                    # add to existing local_c
                    if shell[3] is None or skip_add_container:
                        insert_index = 0
                        for index, object in enumerate(scene.bm_table_of_objects):
                            if object.nm_item_uni_container_master_index == shell[1] and object.nm_item_local_container_master_index == shell[2]:
                                insert_index = index
                        # remove None all highpolies
                        BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                        # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                        BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                        new_item = scene.bm_table_of_objects.add()
                        new_item.global_object_name = shell[0]
                        new_item.nm_this_indent = 2
                        new_item.nm_is_expanded = True
                        # setattr(new_item, shell[4], True)
                        # new_item.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, new_item.bake_batchname)
                        # move item to the right place
                        scene.bm_table_of_objects.move(len(scene.bm_table_of_objects) - 1, insert_index + 1)
                        # update master indexes
                        BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)

                # construct new universal container
                # trash existing new_data to refresh it
                to_remove = []
                for index, object in enumerate(scene.bm_table_of_objects):
                    if object.global_object_name in new_data:
                        to_remove.append(index)
                for index in sorted(to_remove, reverse=True):
                    scene.bm_table_of_objects.remove(index)
                # update table active index
                scene.bm_props.global_active_index = len(scene.bm_table_of_objects) - 1

                # get groups, roots, detached from construct
                NameChunks = BM_Table_of_Objects_NameMatching_GenerateNameChunks
                CombineToRaw = BM_Table_of_Objects_NameMatching_CombineToRaw
                groups, roots, detached = BM_Table_of_Objects_NameMatching_Construct(context, new_data)

                ### constructing new Table_of_Objects items
                for index, shell in enumerate(groups):
                    # adding universal container to the bm_table_of_objects
                    # remove None all highpolies
                    BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                    # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                    BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                    universal_container = context.scene.bm_table_of_objects.add()
                    # name is set to the root_name of the first object in the shell
                    universal_container.nm_container_name_old = BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, CombineToRaw(roots[shell[0]][0]))
                    universal_container.nm_container_name = universal_container.nm_container_name_old
                    universal_container.nm_this_indent = 0
                    universal_container.nm_is_universal_container = True
                    universal_container.nm_is_expanded = True
                    # universal_container.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, universal_container.bake_batchname)

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
                    for local_index, local_names in enumerate(object_names):

                        if len(local_names):
                            # remove None all highpolies
                            BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                            # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                            BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                            local_container = context.scene.bm_table_of_objects.add()
                            local_container.nm_container_name_old = names_starters[local_index]
                            local_container.nm_container_name = names_starters[local_index]
                            local_container.nm_this_indent = 1
                            local_container.nm_is_local_container = True
                            local_container.nm_is_expanded = True
                            setattr(local_container, container_types_props[local_index], True)
                            # local_container.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, local_container.bake_batchname)

                            for obj_index, object_name in enumerate(local_names):
                                # do not add detached names
                                if object_name in detached:
                                    continue
                                # remove None all highpolies
                                BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                                # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                                BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                                new_item = context.scene.bm_table_of_objects.add()
                                new_item.global_object_name = object_name
                                new_item.nm_this_indent = 2
                                new_item.nm_is_expanded = True
                                # setattr(new_item, prefix_props[local_index], True)
                                # new_item.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, new_item.bake_batchname)

                    # auto configure decals, highpolies, and cages
                    universal_container.nm_uni_container_is_global = True

                # adding detached as regular items
                for object_name in detached:
                    # remove None all highpolies
                    BM_ITEM_PROPS_hl_highpoly_UpdateOnAdd(context)
                    # set hl_use_cage to False for data-classes with hl_use_cage True and None hl_cage
                    BM_ITEM_PROPS_hl_cage_UpdateOnAdd(context)
                    new_item = context.scene.bm_table_of_objects.add()
                    new_item.global_object_name = object_name
                    new_item.nm_is_detached = True
                    new_item.nm_is_expanded = True
                    # new_item.bake_batchname_preview = BM_ITEM_PROPS_bake_batchname_ConstructPreview(context, new_item.bake_batchname)

                # update master indexes
                BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)

                # update table active index
                scene.bm_props.global_active_index = len(scene.bm_table_of_objects) - 1

                # update uni containers names
                for index, object in enumerate(context.scene.bm_table_of_objects):
                    if object.nm_is_universal_container:
                        object.nm_container_name = BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, object.nm_container_name, index)

            # refresh nm if was added on empty table
            if refresh_nm_config:
                scene.bm_props.global_use_name_matching = True

        # reports
        if exists:
            self.report({'INFO'}, "Mesh exists in the list")               
        if not is_mesh:
            self.report({'INFO'}, "Expected Mesh Object")
        if len(context.selected_objects) == 0:
            self.report({'INFO'}, "No Objects selected")

        return {'FINISHED'}

class BM_OT_Table_of_Objects_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.table_of_objects_remove'
    bl_label = ""
    bl_description = "Remove active object from the list below.\nWhen Name Matching is on, removing Container will remove all objects underneath it as well"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        global_active_index = scene.bm_props.global_active_index

        if len(scene.bm_table_of_objects):
            item = scene.bm_table_of_objects[global_active_index]
            # default removal
            if scene.bm_props.global_use_name_matching is False or item.nm_is_detached is True:
                # update use_cage
                BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, global_active_index, 'OBJECT')
                removed_was_highpoly = scene.bm_table_of_objects[global_active_index].hl_is_highpoly
                if removed_was_highpoly is False:
                    highpolies_holder = context.scene.bm_table_of_objects[global_active_index]
                    BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, highpolies_holder)
                scene.bm_table_of_objects.remove(global_active_index)
                # update highpolies
                BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, global_active_index, 'OBJECT', removed_was_highpoly)
                # remove obj from texset if it was there
                BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, global_active_index)
                if global_active_index != 0:
                    scene.bm_props.global_active_index -= 1

            else:
                to_remove = []
                uni_removed_index = -1
                # removing local_c and its items
                if item.nm_is_local_container:
                    len_of_local_items = 0
                    to_remove.append(global_active_index)
                    for index, object in enumerate(scene.bm_table_of_objects):
                        if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_item_local_container_master_index == item.nm_master_index:
                            to_remove.append(index)
                        if object.nm_is_universal_container and object.nm_master_index == item.nm_item_uni_container_master_index:
                            uni_removed_index = index
                    
                    # removing uni if there was only one local
                    for index, object in enumerate(scene.bm_table_of_objects):
                        # found local in the same uni
                        if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_is_local_container is False and index not in to_remove:
                            len_of_local_items += 1
                    # removing uni if there was only one local
                    if len_of_local_items == 0 and uni_removed_index != -1:
                        to_remove.append(uni_removed_index)

                    for index in sorted(dict.fromkeys(to_remove), reverse=True):
                        # update use_cage
                        BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, index, 'OBJECT')
                        removed_was_highpoly = scene.bm_table_of_objects[index].hl_is_highpoly
                        if removed_was_highpoly is False:
                            highpolies_holder = context.scene.bm_table_of_objects[index]
                            BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, highpolies_holder)
                        scene.bm_table_of_objects.remove(index)
                        # update highpolies
                        BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, index, 'OBJECT', removed_was_highpoly)
                        # remove obj from texset if it was there
                        BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, index)

                # removing uni_c and its items
                elif item.nm_is_universal_container:
                    to_remove.append(global_active_index)
                    for index, object in enumerate(scene.bm_table_of_objects):
                        if object.nm_item_uni_container_master_index == item.nm_master_index:
                            to_remove.append(index)

                    for index in sorted(to_remove, reverse=True):
                        # update use_cage
                        BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, index, 'OBJECT')
                        removed_was_highpoly = scene.bm_table_of_objects[index].hl_is_highpoly
                        if removed_was_highpoly is False:
                            highpolies_holder = context.scene.bm_table_of_objects[index]
                            BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, highpolies_holder)
                        scene.bm_table_of_objects.remove(index)
                        # update highpolies
                        BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, index, 'OBJECT', removed_was_highpoly)
                        # remove obj from texset if it was there
                        BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, index)
                # removing items in locals
                else:
                    len_of_local = 0
                    len_of_local_items = 0
                    uni_removed_index = -1
                    local_removed_index = -1
                    for index, object in enumerate(scene.bm_table_of_objects):
                        # found item in the same local, adding item to to_remove[]
                        if object.nm_item_local_container_master_index == item.nm_item_local_container_master_index and object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index:
                            len_of_local += 1
                        # found the container the item belongs to
                        if object.nm_is_local_container and object.nm_master_index == item.nm_item_local_container_master_index and object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index:
                            local_removed_index = index
                        if object.nm_is_universal_container and object.nm_master_index == item.nm_item_uni_container_master_index:
                            uni_removed_index = index
                    # item is the only one in the local, detached its pairs and remove uni_c, local_cs, else just remove the item
                    if len_of_local > 1:
                        # update use_cage
                        BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, global_active_index, 'OBJECT')
                        removed_was_highpoly = scene.bm_table_of_objects[global_active_index].hl_is_highpoly
                        if removed_was_highpoly is False:
                            highpolies_holder = context.scene.bm_table_of_objects[global_active_index]
                            BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, highpolies_holder)
                        scene.bm_table_of_objects.remove(global_active_index)
                        # update highpolies
                        BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, global_active_index, 'OBJECT', removed_was_highpoly)
                        # remove obj from texset if it was there
                        BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, global_active_index)
                    else:
                        # same removal as uni_c removal
                        # if remove local container, if only had one local container, remove the uni_container as well then
                        if local_removed_index != -1 and uni_removed_index != -1:
                            to_remove.append(global_active_index)
                            to_remove.append(local_removed_index)
                            # removing uni if there was only one local
                            for index, object in enumerate(scene.bm_table_of_objects):
                                # found local in the same uni
                                if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_is_local_container is False and index not in to_remove:
                                    len_of_local_items += 1
                            # removing uni if there was only one local
                            if len_of_local_items == 0:
                                to_remove.append(uni_removed_index)

                            for index in sorted(dict.fromkeys(to_remove), reverse=True):
                                # update use_cage
                                BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, index, 'OBJECT')
                                removed_was_highpoly = scene.bm_table_of_objects[index].hl_is_highpoly
                                if removed_was_highpoly is False:
                                    highpolies_holder = context.scene.bm_table_of_objects[index]
                                    BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, highpolies_holder)
                                scene.bm_table_of_objects.remove(index)
                                # update highpolies
                                BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, index, 'OBJECT', removed_was_highpoly)
                                # remove obj from texset if it was there
                                BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, index)
                # updating nm master_indexes
                BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)
                # active index update
                if global_active_index >= len(scene.bm_table_of_objects):
                    scene.bm_props.global_active_index = len(scene.bm_table_of_objects) - 1
            # update texset objs order if anything was removed
            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

            # item.use_target = False
            
            # if item.use_source:
            #     for index1, item1 in enumerate(scene.bm_table_of_objects):
            #             if item.source_name == item1.object_pointer.name:
            #                 item1.source = 'NONE'
            #                 break

        return {'FINISHED'}

class BM_OT_Table_of_Objects_Refresh(bpy.types.Operator):
    bl_idname = 'bakemaster.table_of_objects_refresh'
    bl_label = ""
    bl_description = "Some objects cannot be found in the scene. Press the refresh button to remove them from the list"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        to_remove = []

        # return true if item does exist in the scene
        def exists(name: str):
            try:
                scene.objects[name]
            except (KeyError, AttributeError):
                return False
            else:
                return True

        for global_index, global_object in enumerate(scene.bm_table_of_objects):
            try:
                scene.objects[global_object.global_object_name]
            except (KeyError, AttributeError):
                if scene.bm_props.global_use_name_matching is False or global_object.nm_is_detached is True:
                    to_remove.append(global_index)
                else:
                    if global_object.nm_is_local_container or global_object.nm_is_universal_container:
                        continue
                    # refreshing local items
                    item = global_object
                    len_of_local = 0
                    len_of_local_items = 0
                    uni_removed_index = -1
                    local_removed_index = -1
                    for index, object in enumerate(scene.bm_table_of_objects):
                        # found item in the same local
                        if object.nm_item_local_container_master_index == item.nm_item_local_container_master_index and object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and exists(object.global_object_name):
                            len_of_local += 1
                        # found the container the item belongs to
                        if object.nm_is_local_container and object.nm_master_index == item.nm_item_local_container_master_index and object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index:
                            local_removed_index = index
                        if object.nm_is_universal_container and object.nm_master_index == item.nm_item_uni_container_master_index:
                            uni_removed_index = index
                    # item is the only one in the local, remove uni_c, local_cs, else just remove the item
                    if len_of_local > 1:
                        to_remove.append(global_index)
                    else:
                        # same removal as uni_c removal
                        # if remove local container, if only had one local container, remove the uni_container as well then
                        if local_removed_index != -1 and uni_removed_index != -1:
                            to_remove.append(global_index)
                            to_remove.append(local_removed_index)
                            # removing uni if there was only one local
                            for index, object in enumerate(scene.bm_table_of_objects):
                                # found local in the same uni
                                if object.nm_item_uni_container_master_index == item.nm_item_uni_container_master_index and object.nm_is_local_container is False and exists(object.global_object_name):
                                    len_of_local_items += 1
                            if len_of_local_items == 0:
                                to_remove.append(uni_removed_index)
                    # updating nm master_indexes
                    BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)

            else:
                pass
        # removing objects
        for index in sorted(list(dict.fromkeys(to_remove)), reverse=True):
            # update use_cage
            BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, index, 'OBJECT')
            removed_was_highpoly = scene.bm_table_of_objects[index].hl_is_highpoly
            if removed_was_highpoly is False:
                highpolies_holder = context.scene.bm_table_of_objects[index]
                BM_ITEM_PROPS_hl_highpoly_SyncedRemoval_UnsetHighpolies(context, highpolies_holder)
            scene.bm_table_of_objects.remove(index)
            # update highpolies
            BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, index, 'OBJECT', removed_was_highpoly)
            # remove obj from texset if it was there
            BM_TEXSET_OBJECT_PROPS_global_object_SyncedRemoval(context, index)
        # active index update
        if scene.bm_props.global_active_index >= len(scene.bm_table_of_objects):
            scene.bm_props.global_active_index = len(scene.bm_table_of_objects) - 1

                # item.use_target = False

                # if item.use_source:
                #     for index1, item1 in enumerate(scene.bm_table_of_objects):
                #         if item.source_name == item1.object_pointer.name:
                #             item1.source = 'NONE'
                #             break

        return {'FINISHED'}

class BM_OT_Table_of_Objects_Trash(bpy.types.Operator):
    bl_idname = 'bakemaster.table_of_objects_trash'
    bl_label = ""
    bl_description = "Remove all objects from the list (resets BakeMaster)"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        to_remove = []
        for index, item in enumerate(context.scene.bm_table_of_objects):
            to_remove.append(index)
        for index in to_remove[::-1]:
            context.scene.bm_table_of_objects.remove(index)
        # trash texsets
        to_remove = []
        for index, item in enumerate(context.scene.bm_props.global_texturesets_table):
            to_remove.append(index)
        for index in to_remove[::-1]:
            context.scene.bm_props.global_texturesets_table.remove(index)

        context.scene.bm_props.global_active_index = 0
        context.scene.bm_props.bake_available = True
        return {'FINISHED'}

###########################################################################

class BM_OT_ITEM_Highpoly_Table_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.item_highpoly_table_add'
    bl_label = ""
    bl_description = "Add new highpoly for the current object"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        new_item = object.hl_highpoly_table.add()
        new_item.global_item_index = len(object.hl_highpoly_table)
        # set chosen highpoly hl_is_highpoly to True on add
        BM_ITEM_PROPS_hl_add_highpoly_Update(new_item, context)
        object.hl_highpoly_table_active_index = len(object.hl_highpoly_table) - 1

        object.hl_is_lowpoly = True
        return {'FINISHED'}

class BM_OT_ITEM_Highpoly_Table_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.item_highpoly_table_remove'
    bl_label = ""
    bl_description = "Remove new highpoly from the current object"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        if len(object.hl_highpoly_table):
            # BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, object)

            for item in object.hl_highpoly_table:
                if item.global_item_index > object.hl_highpoly_table[object.hl_highpoly_table_active_index].global_item_index:
                    item.global_item_index -= 1
            # set hl_is_highpoly to False for chosen highpoly on remove
            BM_ITEM_PROPS_hl_remove_highpoly_Update(object.hl_highpoly_table[object.hl_highpoly_table_active_index], context)
            object.hl_highpoly_table.remove(object.hl_highpoly_table_active_index)
            BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)
            if object.hl_highpoly_table_active_index > 0:
                object.hl_highpoly_table_active_index -= 1

            if len(object.hl_highpoly_table) == 0:
                object.hl_use_cage = False
                object.hl_is_lowpoly = False
        return {'FINISHED'}

class BM_OT_MAP_Highpoly_Table_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.map_highpoly_table_add'
    bl_label = ""
    bl_description = "Add new highpoly for the current map"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        map = BM_Map_Get(object)
        new_item = map.hl_highpoly_table.add()
        new_item.global_item_index = len(map.hl_highpoly_table)
        # set chosen highpoly hl_is_highpoly to True on add
        BM_ITEM_PROPS_hl_add_highpoly_Update(new_item, context)
        map.hl_highpoly_table_active_index = len(map.hl_highpoly_table) - 1

        object.hl_is_lowpoly = True
        return {'FINISHED'}

class BM_OT_MAP_Highpoly_Table_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.map_highpoly_table_remove'
    bl_label = ""
    bl_description = "Remove highpoly from the current map"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        map = BM_Map_Get(object)
        if len(map.hl_highpoly_table):
            # BM_ITEM_PROPS_hl_highpoly_RemoveNone(context, map)

            for item in map.hl_highpoly_table:
                if item.global_item_index > map.hl_highpoly_table[map.hl_highpoly_table_active_index].global_item_index:
                    item.global_item_index -= 1
            # set hl_is_highpoly to False for chosen highpoly on remove
            BM_ITEM_PROPS_hl_remove_highpoly_Update(map.hl_highpoly_table[map.hl_highpoly_table_active_index], context)
            map.hl_highpoly_table.remove(map.hl_highpoly_table_active_index)
            BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)
            if map.hl_highpoly_table_active_index > 0:
                map.hl_highpoly_table_active_index -= 1

            if len(map.hl_highpoly_table) == 0:
                map.hl_use_cage = False

            # count highpolies and set object.hl_is_lowpoly based of that
            len_of_highpolies = 0
            for map1 in object.global_maps:
                len_of_highpolies += len(map1.hl_highpoly_table)
            if len_of_highpolies == 0:
                object.hl_is_lowpoly = False
        return {'FINISHED'}

class BM_OT_ITEM_ChannelPack_Table_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.item_channelpack_table_add'
    bl_label = ""
    bl_description = "Add new Map Channel Pack for the current object"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        new_item = object.chnlp_channelpacking_table.add()
        new_item.global_channelpack_index = len(object.chnlp_channelpacking_table)
        new_item.global_channelpack_name = "ChannelPack{}".format(len(object.chnlp_channelpacking_table))
        object.chnlp_channelpacking_table_active_index = len(object.chnlp_channelpacking_table) - 1
        return {'FINISHED'}

class BM_OT_ITEM_ChannelPack_Table_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.item_channelpack_table_remove'
    bl_label = ""
    bl_description = "Remove Map Channel Pack for the current object"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        if len(object.chnlp_channelpacking_table):
            for item in object.chnlp_channelpacking_table:
                if item.global_channelpack_index > object.chnlp_channelpacking_table[object.chnlp_channelpacking_table_active_index].global_channelpack_index:
                    item.global_channelpack_index -= 1
            object.chnlp_channelpacking_table.remove(object.chnlp_channelpacking_table_active_index)
            if object.chnlp_channelpacking_table_active_index > 0:
                object.chnlp_channelpacking_table_active_index -= 1
        return {'FINISHED'}

class BM_OT_ITEM_ChannelPack_Table_Trash(bpy.types.Operator):
    bl_idname = 'bakemaster.item_channelpack_table_trash'
    bl_label = ""
    bl_description = "Remove all Map Channel Packs"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        object = BM_Object_Get(context)[0]
        to_remove = []
        for index, item in enumerate(object.chnlp_channelpacking_table):
            to_remove.append(index)
        for index in to_remove[::-1]:
            object.chnlp_channelpacking_table.remove(index)
        object.chnlp_channelpacking_table_active_index = 0
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Table_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_table_add'
    bl_label = ""
    bl_description = "Add new Texture Set.\nTexture Set is a set of objects that share the same image texture file for each map"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        new_item = bm_props.global_texturesets_table.add()
        new_item.global_textureset_index = len(bm_props.global_texturesets_table)
        new_item.global_textureset_name = "TextureSet{}".format(len(bm_props.global_texturesets_table))
        bm_props.global_texturesets_active_index = len(bm_props.global_texturesets_table) - 1
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Table_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_table_remove'
    bl_label = ""
    bl_description = "Remove Texture Set"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        if len(bm_props.global_texturesets_table):
            for item in bm_props.global_texturesets_table:
                if item.global_textureset_index > bm_props.global_texturesets_table[bm_props.global_texturesets_active_index].global_textureset_index:
                    item.global_textureset_index -= 1
                    
            texset = bm_props.global_texturesets_table[bm_props.global_texturesets_active_index]
            table_of_objs = texset.global_textureset_table_of_objects
            for item1 in table_of_objs:
                context.scene.bm_table_of_objects[item1.global_source_object_index].global_is_included_in_texset = False
                BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

            bm_props.global_texturesets_table.remove(bm_props.global_texturesets_active_index)
            if bm_props.global_texturesets_active_index > 0:
                bm_props.global_texturesets_active_index -= 1
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Table_Trash(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_table_trash'
    bl_label = ""
    bl_description = "Remove all Texture Sets"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        to_remove = []
        for index, item in enumerate(bm_props.global_texturesets_table):

            table_of_objs = item.global_textureset_table_of_objects
            for item1 in table_of_objs:
                context.scene.bm_table_of_objects[item1.global_source_object_index].global_is_included_in_texset = False
                BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

            to_remove.append(index)
        for index in to_remove[::-1]:
            bm_props.global_texturesets_table.remove(index)
        bm_props.global_texturesets_active_index = 0
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Objects_Table_Add(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_objects_table_add'
    bl_label = ""
    bl_description = "Add new Object to the current Texture Set"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        table = bm_props.global_texturesets_table[bm_props.global_texturesets_active_index].global_textureset_table_of_objects

        new_item = table.add()
        new_item.global_object_index = len(table)
        new_item.global_object_name_old = new_item.global_object_name
        new_item.global_object_name_include = new_item.global_object_name
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if context.scene.bm_props.global_use_name_matching and object.nm_container_name == new_item.global_object_name:
                new_item.global_source_object_index = index
                break
            elif object.global_object_name == new_item.global_object_name:
                new_item.global_source_object_index = index
                break
        context.scene.bm_table_of_objects[new_item.global_source_object_index].global_is_included_in_texset = True
        BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

        # recreate subitems
        item = context.scene.bm_table_of_objects[new_item.global_source_object_index]
        if item.nm_is_universal_container and context.scene.bm_props.global_use_name_matching:
            # trash
            to_remove = []
            for index, subitem in enumerate(new_item.global_object_name_subitems):
                to_remove.append(index)
            for index in sorted(to_remove, reverse=True):
                new_item.global_object_name_subitems.remove(index)
            # add
            local_c_master_index = -1
            for index, subitem in enumerate(context.scene.bm_table_of_objects):
                if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_is_lowpoly_container:
                    local_c_master_index = subitem.nm_master_index

                if subitem.nm_item_uni_container_master_index == item.nm_master_index and subitem.nm_item_local_container_master_index == local_c_master_index:
                    new_subitem = new_item.global_object_name_subitems.add()
                    new_subitem.global_object_name = subitem.global_object_name
                    new_subitem.global_object_index = len(new_item.global_object_name_subitems)

        bm_props.global_texturesets_table[bm_props.global_texturesets_active_index].global_textureset_table_of_objects_active_index = len(table) - 1
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Objects_Table_Remove(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_objects_table_remove'
    bl_label = ""
    bl_description = "Remove Texture Set Object"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        active_texset = bm_props.global_texturesets_table[bm_props.global_texturesets_active_index]
        objects = active_texset.global_textureset_table_of_objects
        if len(objects):
            for item in objects:
                if item.global_object_index > objects[active_texset.global_textureset_table_of_objects_active_index].global_object_index:
                    item.global_object_index -= 1

            item = active_texset.global_textureset_table_of_objects[active_texset.global_textureset_table_of_objects_active_index]
            context.scene.bm_table_of_objects[item.global_source_object_index].global_is_included_in_texset = False
            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

            objects.remove(active_texset.global_textureset_table_of_objects_active_index)
            if active_texset.global_textureset_table_of_objects_active_index > 0:
                active_texset.global_textureset_table_of_objects_active_index -= 1
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Objects_Table_Trash(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_objects_table_trash'
    bl_label = ""
    bl_description = "Remove all Texture Set Objects"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        table = bm_props.global_texturesets_table[bm_props.global_texturesets_active_index].global_textureset_table_of_objects
        to_remove = []
        for index, item in enumerate(table):

            context.scene.bm_table_of_objects[item.global_source_object_index].global_is_included_in_texset = False
            BM_TEXSET_OBJECT_PROPS_global_object_name_UpdateOrder(context)

            to_remove.append(index)
        for index in to_remove[::-1]:
            table.remove(index)
        bm_props.global_texturesets_active_index = 0
        return {'FINISHED'}

class BM_OT_SCENE_TextureSets_Objects_Table_InvertSubItems(bpy.types.Operator):
    bl_idname = 'bakemaster.scene_texturesets_objects_table_invertsubitems'
    bl_label = ""
    bl_description = "Invert selection of Container's Objects"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        texset = bm_props.global_texturesets_table[bm_props.global_texturesets_active_index]
        table = texset.global_textureset_table_of_objects[texset.global_textureset_table_of_objects_active_index].global_object_name_subitems
        for subitem in table:
            subitem.global_object_include_in_texset = False if subitem.global_object_include_in_texset else True
        return {'FINISHED'}

# class BM_OT_ITEM_BatchNamingTable_Add(bpy.types.Operator):
#     bl_idname = 'bakemaster.item_batchnamingtable_add'
#     bl_label = ""
#     bl_description = "Add keyword to the Batch Naming convention"
#     bl_options = {'INTERNAL', 'UNDO'}

#     def execute(self, context):
#         object = BM_Object_Get(context)[0]
#         new_item = object.bake_batch_name_table.add()
#         new_item.global_keyword_index = len(object.bake_batch_name_table) - 1
#         new_item.global_keyword_old = new_item.global_keyword
#         BM_BATCHNAMINGKEY_PROPS_global_keyword_UpdateOrder(context)
#         object.bake_batch_name_table_active_index = len(object.bake_batch_name_table) - 1
#         return {'FINISHED'}

# class BM_OT_ITEM_BatchNamingTable_Remove(bpy.types.Operator):
#     bl_idname = 'bakemaster.item_batchnamingtable_remove'
#     bl_label = ""
#     bl_description = "Remove keyword from the Batch Naming convention"
#     bl_options = {'INTERNAL', 'UNDO'}

#     def execute(self, context):
#         object = BM_Object_Get(context)[0]
#         keyword = object.bake_batch_name_table[object.bake_batch_name_table_active_index]
#         for keyword1 in object.bake_batch_name_table:
#             if keyword1.global_keyword_index > keyword.global_keyword_index:
#                 keyword1.global_keyword_index -= 1
#         object.bake_batch_name_table.remove(object.bake_batch_name_table_active_index)
#         BM_BATCHNAMINGKEY_PROPS_global_keyword_UpdateOrder(context)
#         if object.bake_batch_name_table_active_index > 0:
#             object.bake_batch_name_table_active_index -= 1
#         return {'FINISHED'}

# class BM_OT_ITEM_BatchNamingTable_Trash(bpy.types.Operator):
#     bl_idname = 'bakemaster.item_batchnamingtable_trash'
#     bl_label = ""
#     bl_description = "Remove all keywords from the Batch Naming convention"
#     bl_options = {'INTERNAL', 'UNDO'}

#     def execute(self, context):
#         object = BM_Object_Get(context)[0]
#         to_remove = []
#         for index, keyword in enumerate(object.bake_batch_name_table):
#             to_remove.append(index)
#         for index in sorted(to_remove, reverse=True):
#             object.bake_batch_name_table.remove(index)
#         object.bake_batch_name_table_active_index = 0
#         return {'FINISHED'}
class BM_OT_ITEM_BatchNaming_Preview(bpy.types.Operator):
    bl_idname = 'bakemaster.item_batchnaming_preview'
    bl_label = "Preview Batch Name"
    bl_description = "Preview how the configured batch naming convention will look in the output image filename.\n(Demo, values for each keyword might be different for each baked map's image file)"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        object = BM_Object_Get(context)[0]
        preview = BM_ITEM_PROPS_bake_batchname_GetPreview(object, context)
        self.report({'INFO'}, preview)
        return {'FINISHED'}

class BM_OT_ITEM_Maps(bpy.types.Operator):
    bl_idname = 'bakemaster.item_maps_table'
    bl_label = ""
    bl_description = "Add/Remove map passes from the list"
    bl_options = {'INTERNAL', 'UNDO'}

    control : bpy.props.EnumProperty(
        items = [('ADD', "Add", ""), ('REMOVE', "Remove", ""), ('TRASH', "Trash", "")])

    def invoke(self, context, event):
        object = BM_Object_Get(context)[0]
        global_active_index = object.global_maps_active_index

        try:
            object.global_maps[global_active_index]
        except IndexError:
            pass
        else:
            if self.control == 'REMOVE' or self.control == 'TRASH':
                BM_ITEM_RemoveLocalPreviews(object, context)

            if self.control == 'REMOVE':
                # update maps indexes
                for map in object.global_maps:
                    if map.global_map_index > object.global_maps[global_active_index].global_map_index:
                        map.global_map_index -= 1

                # trash chnlp if removing last map
                if len(object.global_maps) == 1:
                    to_remove = []
                    for index, _ in enumerate(object.chnlp_channelpacking_table):
                        to_remove.append(index)
                    for index in sorted(to_remove, reverse=True):
                        object.chnlp_channelpacking_table.remove(index)

                if object.global_maps_active_index != 0:
                    object.global_maps_active_index -= 1
                # unset highpolies
                BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, global_active_index, 'MAP', False)
                # update use_cage
                BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, global_active_index, 'MAP')
                object.global_maps.remove(global_active_index)
                BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)
                
            elif self.control == 'TRASH':
                # trash chnlp first
                to_remove = []
                for index, _ in enumerate(object.chnlp_channelpacking_table):
                    to_remove.append(index)
                for index in sorted(to_remove, reverse=True):
                    object.chnlp_channelpacking_table.remove(index)

                # trash maps
                to_remove = []
                for index, _ in enumerate(object.global_maps):
                    to_remove.append(index)
                for index in sorted(to_remove, reverse=True):
                    # unset highpolies
                    BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(context, index, 'MAP', False)
                    # update use_cage
                    BM_ITEM_PROPS_hl_cage_UpdateOnRemove(context, index, 'MAP')
                    object.global_maps.remove(index)
                    BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)

                object.global_maps_active_index = 0

        if self.control == 'ADD':
            new_pass = object.global_maps.add()
            new_pass.global_map_type = 'ALBEDO'
            new_pass.global_map_index = len(object.global_maps)
            object.global_maps_active_index = len(object.global_maps) - 1
            BM_ITEM_OverwriteUpdate(object, context)

        return {'FINISHED'}

class BM_OT_ApplyLastEditedProp_SelectAll(bpy.types.Operator):
    bl_label = "Select All"
    bl_idname = "bakemaster.apply_proprety_selectall"
    bl_description = "Select all Items"
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        object = BM_Object_Get(context)[0]
        prop_is_map = context.scene.bm_props.global_last_edited_prop_is_map
        
        # invert selection of maps
        if prop_is_map and bm_props.global_alep_affect_objects is False and len(object.global_maps):
            for map_item in bm_props.global_alep_maps:
                map_item.use_affect = True
            
        # invert selection of objects
        if (prop_is_map and bm_props.global_alep_affect_objects) or prop_is_map is False:
            for object_item in bm_props.global_alep_objects:
                object_item.use_affect = True

        return {'FINISHED'}

class BM_OT_ApplyLastEditedProp_InvertSelection(bpy.types.Operator):
    bl_label = "Invert"
    bl_idname = "bakemaster.apply_proprety_invert"
    bl_description = "Invert selection of Items"
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        object = BM_Object_Get(context)[0]
        prop_is_map = context.scene.bm_props.global_last_edited_prop_is_map
        
        # invert selection of maps
        if prop_is_map and bm_props.global_alep_affect_objects is False and len(object.global_maps):
            for map_item in bm_props.global_alep_maps:
                map_item.use_affect = False if map_item.use_affect else True
            
        # invert selection of objects
        if (prop_is_map and bm_props.global_alep_affect_objects) or prop_is_map is False:
            for object_item in bm_props.global_alep_objects:
                object_item.use_affect = False if object_item.use_affect else True

        return {'FINISHED'}

class BM_OT_ApplyLastEditedProp(bpy.types.Operator):
    bl_label = "Apply Lastly Edited Property"
    bl_idname = "bakemaster.apply_proprety"
    bl_description = "Select maps or objects to apply value of lastly edited property for"
    bl_options = {'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props

        prop = context.scene.bm_props.global_last_edited_prop
        prop_value = context.scene.bm_props.global_last_edited_prop_value
        prop_type = context.scene.bm_props.global_last_edited_prop_type
        prop_is_map = context.scene.bm_props.global_last_edited_prop_is_map


        if prop_type == "int":
            prop_value_real = int(prop_value)
        elif prop_type == "float":
            prop_value_real = float(prop_value)
        elif prop_type == "bool":
            prop_value_real = bool(int(prop_value))
        elif prop_type == "tuple":
            prop_value_real_array = []
            for x in prop_value:
                prop_value_real_array.append(float(x))
            prop_value_real = tuple(prop_value_real_array)
        else:
            prop_value_real = prop_value

        object = BM_Object_Get(context)[0]

        # apply to maps
        if prop_is_map:
            # apply to object's maps
            if bm_props.global_alep_affect_objects is False:
                for index, map in enumerate(object.global_maps):
                    if bm_props.global_alep_maps[index].use_affect is False:
                        continue
                    try:
                        setattr(map, prop, prop_value_real)
                    except TypeError:
                        self.report({'ERROR'}, "Cannot apply property, aborting")
                        return {'FINISHED'}

            # apply to all chosen object's maps
            else:
                for object1 in context.scene.bm_table_of_objects:
                    if object1.nm_is_universal_container:
                        items = [item for item in bm_props.global_alep_objects if item.object_name == object1.nm_container_name]
                    else:
                        items = [item for item in bm_props.global_alep_objects if item.object_name == object1.global_object_name]
                    if len(items) == 0:
                        continue
                    if items[0].use_affect is False:
                        continue

                    for index, map in enumerate(object1.global_maps):
                        try:
                            setattr(map, prop, prop_value_real)
                        except TypeError:
                            self.report({'ERROR'}, "Cannot apply property, aborting")
                            return {'FINISHED'}

        # apply to selected objects
        else:
            for object1 in context.scene.bm_table_of_objects:
                if object1.nm_is_universal_container:
                    items = [item for item in bm_props.global_alep_objects if item.object_name == object1.nm_container_name]
                else:
                    items = [item for item in bm_props.global_alep_objects if item.object_name == object1.global_object_name]
                if len(items) == 0:
                    continue
                if items[0].use_affect is False:
                    continue

                try:
                    setattr(object1, prop, prop_value_real)
                except TypeError:
                    self.report({'ERROR'}, "Cannot apply property, aborting")
                    return {'FINISHED'}

        self.report({'INFO'}, "Property succesfully applied")
        return {'FINISHED'}

    def draw(self, context):
        bm_props = context.scene.bm_props
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        prop_name = context.scene.bm_props.global_last_edited_prop_name
        prop_is_map = context.scene.bm_props.global_last_edited_prop_is_map

        object = BM_Object_Get(context)[0]

        column = layout.column(align=True)
        column.label(text="Proprety:")
        column.label(text=prop_name)

        if prop_is_map:
            layout.prop(bm_props, "global_alep_affect_objects")

        items_box = layout.box()
        items_box.use_property_split = True
        items_box.use_property_decorate = False
        if prop_is_map:
            if bm_props.global_alep_affect_objects is False and len(object.global_maps):
                rows = len(bm_props.global_alep_maps)

                #items_box.template_list('BM_ALEP_UL_Maps_Item', "", bm_props, 'global_alep_maps', bm_props, 'global_alep_maps_active_index', rows=rows)
                table = items_box.column().row()
                table.template_list('BM_ALEP_UL_Maps_Item', "", bm_props, 'global_alep_maps', bm_props, 'global_alep_maps_active_index', rows=rows)
                column = table.column(align=True)
                column.operator(BM_OT_ApplyLastEditedProp_SelectAll.bl_idname, text="", icon='WORLD')
                column.operator(BM_OT_ApplyLastEditedProp_InvertSelection.bl_idname, text="", icon='CHECKBOX_HLT')

            elif len(object.global_maps) == 0:
                items_box.label(text="Object has no maps")

        if (prop_is_map and bm_props.global_alep_affect_objects) or prop_is_map is False:
            rows = len(bm_props.global_alep_objects)

            #items_box.template_list('BM_ALEP_UL_Objects_Item', "", bm_props, 'global_alep_objects', bm_props, 'global_alep_objects_active_index', rows=rows)
            table = items_box.column().row()
            table.template_list('BM_ALEP_UL_Objects_Item', "", bm_props, 'global_alep_objects', bm_props, 'global_alep_objects_active_index', rows=rows)
            column = table.column(align=True)
            column.operator(BM_OT_ApplyLastEditedProp_SelectAll.bl_idname, text="", icon='WORLD')
            column.operator(BM_OT_ApplyLastEditedProp_InvertSelection.bl_idname, text="", icon='CHECKBOX_HLT')


    def invoke(self, context, event):
        bm_props = context.scene.bm_props
        prop = context.scene.bm_props.global_last_edited_prop
        prop_name = context.scene.bm_props.global_last_edited_prop_name
        prop_value = context.scene.bm_props.global_last_edited_prop_value
        prop_is_map = context.scene.bm_props.global_last_edited_prop_is_map

        # trash all maps and objects items
        bm_props.global_alep_maps_active_index = 0
        to_remove = []
        for index, _ in enumerate(bm_props.global_alep_maps):
            to_remove.append(index)
        for index in sorted(to_remove, reverse=True):
            bm_props.global_alep_maps.remove(index)

        bm_props.global_alep_objects_active_index = 0
        to_remove = []
        for index, _ in enumerate(bm_props.global_alep_objects):
            to_remove.append(index)
        for index in sorted(to_remove, reverse=True):
            bm_props.global_alep_objects.remove(index)

        # construct maps and objects items
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
        
        object = BM_Object_Get(context)[0]
        for map in object.global_maps:
            new_map = bm_props.global_alep_maps.add()
            new_map.map_name = "{} {}".format(map.global_map_index, maps_names[map.global_map_type])

        global_uni_c_master_index = -1
        for object1 in context.scene.bm_table_of_objects:
            add_object = False
            if context.scene.bm_props.global_use_name_matching:
                if object1.nm_is_universal_container and object1.nm_uni_container_is_global is False:
                    global_uni_c_master_index = -1
                if object1.nm_is_detached:
                    add_object = True
                elif object1.nm_is_universal_container and object1.nm_uni_container_is_global:
                    add_object = True
                    global_uni_c_master_index = object1.nm_master_index
                elif not any([object1.hl_is_highpoly, object1.hl_is_cage, object1.nm_item_uni_container_master_index == global_uni_c_master_index, object1.nm_is_local_container]) and object1.nm_item_uni_container_master_index != -1:
                    add_object = True
            elif not any([object1.hl_is_highpoly, object1.hl_is_cage]):
                add_object = True
            
            if add_object:
                new_object = bm_props.global_alep_objects.add()
                if object1.nm_is_universal_container:
                    new_object_name = object1.nm_container_name + " Container"
                else:
                    new_object_name = object1.global_object_name
                new_object.object_name = new_object_name

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

class BM_OT_CreateArtificialUniContainer_DeselectAll(bpy.types.Operator):
    bl_label = "Deselect All"
    bl_idname = "bakemaster.artificial_container_deselect_all"
    bl_description = "Deselect all chosen objects"
    bl_options = {'UNDO', 'INTERNAL'}

    def execute(self, context):
        bm_props = context.scene.bm_props
        data = {
            'use_include' : False,
            'is_highpoly' : False,
            'is_cage' : False,
        }
        for object_item in bm_props.global_cauc_objects:
            for key in data:
                setattr(object_item, key, data[key])
        return {'FINISHED'}

class BM_OT_CreateArtificialUniContainer(bpy.types.Operator):
    bl_label = "Artificial Container"
    bl_idname = "bakemaster.artificial_container"
    bl_description = "Group detached objects into one Container, where all settings can be set at once along other Container pros"
    bl_options = {'UNDO'}

    def execute(self, context):
        bm_props = context.scene.bm_props

        if bm_props.global_use_name_matching is False:
            self.report({'WARNING'}, "Turn on Name Matching to create artificial container")
            return {'FINISHED'}

        # collect chosen lows, highs, cages
        lowpolies = []
        highpolies = []
        cages = []
        has_any_selected = False
        for object_item in bm_props.global_cauc_objects:
            if object_item.use_include:
                lowpolies.append(object_item.object_name)
                has_any_selected = True
            elif object_item.is_highpoly:
                highpolies.append(object_item.object_name)
                has_any_selected = True
            elif object_item.is_cage:
                cages.append(object_item.object_name)
                has_any_selected = True

        if has_any_selected is False:
            self.report({'INFO'}, "No Objects were selected")
            return {'FINISHED'}

        # trash collected from bm_table_of_objects
        all_chosen_names = lowpolies + highpolies + cages
        to_remove = []
        for index, object in enumerate(context.scene.bm_table_of_objects):
            if object.nm_is_detached and object.global_object_name in all_chosen_names:
                to_remove.append(index)
        for index in sorted(to_remove, reverse=True):
            context.scene.bm_table_of_objects.remove(index)

        last_uni_c_index = -1
        # adding universal container to the bm_table_of_objects
        universal_container = context.scene.bm_table_of_objects.add()
        universal_container.nm_master_index = last_uni_c_index + 1
        # name is set to the root_name of the first object in the shell
        universal_container.nm_container_name_old = BM_ITEM_PROPS_nm_container_name_GlobalUpdate_OnCreate(context, "Bake Job")
        universal_container.nm_container_name = universal_container.nm_container_name_old
        universal_container.nm_this_indent = 0
        universal_container.nm_is_universal_container = True
        universal_container.nm_is_expanded = True

        # objs[] : 0 - lowpolies, 1 - highpolies, 2 - cages
        object_names = [lowpolies, highpolies, cages]
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
                local_container.nm_item_uni_container_master_index = last_uni_c_index + 1
                local_container.nm_is_expanded = True
                setattr(local_container, container_types_props[local_index], True)

                for obj_index, object_name in enumerate(local_names):
                    new_item = context.scene.bm_table_of_objects.add()
                    new_item.global_object_name = object_name
                    new_item.nm_master_index = obj_index
                    new_item.nm_this_indent = 2
                    new_item.nm_item_uni_container_master_index = last_uni_c_index + 1
                    new_item.nm_item_local_container_master_index = local_index
                    new_item.nm_is_expanded = True
                    # setattr(new_item, prefix_props[local_index], True)

        # auto configure decals, highpolies, and cages
        universal_container.nm_uni_container_is_global = True

        # update all nm indexes
        BM_Table_of_Objects_NameMatching_UpdateAllNMIndexes(context)
        
        self.report({'INFO'}, "Container succesfully created")
        return {'FINISHED'}
    
    def draw(self, context):
        bm_props = context.scene.bm_props
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if bm_props.global_use_name_matching is False:
            layout.label(text="Cannot create. Enable Name Matching")
            return
        layout.label(text="Choose Objects to create new Container with:")

        items_box = layout.box()
        items_box.use_property_split = True
        items_box.use_property_decorate = False
        rows = len(bm_props.global_cauc_objects)
        table = items_box.column().row()
        table.template_list('BM_CAUC_UL_Objects_Item', "", bm_props, 'global_cauc_objects', bm_props, 'global_cauc_objects_active_index', rows=rows)
        column = table.column(align=True)
        column.operator(BM_OT_CreateArtificialUniContainer_DeselectAll.bl_idname, text="", icon='CHECKBOX_HLT')

    def invoke(self, context, event):
        wm = context.window_manager
        bm_props = context.scene.bm_props

        # trash
        to_remove = []
        for index, _ in enumerate(bm_props.global_cauc_objects):
            to_remove.append(index)
        for index in sorted(to_remove, reverse=True):
            bm_props.global_cauc_objects.remove(index)

        # add
        if bm_props.global_use_name_matching is False:
            return wm.invoke_props_dialog(self, width=300)
        
        for object in context.scene.bm_table_of_objects:
            if object.nm_is_detached:
                new_item = bm_props.global_cauc_objects.add()
                new_item.object_name = object.global_object_name

        return wm.invoke_props_dialog(self, width=300)

class BM_OT_ReportMessage(bpy.types.Operator):
    bl_label = "BakeMaster Message"
    bl_idname = "bakemaster.report_message"
    bl_options = {'INTERNAL'}
    
    message_type : bpy.props.StringProperty(
        name="Type",
        description="Type of the Report Message",
        default="INFO",
        options={'SKIP_SAVE'})
    message : bpy.props.StringProperty(
        name="Message",
        description="Text of the Report Message",
        default="Message not specified",
        options={'SKIP_SAVE'})
    
    def execute(self, context):
        self.report({self.message_type}, self.message)
        return {'FINISHED'}

    def draw(self, context):
        self.layout.label(text=self.message_type.capitilize())
        try:
            self.layout.label(text=self.message, icon=self.message_type)
        except TypeError:
            self.layout.label(text=self.message)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

class BM_OT_Help(bpy.types.Operator):
    bl_label = "BakeMaster Help"
    bl_idname = "bakemaster.help"
    bl_description = BM_Labels.OPERATOR_HELP_DESCRIPTION
    
    def execute(self, context):
        webbrowser.open(BM_Labels.URL_HELP_BASE)
        return {'FINISHED'}
