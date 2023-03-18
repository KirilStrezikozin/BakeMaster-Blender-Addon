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
from .utils import (
    ui as bm_ui_utils,
    get as bm_get,
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
        rows = bm_ui_utils.get_uilist_rows(bakemaster.bakejobs_len, min_rows,
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
        if not hasattr(context.scene, "bakemaster"):
            return False
        try:
            context.scene.bakemaster.bakejobs[
                context.scene.bakemaster.bakejobs_active_index]
        except IndexError:
            return False
        else:
            return True

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'MANAGER'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(bakejob, 'manager_container_type')
        col.prop(bakejob, 'manager_container_share_settings')
        col.prop(bakejob, 'manager_container_share_items')
        col.prop(bakejob, 'manager_use_filter_baked')

        col = layout.column(align=True)
        col.operator('bakemaster.manager_presets', icon='PASTEDOWN')
        col.operator('bakemaster.manager_redolastaction', icon='RECOVER_LAST')
        col.operator('bakemaster.manager_groupcontainers', icon='TRIA_DOWN')
        col.operator('bakemaster.manager_bakejob_tools', icon='SEQUENCE')


################################################################

from .operators.ui import *


class BM_PT_ObjectsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Objects'

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        return bakejob is not None

    def draw_header(self, context):
        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        label = bakejob.manager_container_type.capitalize()
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

        bakejob = bm_get.bakejob(bakemaster)

        box = layout.box()
        row = box.row(align=True)
        row.operator(BM_OT_Table_of_Objects_Add.bl_idname, text="Add",
                     icon='ADD')
        row.operator(BM_OT_Table_of_Objects_Remove.bl_idname, text="Remove",
                     icon='REMOVE')
        row.scale_y = 1.15

        rows = 5 if bakejob.objects_len >= 1 else 4
        refresh = False
        for container in bakejob.objects:
            try:
                scene.objects[container.name]
            except KeyError:
                if any([container.nm_is_uc, container.nm_is_lc]):
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

        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)
        return bm_ui_utils.are_c_props_drawable(bakejob, container)

    def draw_header(self, context):
        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)
        packed = bm_ui_utils.get_c_ui_label(context.scene, bakejob.objects,
                                            container)
        self.object_exists, label, icon = packed
        row = self.layout.row(align=True)
        row.use_property_split = False
        row.label(text=label, icon=icon)

        if container.nm_is_uc:
            row.prop(container, 'nm_uc_is_global', text="",
                     icon='NETWORK_DRIVE')
        BM_PT_OBJECT_Presets.draw_panel_header(row)

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.active = self.object_exists

        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)
        draw_all = any([not bakejob.objects[
            container.nm_uc_index].nm_uc_is_global,
                        container.nm_uc_is_global])

        if draw_all:
            bm_ui_utils.draw_decal(layout, bakemaster, container)
        if not container.decal_is_decal:
            bm_ui_utils.draw_hl(layout, bakemaster, bakejob, container, container,
                                bpy_app_version)
        if draw_all:
            bm_ui_utils.draw_uv(layout, bakemaster, bakejob, container, container)
        bm_ui_utils.draw_matgroups(layout, bakemaster, container)

        if draw_all:
            bm_ui_utils.draw_csh(layout, bakemaster, container)


class BM_PT_MapsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Maps'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)
        return bm_ui_utils.are_c_props_drawable(bakejob, container)

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

        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)

        # maps table
        box = layout.box()
        row = box.row()

        min_rows = 1 if container.maps_len < 2 else 3
        rows = bm_ui_utils.get_uilist_rows(container.maps_len, min_rows, 5)
        row.template_list('BM_UL_Maps_Item', "", container, 'maps',
                          container, 'maps_active_index', rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_ITEM_Maps.bl_idname, text="",
                     icon='ADD').control = 'ADD'
        if container.maps_len > 0:
            col.operator(BM_OT_ITEM_Maps.bl_idname, text="",
                         icon='REMOVE').control = 'REMOVE'
            col.separator(factor=1.0)
            BM_PT_MAP_Presets.draw_panel_header(col)
        else:
            return
        if container.maps_len > 1:
            col.separator(factor=1.0)
            col.operator(BM_OT_ITEM_Maps.bl_idname, text="",
                         icon='TRASH').control = 'TRASH'

        map = container.maps[container.maps_active_index]

        # map settings
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.active = bm_ui_utils.is_mapsettings_active(container, map)

        col.prop(map, 'map_%s_prefix' % map.map_type)

        row_mapprev = None
        if hasattr(map, 'map_%s_use_preview' % map.map_type):
            row_mapprev = col.row()
            row_mapprev.prop(map, 'map_%s_use_preview' % map.map_type)

        if container.nm_is_uc and row_mapprev is not None:
            row_mapprev.active = False

        if hasattr(map, 'map_%s_use_default' % map.map_type):
            col.prop(map, 'map_%s_use_default' % map.map_type)

        bm_ui_utils.draw_mapsettings(context, col, row_mapprev, container, map,
                                     bpy_app_version)
        bm_ui_utils.draw_out(layout, bakemaster, container, map)
        if not container.decal_is_decal and container.hl_use_unique_per_map:
            bm_ui_utils.draw_hl(layout, bakemaster, bakejob, container,
                                bpy_app_version)
        if container.uv_use_unique_per_map:
            bm_ui_utils.draw_uv(layout, bakemaster, container, map)


