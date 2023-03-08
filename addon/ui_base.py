# ##### BEGIN LICENSE BLOCK #####
#
# "BakeMaster" Blender Add-on (version 3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
#
# This License permits you to use this software for any purpose including
# personal, educational, and commercial; You are allowed to modify it to suit
# your needs, and to redistribute the software or any modifications you make
# to it, as long as you follow the terms of this License and the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This License grants permission to redistribute this software to
# UNLIMITED END USER SEATS (OPEN SOURCE VARIANT) defined by the
# acquired License type. A redistributed copy of this software
# must follow and share similar rights of free software and usage
# specifications determined by the GNU General Public License.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License in
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# ##### END LICENSE BLOCK #####

from bpy.app import version as bpy_app_version
from bpy.types import (
    Panel,
)
from .utils.ui import (
    get_uilist_rows as bm_utils_ui_get_uilist_rows,
    get_active_bakejob_and_object as bm_utils_get_active_bakejob_and_object,
    are_object_props_drawable as bm_utils_are_object_props_drawable,
    get_object_ui_label as bm_utils_get_object_ui_label,
    is_mapsettings_active as bm_utils_is_mapsettings_active,
    ui_draw_hl as bm_utils_ui_draw_hl,
    ui_draw_uv as bm_utils_ui_draw_uv,
    ui_draw_out as bm_utils_ui_draw_out,
    ui_draw_decal as bm_utils_ui_draw_decal,
    ui_draw_matgroups as bm_utils_ui_draw_matgroups,
    ui_draw_mapsettings as bm_utils_ui_draw_mapsettings,
    ui_draw_csh as bm_utils_ui_draw_csh,
)
from .presets import (
    BM_PT_FULL_OBJECT_Presets,
    BM_PT_OBJECT_Presets,
    # BM_PT_DECAL_Presets,
    # BM_PT_HL_Presets,
    # BM_PT_UV_Presets,
    # BM_PT_CSH_Presets,
    # BM_PT_OUT_Presets,
    BM_PT_FULL_MAP_Presets,
    BM_PT_MAP_Presets,
    BM_PT_CHNLP_Presets,
    BM_PT_BAKE_Presets,
)


class BM_PT_BakeJobsBase(Panel):
    bl_label = "Bake Jobs"
    bl_idname = 'BM_PT_BakeJobsBase'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
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
        if not hasattr(context.scene, "bakemaster"):
            return False
        return context.scene.bakemaster.prefs_use_pipeline

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'PIPELINE'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        if bakemaster.pipeline_config_is_attached:
            row.operator('bakemaster.pipeline_config',
                         text="Reload Config").action = 'LOAD'
            row.operator('bakemaster.pipeline_config',
                         text="", icon='UNLINKED').action = 'DETACH'
        else:
            row.operator('bakemaster.pipeline_config',
                         text="Load Config").action = 'LOAD'

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('bakemaster.pipeline_import', icon='FILE_BACKUP')
        if bakemaster.pipeline_import_is_used:
            row.operator('bakemaster.pipeline_import',
                         text="", icon='GREASEPENCIL').edit = True
            row.operator('bakemaster.pipeline_import',
                         text="", icon='UNLINKED').detach = True

        col.operator('bakemaster.pipeline_atlas_targets',
                        icon='ASSET_MANAGER')

        if bakemaster.pipeline_config_is_attached:
            col = layout.column(align=True)
            col.prop(bakemaster, 'pipeline_config_use_update')
            col.prop(bakemaster, 'pipeline_use_stamp_assets')

        col = layout.column(align=True)
        prop = col.column()
        prop.prop(bakemaster, 'pipeline_config_auto_cache')
        prop.active = not bakemaster.pipeline_config_is_attached
        col.prop(bakemaster, 'pipeline_bake_use_write_log')

        col = layout.column(align=True)
        col.prop(bakemaster, 'pipeline_item_use_advanced_controls')
        prop = col.column(align=True)
        prop.operator('bakemaster.pipeline_analyse_edits',
                      icon='HIDE_OFF')
        prop.active = bakemaster.pipeline_item_use_advanced_controls

        layout.operator('bakemaster.pipeline_config',
                        text="Save Config").action = 'SAVE'


class BM_PT_ManagerBase(Panel):
    bl_label = "Manager"
    bl_idname = 'BM_PT_ManagerBase'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'MANAGER'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout


################################################################

from .operators.ui import *


