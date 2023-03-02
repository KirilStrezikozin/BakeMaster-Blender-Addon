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

from bpy.app import version as bpy_app_version
from bpy.types import (
    Panel,
)
from .utils.ui import (
    get_uilist_rows as bm_utils_ui_get_uilist_rows,
    get_active_bakejob_and_object as bm_utils_get_active_bakejob_and_object,
    are_object_props_drawable as bm_utils_are_object_props_drawable,
    is_mapsettings_active as bm_utils_is_mapsettings_active,
    ui_draw_hl as bm_utils_ui_draw_hl,
    ui_draw_uv as bm_utils_ui_draw_uv,
    ui_draw_out as bm_utils_ui_draw_out,
    ui_draw_mapsettings as bm_utils_ui_draw_mapsettings,
)


class BM_PT_BakeJobsBase(Panel):
    bl_label = "Bake Jobs"
    bl_idname = 'BM_PT_BakeJobsBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKEJOBS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        box = layout.box()
        row = box.row()
        min_rows = 1 if bakemaster.bakejobs_len < 2 else 5
        rows = bm_utils_ui_get_uilist_rows(bakemaster.bakejobs_len, min_rows,
                                           5)
        row.template_list('BM_UL_BakeJobs_Item', "", bakemaster,
                          'bakejobs', bakemaster,
                          'bakejobs_active_index', rows=rows)
        col = row.column(align=True)
        col.operator('bakemaster.bakejobs_addremove', text="",
                     icon='ADD').action = 'ADD'

        if bakemaster.bakejobs_len < 1:
            return

        col.operator('bakemaster.bakejobs_addremove', text="",
                     icon='REMOVE').action = 'REMOVE'

        if bakemaster.bakejobs_len < 2:
            return

        col.separator(factor=1.0)
        move_up_row = col.row()
        move_up_row.operator('bakemaster.bakejobs_move', text="",
                             icon='TRIA_UP').action = 'MOVE_UP'
        move_up_row.active = bakemaster.bakejobs_active_index - 1 >= 0
        move_down_row = col.row()
        move_down_row.operator('bakemaster.bakejobs_move', text="",
                               icon='TRIA_DOWN').action = 'MOVE_DOWN'
        move_down_row.active = False
        if bakemaster.bakejobs_active_index + 1 < bakemaster.bakejobs_len:
            move_down_row.active = True
        col.separator(factor=1.0)
        col.emboss = 'NONE'
        col.operator('bakemaster.bakejobs_trash', text="", icon='TRASH')


class BM_PT_PipelineBase(Panel):
    bl_label = "Pipeline"
    bl_idname = 'BM_PT_PipelineBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'PIPELINE'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_ManagerBase(Panel):
    bl_label = "Manager"
    bl_idname = 'BM_PT_ManagerBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'MANAGER'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


class BM_PT_ObjectsBase(Panel):
    bl_label = "Objects"
    bl_idname = 'BM_PT_ObjectsBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'OBJECTS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

