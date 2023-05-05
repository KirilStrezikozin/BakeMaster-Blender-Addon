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
)
from bpy.types import (
    UIList,
    AddonPreferences,
)
from bpy.props import (
    StringProperty,
    BoolProperty,
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

        # Help
        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="Help")

        col = split.column(align=True)
        col.prop(bakemaster, "prefs_use_show_help")
        ###

        # BakeJob
        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="BakeJob")
        col = split.column(align=True)
        col.prop(bakemaster, "prefs_default_bakejob_type", text="type")
        ###

        # BakeJob
        split = layout.split(factor=0.4)

        col_heading = split.column()
        col_heading.alignment = 'RIGHT'
        col_heading.label(text="Developer mode")
        col = split.column()
        col.prop(bakemaster, "prefs_use_developer_mode", text="Show Options")
        if bakemaster.prefs_use_developer_mode:
            col.prop(bakemaster, "prefs_developer_use_orange_ob_icons")

            col_aligned = col.column(align=True)
            col_aligned.prop(
                bakemaster, "prefs_developer_use_group_descending_lines")
            col_aligned.prop(bakemaster, "prefs_developer_ui_indent_width")

            col.prop(bakemaster, "prefs_developer_use_show_groups_indexes")
            col.prop(bakemaster, "prefs_developer_show_tickers")
            col.prop(bakemaster, "prefs_developer_use_console_debug")
        ###


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

    use_filter = True
    filter_propname = "name"

    draw_drag_empty_placeholder = False

    filter_name: StringProperty(
        name="Filter by Name",
        description="Only show items matching this name (use '*' as wildcard)",
        default="")

    use_filter_invert: BoolProperty(
        name="Invert",
        description="Invert filtering (show hidden items, and vice versa)",
        default=False)

    def ticker_icon(self, context, bakemaster, data, container):
        custom_value = None
        return None, '', custom_value

    def allow_multi_select_viz(self, bakemaster, container):
        has_selection, _ = bm_get.walk_data_multi_selection_data(
            bakemaster, self.data_name)
        return has_selection and not container.has_drop_prompt

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
                   active_propname, index, allow_multi_select_viz,
                   allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        group, forbid_bake = bm_get.parent_group(
            container, getattr(data, self.data_name), "group_type", "DICTATOR",
            "use_bake", False)

        if group is not None:
            row.active = not forbid_bake
            return
        else:
            row.active = container.use_bake

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

    def draw_group_props(self, context, row, data, container, icon,
                         active_data, active_propname, index, allow_drag_viz,
                         drag_layout, allow_multi_select_viz):
        if not container.is_group:
            return

        bakemaster = context.scene.bakemaster

        old_emboss = row.emboss
        if allow_multi_select_viz:
            row.emboss = 'NONE'
        else:
            row.emboss = 'NORMAL'
        texset_icon = bm_ui_utils.get_icon_id(
            bakemaster, "bakemaster_texset.png")

        if container.index == getattr(data, active_propname):

            subrow = row.row()
            self.draw_prop(
                bakemaster, self.data_name, subrow, "BoolProperty", container,
                "group_is_texset", None, text="", icon_value=texset_icon)

            if not container.group_is_texset:
                subrow.active = False

        elif container.group_is_texset:
            subrow = row.row()

            if allow_multi_select_viz:
                self.draw_prop(
                    bakemaster, self.data_name, subrow, "BoolProperty",
                    container, "group_is_texset", None, text="",
                    icon_value=texset_icon)
                subrow.enabled = False
            else:
                subrow.label(text="", icon_value=texset_icon)

        else:
            row.emboss = old_emboss
            return

        if bakemaster.allow_drag and bakemaster.get_drag_to_index(
                self.data_name) != -1:
            subrow.enabled = False
        row.emboss = old_emboss

    def draw_drag_placeholder(self, context, col, data, container, icon,
                              active_data, active_propname, index,
                              allow_drag_viz, drag_layout):
        if not all([allow_drag_viz, container.is_drag_placeholder,
                    not container.is_drag_empty_placeholder,
                    drag_layout != 'TRANS_TO']):
            return
        if drag_layout == 'TRANS_FROM' and container.is_selected:
            return

        self.draw_drag_placeholder_row(context.scene.bakemaster, col,
                                       data, container)

    def draw_drag_placeholder_row(self, bakemaster, col, data, container):
        dp_row = col.row(align=True)
        dp_row.alignment = 'LEFT'

        self.draw_indent(dp_row, bakemaster, data, container)

        drag_placeholder = dp_row.box()
        drag_placeholder.label(text="")
        drag_placeholder.scale_y = 0.01

    def draw_drag_empty_row(self, bakemaster, col, data, container):
        row = col.row(align=True)
        row.alignment = 'LEFT'
        self.draw_indent(row, bakemaster, data, container)
        return row

    def draw_drag_empty(self, context, col, row, data, container, icon,
                        active_data, active_propname, index, allow_drag_viz,
                        drag_layout, allow_multi_select_viz):
        bakemaster = context.scene.bakemaster
        drag_to_index = bakemaster.get_drag_to_index(self.data_name)
        if any([not allow_drag_viz,
                drag_to_index == -1]):
            return

        containers = getattr(data, self.data_name)
        is_container_last = getattr(
            data, "%s_len" % self.data_name) - 1 == container.index

        # Don't draw drag_empties inside multi selection
        if not is_container_last and all(
                [containers[container.index + 1].is_selected,
                 allow_multi_select_viz]):
            return

        allow_explicit_group_drag_empty = False

        # Explicit drag_empty draw
        if not container.is_drag_empty:
            if is_container_last:
                pass
            elif getattr(containers[container.index + 1],
                         "ui_indent_level") < container.ui_indent_level:
                pass
            elif any([bm_ui_utils.is_group_with_no_childs(
                container, data, getattr(data, self.data_name),
                self.data_name),
                    container.is_group and not container.is_expanded]):
                allow_explicit_group_drag_empty = True
            else:
                return

        if container.is_drag_empty_placeholder:
            if all([bakemaster.drag_from_index != bakemaster.get_drag_to_index(
                    self.data_name),
                    allow_explicit_group_drag_empty]):
                row.label(text="", icon='BACK')

            if drag_layout != 'TRANS_TO':
                self.draw_drag_placeholder_row(bakemaster, col, data,
                                               container)
                return

            row = self.draw_drag_empty_row(bakemaster, col, data, container)
            row = row.box()
            row.alignment = 'LEFT'
            row.scale_y = 0.4
            text = "Move into new..."

        elif drag_layout == 'TRANS_TO':
            row = self.draw_drag_empty_row(bakemaster, col, data, container)
            text = "Move into new..."

        elif drag_layout in {'DEFAULT', 'TRANS_FROM'}:
            row = self.draw_drag_empty_row(bakemaster, col, data, container)
            text = "..."

        else:
            return

        row.prop(container, "drag_empty_ticker", text=text, emboss=False,
                 toggle=True)

    def draw_trans_to_prompts(self, context, row, data, container, icon,
                              active_data, active_propname, index,
                              allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster

        if not all([allow_drag_viz, drag_layout == 'TRANS_TO']):
            return False

        if bakemaster.get_drag_to_index(self.data_name) == -1:
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

    def get_indent_line_color(self, bakemaster, data, container,
                              line_index: int):
        color_tag = ""
        containers = getattr(data, self.data_name)

        while container.ui_indent_level != line_index:
            if any([container.parent_group_index == -1,
                    container.ui_indent_level < line_index]):
                color_tag = ""
                break
            container = containers[container.parent_group_index]
            color_tag = container.group_color_tag

        return bm_ui_utils.get_icon_id(
            bakemaster, "bakemaster_indent_line%s.png" % color_tag)

    def draw_indent(self, row, bakemaster, data, container):
        if bakemaster.prefs_developer_use_show_groups_indexes:
            indent_ad_text = str(container.parent_group_index)
        else:
            indent_ad_text = ""

        if not bakemaster.prefs_developer_use_group_descending_lines:
            native_indent = " "*(
                bakemaster.prefs_developer_ui_indent_width + 6)

            row.label(text=" %s%s" % (
                native_indent*container.ui_indent_level,
                indent_ad_text))
            return

        for line_index in range(container.ui_indent_level):
            row.label(text="", icon_value=self.get_indent_line_color(
                bakemaster, data, container, line_index))
            if bakemaster.prefs_developer_ui_indent_width > 0:
                row.label(text=" "*bakemaster.prefs_developer_ui_indent_width)

    def draw_box_prompt(self, layout, text: str,
                        container=None, ticker_atr=""):
        old_emboss = layout.emboss
        layout.emboss = 'NORMAL'

        placeholder_box = layout.box()
        placeholder_box.scale_y = 0.4
        placeholder_box.alignment = 'LEFT'

        if container is None:
            placeholder_box.label(text=text)
        else:
            placeholder_box.prop(container, ticker_atr, text=text,
                                 emboss=False, toggle=True)

        layout.emboss = old_emboss

    def draw_drag_row_inactive(self, row, bakemaster, data, container,
                               allow_drag_viz, drag_layout,
                               drag_to_row_active):
        if not all([allow_drag_viz,
                    bakemaster.allow_drag, not container.has_drag_prompt,
                    bakemaster.get_drag_to_index(self.data_name) != -1]):
            return False

        if drag_layout in ['DEFAULT', 'TRANS_FROM']:
            row.active = drag_to_row_active

            # back arrow near group user's dragging into
            if container.index == getattr(data, self.data_name)[
                    bakemaster.get_drag_to_index(self.data_name)
                    ].parent_group_index:
                return True

        elif drag_layout == 'TRANS_TO':
            row.active = drag_to_row_active
        return False

    def draw_arrow(self, row, bakemaster, data, container, allow_draw_arrow):
        if not all([allow_draw_arrow,
                    bakemaster.drag_from_index != bakemaster.get_drag_to_index(
                        self.data_name)]):
            return

        for container in getattr(data, self.data_name):
            if not container.is_drag_empty_placeholder:
                continue
            elif any([bm_ui_utils.is_group_with_no_childs(
                container, data, getattr(data, self.data_name),
                self.data_name),
                    container.is_group and not container.is_expanded
                    ]):
                break
        else:
            row.label(text="", icon='BACK')

    def draw_item(self, context, layout, data, container, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster

        allow_multi_select_viz = self.allow_multi_select_viz(
            bakemaster, container)
        allow_drag_viz, drag_layout = self.allow_drag_viz(
            bakemaster, container)

        col = layout.column(align=True)

        # draw a darker line when dragging container
        self.draw_drag_placeholder(context, col, data, container, icon,
                                   active_data, active_propname, index,
                                   allow_drag_viz, drag_layout)

        if allow_multi_select_viz and container.is_selected:
            row = col.box().row(align=True)
            row.scale_y = 0.45
        else:
            row = col.row(align=True)
        row.alignment = 'LEFT'

        if bakemaster.prefs_developer_show_tickers:
            row.label(text=str(container.ticker))

        # draw a drop prompt ("add new...")
        if container.has_drop_prompt:
            row.alignment = 'EXPAND'
            row.prop(container, "drop_name", text="", emboss=True)
            return

        # No emboss for operators
        if container.index != bakemaster.bakejobs_active_index:
            row.emboss = 'NONE'

        # for multiple selection
        if allow_multi_select_viz:
            layout.active = container.is_selected
            row.emboss = 'NONE'

        self.draw_indent(row, bakemaster, data, container)

        # draw group's is_expanded toggle
        if container.is_group:
            old_emboss = row.emboss
            row.emboss = 'NONE'

            if container.is_expanded:
                icon = 'DISCLOSURE_TRI_DOWN'
            else:
                icon = 'DISCLOSURE_TRI_RIGHT'

            # Groups are shown expanded when filtering on name
            if not self.filter_name:

                toggle_expand_ot = row.operator(
                    "bakemaster.%s_toggle_expand" % self.data_name,
                    text="", icon=icon)

                toggle_expand_ot.bakejob_index = container.bakejob_index
                toggle_expand_ot.index = container.index

                parent_index_name = "%s_index" % bm_get.walk_data_parent(
                    self.data_name)[:-1]
                setattr(toggle_expand_ot, parent_index_name,
                        getattr(container, parent_index_name))
            else:
                row.label(text="", icon='DISCLOSURE_TRI_DOWN')

            row.emboss = old_emboss

        row = row.row()
        row.alignment = 'LEFT'

        self.draw_props(context, row, data, container, icon, active_data,
                        active_propname, index, allow_multi_select_viz,
                        allow_drag_viz, drag_layout)

        ticker_icon_type, ticker_icon, _ = self.ticker_icon(
            context, bakemaster, data, container)
        if ticker_icon_type == 'ICON':
            row.prop(container, "ticker", text=container.name, toggle=True,
                     icon=ticker_icon)
        elif ticker_icon_type == 'ICON_VALUE':
            row.prop(container, "ticker", text=container.name, toggle=True,
                     icon_value=ticker_icon)
        else:
            row.prop(container, "ticker", text=container.name, toggle=True)

        self.draw_group_props(context, row, data, container, icon, active_data,
                              active_propname, index, allow_drag_viz,
                              drag_layout, allow_multi_select_viz)

        self.draw_operators(context, row, data, container, icon, active_data,
                            active_propname, index,
                            allow_drag_viz, drag_layout)

        drag_to_row_active = self.draw_trans_to_prompts(
            context, row, data, container, icon, active_data, active_propname,
            index, allow_drag_viz, drag_layout)

        # fade out row while dragging if container in it isn't dragged
        allow_draw_arrow = self.draw_drag_row_inactive(
            row, bakemaster, data, container, allow_drag_viz, drag_layout,
            drag_to_row_active)

        # draw drag_empty
        self.draw_drag_empty(
            context, col, row, data, container, icon, active_data,
            active_propname, index, allow_drag_viz, drag_layout,
            allow_multi_select_viz)

        self.draw_arrow(row, bakemaster, data, container, allow_draw_arrow)

    def draw_filter(self, context, layout):
        bakemaster = context.scene.bakemaster
        if any([all([bakemaster.allow_drag,
                     bakemaster.get_drag_to_index(self.data_name) != -1]),
                not self.use_filter]):
            return

        row = layout.row(align=True)
        row.prop(self, "filter_name", text="")
        row.prop(self, "use_filter_invert", text="", toggle=True,
                 icon='ARROW_LEFTRIGHT')

    def is_pattern_match(self, name, pattern, reverse=False):
        if not reverse:
            return fnmatch(name, "*%s*" % pattern)
        else:
            return not fnmatch(name, "*%s*" % pattern)

    def filter_items_name(self, flt_flags, containers, pattern, reverse=False):

        path_cache = {}

        for container in reversed(containers):
            if container.has_drop_prompt:
                continue

            is_match = self.is_pattern_match(
                getattr(container, self.filter_propname), pattern, reverse)

            if not any([is_match,
                        path_cache.get(str(container.index), False)]):
                flt_flags[container.index] &= ~self.bitflag_filter_item
                continue

            path_cache[str(container.index)] = True
            if container.parent_group_index != -1:
                path_cache[str(container.parent_group_index)] = True

        return flt_flags

    def filter_itmes_groups(self, flt_flags, containers):
        """
        Get flt_flags based of groups' is_expanded value.
        """

        last_is_expanded = True
        last_ui_indent = 0

        # to not resolve top parent group recursively each time
        groups_cache = {}

        # visible if parent groups are expanded
        for container in containers:
            if container.has_drop_prompt:
                continue

            if container.ui_indent_level >= last_ui_indent:
                last_ui_indent = container.ui_indent_level

                if not last_is_expanded:
                    flt_flags[container.index] &= ~self.bitflag_filter_item

                if container.is_group:
                    last_is_expanded = all([last_is_expanded,
                                            container.is_expanded])
                    groups_cache[str(container.index)] = last_is_expanded
                continue

            last_ui_indent = container.ui_indent_level

            if container.parent_group_index == -1:
                last_is_expanded = True
            else:
                try:
                    last_is_expanded = groups_cache[str(
                        container.parent_group_index)]
                except KeyError:
                    last_is_expanded = True

            if not last_is_expanded:
                flt_flags[container.index] &= ~self.bitflag_filter_item

            if container.is_group:
                last_is_expanded = all([last_is_expanded,
                                        container.is_expanded])
                groups_cache[str(container.index)] = last_is_expanded

        return flt_flags

    def filter_items_get_flt_flags(self, data, propname, pattern,
                                   reverse=False):
        containers = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(containers)

        if self.filter_name:
            return self.filter_items_name(flt_flags, containers, pattern,
                                          reverse)

        return self.filter_itmes_groups(flt_flags, containers)

    def filter_items(self, _, data, propname):
        flt_flags = []
        flt_neworder = []

        if self.use_filter:
            flt_flags = self.filter_items_get_flt_flags(
                data, propname, self.filter_name,
                reverse=self.use_filter_invert)

        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * getattr(
                data, "%s_len" % propname)

        return flt_flags, flt_neworder

    def invoke(self, context, event):
        pass


class BM_UL_BakeJobs(BM_WalkHandler_UIList):
    data_name = "bakejobs"

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_multi_select_viz,
                   allow_drag_viz, drag_layout):
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
                           allow_multi_select_viz, allow_drag_viz, drag_layout)