class BM_PT_ObjectsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Objects'

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
        label = "Objects"
        self.layout.label(text=label)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'OBJECTS'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]

        box = layout.box()
        row = box.row(align=True)
        row.operator(BM_OT_Table_of_Objects_Add.bl_idname, text="Add",
                     icon='ADD')
        row.operator(BM_OT_Table_of_Objects_Remove.bl_idname, text="Remove",
                     icon='REMOVE')
        row.scale_y = 1.15

        rows = 5 if bakejob.objects_len >= 1 else 4
        refresh = False
        for object in bakejob.objects:
            try:
                scene.objects[object.name]
            except KeyError:
                if any([object.nm_is_uc, object.nm_is_lc]):
                    continue
                refresh = True
                rows += 1
                break

        row = box.row()
        row.template_list('BM_UL_BakeJob_Objects_Item', "", bakejob,
                          'objects', bakejob, 'objects_active_index',
                          rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_Table_of_Objects.bl_idname, text="",
                     icon='TRIA_UP').control = 'UP'
        col.operator(BM_OT_Table_of_Objects.bl_idname, text="",
                     icon='TRIA_DOWN').control = 'DOWN'
        col.separator()
        col.prop(bakejob, 'use_name_matching', text="",
                 icon='OUTLINER_OB_FONT')
        col.emboss = 'NONE'

        if refresh:
            col.separator()
            col.operator(BM_OT_Table_of_Objects_Refresh.bl_idname,
                         text="", icon='FILE_REFRESH')
        col.separator()
        BM_PT_FULL_OBJECT_Presets.draw_panel_header(col)
        col.separator()
        col.operator(BM_OT_Table_of_Objects_Trash.bl_idname, text="",
                     icon='TRASH')


class BM_PT_ObjectBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Object'
    bl_options = {'DEFAULT_CLOSED'}

    object_exists = True

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        bakejob, object = bm_utils_get_active_bakejob_and_object
        return bm_utils_are_object_props_drawable(bakejob, object)

    def draw_header(self, context):
        bakejob, object = bm_utils_get_active_bakejob_and_object
        packed = bm_utils_get_object_ui_label(context.scene, bakejob.objects,
                                              object)
        self.object_exists, label, icon = packed
        row = self.layout.row(align=True)
        row.use_property_split = False
        row.label(text=label, icon=icon)

        if object.nm_is_uc:
            row.prop(object, 'nm_uc_is_global', text="", icon='NETWORK_DRIVE')
        BM_PT_OBJECT_Presets.draw_panel_header(row)

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.active = self.object_exists

        bakejob, object = bm_utils_get_active_bakejob_and_object
        draw_all = any([not bakejob.objects[
            object.nm_uc_index].nm_uc_is_global,
                        object.nm_uc_is_global])

        if draw_all:
            bm_utils_ui_draw_decal(layout, bakemaster, object)
        if not object.decal_is_decal:
            bm_utils_ui_draw_hl(layout, bakemaster, bakejob, object, object,
                                bpy_app_version)
        if draw_all:
            bm_utils_ui_draw_uv(layout, bakemaster, bakejob, object, object)
        bm_utils_ui_draw_matgroups(layout, bakemaster, object)

        if draw_all:
            bm_utils_ui_draw_csh(layout, bakemaster, object)


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
        if not bakemaster.prefs_use_show_help:
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
        row.template_list('BM_UL_Maps_Item', "", object, 'maps',
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
            row_mapprev.prop(map, 'map_%s_use_preview' % map.map_type)

        if object.nm_is_uc and row_mapprev is not None:
            row_mapprev.active = False

        if hasattr(map, 'map_%s_use_default' % map.map_type):
            col.prop(map, 'map_%s_use_default' % map.map_type)

        bm_utils_ui_draw_mapsettings(context, col, row_mapprev, object, map,
                                     bpy_app_version)
        bm_utils_ui_draw_out(layout, bakemaster, object, map)
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
        if not bakemaster.prefs_use_show_help:
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
            row.template_list('BM_UL_ChannelPacks_Item', "",
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
        if not bakemaster.prefs_use_show_help:
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
        row.template_list('BM_UL_TextureSets_Item', "", bakejob, 'texsets',
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
        row.template_list('BM_UL_TextureSets_Objects_Item', "", texset,
                          'texset_objects', texset,
                          'texset_objects_active_index', rows=rows)
        col = row.column(align=True)
        row = col.row()
        row.operator(BM_OT_SCENE_TextureSets_Objects_Table_Add.bl_idname,
                     text="", icon='ADD')

        # check if can add objects to the texset
        new_texset_objects = TexSet_Object_name_Items(texset,
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
            row.template_list('BM_UL_TextureSets_Objects_Subitems_Item',
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
        if not bakemaster.prefs_use_show_help:
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
        row.operator(BM_OT_Bake.bl_idname,
                     text="Bake This").control = 'BAKE_THIS'

        row = col.row()
        row.operator(BM_OT_Bake.bl_idname,
                     text="Bake All").control = 'BAKE_ALL'
        row.scale_y = 1.5

        col.active = not BM_OT_Bake.is_running()

        col = layout.column(align=True)
        col.operator(BM_OT_ApplyLastEditedProp.bl_idname, text="Apply Lastly Edited Setting")
        col.operator(BM_OT_CreateArtificialUniContainer.bl_idname, text="Create Bake Job Group")

        col = layout.column()
        row = col.row()
        row.prop(bakemaster, "bake_instruction", text="", icon='INFO')
        row.enabled = False