class BM_PT_Item_ObjectBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Object'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        object = BM_Object_Get(None, context)
        if object[0].nm_is_uc:
            return object[0].nm_uc_is_global
        elif object[0].nm_is_lc:
            return False
        elif any([object[0].hl_is_highpoly, object[0].hl_is_cage]):
            return False
        elif bakemaster.use_name_matching and object[0].nm_is_detached is False:
            return True
        return object[1]

    def draw_header(self, context):
        object = BM_Object_Get(None, context)[0]
        if bakemaster.use_name_matching and any([object.nm_is_uc, object.nm_is_lc]):
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
            if object1.nm_is_uc and object1.nm_master_index == object.nm_item_uni_container_master_index:
                draw_all = not object1.nm_uc_is_global

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
            icon = 'TRIA_DOWN' if bakemaster.is_decal_panel_expanded else 'TRIA_RIGHT'
            decal_box_header.prop(bakejob, 'is_decal_panel_expanded', text="", icon=icon)
            decal_box_header.emboss = 'NORMAL'
            decal_box_header.label(text="Decal" + text)
            BM_PT_DECAL_Presets.draw_panel_header(decal_box_header)

            # decal body
            if bakemaster.is_decal_panel_expanded:
                if object.nm_uc_is_global is False:
                    decal_box.prop(object, 'decal_is_decal')
                if object.decal_is_decal or object.nm_uc_is_global:
                    decal_box_column = decal_box.column(align=True)
                    decal_box_column.prop(object, 'decal_use_custom_camera')
                    if object.decal_use_custom_camera:
                        decal_box_column.prop(object, 'decal_custom_camera')
                    decal_box.prop(object, 'decal_upper_coordinate')
                    decal_box.prop(object, 'decal_boundary_offset')

        # skip drawing hl, uv, csh subpanels
        if object.decal_is_decal and object.nm_uc_is_global is False:
            if draw_all is False:
                layout.label(text="No settings available")
            # return

        else:
            # hl
            box = layout.box()
            box.use_property_split = True
            box.use_property_decorate = False
            hl_draw = True

            # hl header
            header = box.row(align=True)
            header.use_property_split = False
            header.emboss = 'NONE'
            icon = 'TRIA_DOWN' if bakemaster.is_hl_panel_expanded else 'TRIA_RIGHT'
            header.prop(bakejob, 'is_hl_panel_expanded', text="", icon=icon)
            header.emboss = 'NORMAL'
            header.label(text="High to Lowpoly")
            BM_PT_HL_Presets.draw_panel_header(header)

            # hl body
            if bakemaster.is_hl_panel_expanded:
                if object.nm_uc_is_global is False and draw_all:
                    box.prop(object, 'hl_use_unique_per_map')

                if object.hl_use_unique_per_map is False or draw_all is False:
                    # highpoly
                    split = box.split(factor=0.4)
                    split.column()
                    col = split.column()
                    label = "Highpoly" if len(object.hl_highpolies) <= 1 else "Highpolies"
                    if object.nm_is_uc and object.nm_uc_is_global:
                        label += " (automatic)"
                        hl_draw = False
                    col.label(text=label)
                    if hl_draw:
                        row = col.column().row()
                        rows = BM_template_list_get_rows(object.hl_highpolies, 1, 1, 5, True)
                        row.template_list('BM_UL_Table_of_Objects_Item_Highpoly', "", object, 'hl_highpolies', object, 'hl_highpolies_active_index', rows=rows)
                        col = row.column(align=True)
                        col.operator(BM_OT_ITEM_Highpoly_Table_Add.bl_idname, text="", icon='ADD')
                        col.operator(BM_OT_ITEM_Highpoly_Table_Remove.bl_idname, text="", icon='REMOVE')
                    # highpoly as decal
                    if len(object.hl_highpolies):
                        highpoly_object_index = object.hl_highpolies[object.hl_highpolies_active_index].highpoly_object_index
                        col = box.column(align=True)
                        if highpoly_object_index != -1:
                            source_object = scene.bm_table_of_objects[highpoly_object_index]
                            col.prop(source_object, 'hl_is_decal')
                        if draw_all:
                            col.prop(object, 'hl_decals_use_separate_texset')
                            if object.hl_decals_use_separate_texset:
                                col.prop(object, 'hl_decals_separate_texset_prefix')
                    if hl_draw is False:
                        col = box.column(align=True)
                        col.prop(object, 'hl_decals_use_separate_texset')
                        if object.hl_decals_use_separate_texset:
                            col.prop(object, 'hl_decals_separate_texset_prefix')
                    # cage
                    if len(object.hl_highpolies):
                        col = box.column(align=True)
                        # col.prop(object, 'hl_cage_type')
                        # if object.hl_cage_type == 'STANDARD':
                        if object.hl_use_cage is False:
                            label = "Extrusion"
                            col.prop(object, 'hl_cage_extrusion', text=label)
                            if bpy.app.version >= (2, 90, 0):
                                col.prop(object, 'hl_max_ray_distance')
                            col.prop(object, 'hl_use_cage')
                        else:
                            label = "Cage Extrusion"
                            col.prop(object, 'hl_cage_extrusion', text=label)
                            if hl_draw:
                                col.prop(object, 'hl_use_cage')
                                col.prop(object, 'hl_cage')
                            else:
                                col.prop(object, 'hl_use_cage', text="Use Cage Object (automatic)")
                        # else:
                            # col.prop(object, 'hl_cage_extrusion', text="Extrusion")
        
        # highs, cage, and matgroups are drawn for global uni_c objects
        # everything else not
        if draw_all:
            # uv
            box = layout.box()
            box.use_property_split = True
            box.use_property_decorate = False

            # uv header
            header = box.row(align=True)
            header.use_property_split = False
            header.emboss = 'NONE'
            icon = 'TRIA_DOWN' if bakemaster.is_uv_panel_expanded else 'TRIA_RIGHT'
            header.prop(bakejob, 'is_uv_panel_expanded', text="", icon=icon)
            header.emboss = 'NORMAL'
            header.label(text="UVs and Layers")
            BM_PT_UV_Presets.draw_panel_header(header)

            # uv body
            if bakemaster.is_uv_panel_expanded:
                box.prop(object, 'uv_use_unique_per_map')

                if object.uv_use_unique_per_map is False:
                    # uv
                    col = box.column(align=True)
                    col.prop(object, 'uv_bake_data')
                    col.prop(object, 'uv_bake_target')
                    if object.uv_bake_target == 'IMAGE_TEXTURES':
                        col = box.column(align=True)
                        col.prop(object, 'uv_active_layer')
                        col.prop(object, 'uv_type')
                        col.prop(object, 'uv_snap_islands_to_pixels')
                        col = box.column(align=True)
                        if object.uv_active_layer != 'NONE_AUTO_CREATE':
                            col.prop(object, 'uv_use_auto_unwrap')
                        if object.uv_use_auto_unwrap or object.uv_active_layer == 'NONE_AUTO_CREATE':
                            col.prop(object, 'uv_auto_unwrap_angle_limit')
                            col.prop(object, 'uv_auto_unwrap_island_margin')
                            col.prop(object, 'uv_auto_unwrap_use_scale_to_bounds')

        # matgroups
        matgroups_box = layout.box()
        matgroups_box.use_property_split = True
        matgroups_box.use_property_decorate = False

        # matgroups_box header
        matgroups_box_header = matgroups_box.row(align=True)
        matgroups_box_header.use_property_split = False
        matgroups_box_header.emboss = 'NONE'
        icon = 'TRIA_DOWN' if bakemaster.is_matgroups_panel_expanded else 'TRIA_RIGHT'
        matgroups_box_header.prop(bakejob, 'is_matgroups_panel_expanded', text="", icon=icon)
        matgroups_box_header.emboss = 'NORMAL'
        matgroups_box_header.label(text="Material Groups")
        # no presets

        # matgroups body
        if bakemaster.is_matgroups_panel_expanded:
            # maps table
            mg_table_box = matgroups_box.box()
            mg_table_row = mg_table_box.row()

            rows = BM_template_list_get_rows(object.matgroups_table_of_mats, 4, 0, 5, False)
            mg_table_row.template_list('BM_UL_Table_of_MatGroups_Item', "", object, 'matgroups_table_of_mats', object, 'matgroups_table_of_mats_active_index', rows=rows)
            mg_table_column = mg_table_row.column(align=True)
            mg_table_column.operator(BM_OT_ITEM_MatGroups_Table_Refresh.bl_idname, text="", icon='FILE_REFRESH')
            mg_table_column.separator(factor=1.0)
            mg_table_column.operator(BM_OT_ITEM_MatGroups_Table_EqualizeGroups.bl_idname, text="", icon='STICKY_UVS_LOC')
            mg_table_column.operator(BM_OT_ITEM_MatGroups_Table_UnequalizeGroups.bl_idname, text="", icon='STICKY_UVS_DISABLE')
            mg_table_props = mg_table_box.column(align=True)
            mg_table_props.prop(object, 'matgroups_batch_naming_type')

        if not draw_all:
            return

        # shading
        csh_box = layout.box()
        csh_box.use_property_split = True
        csh_box.use_property_decorate = False

        # shading header
        csh_box_header = csh_box.row(align=True)
        csh_box_header.use_property_split = False
        csh_box_header.emboss = 'NONE'
        icon = 'TRIA_DOWN' if bakemaster.is_csh_panel_expanded else 'TRIA_RIGHT'
        csh_box_header.prop(bakejob, 'is_csh_panel_expanded', text="", icon=icon)
        csh_box_header.emboss = 'NORMAL'
        csh_box_header.label(text="Shading")
        BM_PT_CSH_Presets.draw_panel_header(csh_box_header)

        # shading body
        if bakemaster.is_csh_panel_expanded:
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
                len_of_highs = len(object.hl_highpolies)
            else:
                for map in object.maps:
                    len_of_highs += len(map.hl_highpolies)
            # draw if uni_c is global
            hl_draw = True
            if object.nm_is_uc and object.nm_uc_is_global:
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


