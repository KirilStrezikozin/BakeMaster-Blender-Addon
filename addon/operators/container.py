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

from bpy.types import Operator
from bpy.props import (
    IntProperty,
    StringProperty,
)


class BM_OT_Container_Add(Operator):
    bl_idname = 'bakemaster.container_add'
    bl_label = "Add"
    bl_description = "Add new Item to selected BakeJobs.\nIf active BakeJob type is Objects, pressing this button will add all valid selected Objects in the scene to the list"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    new_name: StringProperty()

    def add(self, bakejob, name: str):
        new_container = bakejob.containers.add()
        new_container.index = bakejob.containers_len
        new_container.bakejob_index = bakejob.index
        new_container.name = name

        bakejob.containers_active_index = new_container.index
        bakejob.containers_len += 1

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        if bakejob is None:
            return {'CANCELLED'}

        add_errors = 0

        if self.new_name == "":
            names = [object.name for object in context.selected_objects]
        else:
            names = [self.new_name]

        if len(names) == 0:
            self.report({'INFO'}, "Nothing is selected to add")
            return {'CANCELLED'}

        for name in names:
            object, _, _, _, _, error_message = bakemaster.get_object_info(
                context, name)

            if object is None:
                bakemaster.log("o2x0001", error_message)
                add_errors += 1
                continue

            self.add(bakejob, name)

        if add_errors:
            self.report(
                {'WARNING'},
                f"{add_errors} Object(s) could not be added (see Console)")

        bakemaster.wh_recalc_indexes(bakejob, "containers")
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_Container_Remove(Operator):
    bl_idname = 'bakemaster.container_remove'
    bl_label = "Remove"
    bl_description = "Remove selected Items from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        status, message = bakemaster.wh_remove(
            bakemaster.get_bakejob(bakemaster, self.bakejob_index),
            "containers", self.index)

        if message:
            self.report({'INFO'}, message)
        return status

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_Container_Trash(Operator):
    bl_idname = 'bakemaster.container_trash'
    bl_label = "Trash"
    bl_description = "Remove all Items from the list on the left"
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakemaster.wh_trash(
            bakemaster.get_bakejob(bakemaster, self.bakejob_index),
            "containers")
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_Container_Rename(Operator):
    bl_idname = 'bakemaster.container_rename'
    bl_label = "Rename"
    bl_description = "Click to rename the Item"
    bl_options = {'INTERNAL', 'UNDO'}

    index: IntProperty(default=-1)

    new_name: StringProperty(
        name="New name",
        description="Enter new name",
        default="",
        options={'SKIP_SAVE'})

    new_link: StringProperty(
        name="Relink to",
        description="Relink this item to a new Object",
        default="",
        options={'SKIP_SAVE'})

    container = None
    bakejob_type = ''

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        if self.container is None:
            return {'CANCELLED'}

        if self.bakejob_type == 'OBJECTS':
            if self.container.is_group:
                self.container.name = self.new_name
                return {'FINISHED'}

            object, _, _, _, _, error_message = bakemaster.get_object_info(
                context, self.new_link)

            if object is None:
                bakemaster.log("o2x0001", error_message)

            self.container.name = self.new_link

        elif self.bakejob_type == 'MAPS':
            pass

        return {'FINISHED'}

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster)
        self.container = bakemaster.get_container(bakejob, self.index)

        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}
        elif self.container is None:
            bakemaster.log("o2x0000")
            return {'CANCELLED'}

        self.new_name = self.container.name
        self.new_link = self.container.name
        self.bakejob_type = bakejob.type

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, _):
        if self.container is None:
            return

        layout = self.layout

        if self.container.is_group:
            layout.prop(self, "new_name")
        else:
            layout.prop(self, "new_link")


class BM_OT_Container_Toggle_Expand(Operator):
    bl_idname = "bakemaster.container_toggle_expand"
    bl_label = "Expand/Collapse"
    bl_options = {'INTERNAL'}

    bakejob_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        container = bakemaster.get_container(bakejob, self.index)

        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}
        elif container is None:
            bakemaster.log("o2x0000")
            return {'CANCELLED'}
        elif not container.is_group:
            bakemaster.log("o2x0002")
            return {'CANCELLED'}

        container.is_expanded = not container.is_expanded
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)


