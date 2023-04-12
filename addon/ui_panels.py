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
    BM_PT_BakeJobsBase,
    BM_PT_ItemsBase,
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
from fnmatch import fnmatch as fnmatch

bm_space_type = 'VIEW_3D'
bm_region_type = 'UI'
bm_category = "BakeMaster"


class BM_PT_BakeJobs(BM_PT_BakeJobsBase):
    bl_space_type = bm_space_type
    bl_region_type = bm_region_type
    bl_category = bm_category


class BM_PT_Items(BM_PT_ItemsBase):
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


class BM_UIList_for_WalkHandler(UIList):
    """
    UIList for BM_OT_UIList_Walk_Handler for lower cyclomatic complexity of
    UILists for walk handler that requires a bunch of checks.

    UI representation for: drop from Outliner, drag items to new positions,
    select multiple items.

    data_name is an identifier of walk_data_name for this UIList instance.

    Use draw_props() to draw all needed item's properties (aligned row on the
    left). Default includes use_bake.
    Use draw_operators() to draw all needed operators for the item (row on the
    right). Default is emtpy.

    Filtering options on item.name property is on by default. Overwrite
    draw_filter() for custom.

    Overwrite draw_item() method for custom UI.
    """

    data_name = ""

    use_name_filter = True

    def allow_multi_select_viz(self, bakemaster, item):
        if not all([bakemaster.allow_multi_select,
                    not bakemaster.is_multi_selection_empty,
                    not item.has_drop_prompt, not item.is_drag_empty]):
            return False

        walk_data_getter = getattr(bm_get, "walk_data_get_%s" % self.data_name)
        data, _, _ = walk_data_getter(bakemaster)

        if hasattr(data, "index"):
            parent_index = data.index
        else:
            parent_index = ""
        our_multi_selection_data = f"{self.data_name}_{parent_index}"

        return bakemaster.multi_selection_data == our_multi_selection_data

    def draw_props(self, context, row, data, item, icon, active_data,
                   active_propname, index):
        bakemaster = context.scene.bakemaster
        row.emboss = 'NONE'

        icon = 'RESTRICT_RENDER_OFF' if item.use_bake else 'RESTRICT_RENDER_ON'
        subrow = row.row()
        subrow.prop(item, 'use_bake', text="", icon=icon)
        if bakemaster.allow_drag and bakemaster.drag_to_index != -1:
            subrow.enabled = False
        row.active = item.use_bake

    def draw_operators(self, context, row, data, item, icon, active_data,
                       active_propname, index):
        pass

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        bakemaster = context.scene.bakemaster
        allow_multi_select_viz = self.allow_multi_select_viz(bakemaster, item)

        if allow_multi_select_viz and item.is_selected:
            col_layout = layout.box()
            col_layout.scale_y = 0.45
        else:
            col_layout = layout
        col = col_layout.column(align=True)

        # draw a darker line when dragging item
        if item.is_drag_placeholder and bakemaster.allow_drag:
            drag_placeholder = col.row().box()
            drag_placeholder.label(text="")
            drag_placeholder.scale_y = 0.1

        row = col.row(align=True)
        row.alignment = 'LEFT'

        # draw an empty item at the end
        if item.is_drag_empty:
            if bakemaster.drag_to_index == -1:
                return
            row.prop(item, "ticker", text="...", emboss=False,
                     toggle=True)
            return

        # draw a drop prompt ("add new...")
        if item.has_drop_prompt:
            row.alignment = 'EXPAND'
            row.prop(item, "drop_name", text="", emboss=True)
            return

        if item.index != bakemaster.bakejobs_active_index:
            row.emboss = 'NONE'

        # for multiple selection
        if allow_multi_select_viz:
            layout.active = item.is_selected
            row.emboss = 'NONE'

        self.draw_props(context, row, data, item, icon, active_data,
                        active_propname, index)

        row.prop(item, "ticker", text=item.name, toggle=True)

        self.draw_operators(context, row, data, item, icon, active_data,
                            active_propname, index)

        # fade out row while dragging if item in it isn't dragged
        if all([bakemaster.allow_drag, not item.has_drag_prompt,
                bakemaster.drag_to_index != -1]):
            row.active = False

    def draw_filter(self, context, layout):
        if any([all([context.scene.bakemaster.allow_drag,
                     context.scene.bakemaster.drag_to_index != -1]),
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


class BM_UL_BakeJobs(BM_UIList_for_WalkHandler):
    data_name = "bakejobs"

    def draw_props(self, context, row, data, item, icon, active_data,
                   active_propname, index):
        bakemaster = context.scene.bakemaster

        if item.type == 'OBJECTS':
            type_icon = bm_ui_utils.get_icon_id(bakemaster,
                                                "bakemaster_objects.png")
            type_ot = row.operator('bakemaster.bakejob_toggletype',
                                   text="", icon_value=type_icon)
        else:
            type_ot = row.operator('bakemaster.bakejob_toggletype',
                                   text="", icon='RENDERLAYERS')
        type_ot.index = item.index

        super().draw_props(context, row, bakemaster, item, icon, active_data,
                           active_propname, index)


class BM_UL_Items(BM_UIList_for_WalkHandler):
    data_name = "items"


class BM_UL_BakeHistory(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        self.use_filter_sort_reverse = True

        bakemaster = data
        timestamp = bm_ui_utils.bakehistory_timestamp_get_label(bakemaster,
                                                                item)

        row = layout.row()
        row.prop(item, 'name', text="", emboss=False, icon='RENDER_STILL')
        row.label(text=timestamp)

        row.operator('bakemaster.bakehistory_rebake', text="",
                     icon='RECOVER_LAST').index = item.index
        row.operator('bakemaster.bakehistory_config', text="",
                     icon='FOLDER_REDIRECT').index = item.index
        row.operator('bakemaster.bakehistory_remove', text="",
                     icon='TRASH').index = item.index

        if bakemaster.bakehistory_reserved_index == item.index:
            row.active = False

    def draw_filter(self, _, layout):
        row = layout.row(align=True)
        row.prop(self, "filter_name", text="")
        row.prop(self, "use_filter_invert", text="", toggle=True,
                 icon='ARROW_LEFTRIGHT')

    def item_get_name(self, data, item):
        timestamp = bm_ui_utils.bakehistory_timestamp_get_label(data,
                                                                item)
        return "%s%s" % (item.name, timestamp)

    def filter_by_name(self, data, pattern, bitflag, items, propname_getter,
                       reverse=False):
        flt_flags = []
        pattern = "*%s*" % pattern

        for item in items:
            name = propname_getter(data, item)
            if fnmatch(name, pattern):
                flt_flags.append(bitflag)
            else:
                flt_flags.append(~bitflag)

        if reverse:
            flt_flags.reverse()

        return flt_flags

    def filter_items(self, _, data, propname):
        # Sort items by filter_name on item.name + item.timestamp combined

        # Default return values
        flt_flags = []
        flt_neworder = []

        if self.filter_name:
            flt_flags = self.filter_by_name(data, self.filter_name,
                                            self.bitflag_filter_item,
                                            getattr(data, propname),
                                            self.item_get_name,
                                            reverse=self.use_filter_invert)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * data.bakehistory_len

        return flt_flags, flt_neworder

    def invoke(self, context, event):
        pass