class BM_PT_MapsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Maps'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        bakejob, object = bm_utils_get_active_bakejob_and_object(context)
        return bm_utils_are_object_props_drawable(bakejob, object)

    def draw_header(self, context):
        label = "Maps"
        self.layout.label(text=label)
        BM_PT_FULL_MAP_Presets.draw_panel_header(self.layout)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'MAPS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
        object = bakejob.objects[bakejob.objects_active_index]

        # maps table
        box = layout.box()
        row = box.row()

        min_rows = 1 if object.maps_len < 2 else 3
        rows = bm_utils_ui_get_uilist_rows(object.maps_len, min_rows, 5)
        row.template_list('BM_UL_Table_of_Maps_Item', "", object, 'maps',
                          object, 'maps_active_index', rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_ITEM_Maps.bl_idname, text="",
                     icon='ADD').control = 'ADD'
        if object.maps_len > 0:
            col.operator(BM_OT_ITEM_Maps.bl_idname, text="",
                         icon='REMOVE').control = 'REMOVE'
            col.separator(factor=1.0)
            BM_PT_MAP_Presets.draw_panel_header(col)
        else:
            return
        if object.maps_len > 1:
            col.separator(factor=1.0)
            col.operator(BM_OT_ITEM_Maps.bl_idname, text="",
                         icon='TRASH').control = 'TRASH'

        map = object.maps[object.maps_active_index]

        # map settings
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.active = bm_utils_is_mapsettings_active(object, map)

        col.prop(map, 'map_%s_prefix' % map.map_type)

        row_mapprev = None
        if hasattr(map, 'map_%s_use_preview' % map.map_type):
            row_mapprev = col.row()
            row_mapprev.prop(map, 'map_%s_use_preview' % map.map_type,
                             text=BM_Labels.PROP_ITEM_MAP_USEPREVIEW_NAME)

        if object.nm_is_uc and row_mapprev is not None:
            row_mapprev.active = False

        if hasattr(map, 'map_%s_use_default' % map.map_type):
            col.prop(map, 'map_%s_use_default' % map.map_type)

        bm_utils_ui_draw_mapsettings(context, col, row_mapprev, object, map,
                                     bpy_app_version)
        bm_utils_ui_draw_uv(layout, bakemaster, object, map)
        if not object.decal_is_decal and object.hl_use_unique_per_map:
            bm_utils_ui_draw_hl(layout, bakemaster, bakejob, object,
                                bpy_app_version)
        if object.uv_use_unique_per_map:
            bm_utils_ui_draw_uv(layout, bakemaster, object, map)


