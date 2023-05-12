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

import typing

from datetime import datetime
from fnmatch import fnmatch as fnmatch

from bpy.props import BoolProperty, StringProperty

from bpy.types import (
    Context,
    Panel,
    PropertyGroup,
    UILayout as Layout,
    UIList,
)

_bm_space_type = 'VIEW_3D'
_bm_region_type = 'UI'
_bm_category = "BakeMaster"


def get_uilist_rows(len_of_idprop: int, min_rows: int, max_rows: int) -> int:
    return min(max_rows, max(min_rows, len_of_idprop))


def get_bakehistory_timestamp_label(
        bakemaster: PropertyGroup, bakehistory: PropertyGroup) -> str:

    if bakehistory.index == bakemaster.bakehistory_reserved_index:
        return "in progress..."

    try:
        timediff = datetime.now() - datetime.strptime(bakehistory.time_stamp,
                                                      "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return ""
    seconds = timediff.total_seconds()
    if seconds < 1:
        return "in progress..."
    elif seconds < 60:
        return "%dsec ago" % seconds.__int__()
    minutes = seconds / 60
    if minutes < 60:
        return "%dmin ago" % minutes.__int__()
    hours = minutes / 60
    if hours < 24:
        return "%dh ago" % hours.__int__()
    days = hours / 24
    ending = "s" if days.__int__() > 1 else ""
    if days < 30:
        return "%dday%s ago" % (days.__int__(), ending)
    months = days / 30
    ending = "s" if months.__int__() > 1 else ""
    if months < 12:
        return "%dmonth%s ago" % (months.__int__(), ending)
    years = months / 12
    ending = "s" if years.__int__() > 1 else ""
    return "%dyear%s ago" % (years.__int__(), ending)


class BM_UI_ms_draw():
    """
    BakeMaster custom UI props draw methods specifically for drawing props of
    items in a multi selection.

    Case 1. If no valid multi selection, default prop draw is used.

    Case 2. If props of propname are equal in a multi selection, default prop
    draw is used.

    Case 3. If props of prop_name aren't equal in a multi selection, a custom
    draw is used depending on a prop_type with an operator to
    'relinquish' the props = make them equal as such the default
    prop draw will be used.

    Use by inheriting.

    data_name is an identifier of walk_data_name for an instance.

    Example:
    ...

    self.draw_prop(bakemaster, layout, "IntProperty", container, "use_bake",
                   None, text="Bake Visibility", icon='RENDER_STILL',
                   emboss=False)

    self.draw_prop(bakemaster, layout, "Operator", None, None,
                   "bakemaster.bakejobs_add", text="Add", icon='ADD')

    ...
    """

    def draw_prop(self, bakemaster: PropertyGroup, data_name: str,
                  layout: Layout, prop_type: str, data: PropertyGroup,
                  property: str, operator: typing.Union[str, None],
                  *args, **kwargs) -> typing.Optional[typing.Any]:

        if data_name == "":
            data_name = self.data_name

        # Case 1
        if data is None or any(
                [
                    not self.has_multi_selection(
                        bakemaster, data, data_name),
                    not data.is_selected
                ]):
            return self.default_draw_prop(layout, prop_type, data, property,
                                          operator, *args, **kwargs)

        _, containers, _ = getattr(
            bakemaster, "get_active_%s" % data_name)(bakemaster)

        props_equal = True
        old_prop_val = getattr(data, property)
        for container in containers:
            if not container.is_selected or container.has_drop_prompt:
                continue

            # skip checking group prop value if container isn't a group
            elif property.find("group") == 0 and not container.is_group:
                continue
            # skip checking decorator groups
            elif container.is_group and container.group_type == 'DECORATOR':
                continue

            if getattr(container, property) != old_prop_val:
                props_equal = False
                break

        # Case 2
        if props_equal:
            return self.default_draw_prop(layout, prop_type, data, property,
                                          operator, *args, **kwargs)

        # Case 3
        icon_value = bakemaster.get_icon('FLOATING_VALUE')

        if prop_type != "Operator":
            relinquish_operator = layout.operator(
                'bakemaster.helper_ui_prop_relinquish',
                text=kwargs.get("text", ""),
                icon_value=icon_value)
            relinquish_operator.data_name = data_name
            relinquish_operator.prop_name = property
            return

        if kwargs.get("icon") is not None:
            _ = kwargs.pop("icon")
        kwargs["icon_value"] = icon_value
        return layout.operator(operator, *args, **kwargs)

    def default_draw_prop(self, layout: Layout, prop_type: str,
                          data: PropertyGroup, property: str, operator: str,
                          *args, **kwargs) -> typing.Optional[typing.Any]:

        if prop_type == "Operator":
            return layout.operator(operator, *args, **kwargs)

        layout.prop(data, property, *args, **kwargs)

    def has_multi_selection(self, bakemaster: PropertyGroup,
                            data: PropertyGroup, data_name="") -> bool:
        """
        Return True if there is an active multi selection
        in the data_name Collection in data.

        If data_name is not given (empty), self.data_name will be used.
        """

        if data_name == "":
            data_name = self.data_name

        return bakemaster.wh_has_ms(data, data_name)


class BM_PT_Helper(Panel):
    """
    BakeMaster UI Panel Helper class.

    data_name is an identifier of walk_data_name for this Panel instance.
    Mandatory if a Panel will have walk_datas drawn.

    Use by inheriting.
    """

    bl_space_type = _bm_space_type
    bl_region_type = _bm_region_type
    bl_category = _bm_category

    use_help = True  # draw help button
    data_name = ""

    @classmethod
    def poll(cls, context: Context) -> bool:
        # Default poll (determine whether able to draw a panel)
        return all([hasattr(context.scene, "bakemaster"),
                    cls.panel_poll(context)])

    @classmethod
    def panel_poll(cls, _: Context) -> bool:
        # Default empty panel_poll for additional checks
        return True

    def draw_header_preset(self, context: Context) -> None:
        # Draw default header layout

        bakemaster = context.scene.bakemaster
        row = self.layout.row()

        if not all([self.use_help,
                    bakemaster.get_pref(context, "use_show_help")]):
            return

        row.operator('bakemaster.helper_help', text="",
                     icon='HELP').page_id = self.bl_idname


class BM_UI_wh_UIList(UIList, BM_UI_ms_draw):
    """
    UIList for BM_OT_WalkHandler for lower cyclomatic complexity of
    UILists for walk handler that requires a bunch of checks.

    UI representation for: drop from Outliner, drag containers to new
    positions, select multiple containers.

    data_name is an identifier of walk_data_name for a UIList instance.

    Usage:
        1. Use draw_props() to draw all needed container's properties
            (aligned row on the left). Default includes use_bake.

        2. Use draw_operators() to draw all needed operators for the container
            (row on the right). Default is empty.

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

    def ticker_icon(self, context: Context, bakemaster: PropertyGroup,
                    data: PropertyGroup, container: PropertyGroup
                    ) -> typing.Tuple[str, str, bool]:

        return '', '', False

    def allow_multi_select_viz(self, bakemaster: PropertyGroup,
                               data: PropertyGroup, container: PropertyGroup
                               ) -> bool:

        has_ms = bakemaster.wh_has_ms(data, self.data_name)
        return has_ms and not container.has_drop_prompt

    def allow_drag_viz(self, bakemaster: PropertyGroup, _: PropertyGroup
                       ) -> typing.Tuple[bool, str]:

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
        if bakemaster.get_wh_childs_name(
                self.data_name) == bakemaster.drag_data_from:
            return True, 'TRANS_TO'

        return False, ''

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_multi_select_viz,
                   allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        group, forbid_bake = container.get_parent_group(
                getattr(data, self.data_name), "group_type", "DICTATOR",
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

    def draw_add_lowpoly_data_prompt(self, context, row, data, container, icon,
                                     active_data, active_propname, index,
                                     allow_drag_viz, drag_layout,
                                     allow_multi_select_viz):
        # This method is exclusive for lowpoly's 'Add data...' ticker draw.

        bakemaster = context.scene.bakemaster

        if not all([container.get_is_lowpoly(), self.data_name == "containers",
                    container.get_bm_name(
                        bakemaster, self.data_name) == "objects",
                    allow_drag_viz,
                    container.index == bakemaster.get_drag_to_index(
                        self.data_name)]):
            return

        old_emboss = row.emboss
        row.emboss = 'NORMAL'

        if all([bakemaster.is_drag_lowpoly_data,
                container.is_lowpoly_placeholder]):
            sublayout = row.box().row(align=True)
            sublayout.scale_y = 0.4
        else:
            sublayout = row.row(align=True)

        sublayout.alignment = 'LEFT'

        # TODO (from lowpoly_ticker Update):
        # run some stuff in lowpoly_ticker Update to automatically
        # decide hcd type
        hcd_txt = "data"
        sublayout.prop(container, "lowpoly_ticker", text=f"Add {hcd_txt}...",
                       emboss=False, toggle=True)

        row.emboss = old_emboss

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
        texset_icon = bakemaster.get_icon('TEXSET')

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

        self.draw_drag_placeholder_row(context, context.scene.bakemaster, col,
                                       data, container)

    def draw_drag_placeholder_row(self, context, bakemaster, col, data,
                                  container):
        dp_row = col.row(align=True)
        dp_row.alignment = 'LEFT'

        self.draw_indent(context, dp_row, bakemaster, data, container)

        drag_placeholder = dp_row.box()
        drag_placeholder.label(text="")
        drag_placeholder.scale_y = 0.01

    def draw_drag_empty_row(self, context, bakemaster, col, data, container):
        row = col.row(align=True)
        row.alignment = 'LEFT'
        self.draw_indent(context, row, bakemaster, data, container)
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
            elif any([container.group_has_childs(
                data, getattr(data, self.data_name),
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
                self.draw_drag_placeholder_row(context, bakemaster, col, data,
                                               container)
                return

            row = self.draw_drag_empty_row(context, bakemaster, col, data,
                                           container)
            row = row.box()
            row.alignment = 'LEFT'
            row.scale_y = 0.4
            text = "Move into new..."

        elif drag_layout == 'TRANS_TO':
            row = self.draw_drag_empty_row(context, bakemaster, col, data,
                                           container)
            text = "Move into new..."

        elif drag_layout in {'DEFAULT', 'TRANS_FROM'}:
            row = self.draw_drag_empty_row(context, bakemaster, col, data,
                                           container)
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

        return bakemaster.get_icon('INDENT%s' % color_tag)

    def draw_indent(self, context, row, bakemaster, data, container):
        if bakemaster.get_pref(context, "developer_use_show_groups_indexes"):
            indent_ad_text = str(container.parent_group_index)
        else:
            indent_ad_text = ""

        if not bakemaster.get_pref(context,
                                   "developer_use_group_descending_lines"):
            native_indent = " "*(
                bakemaster.get_pref(context, "developer_ui_indent_width") + 6)

            row.label(text=" %s%s" % (
                native_indent*container.ui_indent_level,
                indent_ad_text))
            return

        for line_index in range(container.ui_indent_level):
            row.label(text="", icon_value=self.get_indent_line_color(
                bakemaster, data, container, line_index))
            if bakemaster.get_pref(context, "developer_ui_indent_width") > 0:
                row.label(text=" "*bakemaster.get_pref(
                    context, "developer_ui_indent_width"))

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
            elif any([container.group_has_childs(
                data, getattr(data, self.data_name),
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
            bakemaster, data, container)
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

        if bakemaster.get_pref(context, "developer_show_tickers"):
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

        self.draw_indent(context, row, bakemaster, data, container)

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

                parent_index_name = "%s_index" % bakemaster.get_wh_parent_name(
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

        self.draw_add_lowpoly_data_prompt(context, row, data, container, icon,
                                          active_data, active_propname, index,
                                          allow_drag_viz, drag_layout,
                                          allow_multi_select_viz)

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

    def draw_filter(self, context: Context, layout: Layout):
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
