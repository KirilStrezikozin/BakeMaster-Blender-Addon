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
    AddonPreferences,
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


class BM_PT_Object(BM_PT_ObjectBase):
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


class BM_PREFS_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        bakemaster = context.scene.bakemaster
        layout = self.layout.column(align=True)
        layout.prop(bakemaster, 'lowpoly_tag')
        layout.prop(bakemaster, 'highpoly_tag')
        layout.prop(bakemaster, 'cage_tag')
        layout.prop(bakemaster, 'decal_tag')
        layout = self.layout.column(align=True)
        layout.prop(bakemaster, 'bake_uv_layer_tag')
        layout = self.layout.column(align=True)
        layout.prop(bakemaster, 'use_hide_notbaked')
        layout = self.layout.column(align=True)
        layout.prop(bakemaster, 'bake_match_maps_type')


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


class BM_UL_Redolastaction_Objects_Item(UIList):
    def draw_item(self, context, layout, data, item, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster
        object = bakemaster.bakejobs[item.bakejob_index].objects[
                item.object_index]
        if object is None:
            return

        try:
            context.scene.objects[object.name]
        except KeyError:
            if any([object.nm_is_uc, object.nm_is_lc]):
                icon = 'TRIA_RIGHT'
            else:
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
        column.label(text=item.name, icon=icon)
        row.active = item.use_affect

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass


class BM_UL_Redolastaction_Maps_Item(UIList):
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


class BM_UL_BakeGroups_Item(UIList):
    def draw_item(self, context, layout, data, item, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster
        object = bakemaster.bakejobs[item.bakejob_index].objects[
                item.object_index]
        if object is None:
            return

        active = True
        try:
            context.scene.objects[object.name]
        except KeyError:
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
        column.label(text=item.name)

        if item.is_lowpoly:
            high.active = False
            cage.active = False
        elif item.is_highpoly:
            low.active = False
            cage.active = False
        elif item.is_cage:
            low.active = False
            high.active = False

        layout.active = False
        if active:
            layout.active = any([item.is_lowpoly, item.is_highpoly,
                                 item.is_cage])

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass


class BM_UL_Matchres_Item(UIList):
    def draw_item(self, context, layout, data, item, active_data,
                  active_propname, index):
        row = layout.row()
        row.label(text="%s " % item.image_res)
        row.label(text="%s " % item.image_name)
        row.label(text="%s" % item.socket_and_node_name)

    def invoke(self, context, event):
        pass

    def draw_filter(self, context, layout):
        pass


class BM_UL_BakeJob_Objects_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster
        bakejob = bakemaster.bakejobs[item.bakejob_index]
        row = layout.row()
        row.emboss = 'NONE'

        exists = True
        prop = 'name'
        try:
            context.scene.objects[item.name]
        except KeyError:
            if any([item.nm_is_uc, item.nm_is_lc]):
                icon = 'TRIA_DOWN' if item.nm_is_expanded else 'TRIA_RIGHT'
                prop = 'nm_container_name'
            else:
                icon = 'GHOST_DISABLED'
                exists = False
        else:
            icon = 'OUTLINER_OB_MESH'
            if item.hl_is_lowpoly:
                icon = 'MESH_PLANE'
            elif item.hl_is_highpoly:
                icon = 'VIEW_ORTHO'
            elif item.hl_is_cage:
                icon = 'SELECT_SET'
            if item.hl_is_decal or item.decal_is_decal:
                icon = 'XRAY'

        row.active = exists
        row.active = all([item.use_bake, bakejob.objects[
            item.nm_lc_index].use_bake, bakejob.objects[
                item.nm_uc_index].use_bake])

        if prop == 'name':
            row.label(text=getattr(item, prop), icon=icon)
        else:
            row.prop(item, 'nm_is_expanded', text="", icon=icon)
            row.prop(item, prop, text="")
        use_bake_icon = 'RESTRICT_RENDER_ON'
        if item.use_bake:
            use_bake_icon = 'RESTRICT_RENDER_OFF'
        row.prop(item, 'use_bake', text="", icon=use_bake_icon, emboss=False)

    def draw_filter(self, context, layout):
        pass

    def get_filter(self, items):
        # ftl_flags = []
        ftl_neworder = []

        # all items visible
        ftl_flags = [self.bitflag_filter_item] * len(items)
        # ftl_neworder = [index for index in range(len(items))]

        # item is unvisible if not nm_is_expanded of item's parent container
        visible = False
        parent = None
        parent_mprop = ''
        for item in items:
            if any([item.nm_is_uc, item.nm_is_lc]):
                parent = None
            if parent is not None:
                if getattr(item, parent_mprop) == parent.nm_mindex:
                    # hide item
                    ftl_flags[item.index] &= ~self.bitflag_filter_item
                continue

            visible = item.nm_is_expanded and items[
                    item.nm_uc_index].nm_is_expanded
            if not visible and any([item.nm_is_uc, item.nm_is_lc]):
                parent = item
                ftl_neworder.append(item.index)
            else:
                ftl_neworder.append(item.index)
                continue
            if item.nm_is_uc:
                parent_mprop = 'nm_uc_mindex'
            elif item.nm_is_lc:
                parent_mprop = 'nm_lc_mindex'
                # hide lc if uc is collapsed
                if not visible:
                    ftl_flags[item.index] &= ~self.bitflag_filter_item

        return ftl_flags, ftl_neworder

    def filter_items(self, context, data, propname):
        """
        Filter and order items
        When nm is on, filtered = [items under not collapsed nm_container]
        else, filtered = [all items]
        """
        return self.get_filter(getattr(data, propname))

    def invoke(self, context, event):
        pass


class BM_UL_Highpolies_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        index = item.index
        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index)))
        index_column = split.column()
        index_column.label(text=str(index))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'name', text="")

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_UL_MatGroups_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        space_for_gindex = 0.13  # increase to give more space to gindex
        factor = 1.0 - space_for_gindex*len(str(item.group_index))
        split = layout.row().split(factor=factor)
        split.column().label(text="%s " % item.material_name, icon='MATERIAL')
        index_column = split.column()
        index_column.prop(item, 'group_index', text="")

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_UL_Maps_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster

        index = item.index
        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=0.1*len(str(index)))
        index_column = split.column()
        index_column.label(text=str(index))
        layout.emboss = 'NORMAL'
        row = split.column().row()
        row.prop(item, 'map_type', text="")
        col = row.row()

        icon = 'RESTRICT_RENDER_ON'
        if item.use_bake:
            icon = 'RESTRICT_RENDER_OFF'
        layout.active = item.use_bake

        object = bakemaster.bakejobs[item.bakejob_index].objects[
                item.object_index]

        uv_container = object
        if object.uv_use_unique_per_map:
            uv_container = item

        if item.map_type == 'DECAL' and object.bake_save_internal:
            layout.active = False
            icon = 'RESTRICT_RENDER_ON'
            col.enabled = False

        if all([uv_container.uv_bake_data == 'VERTEX_COLORS',
                item.map_type != 'VERTEX_COLOR_LAYER']):
            layout.active = False
            icon = 'RESTRICT_RENDER_ON'
            col.enabled = False
        if uv_container.uv_bake_target == 'VERTEX_COLORS':
            if all([item.map_type == 'NORMAL',
                    item.map_normal_data == 'MULTIRES']):
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                col.enabled = False
            elif all([item.map_type == 'DISPLACEMENT',
                      item.map_displacement_data in ['HIGHPOLY', 'MULTIRES']]):
                layout.active = False
                icon = 'RESTRICT_RENDER_ON'
                col.enabled = False

        col.prop(item, 'use_bake', text="", icon=icon)

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_UL_ChannelPacks_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemater
        object = bakemaster.bakejobs[item.bakejob_index].objects[
                item.object_index]

        text = ""
        if object.bake_save_internal:
            layout.active = False
            text = " (External Bake only)"

        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=0.1*len(str(item.index)))
        index_column = split.column()
        index_column.label(text=str(item.index))
        layout.emboss = 'NORMAL'
        split.column().prop(item, 'channelpack_name', text=text)

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_UL_TextureSets_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        len_index = len(str(item.index))
        split_factor = 1-0.05*3 if len_index < 4 else len_index
        layout.emboss = 'NONE'
        row = layout.row()
        split = row.split(factor=split_factor)
        try:
            split.column().prop(item, 'textureset_name', text="",
                                icon='OUTLINER_COLLECTION')
        except KeyError:
            split.column().prop(item, 'textureset_name', text="", icon='GROUP')
        index_column = split.column()
        index_column.label(text=str(item.index))

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_UL_TextureSets_Objects_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        len_index = len(str(item.index))
        split_factor = 1-0.05*3 if len_index < 4 else len_index

        icon = 'BLANK1'
        if item.name != 'NONE':
            bakemaster = context.scene.bakemater
            object = bakemaster.bakejobs[item.bakejob_index].objects[
                    item.object_index]
            try:
                context.scene.objects[object.name]
            except KeyError:
                if object.nm_is_uc:
                    icon = 'TRIA_RIGHT'
                else:
                    icon = 'GHOST_DISABLED'
                    layout.active = False
            else:
                icon = 'OUTLINER_OB_MESH'

            if not object.use_bake or object.decal_is_decal:
                layout.active = False

        layout.emboss = 'PULLDOWN_MENU'
        row = layout.row()
        split = row.split(factor=split_factor)
        split.column().prop(item, 'name', text="", icon=icon)
        index_column = split.column()
        index_column.label(text=str(item.index))

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass


class BM_UL_TextureSets_Objects_Subitems_Item(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        len_index = len(str(item.index))
        split_factor = 1-0.05*3 if len_index < 4 else len_index

        bakemaster = context.scene.bakemater
        object = bakemaster.bakejobs[item.bakejob_index].objects[
                item.object_index]

        icon = 'OUTLINER_OB_MESH'
        if object.hl_is_lowpoly:
            icon = 'MESH_PLANE'
        elif object.decal_is_decal:
            icon = 'XRAY'
            layout.active = False
        if not object.use_bake:
            layout.active = False

        try:
            context.scene.objects[object.name]
        except KeyError:
            icon = 'GHOST_DISABLED'
            layout.active = False

        row = layout.row()
        split = row.split(factor=split_factor)
        name_column = split.row()
        name_column.prop(item, 'object_include_in_texset', text="")
        row.emboss = 'NONE'
        name_column_row = name_column.row()
        name_column_row.label(text=item.name, icon=icon)
        index_column = split.column()
        index_column.label(text=str(item.index))
        row.active = item.object_include_in_texset

    def draw_filter(self, context, layout):
        pass

    def invoke(self, context, event):
        pass
