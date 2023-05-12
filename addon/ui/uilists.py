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

from bpy.types import UIList

from bpy.props import (
    StringProperty,
    BoolProperty,
)

from .helpers import (
    fnmatch,
    get_bakehistory_timestamp_label as _get_bakehistory_timestamp_label,
    BM_UI_wh_UIList,
)


# class F():


class BM_UL_BakeJobs(BM_UI_wh_UIList):
    data_name = "bakejobs"

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_multi_select_viz,
                   allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster

        if container.type == 'OBJECTS':
            type_icon = bakemaster.get_icon('OBJECTS')
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


class BM_UL_Containers(BM_UI_wh_UIList):
    data_name = "containers"

    def ticker_icon(self, context, bakemaster, data, container):
        error_icon = bakemaster.get_icon('RED_ERROR')

        if container.is_group:
            if any([getattr(
                data, "%s_active_index" % self.data_name) == container.index,
                    container.group_type == 'DECORATOR']):
                return '', '', True
            group_icon = container.get_group_icon(bakemaster)
            return 'ICON_VALUE', group_icon, True

        if data is None:
            return 'ICON_VALUE', error_icon, False

        elif data.type == 'MAPS':
            return '', '', True

        elif data.type == 'OBJECTS':
            obj, _, obj_icon_type, obj_icon, _, _ = bakemaster.get_object_info(
                    bakemaster, context.scene.objects, container.name)

            if obj is None:
                return 'ICON_VALUE', error_icon, False

            return obj_icon_type, obj_icon, True

        return 'ICON_VALUE', error_icon, False

    def draw_props(self, context, row, data, container, icon, active_data,
                   active_propname, index, allow_multi_select_viz,
                   allow_drag_viz, drag_layout):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        group, forbid_bake = bakemaster.get_wh_parent_name(
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

                parent_index_name = "%s_index" % bakemaster.get_wh_parent_name(
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
            row.active &= container_exists
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

            group_icon = container.get_group_icon(bakemaster)
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
        timestamp = _get_bakehistory_timestamp_label(bakemaster, container)

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
        timestamp = _get_bakehistory_timestamp_label(data, container)
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
