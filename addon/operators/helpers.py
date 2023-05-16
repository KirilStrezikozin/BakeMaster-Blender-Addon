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


from bpy.types import Context, Event, Operator

from bpy.props import StringProperty


class BM_OT_Helper_Free_Icons(Operator):
    """
    Remove Preview Collections of custom icons initialized in the Global
    Properties.
    """

    bl_idname = 'bakemaster.helper_free_icons'
    bl_label = "Remove Custom Icons"
    bl_options = {'INTERNAL'}

    def execute(self, context: Context) -> set:
        import bpy.utils.previews

        bakemaster = context.scene.bakemaster
        preview_collections = bakemaster.get_icon('', reg=True)

        if len(preview_collections) == 0:
            bakemaster.log("mbx0002")

        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)

        preview_collections.clear()
        return {'FINISHED'}


class BM_OT_Helper_Help(Operator):
    """Press to visit the according BakeMaster's online documentation page"""

    bl_idname = 'bakemaster.helper_help'
    bl_label = "Help"
    bl_options = {'INTERNAL'}

    page_id: StringProperty()
    addon_version = "latest"

    def get_url(self) -> str:
        base = "https://bakemaster-blender-addon.readthedocs.io/en/"
        urls = {
            '': r'%s/',
            'BM_PT_Presets': r'%s/',
            'BM_PT_Project': r'%s/',
            'BM_PT_BakeJobs': r'%s/',
            'BM_PT_Containers': r'%s/',
            'BM_PT_Subcontainers': r'%s/',
            'BM_PT_Bake': r'%s/',
            'BM_PT_BakeHistory': r'%s/',
        }

        url = urls.get(self.page_id, r'%s/')
        return url % (base + self.addon_version)

    def execute(self, _: Context) -> set:
        from webbrowser import open as webbrowser_open
        webbrowser_open(self.get_url())
        return {'FINISHED'}

    def invoke(self, context: Context, _: Event) -> set:
        self.addon_version = context.scene.bakemaster.get_addon_version()
        return self.execute(context)


class BM_OT_Helper_Help_Project(BM_OT_Helper_Help):
    """Directory where baked Maps are going to be saved and linked (for Map Atlases). By choosing it, all bake output filepaths will be set up automatically. BakeMaster will analyse edited Maps and Objects faster to decrease time of rebakes."""  # noqa: E501

    bl_idname = 'bakemaster.helper_help_project'
    bl_label = "Bake Project. Press to read more"


class BM_OT_Helper_UI_Prop_Relinquish(Operator):
    bl_idname = 'bakemaster.helper_ui_prop_relinquish'
    bl_label = "Set similar values"
    bl_description = "Each selected item will have the same value of this property"  # noqa: E501
    bl_options = {'INTERNAL', 'UNDO'}

    data_name: StringProperty()
    prop_name: StringProperty()

    def execute(self, context: Context) -> set:
        bakemaster = context.scene.bakemaster

        data, _, attr = getattr(
            bakemaster, "get_active_%s" % self.data_name)(bakemaster)
        if data is None:
            bakemaster.log("o0x0001", self)
            return {'CANCELLED'}

        container = getattr(bakemaster, "get_%s" % attr[:-1])(data)
        setattr(container, self.prop_name, getattr(container, self.prop_name))
        return {'FINISHED'}

    def invoke(self, context: Context, _: Event) -> set:
        return self.execute(context)