class BM_PT_OutputBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Output'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        bakejob, object = bm_utils_get_active_bakejob_and_object(context)
        return bm_utils_are_object_props_drawable(bakejob, object)

    def draw_header(self, context):
        label = "Output"
        self.layout.label(text=label)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'OUTPUT'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
        object = bakejob.objects[bakejob.objects_active_index]

        # channel packing
        box = layout.box()
        box.use_property_split = True
        box.use_property_decorate = False

        # channel packing header
        header = box.row()
        header.use_property_split = False
        header.emboss = 'NONE'
        icon = 'TRIA_DOWN'
        if bakemaster.is_chnlpack_panel_expanded:
            icon = 'TRIA_RIGHT'

            # channel packing body
            row = box.row()

            min_rows = 1 if object.chnlps_len < 2 else 3
            rows = bm_utils_ui_get_uilist_rows(object.chnlps_len, min_rows, 3)
            row.template_list('BM_UL_Table_of_Objects_Item_ChannelPack', "",
                              object, "chnlps", object, "chnlps_active_index",
                              rows=rows)
            col = row.column(align=True)
            col.operator(BM_OT_ITEM_ChannelPack_Table_Add.bl_idname, text="",
                         icon='ADD')
            if object.chnlps_len > 0:
                col.operator(BM_OT_ITEM_ChannelPack_Table_Remove.bl_idname,
                             text="", icon='REMOVE')
            if object.chnlps_len > 1:
                col.separator(factor=1.0)
                col.emboss = 'NONE'
                BM_PT_CHNLP_Presets.draw_panel_header(col)
                col.separator(factor=1.0)
                col.operator(BM_OT_ITEM_ChannelPack_Table_Trash.bl_idname,
                             text="", icon='TRASH')

            try:
                channel_pack = object.chnlps[object.chnlps_active_index]
            except IndexError:
                pass
            else:
                col = box.column(align=True)
                col.use_property_split = False
                col.prop(channel_pack, 'channelpack_type')
                col.separator(factor=1.0)

                chnlp_data = {
                    'R1G1B': ['R', 'G', 'B'],
                    'RGB1A': ['RGB', 'A'],
                    'R1G1B1A': ['R', 'G', 'B', 'A'],
                }
                icons_data = {
                    'R': 'EVENT_R',
                    'G': 'EVENT_G',
                    'B': 'EVENT_B',
                    'A': 'EVENT_A',
                    'RGB': 'IMAGE_RGB',
                }

                chnlp_type = channel_pack.channelpack_type
                for prop in chnlp_data[chnlp_type]:
                    prop_use_channel = '{}_use_{}'.format(chnlp_type, prop)
                    prop_map_channel = '{}_map_{}'.format(chnlp_type, prop)
                    row = col.row(align=True)
                    row.active = getattr(channel_pack, prop_use_channel)
                    split = row.split(factor=0.1)
                    split.column().prop(channel_pack, prop_use_channel,
                                        text="", icon=icons_data[prop])
                    split_row = split.row()
                    split_row.prop(channel_pack, prop_map_channel, text="")

        # finish channel packing header
        header.prop(bakemaster, 'is_chnlpack_panel_expanded', text="",
                    icon=icon)
        header.emboss = 'NORMAL'
        header.label(text="Channel Packing")

        # bake output
        box = layout.box()
        box.use_property_split = True
        box.use_property_decorate = False

        # bake output header
        header = box.row()
        header.use_property_split = False
        header.emboss = 'NONE'
        icon = 'TRIA_DOWN'
        if bakemaster.is_bakeoutput_panel_expanded:
            icon = 'TRIA_RIGHT'
        header.prop(bakejob, 'is_bakeoutput_panel_expanded', text="",
                    icon=icon)
        header.emboss = 'NORMAL'
        header.label(text="Bake Output")
        BM_PT_BAKE_Presets.draw_panel_header(header)

        # bake output body
        if not bakemaster.is_bakeoutput_panel_expanded:
            return

        col = box.column(align=True)
        col.prop(object, 'bake_batchname')
        col.prop(object, 'bake_batchname_use_caps')
        # col.emboss = 'NONE'
        split = col.split(factor=0.4)
        split.column()
        split.column().operator(BM_OT_ITEM_BatchNaming_Preview.bl_idname)

        col = box.column(align=True)
        col.prop(object, 'bake_save_internal')
        if object.bake_save_internal is False:
            col.prop(object, 'bake_output_filepath')
            col.prop(object, 'bake_create_subfolder')
            if object.bake_create_subfolder:
                col.prop(object, 'bake_subfolder_name')
        col = box.column(align=True)
        row = col.row()
        row.prop(object, 'bake_device')
        if object.bake_device != 'GPU':
            row.active = True
        else:
            row.active = context.preferences.addons[
                    'cycles'].preferences.has_active_device()
        if bpy.app.version >= (3, 4, 0):
            col.prop(object, 'bake_view_from')
        col.prop(object, 'bake_create_material')
        col.prop(object, 'bake_assign_modifiers')
        col.prop(bakejob, 'bake_use_save_log')

        col = box.column(align=True)
        col.prop(object, 'bake_hide_when_inactive')
        if object.bake_hide_when_inactive is False:
            col.prop(object, 'bake_vg_index')