class BM_PT_OutputBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Item_Output'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, "bakemaster"):
            return False
        bakemaster = context.scene.bakemaster
        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)
        return bm_ui_utils.are_c_props_drawable(bakejob, container)

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

        bakejob = bm_get.bakejob(bakemaster)
        container = bm_get.container(bakejob)

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

            min_rows = 1 if container.chnlps_len < 2 else 3
            rows = bm_ui_utils.get_uilist_rows(container.chnlps_len, min_rows, 3)
            row.template_list('BM_UL_ChannelPacks_Item', "",
                              container, "chnlps", container, "chnlps_active_index",
                              rows=rows)
            col = row.column(align=True)
            col.operator(BM_OT_ITEM_ChannelPack_Table_Add.bl_idname, text="",
                         icon='ADD')
            if container.chnlps_len > 0:
                col.operator(BM_OT_ITEM_ChannelPack_Table_Remove.bl_idname,
                             text="", icon='REMOVE')
            if container.chnlps_len > 1:
                col.separator(factor=1.0)
                col.emboss = 'NONE'
                BM_PT_CHNLP_Presets.draw_panel_header(col)
                col.separator(factor=1.0)
                col.operator(BM_OT_ITEM_ChannelPack_Table_Trash.bl_idname,
                             text="", icon='TRASH')

            try:
                channel_pack = container.chnlps[container.chnlps_active_index]
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
        col.prop(container, 'bake_batchname')
        col.prop(container, 'bake_batchname_use_caps')
        # col.emboss = 'NONE'
        split = col.split(factor=0.4)
        split.column()
        split.column().operator(BM_OT_ITEM_BatchNaming_Preview.bl_idname)

        col = box.column(align=True)
        col.prop(container, 'bake_save_internal')
        if container.bake_save_internal is False:
            col.prop(container, 'bake_output_filepath')
            col.prop(container, 'bake_create_subfolder')
            if container.bake_create_subfolder:
                col.prop(container, 'bake_subfolder_name')
        col = box.column(align=True)
        row = col.row()
        row.prop(container, 'bake_device')
        if container.bake_device != 'GPU':
            row.active = True
        else:
            row.active = context.preferences.addons[
                    'cycles'].preferences.has_active_device()
        if bpy.app.version >= (3, 4, 0):
            col.prop(container, 'bake_view_from')
        col.prop(container, 'bake_create_material')
        col.prop(container, 'bake_assign_modifiers')
        col.prop(bakejob, 'bake_use_save_log')

        col = box.column(align=True)
        col.prop(container, 'bake_hide_when_inactive')
        if container.bake_hide_when_inactive is False:
            col.prop(container, 'bake_vg_index')


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

        bakejob = bm_get.bakejob(bakemaster)

        box = layout.box()
        row = box.row()

        min_rows = 1 if bakejob.texsets_len < 2 else 3
        rows = bm_ui_utils.get_uilist_rows(bakejob.texsets_len, min_rows, 3)
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

        rows = bm_ui_utils.get_uilist_rows(texset.texset_objects_len, 1, 3)
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
            container = bakejob.objects[texset_object.object_index]
        except IndexError:
            return

        if container.nm_is_uc:
            box.label(text="Container's Objects to include")
            row = box.row()
            rows = bm_ui_utils.get_uilist_rows(texset_object.subitems_len, 1,
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


#####################################################
#####################################################


class BM_PT_BakeBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Bake'

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

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
        pass


class BM_PT_BakeControlsBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_BakeControls'
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header(self, context):
        pass

    def draw_header_preset(self, context):
        pass

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(bakemaster, "bake_wait_user")

        col = layout.column(align=True)
        col.operator('bakemaster.bake_one')
        row = col.row()
        row.operator('bakemaster.bake_all')
        row.scale_y = 1.5
        col.active = not bakemaster.bake_is_running

        row = layout.row(align=True)
        if bakemaster.bake_hold_on_pause:
            text = "Resume"
            icon = 'PLAY'
        else:
            text = "Pause"
            icon = 'PAUSE'
        row.operator('bakemaster.bake_pause', text=text, icon=icon)
        row.operator('bakemaster.bake_stop', icon='QUIT')
        row.operator('bakemaster.bake_cancel', icon='CANCEL')
        row.active = bakemaster.bake_is_running

        row = layout.row()
        row.prop(bakemaster, "short_bake_instruction", text="", icon='INFO')
        row.enabled = False

        layout.separator(factor=1.5)


class BM_PT_BakeHistoryBase(Panel):
    bl_label = " "
    bl_idname = 'BM_PT_BakeHistory'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "bakemaster")

    def draw_header(self, context):
        label = "Bake History"
        icon = 'TIME'
        self.layout.label(text=label, icon=icon)

    def draw_header_preset(self, context):
        bakemaster = context.scene.bakemaster
        if not bakemaster.prefs_use_show_help:
            return
        self.layout.row().operator('bakemaster.help', text="",
                                   icon='HELP').action = 'BAKEHISTORY'

    def draw(self, context):
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        rows = bm_ui_utils.get_uilist_rows(bakemaster.bakehistory_len, 1, 10)
        row.template_list('BM_UL_BakeHistory', "", bakemaster,
                          'bakehistory', bakemaster,
                          'bakehistory_active_index', rows=rows)
