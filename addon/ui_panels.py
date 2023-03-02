# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (version 3.0.0)
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

from .ui_base import (
    BM_PT_BakeJobsBase,
    BM_PT_PipelineBase,
    BM_PT_ManagerBase,
    BM_PT_ObjectsBase,
    BM_PT_ObjectBase,
    BM_PT_MapsBase,
    BM_PT_OutputBase,
    BM_PT_TextureSetsBase,
    BM_PT_BakeBase,
)
from bpy.types import (
    UIList,
)

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"


class BM_PT_BakeJobs(BM_PT_BakeJobsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Pipeline(BM_PT_PipelineBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Manager(BM_PT_ManagerBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Objects(BM_PT_ObjectsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Objec(BM_PT_ObjectBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Objects.bl_idname


class BM_PT_Maps(BM_PT_MapsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Output(BM_PT_OutputBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_TextureSets(BM_PT_TextureSetsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Bake(BM_PT_BakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PREFS_Addon_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        bm_props = bakemaster
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'lowpoly_tag')
        layout.prop(bm_props, 'highpoly_tag')
        layout.prop(bm_props, 'cage_tag')
        layout.prop(bm_props, 'decal_tag')
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'bake_uv_layer_tag')
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'use_hide_notbaked')
        layout = self.layout.column(align=True)
        layout.prop(bm_props, 'bake_match_maps_type')


class BM_UL_BakeJobs_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.emboss = 'NONE'
        layout.prop(item, "name", text="", icon='SEQUENCE')
        icon = 'RESTRICT_RENDER_OFF' if item.use_bake else 'RESTRICT_RENDER_ON'
        layout.prop(item, 'use_bake', text="", icon=icon, emboss=False)
        layout.active = item.use_bake

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_ALEP_UL_Objects_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, active_data,
                  active_propname, index):
        source_object = BM_GETUTILS_source_object(context, item.object_name)
        if source_object:
            object = source_object[0]
            try:
                context.scene.objects[object.object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                icon = 'GHOST_DISABLED'
            else:
                icon = 'OUTLINER_OB_MESH'

            if object.hl_is_lowpoly:
                icon = 'MESH_PLANE'
            if object.decal_is_decal:
                icon = 'XRAY'
        else:
            icon = 'TRIA_RIGHT'

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
    def draw_item(self, context, layout, data, item, active_data,
                  active_propname, index):
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
    def draw_item(self, context, layout, data, item, active_data,
                  active_propname, index):
        source_object = [object for object in context.scene.bm_table_of_objects
                         if object.object_name == item.object_name]
        if len(source_object) == 0:
            layout.label(text="ERROR. Object not found", icon='ERROR')
            return

        active = True
        object = source_object[0]
        try:
            context.scene.objects[object.object_name]
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
        if bakemaster.use_name_matching:
            item_draw_ghost = False
            indents = [0, 2, 4, 6]
            for i in range(indents[item.nm_this_indent]):
                row.split(factor=0.1)

            # drawing object
            if not any ([item.nm_is_uc, item.nm_is_lc]):
                # ghost object
                try:
                    context.scene.objects[item.object_name]
                except (KeyError, AttributeError, UnboundLocalError):
                    row.label(text=item.object_name, icon='GHOST_DISABLED')
                    if not any([item.nm_is_uc, item.nm_is_lc, item.nm_is_detached]):
                        row.prop(item, 'use_bake', text="", icon='RESTRICT_RENDER_ON', emboss=False)
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
                    row.label(text=item.object_name, icon=icon)
            
            # drawing containers
            else:
                row.emboss = 'NONE'
                icon = 'TRIA_DOWN' if item.nm_is_expanded else 'TRIA_RIGHT'
                row.prop(item, "nm_is_expanded", text="", icon=icon)
                #row.emboss = 'NORMAL'
                row.prop(item, "nm_container_name", text="")
            
            # drawing use_bake for universal and detached
            if item.nm_is_uc or item.nm_is_detached:
                if item.use_bake:
                    icon = 'RESTRICT_RENDER_OFF'
                else:
                    row.active = False
                    icon = 'RESTRICT_RENDER_ON'
                if item_draw_ghost:
                    icon = 'RESTRICT_RENDER_ON'
                    row.active = False
                # row.use_property_decorate = False
                row.prop(item, 'use_bake', text="", icon=icon, emboss=False)
            # set row.active to False for items the use_bake of uni_container of which is False
            else:
                for object in context.scene.bm_table_of_objects:
                    if object.nm_is_uc and object.nm_mindex == item.nm_uc_mindex and object.use_bake is False:
                        row.active = False
                        break
        
        # no name matching - default table
        else:
            # ghost object
            try:
                context.scene.objects[item.object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                row.label(text=item.object_name, icon='GHOST_DISABLED')
                row.prop(item, 'use_bake', text="", icon='RESTRICT_RENDER_ON', emboss=False)
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
                row.label(text=item.object_name, icon=icon)

                if item.use_bake:
                    icon = 'RESTRICT_RENDER_OFF'
                else:
                    row.active = False
                    icon = 'RESTRICT_RENDER_ON'
                # row.use_property_decorate = False
                row.prop(item, 'use_bake', text="", icon=icon, emboss=False)

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
        index_value = item.item_index
        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'object_name', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_MatGroups_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        factor=1.0 - 0.13*len(str(item.group_index))
        split = layout.row().split(factor=factor)
        split.column().label(text=item.material_name + " ", icon='MATERIAL')
        index_column = split.column()
        index_column.prop(item, 'group_index', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Maps_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.map_index
        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        props_column = split.column().row()
        props_column.prop(item, 'map_type', text="")
        props_column_use_bake = props_column.row()
        if item.use_bake:
            icon = 'RESTRICT_RENDER_OFF'
        else:
            icon = 'RESTRICT_RENDER_ON'
            layout.active = False

        object = BM_Object_Get(item, context)[0]
        if object.uv_use_unique_per_map:
            uv_container = item
        else:
            uv_container = object

        if item.map_type == 'DECAL' and object.bake_save_internal:
            layout.active = False
            icon = 'RESTRICT_RENDER_ON'
            props_column_use_bake.enabled = False

        if uv_container.uv_bake_data == 'VERTEX_COLORS':
            if item.map_type != 'VERTEX_COLOR_LAYER':
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                props_column_use_bake.enabled = False
        if uv_container.uv_bake_target == 'VERTEX_COLORS':
            if item.map_type == 'NORMAL' and item.map_normal_data == 'MULTIRES':
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                props_column_use_bake.enabled = False
            elif item.map_type == 'DISPLACEMENT' and item.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                props_column_use_bake.enabled = False

        props_column_use_bake.prop(item, 'use_bake', text="", icon=icon)

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Maps_Item_Highpoly(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.item_index
        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index_value)))
        index_column = split.column()
        index_column.label(text=str(index_value))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'object_name', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Objects_Item_ChannelPack(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.channelpack_index

        # channel pack inactive if internal bake
        object = context.scene.bm_table_of_objects[item.channelpack_object_index]
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
        split.column().prop(item, 'channelpack_name', text=text)

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_TextureSets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.textureset_index
        split_factor = 1-0.05*3 if len(str(index_value)) < 4 else len(str(index_value))
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=split_factor)
        if bpy.app.version > (2, 91, 0):
            icon = 'OUTLINER_COLLECTION'
        else:
            icon = 'GROUP'
        split.column().prop(item, 'textureset_name', text="", icon=icon)
        index_column = split.column()
        index_column.label(text=str(index_value))

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_TextureSets_Objects_Table_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.object_index
        split_factor = 1-0.05*3 if len(str(index_value)) < 4 else len(str(index_value))
        
        icon = 'BLANK1'
        if item.object_name != 'NONE':
            object = context.scene.bm_table_of_objects[item.source_object_index]
            try:
                context.scene.objects[object.object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                icon = 'GHOST_DISABLED'
                layout.active = False

            if bakemaster.use_name_matching and object.nm_is_uc:
                icon = 'TRIA_RIGHT'
                layout.active = True
            elif layout.active:
                icon = 'OUTLINER_OB_MESH'

            if object.use_bake is False or object.decal_is_decal:
                layout.active = False

        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=split_factor)
        split.column().prop(item, 'object_name', text="", icon=icon)
        index_column = split.column()
        index_column.label(text=str(index_value))

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_TextureSets_Objects_Table_Item_SubItem(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        index_value = item.object_index
        split_factor = 1-0.05*3 if len(str(index_value)) < 4 else len(str(index_value))
        
        source_object = [object for object in context.scene.bm_table_of_objects if object.object_name == item.global_object_name][0]

        icon = ''
        if source_object.hl_is_lowpoly:
            icon = 'MESH_PLANE'
        if source_object.decal_is_decal:
            icon = 'XRAY'

        if source_object.use_bake is False or source_object.decal_is_decal:
            layout.active = False
        try:
            context.scene.objects[source_object.object_name]
        except (KeyError, AttributeError, UnboundLocalError):
            icon = 'GHOST_DISABLED'
            layout.active = False

        if icon == '':
            icon = 'OUTLINER_OB_MESH'

        row = layout.row()
        split = row.split(factor=split_factor)
        name_column = split.row()
        name_column.prop(item, 'object_include_in_texset', text="")
        row.emboss = 'NONE'
        name_column_row = name_column.row()
        name_column_row.label(text=item.object_name, icon=icon)
        index_column = split.column()
        index_column.label(text=str(index_value))
        row.active = item.object_include_in_texset

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass

class BM_UL_Table_of_Objects_Item_BatchNamingTable_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.emboss = 'NONE'
        layout.prop(item, 'keyword', text="")

    def draw_filter(self, context, layout):
        pass
    
    def invoke(self, context, event):
        pass
