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
from .operators import *
from .operator_bake import BM_OT_ITEM_Bake
from .utils import BM_Object_Get
from .presets import *

class BM_PREFS_Addon_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        bm_props = context.scene.bm_props
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'global_lowpoly_tag')
        layout.prop(bm_props, 'global_highpoly_tag')
        layout.prop(bm_props, 'global_cage_tag')
        layout.prop(bm_props, 'global_decal_tag')
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'global_bake_uv_layer_tag')
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'global_use_hide_notbaked')
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'global_bake_match_maps_type')
        
class BM_ALEP_UL_Objects_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, active_data, active_propname, index):
        source_object = [object for object in context.scene.bm_table_of_objects if object.global_object_name == item.object_name]
        if len(source_object) == 0:
            icon = 'TRIA_RIGHT'
        else:
            object = source_object[0]
            try:
                context.scene.objects[object.global_object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                icon = 'GHOST_DISABLED'
            else:
                icon = 'OUTLINER_OB_MESH'

            if object.hl_is_lowpoly:
                icon = 'MESH_PLANE'
            if object.decal_is_decal:
                icon = 'XRAY'

        row = layout.row()
        split = row.split(factor=0.1)
        column = split.row()
        column.prop(item, 'use_affect', text="")
        row.emboss = 'NONE'
        column = split.row()
        column.label(text=item.object_name, icon=icon)
        row.active = item.use_affect

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass

class BM_ALEP_UL_Maps_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, active_data, active_propname, index):
        row = layout.row()
        split = row.split(factor=0.1)
        column = split.row()
        column.prop(item, 'use_affect', text="")
        row.emboss = 'NONE'
        column = split.row()
        column.label(text=item.map_name, icon='IMAGE_DATA')
        row.active = item.use_affect

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass

class BM_CAUC_UL_Objects_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, active_data, active_propname, index):
        source_object = [object for object in context.scene.bm_table_of_objects if object.global_object_name == item.object_name]
        if len(source_object) == 0:
            layout.label(text="ERROR. Object not found", icon='ERROR')
            return

        active = True
        object = source_object[0]
        try:
            context.scene.objects[object.global_object_name]
        except (KeyError, AttributeError, UnboundLocalError):
            active = False

        row = layout.row()
        split = row.split(factor=0.3)
        column = split.row()
        low = column.row()
        low.prop(item, 'use_include', text="", icon='MESH_PLANE')
        high = column.row()
        high.prop(item, 'is_highpoly', text="", icon='VIEW_ORTHO')
        cage = column.row()
        cage.prop(item, 'is_cage', text="", icon='SELECT_SET')
        column = split.row()
        column.label(text=item.object_name)

        if item.use_include:
            high.active = False
            cage.active = False
        elif item.is_highpoly:
            low.active = False
            cage.active = False
        elif item.is_cage:
            low.active = False
            high.active = False

        if active:
            layout.active = any([item.use_include, item.is_highpoly, item.is_cage])
        else:
            layout.active = False

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass

class BM_FMR_UL_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, active_data, active_propname, index):
        row = layout.row()
        row.label(text="%s " % item.image_res)
        row.label(text="%s " % item.image_name)
        row.label(text="%s" % item.socket_and_node_name)

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass

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
                    if (item.hl_is_highpoly and item.hl_is_decal) or item.decal_is_decal:
                        icon = 'XRAY'
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
                icons = ['MESH_PLANE', 'VIEW_ORTHO', 'SELECT_SET']
                props = [item.hl_is_lowpoly, item.hl_is_highpoly, item.hl_is_cage]
                icon_ = [icon for index, icon in enumerate(icons) if props[index] is True]
                if (len(icon_)):
                    icon = icon_[0]
                else:
                    icon = 'OUTLINER_OB_MESH'
                if (item.hl_is_highpoly and item.hl_is_decal) or item.decal_is_decal:
                    icon = 'XRAY'
                row.label(text=item.global_object_name, icon=icon)

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
        
        # get filtered items
        return BM_Table_of_Objects_GetFTL(context, items, self.bitflag_filter_item)

    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Objects_Item_Highpoly(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_item_index
        layout.emboss = 'PULLDOWN_MENU'
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
        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        props_column = split.column().row()
        props_column.prop(item, 'global_map_type', text="")
        props_column_use_bake = props_column.row()
        if item.global_use_bake:
            icon = 'RESTRICT_RENDER_OFF'
        else:
            icon = 'RESTRICT_RENDER_ON'
            layout.active = False

        object = BM_Object_Get(item, context)[0]
        if object.uv_use_unique_per_map:
            uv_container = item
        else:
            uv_container = object

        if item.global_map_type == 'DECAL' and object.bake_save_internal:
            layout.active = False
            icon = 'RESTRICT_RENDER_ON'
            props_column_use_bake.enabled = False

        if uv_container.uv_bake_data == 'VERTEX_COLORS':
            if item.global_map_type != 'VERTEX_COLOR_LAYER':
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                props_column_use_bake.enabled = False
        if uv_container.uv_bake_target == 'VERTEX_COLORS':
            if item.global_map_type == 'NORMAL' and item.map_normal_data == 'MULTIRES':
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                props_column_use_bake.enabled = False
            elif item.global_map_type == 'DISPLACEMENT' and item.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                props_column_use_bake.enabled = False

        props_column_use_bake.prop(item, 'global_use_bake', text="", icon=icon)

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Maps_Item_Highpoly(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.global_item_index
        layout.emboss = 'PULLDOWN_MENU'
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

        # channel pack inactive if internal bake
        object = context.scene.bm_table_of_objects[item.global_channelpack_object_index]
        if object.bake_save_internal:
            layout.active = False
            text = " (External Bake only)"
        else:
            text = ""

        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'global_channelpack_name', text=text)

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

            if object.global_use_bake is False or object.decal_is_decal:
                layout.active = False

        layout.emboss = 'PULLDOWN_MENU'
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
        
        source_object = [object for object in context.scene.bm_table_of_objects if object.global_object_name == item.global_object_name][0]

        icon = ''
        if source_object.hl_is_lowpoly:
            icon = 'MESH_PLANE'
        if source_object.decal_is_decal:
            icon = 'XRAY'

        if source_object.global_use_bake is False or source_object.decal_is_decal:
            layout.active = False
        try:
            context.scene.objects[source_object.global_object_name]
        except (KeyError, AttributeError, UnboundLocalError):
            icon = 'GHOST_DISABLED'
            layout.active = False

        if icon == '':
            icon = 'OUTLINER_OB_MESH'

        row = layout.row()
        split = row.split(factor=split_factor)
        name_column = split.row()
        name_column.prop(item, 'global_object_include_in_texset', text="")
        row.emboss = 'NONE'
        name_column_row = name_column.row()
        name_column_row.label(text=item.global_object_name, icon=icon)
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

        full_len = len(scene.bm_table_of_objects)
        rows = 5 if full_len >= 1 else 4
        refresh = False
        for object in scene.bm_table_of_objects:
            try:
                scene.objects[object.global_object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                if scene.bm_props.global_use_name_matching and any([object.nm_is_universal_container, object.nm_is_local_container]):
                    continue
                refresh = True
                rows += 1
                break
        if full_len and BM_Object_Get(None, context)[1] is False:
            if scene.bm_props.global_use_name_matching and any([object.nm_is_universal_container, object.nm_is_local_container]):
                rows += 1
            rows -= 1
        
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
            object = BM_Object_Get(None, context)
            if (object[1] is True) or (scene.bm_props.global_use_name_matching and any([object[0].nm_is_universal_container, object[0].nm_is_local_container])): # and object[0].use_source is False:
                BM_PT_FULL_OBJECT_Presets.draw_panel_header(col)
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
        object = BM_Object_Get(None, context)
        label = object[0].global_object_name
        label_end = ""
        icon = 'PROPERTIES'
        draw_unique_per_object = False
        if context.scene.bm_props.global_use_name_matching and any([object[0].nm_is_universal_container, object[0].nm_is_local_container]):
            label_end = "Container"
            if object[0].nm_is_universal_container:
                label = object[0].nm_container_name
                draw_unique_per_object = True
            else:
                for object1 in context.scene.bm_table_of_objects:
                    if object1.nm_is_universal_container and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                        label = object1.nm_container_name
                        label_end = "{} Container".format(object[0].nm_container_name)
                        break
        row = self.layout.row(align=True)
        row.label(text="{} {}".format(label, label_end), icon=icon)
        if draw_unique_per_object:
            row.prop(object[0], 'nm_uni_container_is_global', text="", icon='NETWORK_DRIVE')

    def draw(self, context):
        object = BM_Object_Get(None, context)
        label = ""
        icon = ''
        draw_label = False
        if context.scene.bm_props.global_use_name_matching and object[0].nm_is_universal_container:
            if object[0].nm_uni_container_is_global:
                return
            label = "Universal Container"
            icon = 'TRIA_RIGHT'
            draw_label = True
        elif context.scene.bm_props.global_use_name_matching and object[0].nm_is_local_container:
            label = "Local Container"
            icon = 'TRIA_RIGHT'
            draw_label = True
        elif object[1] is False:
            label = "Object cannot be found"
            icon = 'GHOST_DISABLED'
            draw_label = True
        elif object[0].hl_is_highpoly and object[0].hl_is_decal:
            label = "Decal Object"
            icon = 'XRAY'
            draw_label = True
        elif object[0].hl_is_highpoly:
            label = "Highpoly Object" 
            icon = 'VIEW_ORTHO'
            draw_label = True
        elif object[0].hl_is_cage:
            label = "Cage Object" 
            icon = 'SELECT_SET'
            draw_label = True
        if context.scene.bm_props.global_use_name_matching and object[0].nm_is_detached is False:
            container_name = ""
            draw_configured = False
            for object1 in context.scene.bm_table_of_objects:
                if object1.nm_is_universal_container and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                    container_name = object1.nm_container_name
                    draw_configured = object1.nm_uni_container_is_global
                    break
            if draw_configured:
                label = "Settings configured by %s" % container_name
                draw_label = True
        if draw_label:
            self.layout.label(text=label)

class BM_PT_Item_ObjectBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Object'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = BM_Object_Get(None, context)
        if object[0].nm_is_universal_container:
            return object[0].nm_uni_container_is_global
        elif object[0].nm_is_local_container:
            return False
        elif any([object[0].hl_is_highpoly, object[0].hl_is_cage]):
            return False
        elif context.scene.bm_props.global_use_name_matching and object[0].nm_is_detached is False:
            return True
        return object[1]

    def draw_header(self, context):
        object = BM_Object_Get(None, context)[0]
        if context.scene.bm_props.global_use_name_matching and any([object.nm_is_universal_container, object.nm_is_local_container]):
            label = "Container"
        else:
            label = "Object"
        row = self.layout.row(align=True)
        row.use_property_split = False
        row.label(text=label)
        BM_PT_OBJECT_Presets.draw_panel_header(row)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = BM_Object_Get(None, context)[0]

        draw_all = True
        for object1 in context.scene.bm_table_of_objects:
            if object1.nm_is_universal_container and object1.nm_master_index == object.nm_item_uni_container_master_index:
                draw_all = not object1.nm_uni_container_is_global

        # decal
        if draw_all:
            decal_box = layout.box()
            decal_box.use_property_split = True
            decal_box.use_property_decorate = False
            # inactive if baking internally
            if object.bake_save_internal:
                decal_box.active = False
                text = " (External Bake only)"
            else:
                text = ""
            
            # decal header
            decal_box_header = decal_box.row(align=True)
            decal_box_header.use_property_split = False
            decal_box_header.emboss = 'NONE'
            icon = 'TRIA_DOWN' if scene.bm_props.global_is_decal_panel_expanded else 'TRIA_RIGHT'
            decal_box_header.prop(scene.bm_props, 'global_is_decal_panel_expanded', text="", icon=icon)
            decal_box_header.emboss = 'NORMAL'
            decal_box_header.label(text="Decal" + text)
            BM_PT_DECAL_Presets.draw_panel_header(decal_box_header)

            # decal body
            if scene.bm_props.global_is_decal_panel_expanded:
                if object.nm_uni_container_is_global is False:
                    decal_box.prop(object, 'decal_is_decal')
                if object.decal_is_decal or object.nm_uni_container_is_global:
                    decal_box_column = decal_box.column(align=True)
                    decal_box_column.prop(object, 'decal_use_custom_camera')
                    if object.decal_use_custom_camera:
                        decal_box_column.prop(object, 'decal_custom_camera')
                    decal_box.prop(object, 'decal_upper_coordinate')
                    decal_box.prop(object, 'decal_boundary_offset')

        # skip drawing hl, uv, csh subpanels
        if object.decal_is_decal and object.nm_uni_container_is_global is False:
            if draw_all is False:
                layout.label(text="No settings available")
            # return

        else:
            # hl
            hl_box = layout.box()
            hl_box.use_property_split = True
            hl_box.use_property_decorate = False
            hl_draw = True

            # hl header
            hl_box_header = hl_box.row(align=True)
            hl_box_header.use_property_split = False
            hl_box_header.emboss = 'NONE'
            icon = 'TRIA_DOWN' if scene.bm_props.global_is_hl_panel_expanded else 'TRIA_RIGHT'
            hl_box_header.prop(scene.bm_props, 'global_is_hl_panel_expanded', text="", icon=icon)
            hl_box_header.emboss = 'NORMAL'
            hl_box_header.label(text="High to Lowpoly")
            BM_PT_HL_Presets.draw_panel_header(hl_box_header)

            # hl body
            if scene.bm_props.global_is_hl_panel_expanded:
                if object.nm_uni_container_is_global is False and draw_all:
                    hl_box.prop(object, 'hl_use_unique_per_map')

                if object.hl_use_unique_per_map is False or draw_all is False:
                    # highpoly
                    hl_box_highpoly_frame = hl_box.split(factor=0.4)
                    hl_box_highpoly_frame.column()
                    hl_box_highpoly = hl_box_highpoly_frame.column()
                    label = "Highpoly" if len(object.hl_highpoly_table) <= 1 else "Highpolies"
                    if object.nm_is_universal_container and object.nm_uni_container_is_global:
                        label += " (automatic)"
                        hl_draw = False
                    hl_box_highpoly.label(text=label)
                    if hl_draw:
                        hl_box_highpoly_table = hl_box_highpoly.column().row()
                        rows = BM_template_list_get_rows(object.hl_highpoly_table, 1, 1, 5, True)
                        hl_box_highpoly_table.template_list('BM_UL_Table_of_Objects_Item_Highpoly', "", object, 'hl_highpoly_table', object, 'hl_highpoly_table_active_index', rows=rows)
                        hl_highpoly_table_column = hl_box_highpoly_table.column(align=True)
                        hl_highpoly_table_column.operator(BM_OT_ITEM_Highpoly_Table_Add.bl_idname, text="", icon='ADD')
                        hl_highpoly_table_column.operator(BM_OT_ITEM_Highpoly_Table_Remove.bl_idname, text="", icon='REMOVE')
                    # highpoly as decal
                    if len(object.hl_highpoly_table):
                        highpoly_object_index = object.hl_highpoly_table[object.hl_highpoly_table_active_index].global_highpoly_object_index
                        hl_box_decal = hl_box.column(align=True)
                        if highpoly_object_index != -1:
                            source_object = scene.bm_table_of_objects[highpoly_object_index]
                            hl_box_decal.prop(source_object, 'hl_is_decal')
                        if draw_all:
                            hl_box_decal.prop(object, 'hl_decals_use_separate_texset')
                            if object.hl_decals_use_separate_texset:
                                hl_box_decal.prop(object, 'hl_decals_separate_texset_prefix')
                    if hl_draw is False:
                        hl_box_decal = hl_box.column(align=True)
                        hl_box_decal.prop(object, 'hl_decals_use_separate_texset')
                        if object.hl_decals_use_separate_texset:
                            hl_box_decal.prop(object, 'hl_decals_separate_texset_prefix')
                    # cage
                    if len(object.hl_highpoly_table) and draw_all:
                        hl_box_cage = hl_box.column(align=True)
                        # hl_box_cage.prop(object, 'hl_cage_type')
                        # if object.hl_cage_type == 'STANDARD':
                        if object.hl_use_cage is False:
                            label = "Extrusion"
                            hl_box_cage.prop(object, 'hl_cage_extrusion', text=label)
                            if bpy.app.version >= (2, 90, 0):
                                hl_box_cage.prop(object, 'hl_max_ray_distance')
                            hl_box_cage.prop(object, 'hl_use_cage')
                        else:
                            label = "Cage Extrusion"
                            hl_box_cage.prop(object, 'hl_cage_extrusion', text=label)
                            if hl_draw:
                                hl_box_cage.prop(object, 'hl_use_cage')
                                hl_box_cage.prop(object, 'hl_cage')
                            else:
                                hl_box_cage.prop(object, 'hl_use_cage', text="Use Cage Object (automatic)")
                        # else:
                            # hl_box_cage.prop(object, 'hl_cage_extrusion', text="Extrusion")
        
        # highs and cage are drawn for global uni_c objects
        # everything else not
        if draw_all is False:
            return

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
        BM_PT_UV_Presets.draw_panel_header(uv_box_header)

        # uv body
        if scene.bm_props.global_is_uv_panel_expanded:
            uv_box.prop(object, 'uv_use_unique_per_map')

            if object.uv_use_unique_per_map is False:
                # uv
                uv_box_column = uv_box.column(align=True)
                uv_box_column.prop(object, 'uv_bake_data')
                uv_box_column.prop(object, 'uv_bake_target')
                if object.uv_bake_target == 'IMAGE_TEXTURES':
                    uv_box_column = uv_box.column(align=True)
                    uv_box_column.prop(object, 'uv_active_layer')
                    uv_box_column.prop(object, 'uv_type')
                    uv_box_column.prop(object, 'uv_snap_islands_to_pixels')
                    uv_box_column = uv_box.column(align=True)
                    if object.uv_active_layer != 'NONE_AUTO_CREATE':
                        uv_box_column.prop(object, 'uv_use_auto_unwrap')
                    if object.uv_use_auto_unwrap or object.uv_active_layer == 'NONE_AUTO_CREATE':
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
        BM_PT_CSH_Presets.draw_panel_header(csh_box_header)

        # shading body
        if scene.bm_props.global_is_csh_panel_expanded:
            # shading
            csh_box.prop(object, 'csh_use_triangulate_lowpoly')
            csh_box_column = csh_box.column()
            csh_box_column.prop(object, 'csh_use_lowpoly_recalc_normals')
            csh_box_column.prop(object, 'csh_lowpoly_use_smooth')
            if object.csh_lowpoly_use_smooth:
                csh_box_column.prop(object, 'csh_lowpoly_smoothing_groups_enum', text="Type")
                if object.csh_lowpoly_smoothing_groups_enum == 'AUTO':
                    csh_box_column.prop(object, 'csh_lowpoly_smoothing_groups_angle')
                if object.csh_lowpoly_smoothing_groups_enum == 'VERTEX_GROUPS':
                    csh_box_column.prop(object, 'csh_lowpoly_smoothing_groups_name_contains')
            # highpoly shading
            len_of_highs = 0
            if object.hl_use_unique_per_map is False:
                len_of_highs = len(object.hl_highpoly_table)
            else:
                for map in object.global_maps:
                    len_of_highs += len(map.hl_highpoly_table)
            # draw if uni_c is global
            hl_draw = True
            if object.nm_is_universal_container and object.nm_uni_container_is_global:
                hl_draw = False
            if len_of_highs > 0 or hl_draw is False:
                label = "Highpoly" if len_of_highs == 1 else "Highpolies"
                csh_box_column = csh_box.column()
                csh_box_column.prop(object, 'csh_use_highpoly_recalc_normals', text="Recalculate %s Normals Outside" % label)
                csh_box_column.prop(object, 'csh_highpoly_use_smooth', text="Smooth %s" % label)
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
        object = BM_Object_Get(None, context)
        if object[0].nm_is_universal_container:
            return object[0].nm_uni_container_is_global
        elif object[0].nm_is_local_container:
            return False
        elif any([object[0].hl_is_highpoly, object[0].hl_is_cage]):
            return False
        elif context.scene.bm_props.global_use_name_matching and object[0].nm_is_detached is False:
            for object1 in context.scene.bm_table_of_objects:
                if object1.nm_is_universal_container and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                    return not object1.nm_uni_container_is_global
        return object[1]

    def draw_header(self, context):
        label = "Maps"
        self.layout.label(text=label)
        BM_PT_FULL_MAP_Presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = BM_Object_Get(None, context)[0]
    
        # maps table
        maps_table_box = layout.box()
        maps_table_row = maps_table_box.row()

        rows = BM_template_list_get_rows(object.global_maps, 4, 0, 5, False)
        maps_table_row.template_list('BM_UL_Table_of_Maps_Item', "", object, 'global_maps', object, 'global_maps_active_index', rows=rows)
        maps_table_column = maps_table_row.column(align=True)
        maps_table_column.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='ADD').control = 'ADD'
        maps_table_column.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='REMOVE').control = 'REMOVE'
        maps_table_column.separator(factor=1.0)
        if len(object.global_maps):
            BM_PT_MAP_Presets.draw_panel_header(maps_table_column)
            maps_table_column.separator(factor=1.0)
        maps_table_column.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='TRASH').control = 'TRASH'

        # map settings
        if len(object.global_maps):
            map = BM_Map_Get(None, object)
            # format 
            if (object.uv_use_unique_per_map is False and object.uv_bake_target != 'VERTEX_COLORS') or (object.uv_use_unique_per_map and map.uv_bake_target != 'VERTEX_COLORS'):
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
                    BM_PT_OUT_Presets.draw_panel_header(format_box_header)
                    format_prop_collection = object
                # draw format unique per map
                else:
                    format_box_header.label(text="Map Format")
                    BM_PT_OUT_Presets.draw_panel_header(format_box_header)
                    format_prop_collection = map

                # format body
                if scene.bm_props.global_is_format_panel_expanded:
                    format_box.prop(object, 'out_use_unique_per_map')
                    # format
                    format_box_column = format_box.column(align=True)
                    format_box_column.prop(format_prop_collection, 'out_file_format')
                    # if format_prop_collection.out_file_format == 'PSD':
                        # format_box_column.prop(format_prop_collection, 'out_psd_include')
                    if format_prop_collection.out_file_format == 'OPEN_EXR':
                        format_box_column.prop(format_prop_collection, 'out_exr_codec')
                    elif format_prop_collection.out_file_format == 'PNG':
                        format_box_column.prop(format_prop_collection, 'out_compression')
                    format_box_column = format_box.column(align=True)
                    format_box_column.prop(format_prop_collection, 'out_res', text="Resolution")
                    if format_prop_collection.out_res == 'CUSTOM':
                        format_box_column.prop(format_prop_collection, 'out_res_height')
                        format_box_column.prop(format_prop_collection, 'out_res_width')
                        format_split = format_box_column.split(factor=0.4)
                        format_split.column()
                        format_split.column().operator(BM_OT_ITEM_and_MAP_Format_MatchResolution.bl_idname, icon='FULLSCREEN_ENTER')
                    # elif format_prop_collection.out_res == 'TEXEL':
                        # format_box_column.prop(format_prop_collection, 'out_texel_density_value')
                        # format_box_column.prop(format_prop_collection, 'out_texel_density_match')
                    format_box_column = format_box.column(align=True)
                    if bpy.app.version >= (3, 1, 0):
                        format_box_column.prop(format_prop_collection, 'out_margin_type')
                    format_box_column.prop(format_prop_collection, 'out_margin')
                    format_box_column = format_box.column(align=True)
                    format_box_column.prop(format_prop_collection, 'out_use_32bit')
                    format_box_column.prop(format_prop_collection, 'out_use_alpha')
                    format_box_column.prop(format_prop_collection, 'out_use_transbg')
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
                    format_box_denoise_col = format_box.column(align=True)
                    format_box_denoise_col.prop(format_prop_collection, 'out_use_denoise')
                    format_box_denoise_col.prop(format_prop_collection, 'out_use_scene_color_management')
                    format_box_denoise_col.active = not object.bake_save_internal

            # map settings column
            map_settings_column = maps_table_box.column()
            map_settings_column.use_property_split = True
            map_settings_column.use_property_decorate = False

            if object.uv_use_unique_per_map:
                uv_container = map
            else:
                uv_container = object

            if uv_container.uv_bake_data == 'VERTEX_COLORS':
                if map.global_map_type != 'VERTEX_COLOR_LAYER':
                    map_settings_column.enabled = False
            if uv_container.uv_bake_target == 'VERTEX_COLORS':
                if map.global_map_type == 'NORMAL' and map.map_normal_data == 'MULTIRES':
                    map_settings_column.enabled = False
                elif map.global_map_type == 'DISPLACEMENT' and map.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
                    map_settings_column.enabled = False
            if map.global_map_type == 'DECAL' and object.bake_save_internal:
                    map_settings_column.enabled = False

            # map settings body

            # (affect_by_hl prop is useless)
            # draw_affect_by_hl = False
            # if object.hl_use_unique_per_map and len(map.hl_highpoly_table):
            #     draw_affect_by_hl = True
            # elif len(object.hl_highpoly_table):
            #     draw_affect_by_hl = True
            # if object.decal_is_decal and object.nm_uni_container_is_global is False:
            #     draw_affect_by_hl = False
            # if draw_affect_by_hl and map.global_map_type not in ['NORMAL', 'DISPLACEMENT']:
            #     map_settings_column.prop(map, 'global_affect_by_hl', text="Affect by Highpoly")
            
            map_settings_column.prop(map, 'map_%s_prefix' % map.global_map_type)
            
            try:
                getattr(map, 'map_%s_use_preview' % map.global_map_type)
            except AttributeError:
                pass
            else:
                map_settings_column_preview = map_settings_column.row()
                map_settings_column_preview.prop(map, 'map_%s_use_preview' % map.global_map_type, text="Preview (Full Version)")
                if any([object.nm_is_universal_container, object.hl_is_highpoly, object.hl_is_cage]):
                    map_settings_column_preview.active = False
            try:
                getattr(map, 'map_%s_use_default' % map.global_map_type)
            except AttributeError:
                pass
            else:
                map_settings_column.prop(map, 'map_%s_use_default' % map.global_map_type)


            # map_types_settings = [
            #     'NORMAL',
            #     'DISPLACEMENT',
            #     'VECTOR_DISPLACEMENT',
            #     'AO',
            #     'CAVITY',
            #     'CURVATURE',
            #     'THICKNESS',
            #     'ID',
            #     'MASK',
            #     'XYZMASK',
            #     'GRADIENT',
            #     'EDGE',
            #     'WIREFRAME',
            #     'PASS',
            #     'C_COMBINED',
            #     'C_NORMAL',
            #     'C_DIFFUSE',
            #     'C_GLOSSY',
            #     'C_TRANSMISSION']
            # if map.global_map_type in map_types_settings:
            #     map_settings_column = maps_table_box.column()#align=True)
            #     map_settings_column.use_property_split = True
            #     map_settings_column.use_property_decorate = False

            # Pass and Cycles Maps
            if map.global_map_type == 'PASS':
                map_settings_column.prop(map, 'map_pass_type')

            elif map.global_map_type == 'DECAL':
                map_settings_column.prop(map, 'map_decal_pass_type')
                if map.map_decal_pass_type == 'NORMAL':
                    map_settings_column.prop(map, 'map_decal_normal_preset')
                    if map.map_decal_normal_preset == 'CUSTOM':
                        sub = map_settings_column.column(align=True)
                        sub.prop(map, 'map_decal_normal_custom_preset')
                        # if map.map_decal_normal_custom_preset == 'CUSTOM':
                        #     sub.prop(map, 'map_decal_normal_r', text="Swizzle R")
                        #     sub.prop(map, 'map_decal_normal_g', text="G")
                        #     sub.prop(map, 'map_decal_normal_b', text="B")
                else:
                    map_settings_column.prop(map, 'map_decal_height_opacity_invert')

            elif map.global_map_type == 'VERTEX_COLOR_LAYER':
                map_settings_column.prop(map, 'map_vertexcolor_layer')
            
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
                try:
                    if map.map_normal_data != 'MATERIAL':
                        map_settings_column_preview.active = False
                except NameError:
                    pass
                map_settings_column.prop(map, 'map_normal_data')
                map_settings_column.prop(map, 'map_normal_space')
                map_settings_column.prop(map, 'map_normal_preset')
                if map.map_normal_preset == 'CUSTOM':
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_normal_custom_preset')
                    if map.map_normal_custom_preset == 'CUSTOM':
                        sub.prop(map, 'map_normal_r', text="Swizzle R")
                        sub.prop(map, 'map_normal_g', text="G")
                        sub.prop(map, 'map_normal_b', text="B")
                if map.map_normal_data == 'MULTIRES':
                    map_settings_column.prop(map, 'map_displacement_subdiv_levels')
                    face_count = BM_MAO_PROPS_map_get_subdivided_face_count(context, object, map)
                    map_settings_column.label(text="Face count while baking: " + str(face_count))

            elif map.global_map_type == 'DISPLACEMENT':
                try:
                    if map.map_displacement_data != 'MATERIAL':
                        map_settings_column_preview.active = False
                except NameError:
                    pass
                map_settings_column.prop(map, 'map_displacement_data')
                map_settings_column.prop(map, 'map_displacement_result')
                if map.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
                    map_settings_column.prop(map, 'map_displacement_subdiv_levels')
                    face_count = BM_MAO_PROPS_map_get_subdivided_face_count(context, object, map)
                    map_settings_column.label(text="Face count while baking: " + str(face_count))
                if map.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
                    map_settings_column.prop(map, 'map_displacement_lowresmesh')
        
            elif map.global_map_type == 'VECTOR_DISPLACEMENT':
                map_settings_column.prop(map, 'map_vector_displacement_use_negative')
                map_settings_column.prop(map, 'map_vector_displacement_result')
                # if map.map_vector_displacement_result == 'MODIFIER':
                #     map_settings_column.prop(map, 'map_vector_displacement_subdiv_levels')
                #     try:
                #         object_pointer = scene.objects[object.global_object_name]
                #         face_count = len(object_pointer.data.polygons) * 4 ** map.map_vector_displacement_subdiv_levels # future face count
                #         map_settings_column.label(text="Face count while baking: " + str(face_count))
                #     except KeyError:
                #         pass

            # Masks and Details Maps
            elif map.global_map_type == 'AO':
                if map.map_AO_use_default is False:
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
                if map.map_CAVITY_use_default is False:
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_cavity_black_point', slider=True)
                    sub.prop(map, 'map_cavity_white_point', slider=True)
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_cavity_power')
                    sub.prop(map, 'map_cavity_use_invert', slider=True)

            elif map.global_map_type == 'CURVATURE':
                if map.map_CURVATURE_use_default is False:
                    map_settings_column.prop(map, 'map_curv_samples', slider=True)
                    map_settings_column.prop(map, 'map_curv_radius')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_curv_black_point', slider=True)
                    sub.prop(map, 'map_curv_mid_point', slider=True)
                    sub.prop(map, 'map_curv_white_point', slider=True)
                    sub = map_settings_column.column()
                    sub.prop(map, 'map_curv_body_gamma')

            elif map.global_map_type == 'THICKNESS':
                if map.map_THICKNESS_use_default is False:
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
                map_settings_column.prop(map, 'map_matid_jilter')
            
            elif map.global_map_type == 'MASK':
                map_settings_column.prop(map, 'map_mask_data')
                if map.map_mask_data == 'VERTEX_GROUPS':
                    map_settings_column.prop(map, 'map_mask_vertex_groups_name_contains')
                elif map.map_mask_data == 'MATERIALS':
                    map_settings_column.prop(map, 'map_mask_materials_name_contains')
                map_settings_column.prop(map, 'map_mask_color1')
                map_settings_column.prop(map, 'map_mask_color2')
                map_settings_column.prop(map, 'map_mask_use_invert', slider=True)

            elif map.global_map_type == 'XYZMASK':
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_xyzmask_use_x')
                sub.prop(map, 'map_xyzmask_use_y')
                sub.prop(map, 'map_xyzmask_use_z')
                if not map.map_XYZMASK_use_default:
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_xyzmask_coverage')
                    sub.prop(map, 'map_xyzmask_saturation')
                    sub = map_settings_column.column(align=True)
                    sub.prop(map, 'map_xyzmask_opacity', slider=True)
                    sub.prop(map, 'map_xyzmask_use_invert', slider=True)

            elif map.global_map_type == 'GRADIENT':
                map_settings_column.prop(map, 'map_gmask_type')
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_gmask_location_x')
                sub.prop(map, 'map_gmask_location_y')
                sub.prop(map, 'map_gmask_location_z')
                sub = map_settings_column.column(align=True)
                sub.prop(map, 'map_gmask_rotation_x')
                sub.prop(map, 'map_gmask_rotation_y')
                sub.prop(map, 'map_gmask_rotation_z')
                if not map.map_GRADIENT_use_default: 
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
                if map.map_EDGE_use_default is False:
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

            # skip drawing hl, uv, csh subpanels
            if object.decal_is_decal and object.nm_uni_container_is_global is False:
                # return
                pass
            else:

                # hl
                if object.hl_use_unique_per_map:
                    hl_box = layout.box()
                    hl_box.use_property_split = True
                    hl_box.use_property_decorate = False
                    hl_draw = True
            
                    # hl header
                    hl_box_header = hl_box.row(align=True)
                    hl_box_header.use_property_split = False
                    hl_box_header.emboss = 'NONE'
                    icon = 'TRIA_DOWN' if scene.bm_props.local_is_hl_panel_expanded else 'TRIA_RIGHT'
                    hl_box_header.prop(scene.bm_props, 'local_is_hl_panel_expanded', text="", icon=icon)
                    hl_box_header.emboss = 'NORMAL'
                    hl_box_header.label(text="Map High to Lowpoly")
                    BM_PT_HL_Presets.draw_panel_header(hl_box_header)

                    # hl body
                    if scene.bm_props.local_is_hl_panel_expanded:
                        hl_box_highpoly_frame = hl_box.split(factor=0.4)
                        hl_box_highpoly_frame.column()
                        hl_box_highpoly = hl_box_highpoly_frame.column()
                        label = "Highpoly" if len(map.hl_highpoly_table) <= 1 else "Highpolies"
                        if object.nm_is_universal_container and object.nm_uni_container_is_global:
                            label += " (automatic)"
                            hl_draw = False
                            hl_box_highpoly.label(text=label)
                        if hl_draw:
                            hl_box_highpoly_table = hl_box_highpoly.column().row()
                            rows = BM_template_list_get_rows(map.hl_highpoly_table, 1, 1, 5, True)
                            hl_box_highpoly_table.template_list('BM_UL_Table_of_Maps_Item_Highpoly', "", map, 'hl_highpoly_table', map, 'hl_highpoly_table_active_index', rows=rows)
                            hl_highpoly_table_column = hl_box_highpoly_table.column(align=True)
                            hl_highpoly_table_column.operator(BM_OT_MAP_Highpoly_Table_Add.bl_idname, text="", icon='ADD')
                            hl_highpoly_table_column.operator(BM_OT_MAP_Highpoly_Table_Remove.bl_idname, text="", icon='REMOVE')
                        # highpoly as decal
                        if len(map.hl_highpoly_table):
                            highpoly_object_index = map.hl_highpoly_table[map.hl_highpoly_table_active_index].global_highpoly_object_index
                            hl_box_decal = hl_box.column(align=True)
                            if highpoly_object_index != -1:
                                source_object = scene.bm_table_of_objects[highpoly_object_index]
                                hl_box_decal.prop(source_object, 'hl_is_decal')
                            hl_box_decal.prop(object, 'hl_decals_use_separate_texset')
                            if object.hl_decals_use_separate_texset:
                                hl_box_decal.prop(object, 'hl_decals_separate_texset_prefix')
                        if hl_draw is False:
                            hl_box_decal = hl_box.column(align=True)
                            hl_box_decal.prop(object, 'hl_decals_use_separate_texset')
                            if object.hl_decals_use_separate_texset:
                                hl_box_decal.prop(object, 'hl_decals_separate_texset_prefix')
                        # cage
                        if len(map.hl_highpoly_table) or hl_draw is False:
                            hl_box_cage = hl_box.column(align=True)
                            hl_box_cage.prop(map, 'hl_cage_type')
                            if map.hl_cage_type == 'STANDARD':
                                if map.hl_use_cage is False:
                                    label = "Extrusion"
                                    hl_box_cage.prop(map, 'hl_cage_extrusion', text=label)
                                    if bpy.app.version >= (2, 90, 0):
                                        hl_box_cage.prop(map, 'hl_max_ray_distance')
                                    hl_box_cage.prop(map, 'hl_use_cage')
                                else:
                                    label = "Cage Extrusion"
                                    hl_box_cage.prop(map, 'hl_cage_extrusion', text=label)
                                    if hl_draw:
                                        hl_box_cage.prop(map, 'hl_use_cage')
                                        hl_box_cage.prop(map, 'hl_cage')
                                    else:
                                        hl_box_cage.prop(map, 'hl_use_cage', text="Use Cage Object (auto)")
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
                BM_PT_UV_Presets.draw_panel_header(uv_box_header)

                # uv body
                if scene.bm_props.local_is_uv_panel_expanded:
                    uv_box_column = uv_box.column(align=True)
                    uv_box_column.prop(map, 'uv_bake_data')
                    uv_box_column.prop(map, 'uv_bake_target')
                    if map.uv_bake_target == 'IMAGE_TEXTURES':
                        uv_box_column = uv_box.column(align=True)
                        uv_box_column.prop(map, 'uv_active_layer')
                        uv_box_column.prop(map, 'uv_type')
                        uv_box_column.prop(map, 'uv_snap_islands_to_pixels')
                        uv_box_column = uv_box.column(align=True)
                        if object.uv_active_layer != 'NONE_AUTO_CREATE':
                            uv_box_column.prop(object, 'uv_use_auto_unwrap')
                        if object.uv_use_auto_unwrap or object.uv_active_layer == 'NONE_AUTO_CREATE':
                            uv_box_column.prop(object, 'uv_auto_unwrap_angle_limit')
                            uv_box_column.prop(object, 'uv_auto_unwrap_island_margin')
                            uv_box_column.prop(object, 'uv_auto_unwrap_use_scale_to_bounds')