class BM_PT_TextureSetsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_TextureSets'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        try:
            context.scene.bakemaster.bakejobs[
                    context.scene.bakemaster.bakejobs_active_index]
        except IndexError:
            return False
        else:
            return True

    def draw_header(self, context):
        label = "Texture Sets"
        icon = 'OUTLINER_OB_GROUP_INSTANCE'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'TEXSETS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]

        box = layout.box()
        row = box.row()

        min_rows = 1 if bakejob.texsets_len < 2 else 3
        rows = bm_utils_ui_get_uilist_rows(bakejob.texsets_len, min_rows, 3)
        row.template_list('BM_UL_Table_of_TextureSets', "", bakejob, 'texsets',
                          bakejob, 'texsets_active_index', rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_SCENE_TextureSets_Table_Add.bl_idname, text="",
                     icon='ADD')
        if bakejob.texsets_len > 0:
            col.operator(BM_OT_SCENE_TextureSets_Table_Remove.bl_idname,
                         text="", icon='REMOVE')
        else:
            return
        if bakejob.texsets_len > 1:
            col.separator(factor=1.0)
            col.emboss = 'NONE'
            col.operator(BM_OT_SCENE_TextureSets_Table_Trash.bl_idname,
                         text="", icon='TRASH')

        try:
            texset = bakejob.texsets[bakejob.texsets_active_index]
        except IndexError:
            box.label(text="Please select a Texture Set.")
            return

        box.label(text="Objects in the Texture Set")
        texset = bakejob.texsets[bakejob.texsets_active_index]
        row = box.row()

        rows = bm_utils_ui_get_uilist_rows(texset.texset_objects_len, 1, 3)
        row.template_list('BM_UL_TextureSets_Objects_Table_Item', "", texset,
                          'texset_objects', texset,
                          'texset_objects_active_index', rows=rows)
        col = row.column(align=True)
        row = col.row()
        row.operator(BM_OT_SCENE_TextureSets_Objects_Table_Add.bl_idname,
                     text="", icon='ADD')

        # check if can add objects to the texset
        new_texset_objects = BM_TEXSET_OBJECT_PROPS_object_name_Items(texset,
                                                                      context)
        if len(new_texset_objects) == 1:
            row.enabled = False

        if texset.texset_objects_len > 0:
            col.operator(BM_OT_SCENE_TextureSets_Objects_Table_Remove.bl_idname,
                         text="", icon='REMOVE')
        if texset.texset_objects_len > 1:
            col.separator(factor=1.0)
            col.emboss = 'NONE'
            col.operator(BM_OT_SCENE_TextureSets_Objects_Table_Trash.bl_idname,
                         text="", icon='TRASH')

        if texset.texset_objects_len == 0:
            return

        try:
            texset_object = texset.texset_objects[
                    texset.texset_objects_active_index]
            object = bakejob.objects[texset_object.object_index]
        except IndexError:
            return

        if object.nm_is_uc:
            box.label(text="Container's Objects to include")
            row = box.row()
            rows = bm_utils_ui_get_uilist_rows(texset_object.subitems_len, 1,
                                               3)
            row.template_list('BM_UL_TextureSets_Objects_Table_Item_SubItem',
                              "", texset_object, "subitems", texset_object,
                              "subitems_active_index", rows=rows)
            row.operator(BM_OT_SCENE_TextureSets_Objects_Table_InvertSubItems.bl_idname,
                         text="", icon='CHECKBOX_HLT')

        col = box.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False

        syncer_col = col.column(align=True)
        row = syncer_col.row(align=True)
        row.prop(texset, 'syncer_use', text="")
        row.prop(texset, 'syncer_object_name')
        if texset.syncer_use:
            syncer_col.prop(texset, 'syncer_use_dictate_bake_output')
        syncer_col.active = texset.syncer_use
        col.separator(factor=1.0)

        col.prop(texset, 'uvp_use_uv_repack')
        if texset.uvp_use_uv_repack:
            col.prop(texset, 'uvp_use_islands_rotate')
            col.prop(texset, 'uvp_pack_margin')
            col.prop(texset, 'uvp_use_average_islands_scale')

        row = box.row()
        row.prop(texset, 'textureset_naming')