class BM_OT_Container_Group_Options(Operator):
    bl_idname = "bakemaster.container_group_options"
    bl_label = "Group Options"
    bl_description = "Change Group Options: Type and icon"
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    container = None

    def execute(self, _):
        return {'FINISHED'}

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        self.container = bakemaster.get_container(bakejob, self.index)

        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}
        elif self.container is None:
            bakemaster.log("o2x0000")
            return {'CANCELLED'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        if self.container is None:
            return

        layout = self.layout

        layout.prop(self.container, "group_type", expand=True)
        if self.container.group_type == 'DECORATOR':
            return

        layout.separator(factor=1.0)
        layout.label(text="Group Icon")
        flow = layout.grid_flow(row_major=False, columns=0, even_columns=True,
                                even_rows=False, align=True)

        for color_tag, icon in self.container.get_group_icon(
                context.scene.bakemaster, all=True):
            icon_ot = flow.operator(
                "bakemaster.container_group_set_icon", text="",
                icon_value=icon,
                emboss=color_tag == self.container.group_color_tag)

            icon_ot.bakejob_index = self.bakejob_index
            icon_ot.index = self.index
            icon_ot.new_color_tag = color_tag


class BM_OT_Container_Group_Set_Icon(Operator):
    bl_idname = "bakemaster.container_group_set_icon"
    bl_label = "Change Group icon"
    bl_description = "Change Group icon"
    bl_options = {'INTERNAL'}

    bakejob_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    new_color_tag: StringProperty()

    container = None

    def execute(self, _):
        if self.container is None:
            return {'CANCELLED'}

        self.container.group_color_tag = self.new_color_tag
        return {'FINISHED'}

    def invoke(self, context, _):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        self.container = bakemaster.get_container(bakejob, self.index)

        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}
        elif self.container is None:
            bakemaster.log("o2x0000")
            return {'CANCELLED'}

        return self.execute(context)


class BM_OT_Container_Group(Operator):
    bl_idname = "bakemaster.container_group"
    bl_label = "Group"
    bl_description = "Group selected Objects. Group lets you set settings for all Objects in it at once"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    container_index: IntProperty(default=-1)

    group_insert_index = -1
    last_selected_index = -1

    def eval_group(self, bakemaster, container, s_group_level,
                   curr_group_level, p_continue_selection):
        if self.group_insert_index == -1:
            print(f"BakeMaster Internal Warning: group_insert_index is not defined at {self}")  # noqa: E501
            return False, 'TRYAGAIN_ERROR'

        if all([not container.ui_indent_level >= s_group_level,
                container.is_selected]):
            # don't clear selection on error
            bakemaster.allow_drag_trans = False
            return False, 'LEVEL_ERROR'

        if container.is_selected:
            if self.last_selected_index == -1:
                self.last_selected_index = container.index
            elif container.index != self.last_selected_index + 1:
                # don't clear selection on error
                bakemaster.allow_drag_trans = False
                return False, 'ONEBLOCK_ERROR'
            else:
                self.last_selected_index = container.index

        if container.ui_indent_level == s_group_level:
            return container.is_selected, ''
        elif all([container.ui_indent_level >= curr_group_level,
                  container.ui_indent_level >= s_group_level]):
            return p_continue_selection, ''

        return False, ''

    def add_group_item(self, bakejob, group_level):
        name = "Group"

        new_group = bakejob.containers.add()
        new_group.name = name
        # new_group.bakejob_index = bakejob.index -> in indexes_recalc()
        new_group.is_group = True
        new_group.ui_indent_level = group_level

        bakejob.containers_len += 1
        bakejob.containers_active_index = self.group_insert_index

        bakejob.containers.move(bakejob.containers_len,
                                self.group_insert_index)

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}

        has_ms = bakemaster.wh_has_ms(bakejob, "containers")

        if not has_ms:
            bakemaster.log("ogx0000")
            self.report({'INFO'}, "Select items with Shift, Ctrl to group")
            return {'CANCELLED'}

        errors = {
            'LEVEL_ERROR': "Cannot group with items from levels above first selected",  # noqa: E501
            'ONEBLOCK_ERROR': "One-block selection is required to group",  # noqa: E501
            'TRYAGAIN_ERROR': "Try again. Internal error (see console)"
            }

        to_group = []

        s_group_level = -1  # inital grouping level
        # p_group_index = -1  # index of item's parent group item
        curr_group_level = 0  # level of item's parent group item
        p_continue_selection = False  # continue grouping child items

        for container in bakejob.containers:
            if container.has_drop_prompt:
                continue

            if container.is_selected and s_group_level == -1:
                s_group_level = container.ui_indent_level
                curr_group_level = container.ui_indent_level
                self.group_insert_index = container.index
            elif any([s_group_level == -1, self.group_insert_index == -1]):
                continue

            if container.is_group:
                # p_group_index = container.index
                curr_group_level = container.ui_indent_level
                if curr_group_level == s_group_level:
                    p_continue_selection = container.is_selected
            elif container.ui_indent_level <= curr_group_level:
                # p_group_index = container.parent_group_index
                curr_group_level = container.ui_indent_level
                if curr_group_level == s_group_level:
                    p_continue_selection = False

            allow_group, error_id = self.eval_group(
                bakemaster, container, s_group_level, curr_group_level,
                p_continue_selection)
            if error_id:
                bakemaster.log("ogx0001")
                self.report({'INFO'}, errors[error_id])
                return {'CANCELLED'}
            elif allow_group:
                to_group.append(container)

        for container in to_group:
            container.ui_indent_level += 1
        self.add_group_item(bakejob, s_group_level)

        bakemaster.wh_recalc_indexes(bakejob, "containers", parent_props=[
            ["bakejob_index", bakejob.index]])
        return {'FINISHED'}

    def invoke(self, context, _):
        self.group_insert_index = -1
        self.last_selected_index = -1
        return self.execute(context)