class BM_UL_Containers(BM_WalkHandler_UIList):
    data_name = "containers"

    def ticker_icon(self, context, bakemaster, data, container):
        error_icon = bm_ui_utils.get_icon_id(bakemaster,
                                             "bakemaster_rederror.png")

        if container.is_group:
            if any([getattr(
                data, "%s_active_index" % self.data_name) == container.index,
                    container.group_type == 'DECORATOR']):
                return '', '', True
            group_icon = bm_ui_utils.get_group_icon(bakemaster, container)
            return 'ICON_VALUE', group_icon, True

        if data is None:
            return 'ICON_VALUE', error_icon, False

        elif data.type == 'MAPS':
            return '', '', True

        elif data.type == 'OBJECTS':
            object, _, obj_icon_type, obj_icon, _, _ = bm_get.object_ui_info(
                    bakemaster, context.scene.objects, container.name)

            if object is None:
                return 'ICON_VALUE', error_icon, False

            return obj_icon_type, obj_icon, True

        return 'ICON_VALUE', error_icon, False

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_multi_select_viz,
                   allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        group, forbid_bake = bm_get.parent_group(
            container, getattr(data, self.data_name), "group_type", "DICTATOR",
            "use_bake", False)

        # unpack third ticker_icon() return value -> container_exists
        _, _, container_exists = self.ticker_icon(context, bakemaster,
                                                  data, container)

        # draw is_expanded for lowpolies
        if container.get_is_lowpoly():
            subrow = row.row(align=True)
            subrow.emboss = 'NONE'

            if container.is_expanded:
                icon = 'DISCLOSURE_TRI_DOWN'
            else:
                icon = 'DISCLOSURE_TRI_RIGHT'

            # contianers are shown expanded when filtering on name
            if not self.filter_name:

                toggle_expand_ot = subrow.operator(
                    "bakemaster.%s_toggle_expand" % self.data_name,
                    text="", icon=icon)

                toggle_expand_ot.bakejob_index = container.bakejob_index
                toggle_expand_ot.index = container.index

                parent_index_name = "%s_index" % bm_get.walk_data_parent(
                    self.data_name)[:-1]
                setattr(toggle_expand_ot, parent_index_name,
                        getattr(container, parent_index_name))
            else:
                subrow.label(text="", icon='DISCLOSURE_TRI_DOWN')

            # fade toggle_expand if lowpoly has no HCDs
            containers = getattr(data, self.data_name)
            if not any(
                    [container.get_highpoly(data, containers, self.data_name),
                     container.get_cage(data, containers, self.data_name),
                     container.get_decal(data, containers, self.data_name)]):
                subrow.active = False

        if group is None:
            if container.use_bake:
                icon = 'RESTRICT_RENDER_OFF'
            else:
                icon = 'RESTRICT_RENDER_ON'
                row.active = False

            row.active &= container_exists

            if not container.is_group or container.group_type != 'DECORATOR':
                subrow = row.row()
                self.draw_prop(bakemaster, self.data_name, subrow,
                               "BoolProperty", container, "use_bake", None,
                               text="", icon=icon)
                if bakemaster.allow_drag and bakemaster.get_drag_to_index(
                        self.data_name) != -1:
                    subrow.enabled = False

        else:
            row.active = not forbid_bake

        if not container.is_group:
            return
        else:
            row.active = not forbid_bake and container.use_bake

        # fade out groups when filtering on name
        if self.filter_name:
            row.active &= False or self.is_pattern_match(
                container.name, self.filter_name, self.use_filter_invert)

        if getattr(data,
                   "%s_active_index" % self.data_name) == container.index:
            subrow = row.row()

            if allow_multi_select_viz:
                subrow.emboss = 'NONE'
            else:
                subrow.emboss = 'NORMAL'

            group_icon = bm_ui_utils.get_group_icon(bakemaster, container)
            subrow.operator("bakemaster.containers_groupoptions", text="",
                            icon_value=group_icon)
            subrow.active = row.active and container.group_type != 'DECORATOR'


class BM_UL_BakeHistory(UIList):
    filter_name: StringProperty(
        name="Filter by Name",
        description="Only show items matching this name (use '*' as wildcard)",
        default="")

    use_filter_invert: BoolProperty(
        name="Invert",
        description="Invert filtering (show hidden items, and vice versa)",
        default=False)

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

    def filter_items(self, _, data, propname):
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