class BM_PT_Item_OutputBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Output'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = BM_Object_Get(None, context)
        if object[0].nm_is_universal_container:
            return object[0].nm_uni_container_is_global
        elif object[0].nm_is_local_container:
            return False
        elif any([object[0].hl_is_highpoly, object[0].hl_is_cage]):
            return False
        elif context.scene.bm_props.global_use_name_matching and object[0].nm_is_detached is False:
            for object1 in context.scene.bm_table_of_objects:
                if object1.nm_is_universal_container and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                    return not object1.nm_uni_container_is_global
        return object[1]

    def draw_header(self, context):
        label = "Output"
        self.layout.label(text=label)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = BM_Object_Get(None, context)[0]


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

            # channel packing body
            if scene.bm_props.global_is_chnlpack_panel_expanded:
                row = chnlpack_box.row()

                rows = BM_template_list_get_rows(object.chnlp_channelpacking_table, 4, 0, 5, False)
                row.template_list('BM_UL_Table_of_Objects_Item_ChannelPack', "", object, 'chnlp_channelpacking_table', object, 'chnlp_channelpacking_table_active_index', rows=rows)
                chnlpack_box_column = row.column(align=True)
                chnlpack_box_column.operator(BM_OT_ITEM_ChannelPack_Table_Add.bl_idname, text="", icon='ADD')
                chnlpack_box_column.operator(BM_OT_ITEM_ChannelPack_Table_Remove.bl_idname, text="", icon='REMOVE')
                chnlpack_box_column.separator(factor=1.0)
                chnlpack_box_column.emboss = 'NONE'
                BM_PT_CHNLP_Presets.draw_panel_header(chnlpack_box_column)
                chnlpack_box_column.separator(factor=1.0)
                chnlpack_box_column.operator(BM_OT_ITEM_ChannelPack_Table_Trash.bl_idname, text="", icon='TRASH')

                if len(object.chnlp_channelpacking_table):
                    channel_pack = object.chnlp_channelpacking_table[object.chnlp_channelpacking_table_active_index]
                    col = chnlpack_box.column(align=True)
                    col.use_property_split = False
                    col.prop(channel_pack, 'global_channelpack_type')
                    col.separator(factor=1.0)
                    
                    chnlp_data = {
                        'R1G1B' : ['R', 'G', 'B'],
                        'RGB1A' : ['RGB', 'A'],
                        'R1G1B1A' : ['R', 'G', 'B', 'A'],
                    }
                    icons_data = {
                        'R' : 'EVENT_R',
                        'G' : 'EVENT_G',
                        'B' : 'EVENT_B',
                        'A' : 'EVENT_A',
                        'RGB' : 'IMAGE_RGB',
                    }
                    
                    chnlp_type = channel_pack.global_channelpack_type
                    for prop in chnlp_data[chnlp_type]:
                        prop_use_channel = '{}_use_{}'.format(chnlp_type, prop)
                        prop_map_channel = '{}_map_{}'.format(chnlp_type, prop)
                        row = col.row(align=True)
                        row.active = getattr(channel_pack, prop_use_channel)
                        split = row.split(factor=0.1)
                        split.column().prop(channel_pack, prop_use_channel, text="", icon=icons_data[prop])
                        split_row = split.row()
                        split_row.prop(channel_pack, prop_map_channel, text="")

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
        BM_PT_BAKE_Presets.draw_panel_header(bake_box_header)

        # bake output body
        if scene.bm_props.global_is_bakeoutput_panel_expanded:
            bake_box_column = bake_box.column(align=True)
            bake_box_column.prop(object, 'bake_batchname')
            bake_box_column.prop(object, 'bake_batchname_use_caps')
            # bake_box_column.emboss = 'NONE'
            split = bake_box_column.split(factor=0.4)
            split.column()
            split.column().operator(BM_OT_ITEM_BatchNaming_Preview.bl_idname)
            # bake_box_column.prop(object, 'bake_batchname_preview')

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
            bake_box_column.prop(object, 'bake_assign_modifiers')
            # bake_box_column.prop(scene.bm_props, 'global_bake_use_save_log')

            bake_box_column = bake_box.column(align=True)
            bake_box_column.prop(object, 'bake_hide_when_inactive')
            if object.bake_hide_when_inactive is False:
                bake_box_column.prop(object, 'bake_vg_index')

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

        rows = BM_template_list_get_rows(bm_props.global_texturesets_table, 3, 3, 5, True)
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

            rows = BM_template_list_get_rows(texset.global_textureset_table_of_objects, 3, 3, 5, True)
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
                    texset_box_texset_item_subitems_row = texsets_box.row()
                    rows = BM_template_list_get_rows(item.global_object_name_subitems, 3, 3, 5, True)
                    texset_box_texset_item_subitems_row.template_list('BM_UL_TextureSets_Objects_Table_Item_SubItem', "", item, 'global_object_name_subitems', item, 'global_object_name_subitems_active_index', rows=rows)
                    texset_box_texset_item_subitems_row.operator(BM_OT_SCENE_TextureSets_Objects_Table_InvertSubItems.bl_idname, text="", icon='CHECKBOX_HLT')

                texset_column = texsets_box.column(align=True)
                texset_column.use_property_split = True
                texset_column.use_property_decorate = False

                texset_column.prop(texset, 'uvp_use_uv_repack')
                if texset.uvp_use_uv_repack:
                    texset_column.prop(texset, 'uvp_use_islands_rotate')
                    texset_column.prop(texset, 'uvp_pack_margin')
                    texset_column.prop(texset, 'uvp_use_average_islands_scale')
            
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
        object_full = BM_Object_Get(None, context)
        object = object_full[0]

        # bake body
        layout.prop(scene.bm_props, 'global_use_bake_overwrite')
        layout.prop(scene.bm_props, 'global_use_bakemaster_reset')

        bake_column = layout.column(align=True)
        bake_column_bake_this = bake_column.row()
        bake_column_bake_this.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake This").control = 'BAKE_THIS'

        # object_exists = object_full[1]
        # if object.nm_is_universal_container:
        #     object_exists = True
        # if any([object.hl_is_cage, object.hl_is_highpoly, object.nm_is_local_container, object_exists is False, object.global_use_bake is False]):
        #     bake_column_bake_this.active = False

        bake_column_bake_all = bake_column.row()
        bake_column_bake_all.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake All").control = 'BAKE_ALL'
        bake_column_bake_all.scale_y = 1.5

        # bake_column.enabled = not BM_OT_ITEM_Bake.is_running()
        # bake_column.enabled = context.scene.bm_props.global_bake_available

        # additional operators
        ad_column = layout.column(align=True)
        ad_column.operator(BM_OT_ApplyLastEditedProp.bl_idname, text="Apply Lastly Edited Setting")
        ad_column.operator(BM_OT_CreateArtificialUniContainer.bl_idname, text="Create Bake Job Group")

        # help body
        help_column = layout.column()
        help_column_instruction = help_column.row()
        help_column_instruction.prop(context.scene.bm_props, "global_bake_instruction", text="", icon='INFO')
        help_column_instruction.enabled = False

class BM_PT_HelpBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Help'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw_header(self, context):
        label = "Help"
        icon = 'HELP'
        self.layout.label(text=label, icon=icon)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        # draw operator calls for user to get help
        pages = [
            "Main Page",
            "How to Setup Objects",
            "How to Setup Maps",
            "How to Bake",
            "Support",
        ]

        layout.label(text="Documentaion:")
        help_column = layout.column(align=True)
        for page in pages:
            help_column.operator(BM_OT_Help.bl_idname, text=page).url_base_type = page