class BM_OT_Container_Ungroup(Operator):
    bl_idname = "bakemaster.container_ungroup"
    bl_label = "Ungroup"
    bl_description = "Ungroup selected Objects"
    bl_options = {'INTERNAL', 'UNDO'}

    bakejob_index: IntProperty(default=-1)
    container_index: IntProperty(default=-1)
    index: IntProperty(default=-1)

    s_ungroup_level = -1  # inital ungrouping level
    new_active_index = -1

    def ungroup(self, bakemaster, bakejob, container):
        if self.s_ungroup_level == -1:
            bakemaster.log("ogx0002")
        container.ui_indent_level = self.s_ungroup_level

        if bakejob.containers_active_index != self.new_active_index:
            bakejob.containers_active_index = self.new_active_index

        if container.parent_group_index == -1:
            return

        # if parent group is dictator, copy settings from it,
        # else do not copy anything.
        parent_container = bakejob.containers[container.parent_group_index]
        if parent_container.group_type == 'DECORATOR':
            return

        exclude_copy = {
            "name": True,
            "index": True,
            "bakejob_index": True,
            "is_group": True,
            "is_expanded": True,
            "group_type": True,
            "group_is_texset": True,
            "group_color_tag": True,
            "lowpoly_index": True,
            "lowpoly_name": True,
            "is_cage": True,
            "is_decal": True
        }
        _ = bakemaster.wh_copy(parent_container, bakejob.containers,
                               container.index, exclude_copy)

    def ungroup_has_selection_errors(self, has_selection, container,
                                     last_selected_index):
        if not all([has_selection and container.is_selected]):
            return last_selected_index, ''

        if all([last_selected_index != -1,
                container.index != last_selected_index + 1]):
            return last_selected_index, 'ONEBLOCK_ERROR'
        elif container.ui_indent_level < self.s_ungroup_level:
            return last_selected_index, 'LEVEL_ERROR'
        return container.index, ''

    def ungroup_is_finished(self, has_selection, container, f_group_index):
        selection_passed = all(
            [has_selection, not container.is_selected,
             container.ui_indent_level <= self.s_ungroup_level])
        active_container_passed = all(
            [not has_selection,
             container.ui_indent_level <= self.s_ungroup_level,
             any([
                 all([container.is_group,
                      container.index != f_group_index]),
                 all([not container.is_group,
                      container.parent_group_index != f_group_index])
                 ])
             ])
        return selection_passed or active_container_passed

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        bakejob = bakemaster.get_bakejob(bakemaster, self.bakejob_index)
        active_container = bakemaster.get_container(bakejob, self.index)

        if bakejob is None:
            bakemaster.log("o1x0000")
            return {'CANCELLED'}
        elif active_container is None:
            bakemaster.log("o2x0000")
            return {'CANCELLED'}

        has_ms = bakemaster.wh_has_ms(bakejob, "containers")

        if not has_ms and not active_container.is_group:
            self.report({'INFO'}, "Select at least one group to ungroup")
            return {'CANCELLED'}

        errors = {
            'LEVEL_ERROR': "Cannot ungroup items from levels above first selected",  # noqa: E501
            'ONEBLOCK_ERROR': "One-block selection is required to ungroup"  # noqa: E501
        }

        # when not has_selection, index of first group on self.s_ungroup_level:
        f_group_index = -1
        last_selected_index = -1

        to_ungroup = []
        to_remove = []

        for container in bakejob.containers:
            if container.has_drop_prompt:
                continue

            if all([self.s_ungroup_level == -1,
                    has_ms, container.is_selected]):
                self.s_ungroup_level = container.ui_indent_level
                self.new_active_index = container.index
            elif all([self.s_ungroup_level == -1, not has_ms,
                      container.index == self.container_index]):
                self.s_ungroup_level = container.ui_indent_level
                self.new_active_index = container.index
                f_group_index = container.index
            elif self.s_ungroup_level == -1:
                continue

            # check oselection
            last_selected_index, error_id = self.ungroup_has_selection_errors(
                has_ms, container, last_selected_index)
            if error_id != '':
                bakemaster.log("ogx0003")
                self.report({'INFO'}, errors[error_id])
                return {'CANCELLED'}

            # check no more to ungroup
            if self.ungroup_is_finished(has_ms, container,
                                        f_group_index):
                break

            if container.is_group:
                to_remove.append(container.index)
                continue
            to_ungroup.append(container)

        for container in to_ungroup:
            self.ungroup(bakemaster, bakejob, container)

        for index in reversed(to_remove):
            bakejob.containers.remove(index)
        bakejob.containers_len -= len(to_remove)

        bakemaster.wh_recalc_indexes(bakejob, "containers")
        return {'FINISHED'}

    def invoke(self, context, _):
        self.s_ungroup_level = -1
        self.new_active_index = -1
        return self.execute(context)