class BM_PT_BakeBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Bake'

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        try:
            context.scene.bakemaster.bakejobs[
                    context.scene.bakemaster.bakejobs_active_index]
        except IndexError:
            return False
        else:
            return True

    def draw_header(self, context):
        label = "Bake"
        icon = 'RENDER_STILL'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKE'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]

        layout.prop(bakejob, 'use_bake_overwrite')
        layout.prop(bakemaster, 'use_bakemaster_reset')

        col = layout.column(align=True)
        row = col.row()
        row.operator(BM_OT_ITEM_Bake.bl_idname,
                     text="Bake This").control = 'BAKE_THIS'

        row = col.row()
        row.operator(BM_OT_ITEM_Bake.bl_idname,
                     text="Bake All").control = 'BAKE_ALL'
        row.scale_y = 1.5

        col.active = not BM_OT_ITEM_Bake.is_running()

        col = layout.column(align=True)
        col.operator(BM_OT_ApplyLastEditedProp.bl_idname, text="Apply Lastly Edited Setting")
        col.operator(BM_OT_CreateArtificialUniContainer.bl_idname, text="Create Bake Job Group")

        col = layout.column()
        row = col.row()
        row.prop(bakemaster, "bake_instruction", text="", icon='INFO')
        row.enabled = False



















