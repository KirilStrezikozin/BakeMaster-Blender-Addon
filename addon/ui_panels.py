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

from .ui_base import (
    BM_UI_ml_draw,
    BM_PT_BakeJobsBase,
    BM_PT_ContainersBase,
    BM_PT_BakeControlsBase,
    BM_PT_BakeHistoryBase,
    BM_PT_BakeBase,
    bm_ui_utils,
    bm_get,
    bpy_version,
)
from bpy.types import (
    UIList,
    AddonPreferences,
)
from fnmatch import fnmatch as fnmatch

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"


class BM_PT_BakeJobs(BM_PT_BakeJobsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Containers(BM_PT_ContainersBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Bake(BM_PT_BakeBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_BakeControls(BM_PT_BakeControlsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Bake.bl_idname


class BM_PT_BakeHistory(BM_PT_BakeHistoryBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category
    bl_parent_id = BM_PT_Bake.bl_idname


class BM_PREFS_AddonPreferences(AddonPreferences):
    # dev: __package__ is 'BakeMaster.addon'
    # end user: __package__ is 'BakeMaster'
    bl_idname = __package__.split(".")[0]

    def poll(self, context):
        return hasattr(context.scene, "bakemaster")

    def draw(self, context):
        bakemaster = context.scene.bakemaster
        layout = self.layout

        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="Help")

        col = split.column(align=True)
        col.prop(bakemaster, "prefs_use_show_help")

        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="BakeJob")
        col = split.column(align=True)
        col.prop(bakemaster, "prefs_default_bakejob_type", text="type")


class BM_WalkHandler_UIList(UIList, BM_UI_ml_draw):
    """
    UIList for BM_OT_UIList_Walk_Handler for lower cyclomatic complexity of
    UILists for walk handler that requires a bunch of checks.

    UI representation for: drop from Outliner, drag containers to new
    positions, select multiple containers.

    data_name is an identifier of walk_data_name for this UIList instance.

    Use draw_props() to draw all needed container's properties (aligned row on
    the left). Default includes use_bake.
    Use draw_operators() to draw all needed operators for the container (row on
    the right). Default is emtpy.

    Filtering options on container.name property is on by default. Overwrite
    draw_filter() for custom.

    Define icon or icon_value for ticker prop in ticker_icon().

    Overwrite draw_item() method for custom UI.
    """

    data_name = ""

    use_name_filter = True

    def ticker_icon(self, context, bakemaster, container):
        custom_value = None
        return None, '', custom_value

    def allow_multi_select_viz(self, bakemaster, container):
        has_selection, _ = bm_get.walk_data_multi_selection_data(
            bakemaster, self.data_name)
        return has_selection and all([not container.has_drop_prompt,
                                      not container.is_drag_empty])

    def allow_drag_viz(self, bakemaster, _):
        if not bakemaster.allow_drag:
            return False, ''

        if self.data_name != bakemaster.walk_data_name:
            return False, ''

        if not bakemaster.allow_drag_trans:
            if self.data_name == bakemaster.drag_data_from:
                return True, 'DEFAULT'
            else:
                return False, ''

        if self.data_name == bakemaster.drag_data_from:
            return True, 'TRANS_FROM'
        if bm_get.walk_data_child(self.data_name) == bakemaster.drag_data_from:
            return True, 'TRANS_TO'

        return False, ''

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        if container.use_bake:
            icon = 'RESTRICT_RENDER_OFF'
        else:
            icon = 'RESTRICT_RENDER_ON'

        subrow = row.row()
        self.draw_prop(bakemaster, self.data_name, subrow, "BoolProperty",
                       container, "use_bake", None, text="", icon=icon)
        if bakemaster.allow_drag and bakemaster.get_drag_to_index(
                self.data_name) != -1:
            subrow.enabled = False
        row.active = container.use_bake

    def draw_operators(self, context, row, data, container, icon, active_data,
                       active_propname, index, allow_drag_viz, drag_layout):
        pass

    def draw_drag_empty(self, context, row, data, container, icon, active_data,
                        active_propname, index, allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster

        if any([drag_layout == 'DEFAULT',
                all([drag_layout == 'TRANS_FROM',
                     bakemaster.allow_multi_selection_drag])]):
            text = "..."
            if bakemaster.get_drag_to_index(self.data_name) == -1:
                return
        elif drag_layout == 'TRANS_TO':
            if container.is_drag_placeholder:
                row = row.box()
                row.scale_y = 0.4
                row.alignment = 'LEFT'
            text = "Move into new..."
        else:
            return

        row.prop(container, "ticker", text=text, emboss=False,
                 toggle=True)

    def draw_trans_to_prompts(self, context, row, data, container, icon,
                              active_data, active_propname, index,
                              allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster

        if not all([allow_drag_viz, drag_layout == 'TRANS_TO']):
            return False

        if container.index == getattr(data, active_propname):
            if not container.is_drag_placeholder:
                row.label(text="", icon='FORWARD')
                return True
            self.draw_box_prompt(row, "Discard move")
            return True

        elif all([container.index == bakemaster.get_drag_to_index(
                      self.data_name),
                  container.is_drag_placeholder]):
            self.draw_box_prompt(row, "Move here...")
            return True

        return False

    def draw_box_prompt(self, layout, text: str):
        old_emboss = layout.emboss
        layout.emboss = 'NORMAL'

        placeholder_box = layout.box()
        placeholder_box.scale_y = 0.4
        placeholder_box.alignment = 'LEFT'
        placeholder_box.label(text=text)

        layout.emboss = old_emboss

    def draw_item(self, context, layout, data, container, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster

        allow_multi_select_viz = self.allow_multi_select_viz(
            bakemaster, container)
        allow_drag_viz, drag_layout = self.allow_drag_viz(
            bakemaster, container)

        if allow_multi_select_viz and container.is_selected:
            col_layout = layout.box()
            col_layout.scale_y = 0.45
        else:
            col_layout = layout
        col = col_layout.column(align=True)

        # draw a darker line when dragging container
        if all([allow_drag_viz, container.is_drag_placeholder,
                any([drag_layout == 'DEFAULT',
                     drag_layout == 'TRANS_FROM' and any([
                         not container.is_selected,
                         container.is_drag_empty])])]):
            drag_placeholder = col.row().box()
            drag_placeholder.label(text="")
            drag_placeholder.scale_y = 0.1

        row = col.row(align=True)
        row.alignment = 'LEFT'

        # draw an empty container at the end
        if container.is_drag_empty:
            if not allow_drag_viz:
                return
            self.draw_drag_empty(context, row, data, container, icon,
                                 active_data, active_propname, index,
                                 allow_drag_viz, drag_layout)
            return

        # draw a drop prompt ("add new...")
        if container.has_drop_prompt:
            row.alignment = 'EXPAND'
            row.prop(container, "drop_name", text="", emboss=True)
            return

        if container.index != bakemaster.bakejobs_active_index:
            row.emboss = 'NONE'

        # for multiple selection
        if allow_multi_select_viz:
            layout.active = container.is_selected
            row.emboss = 'NONE'

        self.draw_props(context, row, data, container, icon, active_data,
                        active_propname, index,
                        allow_drag_viz, drag_layout)

        # TODO:
        # Group and indent visualization
        if container.parent_group_index != -1:
            row.label(text="      "*container.ui_indent_level + str(container.parent_group_index))

        ticker_icon_type, ticker_icon, _ = self.ticker_icon(
            context, bakemaster, container)
        if ticker_icon_type == 'ICON':
            row.prop(container, "ticker", text=container.name, toggle=True,
                     icon=ticker_icon)
        elif ticker_icon_type == 'ICON_VALUE':
            row.prop(container, "ticker", text=container.name, toggle=True,
                     icon_value=ticker_icon)
        else:
            row.prop(container, "ticker", text=container.name, toggle=True)

        drag_to_row_active = self.draw_trans_to_prompts(
            context, row, data, container, icon, active_data, active_propname,
            index, allow_drag_viz, drag_layout)

        self.draw_operators(context, row, data, container, icon, active_data,
                            active_propname, index,
                            allow_drag_viz, drag_layout)

        # fade out row while dragging if container in it isn't dragged
        if all([allow_drag_viz,
                bakemaster.allow_drag, not container.has_drag_prompt,
                bakemaster.get_drag_to_index(self.data_name) != -1,
                drag_layout in ['DEFAULT', 'TRANS_TO']]):
            row.active = drag_to_row_active

    def draw_filter(self, context, layout):
        bakemaster = context.scene.bakemaster
        if any([all([bakemaster.allow_drag,
                     bakemaster.get_drag_to_index(self.data_name) != -1]),
                not self.use_name_filter]):
            return

        row = layout.row()

        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        subrow.prop(self, "use_filter_invert", text="", toggle=True,
                    icon='ARROW_LEFTRIGHT')

        subrow = row.row(align=True)
        subrow.prop(self, "use_filter_sort_alpha", text="", toggle=True,
                    icon='SORTALPHA')
        if self.use_filter_sort_reverse:
            icon = 'SORT_DESC'
        else:
            icon = 'SORT_ASC'
        subrow.prop(self, "use_filter_sort_reverse", text="", toggle=True,
                    icon=icon)

    def invoke(self, context, event):
        pass


class BM_UL_BakeJobs(BM_WalkHandler_UIList):
    data_name = "bakejobs"

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster

        if container.type == 'OBJECTS':
            type_icon = bm_ui_utils.get_icon_id(bakemaster,
                                                "bakemaster_objects.png")
            type_ot = self.draw_prop(
                bakemaster, self.data_name, row, "Operator", container, "type",
                'bakemaster.bakejob_toggletype', text="", icon_value=type_icon)
        else:
            type_ot = self.draw_prop(
                bakemaster, self.data_name, row, "Operator", container, "type",
                'bakemaster.bakejob_toggletype', text="", icon='RENDERLAYERS')
        if type_ot is not None:
            type_ot.index = container.index

        super().draw_props(context, row, bakemaster, container, icon,
                           active_data, active_propname, index,
                           allow_drag_viz, drag_layout)


class BM_UL_Containers(BM_WalkHandler_UIList):
    data_name = "containers"

    def ticker_icon(self, context, bakemaster, container):
        bakejob = bm_get.bakejob(bakemaster, container.bakejob_index)
        error_icon = bm_ui_utils.get_icon_id(bakemaster,
                                             "bakemaster_rederror.png")

        if container.is_group:
            if bpy_version > (2, 91, 0):
                group_icon = 'OUTLINER_COLLECTION'
            else:
                group_icon = 'GROUP'
            return 'ICON', group_icon, True

        if bakejob is None:
            return 'ICON_VALUE', error_icon, False

        elif bakejob.type == 'MAPS':
            return '', '', True

        elif bakejob.type == 'OBJECTS':
            object, _, obj_icon, _, _ = bm_get.object_ui_info(
                    context.scene.objects, container.name)

            if object is None:
                return 'ICON_VALUE', error_icon, False

            return 'ICON', obj_icon, True

        return 'ICON_VALUE', error_icon, False

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        # unpack third ticker_icon() return value -> container_exists
        _, _, container_exists = self.ticker_icon(context, bakemaster,
                                                  container)
        row.active = container_exists

        if container.use_bake:
            icon = 'RESTRICT_RENDER_OFF'
        else:
            icon = 'RESTRICT_RENDER_ON'
            row.active = False

        subrow = row.row()
        self.draw_prop(bakemaster, self.data_name, subrow, "BoolProperty",
                       container, "use_bake", None, text="", icon=icon)
        if bakemaster.allow_drag and bakemaster.get_drag_to_index(
                self.data_name) != -1:
            subrow.enabled = False


class BM_UL_BakeHistory(UIList):
    def draw_item(self, context, layout, data, container, icon, active_data,
                  active_propname, index):
        self.use_filter_sort_reverse = True

        bakemaster = data
        timestamp = bm_ui_utils.bakehistory_timestamp_get_label(bakemaster,
                                                                container)

        row = layout.row()
        row.prop(container, 'name', text="", emboss=False, icon='RENDER_STILL')
        row.label(text=timestamp)

        row.operator('bakemaster.bakehistory_rebake', text="",
                     icon='RECOVER_LAST').index = container.index
        row.operator('bakemaster.bakehistory_config', text="",
                     icon='FOLDER_REDIRECT').index = container.index
        row.operator('bakemaster.bakehistory_remove', text="",
                     icon='TRASH').index = container.index

        if bakemaster.bakehistory_reserved_index == container.index:
            row.active = False

    def draw_filter(self, _, layout):
        row = layout.row(align=True)
        row.prop(self, "filter_name", text="")
        row.prop(self, "use_filter_invert", text="", toggle=True,
                 icon='ARROW_LEFTRIGHT')

    def container_get_name(self, data, container):
        timestamp = bm_ui_utils.bakehistory_timestamp_get_label(data,
                                                                container)
        return "%s%s" % (container.name, timestamp)

    def filter_by_name(self, data, pattern, bitflag, containers,
                       propname_getter, reverse=False):
        flt_flags = []
        pattern = "*%s*" % pattern

        for container in containers:
            name = propname_getter(data, container)
            if fnmatch(name, pattern):
                flt_flags.append(bitflag)
            else:
                flt_flags.append(~bitflag)

        if reverse:
            flt_flags.reverse()

        return flt_flags

    def filter_containers(self, _, data, propname):
        # Sort containers by filter_name on
        # container.name + container.timestamp combined

        # Default return values
        flt_flags = []
        flt_neworder = []

        if self.filter_name:
            flt_flags = self.filter_by_name(data, self.filter_name,
                                            self.bitflag_filter_item,
                                            getattr(data, propname),
                                            self.container_get_name,
                                            reverse=self.use_filter_invert)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * data.bakehistory_len

        return flt_flags, flt_neworder

    def invoke(self, context, event):
        pass
