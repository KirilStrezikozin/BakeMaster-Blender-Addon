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

from bpy.utils import (
    register_class as bpy_utils_register_class,
    unregister_class as bpy_utils_unregister_class,
)
from bpy.types import Scene as bpy_types_Scene
from bpy.props import PointerProperty

from . import ui_panels
from . import properties
from . import operators

if "bpy_utils_register_class" in locals():
    from importlib import reload as module_reload

    module_reload(ui_panels)
    module_reload(properties)
    module_reload(operators)

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
    ui_panels.BM_PT_BakeJobs,
    ui_panels.BM_PT_Bake,
    ui_panels.BM_PT_BakeControls,
    ui_panels.BM_PT_BakeHistory,

    ui_panels.BM_PREFS_AddonPreferences,
    ui_panels.BM_UL_BakeJobs_Item,
    ui_panels.BM_UL_BakeHistory,

    operators.ui.BM_OT_Help,
    operators.ui.BM_OT_BakeJobs_AddRemove,
    operators.ui.BM_OT_BakeJobs_Move,
    operators.ui.BM_OT_BakeJobs_Trash,
    operators.ui.BM_OT_Setup,
    operators.ui.BM_OT_Config,
    operators.ui.BM_OT_Bake_One,
    operators.ui.BM_OT_Bake_All,
    operators.ui.BM_OT_Bake_Pause,
    operators.ui.BM_OT_Bake_Stop,
    operators.ui.BM_OT_Bake_Cancel,
    operators.ui.BM_OT_BakeHistory_Rebake,
    operators.ui.BM_OT_BakeHistory_Config,
    operators.ui.BM_OT_BakeHistory_Remove,

    properties.BakeJob,
    properties.BakeHistory,
    properties.Global,
)


def register():
    for cls in classes:
        bpy_utils_register_class(cls)
    bpy_types_Scene.bakemaster = PointerProperty(type=properties.Global)


def unregister():
    for cls in reversed(classes):
        bpy_utils_unregister_class(cls)
    del bpy_types_Scene.bakemaster


if __name__ == "__main__":
    register()