###############################################
###############################################
###############################################
###############################################
###############################################
















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
from .presets import (BM_PT_FULL_OBJECT_Presets,
                      BM_PT_OBJECT_Presets,
                      BM_PT_DECAL_Presets,
                      BM_PT_HL_Presets,
                      BM_PT_UV_Presets,
                      BM_PT_CSH_Presets,
                      BM_PT_FULL_MAP_Presets,
                      BM_PT_MAP_Presets,
                      BM_PT_OUT_Presets,
                      BM_PT_CHNLP_Presets,
                      BM_PT_BAKE_Presets)
from .operators import *
from .operator_bake import BM_OT_ITEM_Bake
from .labels import BM_Labels
from utils.bm_utils import source_object as BM_GETUTILS_source_object


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
                    if object.nm_is_uc and object.nm_master_index == item.nm_item_uni_container_master_index and object.use_bake is False:
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
                scene.objects[object.object_name]
            except (KeyError, AttributeError, UnboundLocalError):
                if bakemaster.use_name_matching and any([object.nm_is_uc, object.nm_is_lc]):
                    continue
                refresh = True
                rows += 1
                break
        if full_len and BM_Object_Get(None, context)[1] is False:
            if bakemaster.use_name_matching and any([object.nm_is_uc, object.nm_is_lc]):
                rows += 1
            rows -= 1
        
        row = box.row()
        row.template_list('BM_UL_Table_of_Objects_Item', "", scene, 'bm_table_of_objects', bakemaster, 'active_index', rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_Table_of_Objects.bl_idname, text="", icon='TRIA_UP').control = 'UP'
        col.operator(BM_OT_Table_of_Objects.bl_idname, text="", icon='TRIA_DOWN').control = 'DOWN'
        col.separator()

        col.prop(bakejob, 'use_name_matching', text="", icon='OUTLINER_OB_FONT')

        col.emboss = 'NONE'

        if refresh:
            col.separator()
            col.operator(BM_OT_Table_of_Objects_Refresh.bl_idname, text="", icon='FILE_REFRESH')
        col.separator()

        if len(scene.bm_table_of_objects):
            object = BM_Object_Get(None, context)
            if (object[1] is True) or (bakemaster.use_name_matching and any([object[0].nm_is_uc, object[0].nm_is_lc])): # and object[0].use_source is False:
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
        label = object[0].object_name
        label_end = ""
        icon = 'PROPERTIES'
        draw_unique_per_object = False
        if bakemaster.use_name_matching and any([object[0].nm_is_uc, object[0].nm_is_lc]):
            label_end = "Container"
            if object[0].nm_is_uc:
                label = object[0].nm_container_name
                draw_unique_per_object = True
            else:
                for object1 in context.scene.bm_table_of_objects:
                    if object1.nm_is_uc and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                        label = object1.nm_container_name
                        label_end = "{} Container".format(object[0].nm_container_name)
                        break
        row = self.layout.row(align=True)
        row.label(text="{} {}".format(label, label_end), icon=icon)
        if draw_unique_per_object:
            row.prop(object[0], 'nm_uc_is_global', text="", icon='NETWORK_DRIVE')

    def draw(self, context):
        object = BM_Object_Get(None, context)
        label = ""
        icon = ''
        draw_label = False
        if bakemaster.use_name_matching and object[0].nm_is_uc:
            if object[0].nm_uc_is_global:
                return
            label = "Universal Container"
            icon = 'TRIA_RIGHT'
            draw_label = True
        elif bakemaster.use_name_matching and object[0].nm_is_lc:
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
        if bakemaster.use_name_matching and object[0].nm_is_detached is False:
            container_name = ""
            draw_configured = False
            for object1 in context.scene.bm_table_of_objects:
                if object1.nm_is_uc and object1.nm_master_index == object[0].nm_item_uni_container_master_index:
                    container_name = object1.nm_container_name
                    draw_configured = object1.nm_uc_is_global
                    break
            if draw_configured:
                label = "Settings configured by %s" % container_name
                draw_label = True
        if draw_label:
            self.layout.label(text=label)
