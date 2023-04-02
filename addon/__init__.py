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

from bpy import context as bpy_context
from bpy.utils import (
    register_class as bpy_utils_register_class,
    unregister_class as bpy_utils_unregister_class,
)
import bpy.utils.previews as bpy_utils_previews
from bpy.types import Scene as bpy_types_Scene
from bpy.props import PointerProperty
from bpy import ops as bpy_ops
from bpy.app.handlers import (
    depsgraph_update_pre as bpy_depsgraph_update_pre,
    persistent,
)

from . import ui_panels
from . import properties
from .operators import (
    ui as operators_ui,
)


if "bpy_utils_register_class" in locals():
    from importlib import reload as module_reload

    module_reload(ui_panels)
    module_reload(properties)
    module_reload(operators_ui)

bl_info = {
    "name": "BakeMaster",
    "description":
        "Bake various PBR-based or Cycles maps with ease and comfort",
    "author": "kemplerart",
    "version": (3, 0, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > BakeMaster",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Material"
}

classes = (
    properties.Item,
    properties.BakeJob,
    properties.BakeHistory,
    properties.Global,

    ui_panels.BM_PT_BakeJobs,
    ui_panels.BM_PT_Bake,
    ui_panels.BM_PT_BakeControls,
    ui_panels.BM_PT_BakeHistory,

    ui_panels.BM_PREFS_AddonPreferences,
    ui_panels.BM_UL_BakeJobs,
    ui_panels.BM_UL_BakeHistory,

    operators_ui.BM_OT_Help,
    operators_ui.BM_OT_UIList_WalkHandler,
    operators_ui.BM_OT_BakeJobs_AddRemove,
    operators_ui.BM_OT_BakeJobs_AddDropped,
    operators_ui.BM_OT_BakeJobs_Trash,
    operators_ui.BM_OT_BakeJob_Rename,
    operators_ui.BM_OT_BakeJob_ToggleType,
    operators_ui.BM_OT_FileChooseDialog,
    operators_ui.BM_OT_Setup,
    operators_ui.BM_OT_Config,
    operators_ui.BM_OT_Bake_One,
    operators_ui.BM_OT_Bake_All,
    operators_ui.BM_OT_Bake_Pause,
    operators_ui.BM_OT_Bake_Stop,
    operators_ui.BM_OT_Bake_Cancel,
    operators_ui.BM_OT_BakeHistory_Rebake,
    operators_ui.BM_OT_BakeHistory_Config,
    operators_ui.BM_OT_BakeHistory_Remove,
)


@persistent
def BM_UIList_WalkHandler_callback(scene):
    ticker = scene.bakemaster.uilist_walkhandler_ticker
    scene.bakemaster.uilist_walkhandler_ticker = not ticker
    # print("no")
    # bpy_ops.bakemaster.uilist_walkhandler('INVOKE_DEFAULT')


def register():
    for cls in classes:
        bpy_utils_register_class(cls)
    bpy_types_Scene.bakemaster = PointerProperty(type=properties.Global)

    bpy_depsgraph_update_pre.append(BM_UIList_WalkHandler_callback)


def unregister():
    for cls in reversed(classes):
        bpy_utils_unregister_class(cls)

    # clearing preview_collections - custom icons
    # for scene in bpy_context.data.scenes:
    #     if not hasattr(scene, "bakemaster"):
    #         continue
    #     for pcoll in scene.bakemaster.preview_collections.values():
    #         bpy_utils_previews.remove(pcoll)
    #     scene.bakemaster.preview_collections.clear()

    # removing calls handlers
    for item in bpy_depsgraph_update_pre:
        if item.__name__ != "bakemaster_uilist_walkhandler_callhandler":
            continue
        bpy_depsgraph_update_pre.remove(item)

    del bpy_types_Scene.bakemaster


if __name__ == "__main__":
    register()
