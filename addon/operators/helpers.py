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

from os import path as os_path

from bpy import ops as bpy_ops

from bpy.types import Operator

from bpy.props import (
    BoolProperty,
    StringProperty,
)

from bpy_extras.io_utils import ImportHelper


class BM_OT_Global_Free_Icons(Operator):
    """
    Remove Preview Collections of custom icons initialized in the Global
    Properties.
    """

    bl_idname = 'bakemaster.global_free_icons'
    bl_label = "Remove Custom Icons"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        import bpy.utils.previews
        preview_collections = context.scene.bakemaster.get_icon(reg=True)

        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)

        preview_collections.clear()
        return {'FINISHED'}


class BM_OT_Global_Help(Operator):
    bl_idname = 'bakemaster.global_help'
    bl_label = "Help"
    bl_description = "Press to visit the according BakeMaster's online documentation page"  # noqa: E501
    bl_options = {'INTERNAL'}

    page_id: StringProperty()
    addon_version = "latest"

    def get_url(self):
        base = "https://bakemaster-blender-addon.readthedocs.io/en/"
        urls = {
            '': r'%s/',
            'bakejobs': r'%s/',
            'objects': r'%s/',
            'maps': r'%s/',
            'bake': r'%s/',
            'bakehistory': r'%s/',
        }

        url = urls.get(self.page_id, r'%s/')
        return url % (base + self.addon_version)

    def invoke(self, context, _):
        self.addon_version = context.scene.bakemaster.get_addon_version()
        return self.execute(context)

    def execute(self, _):
        from webbrowser import open as webbrowser_open
        webbrowser_open(self.get_url())
        return {'FINISHED'}


class BM_OT_Helper_FileChooseDialog(Operator, ImportHelper):
    bl_idname = 'bakemaster.helper_filechoosedialog'
    bl_label = "Choose a filepath"
    bl_description = "Open a file browser, hold Shift to open the file, Alt to browse containing directory"  # noqa: E501
    bl_options = {'INTERNAL'}

    prop_name: StringProperty(options={'HIDDEN'})

    config_lookup: BoolProperty(default=False, options={'HIDDEN'})
    config_action: StringProperty(options={'HIDDEN'})

    message: StringProperty(options={'HIDDEN'})

    def process_exit(self):
        if self.message != "":
            self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def execute(self, context):
        if os_path.isfile(self.filepath):
            self.filepath = os_path.dirname(self.filepath)
        # no safe check if property is invalid
        setattr(context.scene.bakemaster, self.prop_name, self.filepath)

        if not self.config_lookup:
            return self.process_exit()

        bpy_ops.bakemaster.config('EXEC_DEFAULT', action=self.config_action)


class BM_OT_Global_UI_Prop_Relinquish(Operator):
    bl_idname = 'bakemaster.global_ui_prop_relinquish'
    bl_label = "Set similar values"
    bl_description = "Each selected item will have the same value of this property"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    data_name: StringProperty()
    prop_name: StringProperty()

    def execute(self, context):
        bakemaster = context.scene.bakemaster

        data, _, attr = getattr(
            bakemaster, "get_active_%s" % self.data_name)(bakemaster)
        if data is None:
            bakemaster.log("o0x0001", self)
            return {'CANCELLED'}

        container = getattr(bakemaster, "get_%s" % attr[:-1])(data)
        setattr(container, self.prop_name, getattr(container, self.prop_name))
        return {'FINISHED'}

    def invoke(self, context, _):
        return self.execute(context)
