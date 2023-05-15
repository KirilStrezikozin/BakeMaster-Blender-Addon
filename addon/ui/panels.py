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

__all__ = [
        "BM_PT_Preferences",
        "BM_PT_BakeJobs",
        "BM_PT_Containers",
        "BM_PT_Bake",
        "BM_PT_BakeControls",
        "BM_PT_BakeHistory",
]

from bpy.types import (
    Context,
    AddonPreferences,
)

from bpy.props import (
    EnumProperty,
    BoolProperty,
    IntProperty,
)

from .helpers import (
    get_uilist_rows as _get_uilist_rows,
    BM_UI_ms_draw,
    BM_PT_Helper,
)


# class F():


class BM_PT_Preferences(AddonPreferences):

    # dev: __package__ is 'BakeMaster.addon'
    # end user: __package__ is 'BakeMaster'
    bl_idname = __package__.split(".")[0]

    # Addon Preferences Props

    use_show_help: BoolProperty(
        name="Show Help buttons",
        description="Allow help buttons in panels' headers",
        default=True)

    default_bakejob_type: EnumProperty(
        name="Default type",
        description="Choose BakeJob's default type. Hover over values to see descriptions",  # noqa: E501
        default='OBJECTS',
        items=[('OBJECTS', "Objects", "Bake Job will contain Objects, where each of them will contain Maps to bake"),  # noqa: E501
               ('MAPS', "Maps", "Bake Job will contain Maps, where each of them will contain Objects the map should be baked for")])  # noqa: E501

    use_developer_mode: BoolProperty(
        name="Developer mode",
        description="Toggle debugging and developer UI controls and features",
        default=False)

    developer_use_console_debug: BoolProperty(
        name="Debug to Console",
        description="Debug statuses, process progress, and error codes to the Console",  # noqa: E501
        default=True)

    developer_use_show_groups_indexes: BoolProperty(
        name="Show groups indexes",
        default=False)

    developer_show_tickers: BoolProperty(
        name="Show tickers values",
        default=False)

    developer_ui_indent_width: IntProperty(
        name="Indent width",
        description="Indent width for items in groups. Recommended: from 0 to 4",  # noqa: E501
        default=0)

    developer_use_group_descending_lines: BoolProperty(
        name="Descending lines for Groups",
        default=True)

    developer_use_orange_ob_icons: BoolProperty(
        name="Orange Object icon",
        description="Toggle between orange and white object icons",
        default=True)

    def poll(self, context: Context) -> bool:
        return hasattr(context.scene, "bakemaster")

    def draw(self, context: Context) -> None:
        bakemaster = context.scene.bakemaster
        layout = self.layout

        # Help
        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="Help")

        col = split.column(align=True)
        col.prop(self, "use_show_help")
        ###

        # BakeJob
        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="BakeJob")
        col = split.column(align=True)
        col.prop(self, "default_bakejob_type", text="type")
        ###

        # BakeJob
        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="Developer mode")
        col = split.column()
        col.prop(self, "use_developer_mode", text="Show Options")
        if bakemaster.get_pref(context, "use_developer_mode"):
            col.prop(self, "developer_use_orange_ob_icons")

            col_aligned = col.column(align=True)
            col_aligned.prop(self, "developer_use_group_descending_lines")
            col_aligned.prop(self, "developer_ui_indent_width")

            col.prop(self, "developer_use_show_groups_indexes")
            col.prop(self, "developer_show_tickers")
            col.prop(self, "developer_use_console_debug")


class BM_PT_BakeJobs(BM_PT_Helper, BM_UI_ms_draw):
    bl_label = "Bake Jobs"
    bl_idname = 'BM_PT_BakeJobs'

    data_name = "bakejobs"

    def draw(self, context: Context) -> None:
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        box = layout.box()
        row = box.row()

        # check if tools for multi selection are available
        ml_rows = 0
        if self.has_multi_selection(bakemaster, bakemaster):
            seq = bakemaster.get_seq("bakejobs", "is_selected", bool)
            if seq[seq].size > 0:
                ml_rows = 1
            else:
                ml_rows = 0

        if bakemaster.bakejobs_len < 2 + ml_rows:
            min_rows = 2 + ml_rows
        else:
            min_rows = 4 + ml_rows
        rows = _get_uilist_rows(bakemaster.bakejobs_len + ml_rows,
                                min_rows, 4 + ml_rows)

        row.template_list('BM_UL_BakeJobs', "", bakemaster,
                          'bakejobs', bakemaster,
                          'bakejobs_active_index', rows=rows)
        col = row.column(align=True)
        col.operator('bakemaster.bakejob_add', text="",
                     icon='ADD').index = bakemaster.bakejobs_active_index

        if bakemaster.bakejobs_len > 0:
            remove_ot = col.operator('bakemaster.bakejob_remove', text="",
                                     icon='REMOVE')
            remove_ot.index = bakemaster.bakejobs_active_index

        col.emboss = 'NONE'
        if bakemaster.bakejobs_len > 1:
            col.separator(factor=1.0)
            col.operator('bakemaster.bakejob_trash', text="", icon='TRASH')

        col.separator(factor=1.0)
        col.operator('bakemaster.bake_setup', text="", icon='PREFERENCES')

        if ml_rows == 0:
            return
        col.separator(factor=1.0)
        col.emboss = 'NORMAL'
        col.operator('bakemaster.bakejob_merge', text="",
                     icon='SELECT_EXTEND')


