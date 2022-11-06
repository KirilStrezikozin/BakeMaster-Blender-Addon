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
from .operators import *
from .operator_bake import BM_OT_ITEM_Bake
from .utils import BM_Object_Get
from .presets import *

class BM_UL_Table_of_Objects_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()   
        # name matching - handling indent and rowman OTs
        if context.scene.bm_props.global_use_name_matching:
            item_draw_ghost = False
            indents = [0, 2, 4, 6]
            for i in range(indents[item.nm_this_indent]):
                row.split(factor=0.1)

            # drawing object
            if not any ([item.nm_is_universal_container, item.nm_is_local_container]):
                # ghost object
                try:
                    context.scene.objects[item.global_object_name]
                except (KeyError, AttributeError, UnboundLocalError):
                    row.label(text=item.global_object_name, icon='GHOST_DISABLED')
                    if not any([item.nm_is_universal_container, item.nm_is_local_container, item.nm_is_detached]):
                        row.prop(item, 'global_use_bake', text="", icon='RESTRICT_RENDER_ON', emboss=False)
                    else:
                        item_draw_ghost = True
                    row.enabled = False
                # normal object
                else:
                    icons = ['MESH_PLANE', 'VIEW_ORTHO', 'SELECT_SET']
                    props = [item.hl_is_lowpoly, item.hl_is_highpoly, item.hl_is_cage]
                    icon_ = [icon for index, icon in enumerate(icons) if props[index] is True]
                    if (len(icon_)):
                        icon = icon_[0]
                    else:
                        icon = 'OUTLINER_OB_MESH'
                    row.label(text=item.global_object_name, icon=icon)
            
            # drawing containers
            else:
                row.emboss = 'NONE'
                icon = 'TRIA_DOWN' if item.nm_is_expanded else 'TRIA_RIGHT'
                row.prop(item, "nm_is_expanded", text="", icon=icon)
                #row.emboss = 'NORMAL'
                row.prop(item, "nm_container_name", text="")
            
            # drawing use_bake for universal and detached
            if item.nm_is_universal_container or item.nm_is_detached:
                if item.global_use_bake:
                    icon = 'RESTRICT_RENDER_OFF'
                else:
                    row.active = False
                    icon = 'RESTRICT_RENDER_ON'
                if item_draw_ghost:
                    icon = 'RESTRICT_RENDER_ON'
                    row.active = False
                # row.use_property_decorate = False
                row.prop(item, 'global_use_bake', text="", icon=icon, emboss=False)
            # set row.active to False for items the use_bake of uni_container of which is False
            else:
                for object in context.scene.bm_table_of_objects:
                    if object.nm_is_universal_container and object.nm_master_index == item.nm_item_uni_container_master_index and object.global_use_bake is False:
                        row.active = False
                        break
        
        # no name matching - default table
        else:
            # ghost object
            try:
                context.scene.objects[item.global_object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                row.label(text=item.global_object_name, icon='GHOST_DISABLED')
                row.prop(item, 'global_use_bake', text="", icon='RESTRICT_RENDER_ON', emboss=False)
                row.enabled = False
            # normal object
            else:
                row.label(text=item.global_object_name, icon='OUTLINER_OB_MESH')

                if item.global_use_bake:
                    icon = 'RESTRICT_RENDER_OFF'
                else:
                    row.active = False
                    icon = 'RESTRICT_RENDER_ON'
                # row.use_property_decorate = False
                row.prop(item, 'global_use_bake', text="", icon=icon, emboss=False)

    def draw_filter(self, context, layout):
        pass
    
    def filter_items(self, context, data, propname):
        """
        Filter and order items
        When nm is on, filtered = [items under not collapsed nm_container]
        else, filtered = [all items]
        """
        # data collection class
        items = getattr(data, propname)
        # default return values
        ftl_flags = []
        ftl_neworder = []

        # initialize with all items visible
        if context.scene.bm_props.global_use_name_matching is False:
            ftl_flags = [self.bitflag_filter_item] * len(items)
            ftl_neworder = [index for index, _ in enumerate(items)]
            
        # initialize with items unvisible if items' parent container nm_is_expanded is False
        else:
            ftl_flags = [self.bitflag_filter_item] * len(items)
            for global_index, global_object in enumerate(items):
                # visible universal container, all its items unvisible
                if global_object.nm_is_universal_container and global_object.nm_is_expanded is False:
                    ftl_neworder.append(global_index)
                    for local_index, local_object in enumerate(items):
                        if local_object.nm_item_uni_container_master_index == global_object.nm_master_index:
                            ftl_flags[local_index] &= ~self.bitflag_filter_item
                # visible local container, all its items unvisible
                elif global_object.nm_is_local_container and global_object.nm_is_expanded is False:
                    ftl_neworder.append(global_index)
                    for local_index, local_object in enumerate(items):
                        if local_object.nm_item_uni_container_master_index == global_object.nm_item_uni_container_master_index and local_object.nm_item_local_container_master_index == global_object.nm_master_index:
                            ftl_flags[local_index] &= ~self.bitflag_filter_item
            ftl_neworder = sorted([index for index, item in enumerate(items) if ftl_flags[index] == ~self.bitflag_filter_item])

        return ftl_flags, ftl_neworder

    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Objects_Item_Highpoly(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_item_index
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'global_object_name', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Maps_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_map_index
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'global_map_type', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Maps_Item_Highpoly(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_item_index
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'global_object_name', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Objects_Item_ChannelPack(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_channelpack_index
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'global_channelpack_name', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_TextureSets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_textureset_index
        split_factor = 1-0.05*3 if len(str(index_value)) < 4 else len(str(index_value))
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=split_factor)
        if bpy.app.version > (2, 91, 0):
            icon = 'OUTLINER_COLLECTION'
        else:
            icon = 'GROUP'
        split.column().prop(item, 'global_textureset_name', text="", icon=icon)
        index_column = split.column()
        index_column.label(text=str(index_value))

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_TextureSets_Objects_Table_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_object_index
        split_factor = 1-0.05*3 if len(str(index_value)) < 4 else len(str(index_value))
        
        icon = 'BLANK1'
        if item.global_object_name != 'NONE':
            object = context.scene.bm_table_of_objects[item.global_source_object_index]
            try:
                context.scene.objects[object.global_object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                icon = 'GHOST_DISABLED'
                layout.active = False

            if context.scene.bm_props.global_use_name_matching and object.nm_is_universal_container:
                icon = 'TRIA_RIGHT'
                layout.active = True
            elif layout.active:
                icon = 'OUTLINER_OB_MESH'

            if object.global_use_bake is False:
                layout.active = False

        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=split_factor)
        split.column().prop(item, 'global_object_name', text="", icon=icon)
        index_column = split.column()
        index_column.label(text=str(index_value))

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_TextureSets_Objects_Table_Item_SubItem(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_object_index
        split_factor = 1-0.05*3 if len(str(index_value)) < 4 else len(str(index_value))
        
        # icon = 'MESH_PLANE'
        source_object = [object for object in context.scene.bm_table_of_objects if object.global_object_name == item.global_object_name][0]

        if source_object.global_use_bake is False:
            layout.active = False
        try:
            context.scene.objects[source_object.global_object_name]
        except (KeyError, AttributeError, UnboundLocalError):
            # icon = 'GHOST_DISABLED'
            layout.active = False

        row = layout.row()
        split = row.split(factor=split_factor)
        name_column = split.row()
        name_column.prop(item, 'global_object_include_in_texset', text="")
        row.emboss = 'NONE'
        name_column_row = name_column.row()
        name_column_row.label(text=item.global_object_name)
        index_column = split.column()
        index_column.label(text=str(index_value))
        row.active = item.global_object_include_in_texset

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Objects_Item_BatchNamingTable_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.emboss = 'NONE'
        layout.prop(item, 'global_keyword', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_PT_MainBase(bpy.types.Panel):
    bl_label = "BakeMaster"
    bl_idname = 'BM_PT_Main'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        row.operator(BM_OT_Table_of_Objects_Add.bl_idname, text="Add", icon='ADD')
        row.operator(BM_OT_Table_of_Objects_Remove.bl_idname, text="Remove", icon='REMOVE')
        row.scale_y = 1.15

        refresh = False
        is_len = True if len(scene.bm_table_of_objects) else False
        min_rows = 5 if is_len else 4
        for index, object in enumerate(scene.bm_table_of_objects):
            try:
                scene.objects[object.global_object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                if scene.bm_props.global_use_name_matching and any([object.nm_is_universal_container, object.nm_is_local_container]):
                    continue
                refresh = True
                min_rows += 1
                break
        if is_len and not BM_Object_Get(context)[1]:
            min_rows -= 1

        if len(scene.bm_table_of_objects) > min_rows:
            rows = len(scene.bm_table_of_objects)
            # decrease number of rows for every hidden item
            checked_unis = []
            if scene.bm_props.global_use_name_matching:
                for global_index, global_object in enumerate(scene.bm_table_of_objects):
                    # visible universal container, all its items unvisible
                    if global_object.nm_is_universal_container and global_object.nm_is_expanded is False:
                        checked_unis.append(global_object.nm_master_index)
                        for local_object in scene.bm_table_of_objects:
                            if local_object.nm_item_uni_container_master_index == global_object.nm_master_index and rows > min_rows:
                                rows -= 1
                    # visible local container, all its items unvisible
                    elif global_object.nm_is_local_container and global_object.nm_is_expanded is False:
                        if global_object.nm_item_uni_container_master_index in checked_unis:
                            continue
                        for local_object in scene.bm_table_of_objects:
                            if local_object.nm_item_uni_container_master_index == global_object.nm_item_uni_container_master_index and local_object.nm_item_local_container_master_index == global_object.nm_master_index and rows > min_rows:
                                rows -= 1
        else:
            rows = min_rows
        
        row = box.row()
        row.template_list('BM_UL_Table_of_Objects_Item', "", scene, 'bm_table_of_objects', scene.bm_props, 'global_active_index', rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_Table_of_Objects.bl_idname, text="", icon='TRIA_UP').control = 'UP'
        col.operator(BM_OT_Table_of_Objects.bl_idname, text="", icon='TRIA_DOWN').control = 'DOWN'
        col.separator()

        col.prop(scene.bm_props, 'global_use_name_matching', text="", icon='OUTLINER_OB_FONT')

        col.emboss = 'NONE'

        if refresh:
            col.separator()
            col.operator(BM_OT_Table_of_Objects_Refresh.bl_idname, text="", icon='FILE_REFRESH')
        col.separator()

        if len(scene.bm_table_of_objects):
            object = BM_Object_Get(context)
            if (object[1] is True) or (scene.bm_props.global_use_name_matching and any([object[0].nm_is_universal_container, object[0].nm_is_local_container])): # and object[0].use_source is False:
                BM_PT_ObjectConfigurator_Presets.draw_panel_header(col)
                col.separator()

        col.operator(BM_OT_Table_of_Objects_Trash.bl_idname, text="", icon='TRASH')

class BM_PT_ItemBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.bm_table_of_objects) > 0

    def draw_header(self, context):
        object = BM_Object_Get(context)
        label = object[0].global_object_name
        label_end = ""
        icon = 'PROPERTIES'
        if context.scene.bm_props.global_use_name_matching and any([object[0].nm_is_universal_container, object[0].nm_is_local_container]):
            label_end = "Container"
            if object[0].nm_is_universal_container:
                label = object[0].nm_container_name
            else:
                for object1 in context.scene.bm_table_of_objects:
                    if object1.nm_is_universal_container and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                        label = object1.nm_container_name
                        label_end = "{} Container".format(object[0].nm_container_name)
                        break
        self.layout.label(text="{} {}".format(label, label_end), icon=icon)

    def draw(self, context):
        object = BM_Object_Get(context)
        if any([object[0].nm_is_universal_container, object[0].nm_is_local_container]):
            return
        try:
            context.scene.objects[object[0].global_object_name]
        except (KeyError, AttributeError):
            label = "Object cannot be found"
            icon = 'GHOST_DISABLED'
            self.layout.label(text=label, icon=icon)

class BM_PT_Item_ObjectBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Object'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = BM_Object_Get(context)
        if any([object[0].nm_is_universal_container, object[0].nm_is_local_container]):
            return True
        try:
            context.scene.objects[object[0].global_object_name]
        except (KeyError, AttributeError):
            return False
        else:
            return True

    def draw_header(self, context):
        object = BM_Object_Get(context)[0]
        if context.scene.bm_props.global_use_name_matching and any([object.nm_is_universal_container, object.nm_is_local_container]):
            label = "Container"
        else:
            label = "Object"
        self.layout.label(text=label)
        BM_PT_MapsConfigurator_Presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = BM_Object_Get(context)[0]

        # hl
        hl_box = layout.box()
        hl_box.use_property_split = True
        hl_box.use_property_decorate = False

        # hl header
        hl_box_header = hl_box.row(align=True)
        hl_box_header.use_property_split = False
        hl_box_header.emboss = 'NONE'
        icon = 'TRIA_DOWN' if scene.bm_props.global_is_hl_panel_expanded else 'TRIA_RIGHT'
        hl_box_header.prop(scene.bm_props, 'global_is_hl_panel_expanded', text="", icon=icon)
        hl_box_header.emboss = 'NORMAL'
        hl_box_header.label(text="High to Lowpoly")
        BM_PT_MapsConfigurator_Presets.draw_panel_header(hl_box_header)

        # hl body
        if scene.bm_props.global_is_hl_panel_expanded:
            hl_box.prop(object, 'hl_use_unique_per_map')

            if object.hl_use_unique_per_map is False:
                # highpoly
                if len(object.hl_highpoly_table) > 1:
                    rows = len(object.hl_highpoly_table)
                else:
                    rows = 1
                hl_box_highpoly_frame = hl_box.split(factor=0.4)
                hl_box_highpoly_frame.column()
                hl_box_highpoly = hl_box_highpoly_frame.column()
                label = "Highpoly" if len(object.hl_highpoly_table) <= 1 else "Highpolies"
                hl_box_highpoly.label(text=label)
                hl_box_highpoly_table = hl_box_highpoly.column().row()
                hl_box_highpoly_table.template_list('BM_UL_Table_of_Objects_Item_Highpoly', "", object, 'hl_highpoly_table', object, 'hl_highpoly_table_active_index', rows=rows)
                hl_highpoly_table_column = hl_box_highpoly_table.column(align=True)
                hl_highpoly_table_column.operator(BM_OT_ITEM_Highpoly_Table_Add.bl_idname, text="", icon='ADD')
                hl_highpoly_table_column.operator(BM_OT_ITEM_Highpoly_Table_Remove.bl_idname, text="", icon='REMOVE')
                # cage
                hl_box_cage = hl_box.column(align=True)
                hl_box_cage.prop(object, 'hl_use_cage')
                if object.hl_use_cage:
                    hl_box_cage.prop(object, 'hl_cage_type')
                    if object.hl_cage_type == 'STANDARD':
                        if object.hl_cage == 'NONE':
                            label = "Extrusion"
                        else:
                            label = "Cage Extrusion"
                        hl_box_cage.prop(object, 'hl_cage_extrusion', text=label)
                        if bpy.app.version >= (2, 90, 0):
                            hl_box_cage.prop(object, 'hl_max_ray_distance')
                        hl_box_cage.prop(object, 'hl_cage')
                    else:
                        hl_box_cage.prop(object, 'hl_cage_extrusion', text="Extrusion")
        
        # uv
        uv_box = layout.box()
        uv_box.use_property_split = True
        uv_box.use_property_decorate = False

        # uv header
        uv_box_header = uv_box.row(align=True)
        uv_box_header.use_property_split = False
        uv_box_header.emboss = 'NONE'
        icon = 'TRIA_DOWN' if scene.bm_props.global_is_uv_panel_expanded else 'TRIA_RIGHT'
        uv_box_header.prop(scene.bm_props, 'global_is_uv_panel_expanded', text="", icon=icon)
        uv_box_header.emboss = 'NORMAL'
        uv_box_header.label(text="UVs and Layers")
        BM_PT_MapsConfigurator_Presets.draw_panel_header(uv_box_header)

        # uv body
        if scene.bm_props.global_is_uv_panel_expanded:
            uv_box.prop(object, 'uv_use_unique_per_map')

            if object.uv_use_unique_per_map is False:
                # uv
                uv_box.prop(object, 'uv_bake_target')
                if object.uv_bake_target == 'IMAGE_TEXTURES':
                    uv_box_column = uv_box.column(align=True)
                    uv_box_column.prop(object, 'uv_active_layer')
                    uv_box_column.prop(object, 'uv_type')
                    uv_box_column.prop(object, 'uv_snap_islands_to_pixels')
                    if object.uv_type == 'SINGLE':
                        uv_box_column = uv_box.column()
                        uv_box_column.prop(object, 'uv_use_auto_unwrap')
                        if object.uv_use_auto_unwrap:
                            uv_box_column.prop(object, 'uv_auto_unwrap_angle_limit')
                            uv_box_column.prop(object, 'uv_auto_unwrap_island_margin')
                            uv_box_column.prop(object, 'uv_auto_unwrap_use_scale_to_bounds')

        # shading
        csh_box = layout.box()
        csh_box.use_property_split = True
        csh_box.use_property_decorate = False

        # shading header
        csh_box_header = csh_box.row(align=True)
        csh_box_header.use_property_split = False
        csh_box_header.emboss = 'NONE'
        icon = 'TRIA_DOWN' if scene.bm_props.global_is_csh_panel_expanded else 'TRIA_RIGHT'
        csh_box_header.prop(scene.bm_props, 'global_is_csh_panel_expanded', text="", icon=icon)
        csh_box_header.emboss = 'NORMAL'
        csh_box_header.label(text="Shading")
        BM_PT_MapsConfigurator_Presets.draw_panel_header(csh_box_header)

        # shading body
        if scene.bm_props.global_is_csh_panel_expanded:
            # shading
            csh_box.prop(object, 'csh_use_triangulate_lowpoly')
            csh_box_column = csh_box.column()
            csh_box_column.prop(object, 'csh_use_lowpoly_reset_normals')
            csh_box_column.prop(object, 'csh_lowpoly_use_smooth')
            if object.csh_lowpoly_use_smooth:
                csh_box_column.prop(object, 'csh_lowpoly_smoothing_groups_enum', text="Type")
                if object.csh_lowpoly_smoothing_groups_enum == 'AUTO':
                    csh_box_column.prop(object, 'csh_lowpoly_smoothing_groups_angle')
                if object.csh_lowpoly_smoothing_groups_enum == 'VERTEX_GROUPS':
                    csh_box_column.prop(object, 'csh_lowpoly_smoothing_groups_name_contains')
            csh_box_column = csh_box.column()
            csh_box_column.prop(object, 'csh_use_highpoly_reset_normals')
            csh_box_column.prop(object, 'csh_highpoly_use_smooth')
            if object.csh_highpoly_use_smooth:
                csh_box_column.prop(object, 'csh_highpoly_smoothing_groups_enum', text="Type")
                if object.csh_highpoly_smoothing_groups_enum == 'AUTO':
                    csh_box_column.prop(object, 'csh_highpoly_smoothing_groups_angle')
                if object.csh_highpoly_smoothing_groups_enum == 'VERTEX_GROUPS':
                    csh_box_column.prop(object, 'csh_highpoly_smoothing_groups_name_contains')

class BM_PT_Item_MapsBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Maps'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = BM_Object_Get(context)
        if any([object[0].nm_is_universal_container, object[0].nm_is_local_container]):
            return True
        try:
            context.scene.objects[object[0].global_object_name]
        except (KeyError, AttributeError):
            return False
        else:
            return True

    def draw_header(self, context):
        label = "Maps"
        self.layout.label(text=label)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = BM_Object_Get(context)[0]
    
        # maps table
        maps_table_box = layout.box()
        maps_table_row = maps_table_box.row()

        if len(object.global_maps) > 4:
            rows = len(object.global_maps)
        else:
            rows = 4
        
        maps_table_row.template_list('BM_UL_Table_of_Maps_Item', "", object, 'global_maps', object, 'global_maps_active_index', rows=rows)
        maps_table_column = maps_table_row.column(align=True)
        maps_table_column.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='ADD').control = 'ADD'
        maps_table_column.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='REMOVE').control = 'REMOVE'
        maps_table_column.separator(factor=1.0)
        BM_PT_MapsConfigurator_Presets.draw_panel_header(maps_table_column)
        maps_table_column.separator(factor=1.0)
        maps_table_column.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='TRASH').control = 'TRASH'

        # map settings
        if len(object.global_maps):
            map = BM_Map_Get(object)
            # format 
            format_box = layout.box()
            format_box.use_property_split = True
            format_box.use_property_decorate = False

            # format header
            format_box_header = format_box.row()
            format_box_header.use_property_split = False
            format_box_header.emboss = 'NONE'
            icon = 'TRIA_DOWN' if scene.bm_props.global_is_format_panel_expanded else 'TRIA_RIGHT'
            format_box_header.prop(scene.bm_props, 'global_is_format_panel_expanded', text="", icon=icon)
            format_box_header.emboss = 'NORMAL'

            # draw format for all maps
            if object.out_use_unique_per_map is False:
                format_box_header.label(text="Format")
                BM_PT_MapsConfigurator_Presets.draw_panel_header(format_box_header)
                format_prop_collection = object
            # draw format unique per map
            else:
                format_box_header.label(text="Map Format")
                BM_PT_MapsConfigurator_Presets.draw_panel_header(format_box_header)
                format_prop_collection = map

            # format body
            if scene.bm_props.global_is_format_panel_expanded:
                format_box.prop(object, 'out_use_unique_per_map')
                # format
                format_box_column = format_box.column(align=True)
                format_box_column.prop(format_prop_collection, 'out_file_format')
                if format_prop_collection.out_file_format == 'PSD':
                    format_box_column.prop(format_prop_collection, 'out_psd_include')
                elif format_prop_collection.out_file_format == 'OPEN_EXR':
                    format_box_column.prop(format_prop_collection, 'out_exr_codec')
                elif format_prop_collection.out_file_format == 'PNG':
                    format_box_column.prop(format_prop_collection, 'out_compression')
                format_box_column = format_box.column(align=True)
                format_box_column.prop(format_prop_collection, 'out_res', text="Resolution")
                if format_prop_collection.out_res == 'CUSTOM':
                    format_box_column.prop(format_prop_collection, 'out_res_height')
                    format_box_column.prop(format_prop_collection, 'out_res_width')
                elif format_prop_collection.out_res == 'TEXEL':
                    format_box_column.prop(format_prop_collection, 'out_texel_density_value')
                    format_box_column.prop(format_prop_collection, 'out_texel_density_match')
                format_box_column = format_box.column(align=True)
                if bpy.app.version >= (3, 1, 0):
                    format_box_column.prop(format_prop_collection, 'out_margin_type')
                format_box_column.prop(format_prop_collection, 'out_margin')
                format_box_column = format_box.column(align=True)
                format_box_column.prop(format_prop_collection, 'out_use_32bit')
                format_box_column.prop(format_prop_collection, 'out_use_alpha')
                if format_prop_collection.uv_type == 'TILED':
                    format_box_column = format_box.column(align=True)
                    format_box_column.prop(format_prop_collection, 'out_udim_start_tile', text="Start Tile")
                    format_box_column.prop(format_prop_collection, 'out_udim_end_tile', text="End Tile")
                format_box.prop(format_prop_collection, 'out_super_sampling_aa')
                format_box_column = format_box.column(align=True)
                format_box_column.prop(format_prop_collection, 'out_use_adaptive_sampling')
                if format_prop_collection.out_use_adaptive_sampling:
                    format_box_column.prop(format_prop_collection, 'out_adaptive_threshold')
                    format_box_column.prop(format_prop_collection, 'out_samples', text="Bake Max Samples")
                    format_box_column.prop(format_prop_collection, 'out_min_samples')
                else:
                    format_box_column.prop(format_prop_collection, 'out_samples')
                format_box.prop(format_prop_collection, 'out_use_denoise')            

            # map settings column
            map_settings_column = maps_table_box.column()
            map_settings_column.use_property_split = True
            map_settings_column.use_property_decorate = False

            # map settings body
            if (object.hl_use_unique_per_map is False and len(object.hl_highpoly_table) > 0) or (object.hl_use_unique_per_map and len(map.hl_highpoly_table)):
                map_settings_column.prop(map, 'global_affect_by_hl', text="Affect by Highpoly")
            map_types_settings = [
                'NORMAL',
                'DISPLACEMENT',
                'VECTOR_DISPLACEMENT',
                'AO',
                'CAVITY',
                'CURVATURE',
                'THICKNESS',
                'ID',
                'MASK',
                'XYZMASK',
                'GRADIENT',
                'EDGE',
                'WIREFRAME',
                'PASS',
                'C_COMBINED',
                'C_NORMAL',
                'C_DIFFUSE',
                'C_GLOSSY',
                'C_TRANSMISSION']
            if map.global_map_type in map_types_settings:
                map_settings_column = maps_table_box.column()#align=True)
                map_settings_column.use_property_split = True
                map_settings_column.use_property_decorate = False

            # Pass and Cycles Maps
            if map.global_map_type == 'PASS':
                map_settings_column.prop(map, 'map_pass_type')
            
            elif map.global_map_type == 'C_NORMAL':
                map_settings_column.prop(map, 'map_normal_space', text="Space")
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_normal_r', text="Swizzle R")
                sub.prop(map, 'map_normal_g', text="G")
                sub.prop(map, 'map_normal_b', text="B")

            elif map.global_map_type == 'C_COMBINED':
                row = map_settings_column.row(align=True)
                row.use_property_split = False
                row.prop(map, 'map_cycles_use_pass_direct', toggle=True)
                row.prop(map, 'map_cycles_use_pass_indirect', toggle=True)
                flow = map_settings_column.grid_flow(row_major=False, columns=0, even_columns=False, even_rows=False, align=True)
                flow.active = map.map_cycles_use_pass_direct or map.map_cycles_use_pass_indirect
                flow.prop(map, 'map_cycles_use_pass_diffuse')
                flow.prop(map, 'map_cycles_use_pass_glossy')
                flow.prop(map, 'map_cycles_use_pass_transmission')
                if bpy.app.version < (3, 0, 0):
                    flow.prop(map, 'map_cycles_use_pass_ambient_occlusion')
                flow.prop(map, 'map_cycles_use_pass_emit')

            elif map.global_map_type in ['C_DIFFUSE', 'C_GLOSSY', 'C_TRANSMISSION']:
                row = map_settings_column.row(align=True)
                row.use_property_split = False
                row.prop(map, 'map_cycles_use_pass_direct', toggle=True)
                row.prop(map, 'map_cycles_use_pass_indirect', toggle=True)
                row.prop(map, 'map_cycles_use_pass_color', toggle=True)
            
            # Object-based Maps
            elif map.global_map_type == 'NORMAL':
                map_settings_column.prop(map, 'map_normal_space')
                map_settings_column.prop(map, 'map_normal_preset')
                if map.map_normal_preset == 'CUSTOM':
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_normal_custom_preset')
                    if map.map_normal_custom_preset == 'CUSTOM':
                        sub.prop(map, 'map_normal_r', text="Swizzle R")
                        sub.prop(map, 'map_normal_g', text="G")
                        sub.prop(map, 'map_normal_b', text="B")

            elif map.global_map_type == 'DISPLACEMENT':
                map_settings_column.prop(map, 'map_displacement_data')
                map_settings_column.prop(map, 'map_displacement_result')
                if map.map_displacement_result == 'MODIFIER':
                    map_settings_column.prop(map, 'map_displacement_subdiv_levels')
                    try:
                        object_pointer = scene.objects[object.global_object_name]
                        face_count = len(object_pointer.data.polygons) * 4 ** map.map_displacement_subdiv_levels # future face count
                        map_settings_column.label(text="Face count while baking: " + str(face_count))
                    except KeyError:
                        pass
        
            elif map.global_map_type == 'VECTOR_DISPLACEMENT':
                map_settings_column.prop(map, 'map_vector_displacement_use_default')
                if map.map_vector_displacement_use_default is False:
                    map_settings_column.prop(map, 'map_vector_diplacement_use_negative')
                    map_settings_column.prop(map, 'map_vector_displacement_result')
                    if map.map_vector_displacement_result == 'MODIFIER':
                        map_settings_column.prop(map, 'map_vector_displacement_subdiv_levels')
                        try:
                            object_pointer = scene.objects[object.global_object_name]
                            face_count = len(object_pointer.data.polygons) * 4 ** map.map_vector_displacement_subdiv_levels # future face count
                            map_settings_column.label(text="Face count while baking: " + str(face_count))
                        except KeyError:
                            pass

            # Masks and Details Maps
            elif map.global_map_type == 'AO':
                map_settings_column.prop(map, 'map_ao_use_preview')
                map_settings_column.prop(map, 'map_ao_use_default')
                if map.map_ao_use_default is False:
                    map_settings_column.prop(map, 'map_ao_samples', slider=True)
                    map_settings_column.prop(map, 'map_ao_distance')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_ao_black_point', slider=True)
                    sub.prop(map, 'map_ao_white_point', slider=True)
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_ao_brightness')
                    sub.prop(map, 'map_ao_contrast')
                    sub.prop(map, 'map_ao_opacity', slider=True)
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_ao_use_local')
                    sub.prop(map, 'map_ao_use_invert', slider=True)

            elif map.global_map_type == 'CAVITY':
                map_settings_column.prop(map, 'map_cavity_use_preview')
                map_settings_column.prop(map, 'map_cavity_use_default')
                if map.map_cavity_use_default is False:
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_cavity_black_point', slider=True)
                    sub.prop(map, 'map_cavity_white_point', slider=True)
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_cavity_power')
                    sub.prop(map, 'map_cavity_use_invert', slider=True)

            elif map.global_map_type == 'CURVATURE':
                map_settings_column.prop(map, 'map_curv_use_preview')
                map_settings_column.prop(map, 'map_curv_use_default')
                if map.map_curv_use_default is False:
                    map_settings_column.prop(map, 'map_curv_samples', slider=True)
                    map_settings_column.prop(map, 'map_curv_radius')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_curv_black_point', slider=True)
                    sub.prop(map, 'map_curv_mid_point', slider=True)
                    sub.prop(map, 'map_curv_white_point', slider=True)
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_curv_body_gamma')
                    sub.prop(map, 'map_curv_use_invert', slider=True)

            elif map.global_map_type == 'THICKNESS':
                map_settings_column.prop(map, 'map_thick_use_preview')
                map_settings_column.prop(map, 'map_thick_use_default')
                if map.map_thick_use_default is False:
                    map_settings_column.prop(map, 'map_thick_samples', slider=True)
                    map_settings_column.prop(map, 'map_thick_distance')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_thick_black_point', slider=True)
                    sub.prop(map, 'map_thick_white_point', slider=True)
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_thick_brightness')
                    sub.prop(map, 'map_thick_contrast')
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_thick_use_invert', slider=True)

            elif map.global_map_type == 'ID':
                map_settings_column.prop(map, 'map_matid_data')
                if map.map_matid_data == 'VERTEX_GROUPS':
                    map_settings_column.prop(map, 'map_matid_vertex_groups_name_contains')
                map_settings_column.prop(map, 'map_matid_algorithm')
            
            elif map.global_map_type == 'MASK':
                map_settings_column.prop(map, 'map_mask_data')
                if map.map_mask_data == 'VERTEX_GROUPS':
                    map_settings_column.prop(map, 'map_mask_vertex_groups_name_contains')
                elif map.map_mask_data == 'MATERIALS':
                    map_settings_column.prop(map, 'map_mask_materials_name_contains')
                map_settings_column.prop(map, 'map_mask_color1')
                map_settings_column.prop(map, 'map_mask_color2')

            elif map.global_map_type == 'XYZMASK':
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_xyzmask_use_x')
                sub.prop(map, 'map_xyzmask_use_y')
                sub.prop(map, 'map_xyzmask_use_z')
                sub.prop(map, 'map_xyzmask_use_preview')     
                sub.prop(map, 'map_xyzmask_use_default')
                if not map.map_xyzmask_use_default:
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_xyzmask_coverage')
                    sub.prop(map, 'map_xyzmask_saturation')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_xyzmask_opacity', slider=True)
                    sub.prop(map, 'map_xyzmask_use_invert', slider=True)

            elif map.global_map_type == 'GRADIENT':
                map_settings_column.prop(map, 'map_gmask_use_preview')
                map_settings_column.prop(map, 'map_gmask_type')
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_gmask_location_x')
                sub.prop(map, 'map_gmask_location_y')
                sub.prop(map, 'map_gmask_location_z')
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_gmask_rotation_x')
                sub.prop(map, 'map_gmask_rotation_y')
                sub.prop(map, 'map_gmask_rotation_z')
                sub = map_settings_column.column()
                sub.prop(map, 'map_gmask_use_default')
                if not map.map_gmask_use_default: 
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_gmask_scale_x')
                    sub.prop(map, 'map_gmask_scale_y')
                    sub.prop(map, 'map_gmask_scale_z')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_gmask_coverage')
                    sub.prop(map, 'map_gmask_contrast')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_gmask_saturation')
                    sub.prop(map, 'map_gmask_opacity', slider=True)
                    sub.prop(map, 'map_gmask_use_invert', slider=True)

            elif map.global_map_type == 'EDGE':
                map_settings_column.prop(map, 'map_edgemask_use_preview')
                map_settings_column.prop(map, 'map_edgemask_use_default')
                if map.map_edgemask_use_default is False:
                    map_settings_column.prop(map, 'map_edgemask_samples', slider=True)
                    map_settings_column.prop(map, 'map_edgemask_radius')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_edgemask_edge_contrast')
                    sub.prop(map, 'map_edgemask_body_contrast')
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_edgemask_use_invert')
            
            elif map.global_map_type == 'WIREFRAME':
                map_settings_column.prop(map, 'map_wireframemask_line_thickness')
                map_settings_column.prop(map, 'map_wireframemask_use_invert')
        
            # unique map settings
            # hl
            if object.hl_use_unique_per_map:
                hl_box = layout.box()
                hl_box.use_property_split = True
                hl_box.use_property_decorate = False
        
                # hl header
                hl_box_header = hl_box.row(align=True)
                hl_box_header.use_property_split = False
                hl_box_header.emboss = 'NONE'
                icon = 'TRIA_DOWN' if scene.bm_props.local_is_hl_panel_expanded else 'TRIA_RIGHT'
                hl_box_header.prop(scene.bm_props, 'local_is_hl_panel_expanded', text="", icon=icon)
                hl_box_header.emboss = 'NORMAL'
                hl_box_header.label(text="Map High to Lowpoly")
                BM_PT_MapsConfigurator_Presets.draw_panel_header(hl_box_header)

                # hl body
                if scene.bm_props.local_is_hl_panel_expanded:
                    if len(map.hl_highpoly_table) > 1:
                        rows = len(map.hl_highpoly_table)
                    else:
                        rows = 1
                    hl_box_highpoly_frame = hl_box.split(factor=0.4)
                    hl_box_highpoly_frame.column()
                    hl_box_highpoly = hl_box_highpoly_frame.column()
                    label = "Highpoly" if len(map.hl_highpoly_table) <= 1 else "Highpolies"
                    hl_box_highpoly.label(text=label)
                    hl_box_highpoly_table = hl_box_highpoly.column().row()
                    hl_box_highpoly_table.template_list('BM_UL_Table_of_Maps_Item_Highpoly', "", map, 'hl_highpoly_table', map, 'hl_highpoly_table_active_index', rows=rows)
                    hl_highpoly_table_column = hl_box_highpoly_table.column(align=True)
                    hl_highpoly_table_column.operator(BM_OT_MAP_Highpoly_Table_Add.bl_idname, text="", icon='ADD')
                    hl_highpoly_table_column.operator(BM_OT_MAP_Highpoly_Table_Remove.bl_idname, text="", icon='REMOVE')
                    # cage
                    hl_box_cage = hl_box.column(align=True)
                    hl_box_cage.prop(map, 'hl_use_cage')
                    if map.hl_use_cage:
                        hl_box_cage.prop(map, 'hl_cage_type')
                        if map.hl_cage_type == 'STANDARD':
                            if map.hl_cage == 'NONE':
                                label = "Extrusion"
                            else:
                                label = "Cage Extrusion"
                            hl_box_cage.prop(map, 'hl_cage_extrusion', text=label)
                            if bpy.app.version >= (2, 90, 0):
                                hl_box_cage.prop(map, 'hl_max_ray_distance')
                            hl_box_cage.prop(map, 'hl_cage')
                        else:
                            hl_box_cage.prop(map, 'hl_cage_extrusion', text="Extrusion")
        
            # uv
            if object.uv_use_unique_per_map:
                uv_box = layout.box()
                uv_box.use_property_split = True
                uv_box.use_property_decorate = False

                # uv header
                uv_box_header = uv_box.row(align=True)
                uv_box_header.use_property_split = False
                uv_box_header.emboss = 'NONE'
                icon = 'TRIA_DOWN' if scene.bm_props.local_is_uv_panel_expanded else 'TRIA_RIGHT'
                uv_box_header.prop(scene.bm_props, 'local_is_uv_panel_expanded', text="", icon=icon)
                uv_box_header.emboss = 'NORMAL'
                uv_box_header.label(text="Map UVs and Layers")
                BM_PT_MapsConfigurator_Presets.draw_panel_header(uv_box_header)

                # uv body
                if scene.bm_props.local_is_uv_panel_expanded:
                    uv_box.prop(map, 'uv_bake_target')
                    if map.uv_bake_target == 'IMAGE_TEXTURES':
                        uv_box_column = uv_box.column(align=True)
                        uv_box_column.prop(map, 'uv_active_layer')
                        uv_box_column.prop(map, 'uv_type')
                        uv_box_column.prop(map, 'uv_snap_islands_to_pixels')
                        if map.uv_type == 'SINGLE':
                            uv_box_column = uv_box.column()
                            uv_box_column.prop(map, 'uv_use_auto_unwrap')
                            if map.uv_use_auto_unwrap:
                                uv_box_column.prop(map, 'uv_auto_unwrap_angle_limit')
                                uv_box_column.prop(map, 'uv_auto_unwrap_island_margin')
                                uv_box_column.prop(map, 'uv_auto_unwrap_use_scale_to_bounds')

class BM_PT_Item_OutputBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Output'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = BM_Object_Get(context)
        if any([object[0].nm_is_universal_container, object[0].nm_is_local_container]):
            return True
        try:
            context.scene.objects[object[0].global_object_name]
        except (KeyError, AttributeError):
            return False
        else:
            return True

    def draw_header(self, context):
        label = "Output"
        self.layout.label(text=label)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = BM_Object_Get(context)[0]


        # channel packing
        if len(object.global_maps):
            chnlpack_box = layout.box()
            chnlpack_box.use_property_split = True
            chnlpack_box.use_property_decorate = False

            # channel packing header
            chnlpack_box_header = chnlpack_box.row()
            chnlpack_box_header.use_property_split = False
            chnlpack_box_header.emboss = 'NONE'
            icon = 'TRIA_DOWN' if scene.bm_props.global_is_chnlpack_panel_expanded else 'TRIA_RIGHT'
            chnlpack_box_header.prop(scene.bm_props, 'global_is_chnlpack_panel_expanded', text="", icon=icon)
            chnlpack_box_header.emboss = 'NORMAL'
            chnlpack_box_header.label(text="Channel Packing")
            BM_PT_MapsConfigurator_Presets.draw_panel_header(chnlpack_box_header)

            # channel packing body
            if scene.bm_props.global_is_chnlpack_panel_expanded:
                row = chnlpack_box.row()

                if len(object.chnlp_channelpacking_table) > 3:
                    rows = len(object.chnlp_channelpacking_table)
                else:
                    rows = 3
        
                row.template_list('BM_UL_Table_of_Objects_Item_ChannelPack', "", object, 'chnlp_channelpacking_table', object, 'chnlp_channelpacking_table_active_index', rows=rows)
                chnlpack_box_column = row.column(align=True)
                chnlpack_box_column.operator(BM_OT_ITEM_ChannelPack_Table_Add.bl_idname, text="", icon='ADD')
                chnlpack_box_column.operator(BM_OT_ITEM_ChannelPack_Table_Remove.bl_idname, text="", icon='REMOVE')
                chnlpack_box_column.separator(factor=1.0)
                chnlpack_box_column.emboss = 'NONE'
                chnlpack_box_column.operator(BM_OT_ITEM_ChannelPack_Table_Trash.bl_idname, text="", icon='TRASH')

                if len(object.chnlp_channelpacking_table):
                    channel_pack = object.chnlp_channelpacking_table[object.chnlp_channelpacking_table_active_index]
                    col = chnlpack_box.column(align=True)
                    col.use_property_split = False
                
                    row = col.row(align=True)
                    row.active = channel_pack.global_use_r
                    split = row.split(factor=0.1)
                    split.column().prop(channel_pack, 'global_use_r', text="", icon='EVENT_R')
                    split_row = split.row()
                    split_row.prop(channel_pack, 'global_r_map', text="")
                    # split_row.label(text=" R ")

                    row = col.row(align=True)
                    row.active = channel_pack.global_use_g
                    split = row.split(factor=0.1)
                    split.column().prop(channel_pack, 'global_use_g', text="", icon='EVENT_G')
                    split_row = split.row()
                    split_row.prop(channel_pack, 'global_g_map', text="")
                    # split_row.label(text=" G ")

                    row = col.row(align=True)
                    row.active = channel_pack.global_use_b
                    split = row.split(factor=0.1)
                    split.column().prop(channel_pack, 'global_use_b', text="", icon='EVENT_B')
                    split_row = split.row()
                    split_row.prop(channel_pack, 'global_b_map', text="")
                    # split_row.label(text=" B ")

                    row = col.row(align=True)
                    row.active = channel_pack.global_use_a
                    split = row.split(factor=0.1)
                    split.column().prop(channel_pack, 'global_use_a', text="", icon='EVENT_A')
                    split_row = split.row()
                    split_row.prop(channel_pack, 'global_a_map', text="")
                    # split_row.label(text=" A ")

        # bake output
        bake_box = layout.box()
        bake_box.use_property_split = True
        bake_box.use_property_decorate = False

        # bake output header
        bake_box_header = bake_box.row()
        bake_box_header.use_property_split = False
        bake_box_header.emboss = 'NONE'
        icon = 'TRIA_DOWN' if scene.bm_props.global_is_bakeoutput_panel_expanded else 'TRIA_RIGHT'
        bake_box_header.prop(scene.bm_props, 'global_is_bakeoutput_panel_expanded', text="", icon=icon)
        bake_box_header.emboss = 'NORMAL'
        bake_box_header.label(text="Bake Output")
        BM_PT_MapsConfigurator_Presets.draw_panel_header(bake_box_header)

        # bake output body
        if scene.bm_props.global_is_bakeoutput_panel_expanded:
            # # batch naming            
            # bake_box_batchname_split = bake_box.split(factor=0.001)
            # bake_box_batchname_split.column()
            # bake_box_batchname_frame = bake_box_batchname_split.column()
            # bake_box_batchname_header = bake_box_batchname_frame.row()
            # bake_box_batchname_header.use_property_split = False
            # bake_box_batchname_header.emboss = 'NONE'
            # icon = 'TRIA_DOWN' if scene.bm_props.local_is_batchname_panel_expanded else 'TRIA_RIGHT'
            # bake_box_batchname_header.prop(scene.bm_props, 'local_is_batchname_panel_expanded', text="", icon=icon)
            # bake_box_batchname_header.emboss = 'NORMAL'
            # bake_box_batchname_header.label(text="Batch Naming")
            # BM_PT_MapsConfigurator_Presets.draw_panel_header(bake_box_batchname_header)

            # if scene.bm_props.local_is_batchname_panel_expanded:
            #     bake_box_column = bake_box_batchname_frame.column(align=True)
            #     bake_box_column.use_property_split = False
            #     bake_box_column_row = bake_box_column.row()
            #     bake_box_column_row.prop(object, 'bake_batch_name_use_custom', text="")
            #     bake_box_column_row_prop = bake_box_column_row.column(align=True)
            #     bake_box_column_row_prop.prop(object, 'bake_batch_name_custom', text="Custom")
            #     bake_box_column_row_prop.enabled = object.bake_batch_name_use_custom
            #     if object.bake_batch_name_use_custom is False:
            #         bake_box_row = bake_box_batchname_frame.row()
            #         if len(object.bake_batch_name_table) > 5:
            #             rows = len(object.bake_batch_name_table)
            #         else:
            #             rows = 5
            #         bake_box_row.template_list('BM_UL_Table_of_Objects_Item_BatchNamingTable_Item', "", object, 'bake_batch_name_table', object, 'bake_batch_name_table_active_index', rows=rows)
            #         bake_box_column = bake_box_row.column(align=True)
            #         bake_box_column.operator(BM_OT_ITEM_BatchNamingTable_Add.bl_idname, text="", icon='ADD')
            #         bake_box_column.operator(BM_OT_ITEM_BatchNamingTable_Remove.bl_idname, text="", icon='REMOVE')
            #         bake_box_column.separator(factor=1.0)
            #         bake_box_column.separator(factor=1.0)
            #         bake_box_column.emboss = 'NONE'
            #         bake_box_column.operator(BM_OT_ITEM_BatchNamingTable_Trash.bl_idname, text="", icon='TRASH')

            #         if len(object.bake_batch_name_table):
            #             keyword = object.bake_batch_name_table[object.bake_batch_name_table_active_index]
            #             bake_box_column = bake_box_batchname_frame.column(align=True)
            #             if keyword.global_keyword in ["OBJECT_NAME", "CONTAINER_NAME", "PACK_NAME", "TEXSET_NAME", "MAP_NAME", "MAP_SSAA", "MAP_NORMAL", "MAP_UV", "ENGINE"]:
            #                 bake_box_column.prop(keyword, 'global_use_caps')
            #             if keyword.global_keyword == 'MAP_RES':
            #                 bake_box_column.prop(keyword, 'mapres_use_k')
            #             elif keyword.global_keyword == 'MAP_RES':
            #                 bake_box_column.prop(keyword, 'mapres_use_k')
            #             elif keyword.global_keyword == 'MAP_TRANS':
            #                 bake_box_column.prop(keyword, 'maptrans_custom')
            #             elif keyword.global_keyword == 'MAP_DENOISE':
            #                 bake_box_column.prop(keyword, 'mapdenoise_custom')
            #             elif keyword.global_keyword == 'AUTO_UV':
            #                 bake_box_column.prop(keyword, 'autouv_custom')
                # bake_box.separator(factor=1.0)

            bake_box_column = bake_box.column(align=True)
            bake_box_column.prop(object, 'bake_batchname')
            bake_box_column.prop(object, 'bake_batchname_use_caps')
            bake_box_column.emboss = 'NONE'
            bake_box_column.prop(object, 'bake_batchname_preview')

            bake_box_column = bake_box.column(align=True)
            bake_box_column.prop(object, 'bake_save_internal')
            if object.bake_save_internal is False:
                bake_box_column.prop(object, 'bake_output_filepath')
                bake_box_column.prop(object, 'bake_create_subfolder')
                if object.bake_create_subfolder:
                    bake_box_column.prop(object, 'bake_subfolder_name')
            bake_box_column = bake_box.column(align=True)
            bake_layout_device = bake_box_column.row()
            bake_layout_device.prop(object, 'bake_device')
            if object.bake_device != 'GPU':
                bake_layout_device.active = True
            else:
                bake_layout_device.active = context.preferences.addons['cycles'].preferences.has_active_device()
            bake_box_column.prop(object, 'bake_create_material')
            bake_box_column.prop(scene.bm_props, 'global_bake_use_save_log')

class BM_PT_TextureSetsBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_TextureSets'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.bm_table_of_objects) > 0

    def draw_header(self, context):
        label = "Texture Sets"
        icon = 'OUTLINER_OB_GROUP_INSTANCE'
        self.layout.label(text=label, icon=icon)

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        bm_props = scene.bm_props

        # texset table
        texsets_box = layout.box()
        texsets_row = texsets_box.row()

        if len(bm_props.global_texturesets_table) > 3:
            rows = len(bm_props.global_texturesets_table)
        else:
            rows = 3
        
        texsets_row.template_list('BM_UL_Table_of_TextureSets', "", bm_props, 'global_texturesets_table', bm_props, 'global_texturesets_active_index', rows=rows)
        texsets_column = texsets_row.column(align=True)
        texsets_column.operator(BM_OT_SCENE_TextureSets_Table_Add.bl_idname, text="", icon='ADD')
        texsets_column.operator(BM_OT_SCENE_TextureSets_Table_Remove.bl_idname, text="", icon='REMOVE')
        texsets_column.separator(factor=1.0)
        texsets_column.emboss = 'NONE'
        texsets_column.operator(BM_OT_SCENE_TextureSets_Table_Trash.bl_idname, text="", icon='TRASH')

        # texset body
        if len(bm_props.global_texturesets_table):
            # table of objects for texset
            texsets_box.label(text="Texture Set Objects/Containers")
            texset = bm_props.global_texturesets_table[bm_props.global_texturesets_active_index]
            texset_objects_row = texsets_box.row()

            if len(texset.global_textureset_table_of_objects) > 3:
                rows = len(texset.global_textureset_table_of_objects)
            else:
                rows = 3
        
            texset_objects_row.template_list('BM_UL_TextureSets_Objects_Table_Item', "", texset, 'global_textureset_table_of_objects', texset, 'global_textureset_table_of_objects_active_index', rows=rows)
            texset_objects_column = texset_objects_row.column(align=True)
            
            texset_objects_column_row = texset_objects_column.row()
            texset_objects_column_row.operator(BM_OT_SCENE_TextureSets_Objects_Table_Add.bl_idname, text="", icon='ADD')

            # check if can add objects to texset
            for texset1 in bm_props.global_texturesets_table:
                if len(texset1.global_textureset_table_of_objects):
                    texset_obj_items = BM_TEXSET_OBJECT_PROPS_global_object_name_Items(texset1.global_textureset_table_of_objects[texset1.global_textureset_table_of_objects_active_index], context)
                    if len(texset_obj_items) == 1:
                        texset_objects_column_row.enabled = False
                        break

            texset_objects_column.operator(BM_OT_SCENE_TextureSets_Objects_Table_Remove.bl_idname, text="", icon='REMOVE')
            texset_objects_column.separator(factor=1.0)
            texset_objects_column.emboss = 'NONE'
            texset_objects_column.operator(BM_OT_SCENE_TextureSets_Objects_Table_Trash.bl_idname, text="", icon='TRASH')


            # texset options
            if len(texset.global_textureset_table_of_objects):
                # texset object subitems
                item = texset.global_textureset_table_of_objects[texset.global_textureset_table_of_objects_active_index]
                if context.scene.bm_props.global_use_name_matching and context.scene.bm_table_of_objects[item.global_source_object_index].nm_is_universal_container:
                    texsets_box.label(text="Container's Objects to include")
                    if len(item.global_object_name_subitems) > 3:
                        rows = len(item.global_object_name_subitems)
                    else:
                        rows = 3
                    texset_box_texset_item_subitems_row = texsets_box.row()
                    texset_box_texset_item_subitems_row.template_list('BM_UL_TextureSets_Objects_Table_Item_SubItem', "", item, 'global_object_name_subitems', item, 'global_object_name_subitems_active_index', rows=rows)
                    texset_box_texset_item_subitems_row.operator(BM_OT_SCENE_TextureSets_Objects_Table_InvertSubItems.bl_idname, text="", icon='CHECKBOX_HLT')

                texset_column = texsets_box.column(align=True)
                texset_column.use_property_split = True
                texset_column.use_property_decorate = False

                texset_column.prop(texset, 'uvp_use_uv_repack')
                if texset.uvp_use_uv_repack:
                    texset_column.prop(texset, 'uvp_use_islands_rotate')
                    texset_column.prop(texset, 'uvp_pack_margin')
            
                texset_row = texsets_box.row()
                texset_row.use_property_split = True
                texset_row.use_property_decorate = False
                texset_row.prop(texset, 'global_textureset_naming')
            
class BM_PT_BakeBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Bake'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.bm_table_of_objects) > 0
    
    def draw_header(self, context):
        label = "Bake"
        icon = 'RENDER_STILL'
        self.layout.label(text=label, icon=icon)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        object = BM_Object_Get(context)[0]

        # bake body
        layout.prop(scene.bm_props, 'global_use_bakemaster_reset')

        bake_column = layout.column(align=True)
        bake_column_bake_this = bake_column.row()
        bake_column_bake_this.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake This").control = 'BAKE_THIS'
        bake_column_bake_all = bake_column.row()
        bake_column_bake_all.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake All").control = 'BAKE_ALL'
        bake_column_bake_all.scale_y = 1.5
        bake_column.enabled = context.scene.bm_props.global_bake_available

        # help body
        help_column = layout.column()
        help_column_instruction = help_column.row()
        help_column_instruction.prop(context.scene.bm_props, "global_bake_instruction", text="", icon='INFO')
        help_column_instruction.enabled = False
        help_column_doc = help_column.row()
        help_column_doc.operator(BM_OT_Help.bl_idname, text="Documentation", icon='HELP')
        help_column_doc.active = False

# class BM_PT_Item_STTBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_STTBase"
#     bl_options = {'DEFAULT_CLOSED'}
    
#     @classmethod
#     def poll(cls, context):
#         return (BM_ITEM_Get(context)[1])
    
#     def draw_header(self, context):
#         self.layout.label(text="Source to Target")#, icon='FILE_TICK')

#     def draw_header_preset(self, context):
#         item = BM_ITEM_Get(context)
#         if item[1] is True and item[0].use_source is False:
#             BM_PT_STTSettings_Presets.draw_panel_header(self.layout)

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         item = BM_ITEM_Get(context)[0]
#         col = layout.column()

#         if not item.use_source:
#             col.prop(item, 'use_target', text="Target")

#             if item.use_target:
#                 col.prop(item, 'source', text="Source")

#                 if item.source != 'NONE':
#                     col.prop(item, 'use_cage', text="Cage")

#                     if item.use_cage:
#                         col.prop(item, 'cage_object', text="Cage Object")
#                         col.prop(item, 'cage_extrusion', text="Extrusion")
#                     else:
#                         col.prop(item, 'cage_extrusion', text="Ray Distance")

#                     if bpy.app.version >= (2, 90, 0):
#                         col.prop(item, 'max_ray_distance', text="Max Ray Distance")
#         else:
#             col.label(text="Source for %s" % item.source_name)

# class BM_PT_Item_UVMapBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_UVMapBase"
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         item = BM_ITEM_Get(context)
#         return (item[1] and not item[0].use_source)
    
#     def draw_header(self, context):
#         self.layout.label(text="UV Maps")#, icon='GROUP_UVS')

#     def draw_header_preset(self, context):
#         BM_PT_UVSettings_Presets.draw_panel_header(self.layout)

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         item = BM_ITEM_Get(context)[0]
#         col = layout.column()

#         col.prop(item, 'active_uv', text="UV Map")
#         col.prop(item, 'uv_type', text="Type")

#         # col active if at least one map bake_target is IMAGE_TEXTURES
#         len_maps_to_img = len(list(filter(lambda map: map.bake_target == 'IMAGE_TEXTURES', item.maps)))
#         #len_maps_to_vrtx = len(list(filter(lambda map: map.bake_target == 'VERTEX_COLORS', item.maps)))
#         if len(item.maps) != 0 and len_maps_to_img == 0:
#             col.active = False
#         else:
#             col.active = True

#         if item.uv_type != 'TILED':
#             col = layout.column()
#             col.prop(item, 'use_islands_pack', text="Include in UV Pack")

#             if item.use_islands_pack:
#                 col.prop(context.scene.bm_props, 'use_islands_rotate', text="Rotate UV islands")
#                 col.prop(context.scene.bm_props, 'uv_pack_margin', text="Margin", slider=True)

# class BM_PT_Item_OutputBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_OutputBase"
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         item = BM_ITEM_Get(context)
#         return (item[1] and not item[0].use_source)
    
#     def draw_header(self, context):
#         self.layout.label(text="Output")#, icon='OUTPUT')

#     def draw_header_preset(self, context):
#         BM_PT_OutputSettings_Presets.draw_panel_header(self.layout)       

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         item = BM_ITEM_Get(context)[0]
        
#         col = layout.column()
#         col.prop(item, 'use_overwrite', text="Overwrite Maps Settings")
        
#         if item.use_overwrite:
#             if bpy.app.version >= (2, 92, 0):
#                 col.prop(item, 'overwrite_bake_target', text="Target")

#                 if item.overwrite_bake_target == 'VERTEX_COLORS':
#                     return

#             col.prop(item, 'overwrite_file_format', text="File Format")
#             col.prop(item, 'overwrite_res_enum', text="Resolution")

#             if item.overwrite_res_enum == 'CUSTOM':
#                 col = layout.column(align=True)
#                 col.prop(item, 'overwrite_res_height', text="Custom Height")
#                 col.prop(item, 'overwrite_res_width', text="Custom Width")

#             col = layout.column()
#             if bpy.app.version >= (3, 1, 0):
#                 col.prop(item, 'overwrite_margin_type', text="Margin Type")
#             col.prop(item, 'overwrite_margin', text="Margin")
#             col.prop(item, 'overwrite_use_32bit', text="32 bit Float")
#             col.prop(item, 'overwrite_use_alpha', text="Alpha")

#             col = layout.column()
#             col.active = False if item.use_internal or item.uv_type == 'TILED' else True
#             col.prop(item, 'overwrite_use_denoise', text="Denoise")
            
#             if item.uv_type == 'TILED':
#                 col.separator(factor=1.2)
#                 col = layout.column(align=True)
#                 col.prop(item, 'overwrite_udim_start_tile', text="Start Tile")
#                 col.prop(item, 'overwrite_udim_end_tile', text="End Tile")

# class BM_PT_Item_MapListBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_Item_MapListBase"
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         if len(context.scene.bm_aol):
#             item = BM_ITEM_Get(context)
#             return (item[1] and not item[0].use_source)
#         else:
#             return False
    
#     def draw_header(self, context):
#         self.layout.label(text="Map Settings", icon='IMAGE')

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         item = BM_ITEM_Get(context)[0]
#         box = layout.box()
#         row = box.row()

#         if len(item.maps) > 4:
#             rows = len(item.maps)
#         else:
#             rows = 4
        
#         row.template_list('BM_UL_ITEM_Maps', "", item, 'maps', item, 'maps_active_index', rows = rows)
#         col = row.column(align=True)
#         col.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='ADD').control = 'ADD'
#         col.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='REMOVE').control = 'REMOVE'
#         col.separator(factor=1.0)
#         BM_PT_MapsConfigurator_Presets.draw_panel_header(col)
#         col.separator(factor=1.0)
#         col.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='TRASH').control = 'TRASH'

# class BM_PT_Item_MapBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_Item_MapBase"
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         if len(context.scene.bm_aol):
#             item = BM_ITEM_Get(context)
#             return (item[1] and not item[0].use_source and len(item[0].maps))
#         else:
#             return False
    
#     def draw_header(self, context):
#         item = BM_ITEM_Get(context)[0]
#         label =  item.maps[item.maps_active_index].map_type.lower().capitalize()
#         if label.find('_c_') != -1:
#             label = "Cycles " + label[3:]
#         self.layout.label(text=f"{label} settings")#, icon='IMAGE_DATA')
        
#     def draw_header_preset(self, context):
#         BM_PT_MapSettings_Presets.draw_panel_header(self.layout)

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         item = BM_ITEM_Get(context)[0]
#         map = item.maps[item.maps_active_index]
#         stt_affect = True
#         stt_affect_used = False
#         use_output_sep = True
#         col = layout.column()

#         # Cycles maps
#         if map.map_type == '_C_NORMAL':
#             col.prop(map, 'normal_space', text="Space")

#             sub = col.column(align=True)
#             sub.prop(map, 'normal_r', text="Swizzle R")
#             sub.prop(map, 'normal_g', text="G")
#             sub.prop(map, 'normal_b', text="B")

#         elif map.map_type == '_C_COMBINED':
#             row = col.row(align=True)
#             row.use_property_split = False
#             row.prop(map, 'cycles_use_pass_direct', toggle=True)
#             row.prop(map, 'cycles_use_pass_indirect', toggle=True)

#             flow = col.grid_flow(row_major = False, columns = 0, even_columns = False, even_rows = False, align=True)

#             flow.active = map.cycles_use_pass_direct or map.cycles_use_pass_indirect
#             flow.prop(map, 'cycles_use_pass_diffuse')
#             flow.prop(map, 'cycles_use_pass_glossy')
#             flow.prop(map, 'cycles_use_pass_transmission')
#             if bpy.app.version < (3, 0, 0):
#                 flow.prop(map, 'cycles_use_pass_ambient_occlusion')
#             flow.prop(map, 'cycles_use_pass_emit')

#         elif map.map_type in {'_C_DIFFUSE', '_C_GLOSSY', '_C_TRANSMISSION'}:
#             row = col.row(align=True)
#             row.use_property_split = False
#             row.prop(map, 'cycles_use_pass_direct', toggle=True)
#             row.prop(map, 'cycles_use_pass_indirect', toggle=True)
#             row.prop(map, 'cycles_use_pass_color', toggle=True)
#         ###

#         elif map.map_type == 'NORMAL':
#             col.prop(map, 'normal_space', text="Space")
#             sub = col.column(align=True)
#             sub.prop(map, 'normal_r', text="Swizzle R")
#             sub.prop(map, 'normal_g', text="G")
#             sub.prop(map, 'normal_b', text="B")
#             col.prop(map, 'use_smooth_normals', text="Bake Smooth Normals")
#             if map.use_smooth_normals:
#                 col.prop(map, 'normal_cage', text="Ray Distance")
#                 stt_affect = False

#         elif map.map_type == 'DISPLACEMENT':
#             if item.use_target and item.source != 'NONE' and map.use_source_target:
#                 col.prop(map, 'displacement_subdiv_levels', text="Subdiv Levels")
#                 face_count = len(item.object_pointer.data.polygons) * 4 ** map.displacement_subdiv_levels #future face count
#                 col.label(text="Face count while baking: " + str(face_count))
#             else:
#                 use_output_sep = False

#         #elif map.map_type == 'EMISSION':
#         #    col.prop(map, 'emission_use_mask', text="Mask")

#         elif map.map_type == 'AO':
#             col.prop(map, 'ao_use_preview', text="Preview")
#             col.prop(map, 'ao_use_default', text="Default")
#             if not map.ao_use_default:
#                 col.prop(map, 'ao_samples', text="Samples", slider=True)
#                 col.prop(map, 'ao_distance', text="Distance")
#                 col = layout.column(align=True)
#                 col.prop(map, 'ao_black_point', text="Blacks", slider=True)
#                 col.prop(map, 'ao_white_point', text="Whites", slider=True)
#                 col = layout.column(align=True)
#                 col.prop(map, 'ao_brightness', text="Brightness")
#                 col.prop(map, 'ao_contrast', text="Contrast")
#                 col.prop(map, 'ao_opacity', text="Opacity", slider=True)
#                 col = layout.column()
#                 col.prop(map, 'ao_use_local', text="Only Local")
#                 col.prop(map, 'ao_use_invert', text="Invert", slider=True)

#         elif map.map_type == 'CAVITY':
#             col.prop(map, 'cavity_use_preview', text="Preview")
#             col.prop(map, 'cavity_use_default', text="Default")
#             if not map.cavity_use_default:
#                 col = layout.column(align=True)
#                 col.prop(map, 'cavity_black_point', text="Blacks", slider=True)
#                 col.prop(map, 'cavity_white_point', text="Whites", slider=True)
#                 col = layout.column()
#                 col.prop(map, 'cavity_power', text="Power")
#                 col.prop(map, 'cavity_use_invert', text="Invert", slider=True)

#         elif map.map_type == 'CURVATURE':
#             col.prop(map, 'curv_use_preview', text="Preview")
#             col.prop(map, 'curv_use_default', text="Default")
#             if not map.curv_use_default:
#                 col.prop(map, 'curv_samples', text="Samples", slider=True)
#                 col.prop(map, 'curv_radius', text="Radius")
#                 col = layout.column(align=True)
#                 col.prop(map, 'curv_edge_contrast', text="Edge")
#                 col.prop(map, 'curv_body_contrast', text="Body")
#                 col = layout.column()
#                 col.prop(map, 'curv_use_invert', text="Invert", slider=True)

#         elif map.map_type == 'THICKNESS':
#             col.prop(map, 'thick_use_preview', text="Preview")
#             col.prop(map, 'thick_use_default', text="Default")
#             if not map.thick_use_default:
#                 col.prop(map, 'thick_samples', text="Samples", slider=True)
#                 col.prop(map, 'thick_distance', text="Distance")
#                 col = layout.column(align=True)
#                 col.prop(map, 'thick_black_point', text="Blacks", slider=True)
#                 col.prop(map, 'thick_white_point', text="Whites", slider=True)
#                 col = layout.column(align=True)
#                 col.prop(map, 'thick_brightness', text="Brightness")
#                 col.prop(map, 'thick_contrast', text="Contrast")
#                 col = layout.column()
#                 col.prop(map, 'thick_use_invert', text="Invert", slider=True)

#         #elif map.map_type == 'MATID':
#             #col.prop(map, 'matid_source', text="Source")
#             #col.prop(map, 'matid_algorithm', text="Algorithm")

#         elif map.map_type == 'XYZMASK':
#             col = layout.column(align=True)
#             col.prop(map, 'xyzmask_use_x', text="X")
#             col.prop(map, 'xyzmask_use_y', text="Y")
#             col.prop(map, 'xyzmask_use_z', text="Z")
#             col.prop(map, 'xyzmask_use_preview', text="Preview")     
#             col.prop(map, 'xyzmask_use_default', text="Default")
#             if not map.xyzmask_use_default:
#                 col = layout.column(align=True)
#                 col.prop(map, 'xyzmask_coverage', text="Coverage")
#                 col.prop(map, 'xyzmask_saturation', text="Saturation")
#                 col = layout.column()
#                 col.prop(map, 'xyzmask_opacity', text="Opacity", slider=True)
#                 col.prop(map, 'xyzmask_use_invert', text="Invert", slider=True)

#         elif map.map_type == 'GRADIENT':
#             col.prop(map, 'gmask_use_preview', text="Preview")
#             col.prop(map, "gmask_type", text="Type")
#             col = layout.column(align=True)
#             col.prop(map, "gmask_location_x", text="Location X")
#             col.prop(map, "gmask_location_y", text="Location Y")
#             col.prop(map, "gmask_location_z", text="Location Z")
#             col = layout.column(align=True)
#             col.prop(map, "gmask_rotation_x", text="Rotation X")
#             col.prop(map, "gmask_rotation_y", text="Rotation Y")
#             col.prop(map, "gmask_rotation_z", text="Rotation Z")
#             col = layout.column()
#             col.prop(map, 'gmask_use_default', text="Default")
#             if not map.gmask_use_default: 
#                 col = layout.column(align=True)
#                 col.prop(map, "gmask_scale_x", text="Scale X")
#                 col.prop(map, "gmask_scale_y", text="Scale Y")
#                 col.prop(map, "gmask_scale_z", text="Scale Z")
#                 col = layout.column(align=True)
#                 col.prop(map, 'gmask_coverage', text="Coverage")
#                 col.prop(map, 'gmask_contrast', text="Contrast")
#                 col = layout.column(align=True)
#                 col.prop(map, 'gmask_saturation', text="Saturation")
#                 col.prop(map, 'gmask_opacity', text="Opacity", slider=True)
#                 col.prop(map, 'gmask_use_invert', text="Invert", slider=True)
        
#         else:
#             use_output_sep = False

#         if stt_affect and item.use_target and item.source != 'NONE':
#             if use_output_sep:
#                 col.separator(factor=2.0)
#             col.prop(map, 'use_source_target', text="Affect by Source")
#             stt_affect_used = True

#         # Map Output Settings
#         if use_output_sep or stt_affect_used:
#             col.separator(factor=2.0)

#         col = layout.column()
#         if bpy.app.version >= (2, 92, 0):
#             col.prop(map, 'bake_target', text="Target")

#             if map.bake_target == 'VERTEX_COLORS':
#                 return

#         col.prop(map, 'file_format', text="File Format")
#         col.prop(map, 'res_enum', text="Resolution")

#         if map.res_enum == 'CUSTOM':
#             col = layout.column(align=True)
#             col.prop(map, 'res_height', text="Custom Height")
#             col.prop(map, 'res_width', text="Custom Width")

#         col = layout.column()
#         if bpy.app.version >= (3, 1, 0):
#             col.prop(map, 'margin_type', text="Margin Type")
#         col.prop(map, 'margin', text="Margin")
#         col.prop(map, 'use_32bit', text="32 bit Float")
#         col.prop(map, 'use_alpha', text="Alpha")

#         col = layout.column()
#         col.active = False if item.use_internal or item.uv_type == 'TILED' else True
#         col.prop(map, 'use_denoise', text="Denoise")

#         if item.uv_type == 'TILED':
#             col.separator(factor=1.2)
#             col = layout.column(align=True)
#             if item.uv_type == 'TILED':
#                 col.prop(map, 'udim_start_tile', text="Start Tile")
#                 col.prop(map, 'udim_end_tile', text="End Tile")

# class BM_PT_Item_MainBakeBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_Item_MainBakeBase"
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         return len(context.scene.bm_aol)

#     def draw_header_preset(self, context):
#         item = BM_ITEM_Get(context)
#         if item[1] is True and item[0].use_source is False:
#             BM_PT_BakeSettings_Presets.draw_panel_header(self.layout)

#     def draw_header(self, context):
#         self.layout.label(text="Bake Settings", icon='RENDER_STILL')

#     def draw(self, context):
#         pass

# class BM_PT_Item_BakeBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_Item_BakeBase"
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         if len(context.scene.bm_aol):
#             item = BM_ITEM_Get(context)
#             return (item[1] and not item[0].use_source)
#         else:
#             return False

#     def draw_header(self, context):
#         item = BM_ITEM_Get(context)[0]
#         self.layout.label(text="%s Bake Settings" % item.object_pointer.name)

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         item = BM_ITEM_Get(context)[0]
#         col = layout.column()

#         if len(list(filter(lambda map: map.bake_target == 'IMAGE_TEXTURES', item.maps))):
#             col.prop(item, 'use_material', text="Material")
#             col.prop(item, 'use_internal', text="Internal")

#             if not item.use_internal:
#                 col.prop(item, 'output_filepath', text="")
#                 col.prop(item, 'use_subfolder', text="Subfolder")
                
#                 if item.use_subfolder:
#                     col.prop(item, 'subfolder_name', text="Subfolder Name")

#             col.prop(item, 'batch_name', text="Batch Name")
#             col.separator(factor=1.0)
#             #col.prop(item, 'use_save_log', text="Save Log")
#             col_bd = layout.column()
#             col_bd.prop(item, 'bake_device', text="Bake Device")

#             col = layout.column()
#             col.prop(item, 'bake_use_adaptive_sampling', text="Adaptive Sampling")

#             if item.bake_use_adaptive_sampling:
#                 col.prop(item, 'bake_adaptive_threshold', text="Noise Threshold")
#                 col = layout.column(align=True)
#                 col.prop(item, 'bake_samples', text="Max Samples")
#                 col.prop(item, 'bake_min_samples', text="Min Samples")
#             else:
#                 col.prop(item, 'bake_samples', text="Samples")

#         else:
#             col_bd = layout.column()
#             col_bd.prop(item, 'bake_device', text="Bake Device")

#         if item.bake_device != 'GPU':
#             col_bd.active = True
#         else:
#             col_bd.active = context.preferences.addons['cycles'].preferences.has_active_device()

# class BM_PT_Item_MainBakeSettingsBase(bpy.types.Panel):
#     bl_label = " "
#     bl_idname = "BM_PT_Item_MainBakeSettingsBase"
#     bl_options = {'HIDE_HEADER'}

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         col = layout.column()
#         #col.prop(context.scene.bm_props, 'use_background_bake', text="Bake in the Background")
#         col.prop(context.scene.bm_props, 'use_bakemaster_reset', text="Reset BakeMaster")

#         col = layout.column(align=True)
#         sub = col.column()
#         sub.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake This", icon='RENDER_STILL').control = 'BAKE_THIS'
        
#         # checking if bake_this available
#         item = BM_ITEM_Get(context)[0]
#         if not item.use_bake or item.use_source:
#             sub.enabled = False

#         # list of map with True use_bake
#         active_maps = list(filter(lambda map: map.use_bake is True, item.maps))
#         # enabled if any maps to bake and bake_ot is not running
#         sub.enabled = all([len(active_maps) != 0, context.scene.bm_props.bake_available])

#         # bake_all will be always enabled and raise OT errors
#         sub = col.column()
#         sub.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake All", icon='RENDER_STILL').control = 'BAKE_ALL'
#         sub.scale_y = 1.5
#         sub.enabled = context.scene.bm_props.bake_available

#         col = layout.column()
#         col.prop(context.scene.bm_props, "bake_instruction", text="", icon='INFO')
#         col.enabled = False