class BM_PT_Containers(BM_PT_Helper, BM_UI_ms_draw):
    bl_label = " "
    bl_idname = 'BM_PT_Containers'

    data_name = "containers"

    @classmethod
    def panel_poll(cls, context: Context) -> bool:
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster)
        if bakejob is None:
            return False

        if all([cls.has_multi_selection(cls, bakemaster, bakejob, "bakejobs"),
                not bakejob.is_selected]):
            return False

        return True

    def draw_header(self, context: Context) -> None:
        bakemaster = context.scene.bakemaster
        bakejob = bakemaster.get_bakejob(bakemaster)
        if bakejob is None:
            return

        row = self.layout.row(align=True)
        row.active = bakejob.use_bake

        if bakejob.type == 'OBJECTS':
            type_icon = bakemaster.get_icon('OBJECTS')
            type_ot = self.draw_prop(
                bakemaster, "bakejobs", row, "Operator", bakejob, "type",
                'bakemaster.bakejob_change_type', text="",
                icon_value=type_icon)
        else:
            type_ot = self.draw_prop(
                bakemaster, "bakejobs", row, "Operator", bakejob, "type",
                'bakemaster.bakejob_change_type', text="", icon='RENDERLAYERS')
        if type_ot is not None:
            type_ot.index = bakejob.index

        label = "  %s" % bakejob.type.capitalize()
        row.label(text=label)

    def draw(self, context: Context) -> None:
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        bakejob = bakemaster.get_bakejob(bakemaster)
        if bakejob is None:
            return

        box = layout.box()
        row = box.row()

        # check if tools for multi selection are available
        ml_rows = 0
        if self.has_multi_selection(bakemaster, bakejob):
            seq = bakejob.get_seq("containers", "is_selected", bool)
            if seq[seq].size > 0:
                ml_rows = 1
            else:
                ml_rows = 0

        if bakejob.containers_len < 2 + ml_rows:
            min_rows = 2 + ml_rows
        else:
            min_rows = 4 + ml_rows
        rows = _get_uilist_rows(bakejob.containers_len + ml_rows,
                                min_rows, 4 + ml_rows)

        row.template_list('BM_UL_Containers', "", bakejob,
                          'containers', bakejob,
                          'containers_active_index', rows=rows)
        col = row.column(align=True)
        col.operator('bakemaster.container_add', text="",
                     icon='ADD').bakejob_index = bakejob.index

        if bakejob.containers_len > 0:
            remove_ot = col.operator('bakemaster.container_remove', text="",
                                     icon='REMOVE')
            remove_ot.bakejob_index = bakejob.index
            remove_ot.index = bakejob.containers_active_index

        col.emboss = 'NONE'
        if bakejob.containers_len > 1:
            col.separator(factor=1.0)
            trash_ot = col.operator('bakemaster.container_trash', text="",
                                    icon='TRASH')
            trash_ot.bakejob_index = bakejob.index

        container = bakemaster.get_container(bakejob)
        if container is None:
            return

        if ml_rows != 0 or container.is_group:
            col.separator(factor=1.0)
            subcol = col.column(align=True)
            subcol.emboss = 'NORMAL'

            if ml_rows != 0:
                icon_value = bakemaster.get_icon('GROUP')
                group_ot = subcol.operator('bakemaster.container_group',
                                           text="", icon_value=icon_value)
                group_ot.bakejob_index = bakejob.index

            if container.is_group or ml_rows != 0:
                icon_value = bakemaster.get_icon('UNGROUP')
                ungroup_ot = subcol.operator('bakemaster.container_ungroup',
                                             text="", icon_value=icon_value)
                ungroup_ot.bakejob_index = bakejob.index
                ungroup_ot.container_index = bakejob.containers_active_index


class BM_PT_Bake(BM_PT_Helper):
    bl_label = " "
    bl_idname = 'BM_PT_Bake'

    def draw_header(self, _: Context) -> None:
        label = "Bake"
        icon = 'RENDER_STILL'
        self.layout.label(text=label, icon=icon)

    def draw(self, _: Context) -> None:
        pass


class BM_PT_BakeControls(BM_PT_Helper):
    bl_label = " "
    bl_idname = 'BM_PT_BakeControls'
    bl_options = {'HIDE_HEADER'}

    bl_parent_id = BM_PT_Bake.bl_idname

    def draw_header(self, _: Context) -> None:
        pass

    def draw_header_preset(self, _: Context) -> None:
        pass

    def draw(self, context: Context) -> None:
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
        row.operator('bakemaster.bake_toggle_pause', text=text, icon=icon)
        row.operator('bakemaster.bake_stop', icon='QUIT')
        row.operator('bakemaster.bake_cancel', icon='CANCEL')
        row.active = bakemaster.bake_is_running

        row = layout.row()
        row.prop(bakemaster, "short_bake_instruction", text="", icon='INFO')
        row.enabled = False

        layout.separator(factor=1.5)


class BM_PT_BakeHistory(BM_PT_Helper):
    bl_label = " "
    bl_idname = 'BM_PT_BakeHistory'
    bl_options = {'DEFAULT_CLOSED'}

    bl_parent_id = BM_PT_Bake.bl_idname

    def draw_header(self, _: Context) -> None:
        label = "Bake History"
        icon = 'TIME'
        self.layout.label(text=label, icon=icon)

    def draw(self, context: Context) -> None:
        scene = context.scene
        bakemaster = scene.bakemaster
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        if bakemaster.bakehistory_len == 0:
            row.label(text="No bakes in the history")
            return
        rows = _get_uilist_rows(bakemaster.bakehistory_len, 1, 10)
        row.template_list('BM_UL_BakeHistory', "", bakemaster,
                          'bakehistory', bakemaster,
                          'bakehistory_active_index', rows=rows)
