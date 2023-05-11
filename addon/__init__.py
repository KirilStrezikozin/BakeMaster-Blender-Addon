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

import bpy


if "bpy" not in locals():
    from . import properties
    from . import operators
    from . import ui

else:
    import importlib

    properties = importlib.reload(properties)
    operators = importlib.reload(operators)
    ui = importlib.reload(ui)

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
    properties.properties.Subcontainer,
    properties.properties.Container,
    properties.properties.BakeJob,
    properties.properties.BakeHistory,
    properties.properties.Global,

    ui.panels.BM_PT_Preferences,
    ui.panels.BM_PT_BakeJobs,
    ui.panels.BM_PT_Containers,
    ui.panels.BM_PT_Bake,
    ui.panels.BM_PT_BakeControls,
    ui.panels.BM_PT_BakeHistory,

    ui.uilists.BM_UL_BakeJobs,
    ui.uilists.BM_UL_Containers,
    ui.uilists.BM_UL_BakeHistory,

    operators.helpers.BM_OT_Global_Free_Icons,
    operators.helpers.BM_OT_Global_Help,
    operators.helpers.BM_OT_Helper_FileChooseDialog,
    operators.helpers.BM_OT_Global_UI_Prop_Relinquish,

    operators.walk_handler.BM_OT_Global_WalkHandler,
    operators.walk_handler.BM_OT_Global_WalkData_Move,
    operators.walk_handler.BM_OT_Global_WalkData_Trans,
    operators.walk_handler.BM_OT_Global_WalkData_Move_Lowpoly_Data,
    operators.walk_handler.BM_OT_Global_WalkData_AddDropped,

    operators.bakejob.BM_OT_BakeJob_Add,
    operators.bakejob.BM_OT_BakeJob_Remove,
    operators.bakejob.BM_OT_BakeJob_Trash,
    operators.bakejob.BM_OT_BakeJob_Rename,
    operators.bakejob.BM_OT_BakeJob_Change_Type,
    operators.bakejob.BM_OT_BakeJob_Merge,

    operators.container.BM_OT_Container_Add,
    operators.container.BM_OT_Containers_Remove,
    operators.container.BM_OT_Containers_Trash,
    operators.container.BM_OT_Container_Rename,
    operators.container.BM_OT_Containers_Toggle_Expand,
    operators.container.BM_OT_Containers_Group_SetIcon,
    operators.container.BM_OT_Containers_GroupOptions,
    operators.container.BM_OT_Containers_Group,
    operators.container.BM_OT_Containers_Ungroup,

    operators.subcontainer.BM_OT_Subcontainer_Trash,
    operators.subcontainer.BM_OT_Subcontainers_Toggle_Expand,

    operators.bake.BM_OT_Bake_All,
    operators.bake.BM_OT_Bake_One,
    operators.bake.BM_OT_Bake_Toggle_Pause,
    operators.bake.BM_OT_Bake_Stop,
    operators.bake.BM_OT_Bake_Cancel,
    operators.bake.BM_OT_Bake_Setup,
    operators.bake.BM_OT_Bake_Config,
    operators.bake.BM_OT_BakeHistory_Remove,
    operators.bake.BM_OT_BakeHistory_Rebake,
    operators.bake.BM_OT_BakeHistory_Config,
)

_is_walk_handler_timer_started = False


@bpy.app.handlers.persistent
def BM_WalkHandler_caller(_):
    """
    Walk Handler caller. After the first invoke, if Handler was cancelled,
    try to reinvoke every 5 seconds.
    """

    if operators.walk_handler._walk_handler_invoked:
        return

    global _is_walk_handler_timer_started

    time = operators.walk_handler.time

    invoke_time = operators.walk_handler._walk_handler_invoke_time
    time_diff = time() - invoke_time

    if not any([time_diff > 5,
                not _is_walk_handler_timer_started]):
        return

    _is_walk_handler_timer_started = True
    operators.walk_handler._walk_handler_invoke_time = time()

    bpy.ops.bakemaster.global_walkhandler('INVOKE_DEFAULT')


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bakemaster = bpy.props.PointerProperty(
        type=properties.properties.Global)

    bpy.app.handlers.depsgraph_update_pre.append(BM_WalkHandler_caller)


def unregister():
    # remove custom icons
    bpy.ops.bakemaster.global_free_icons('EXEC_DEFAULT')

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # remove calls handlers
    for item in bpy.app.handlers.depsgraph_update_pre:
        if item.__name__ != "BM_WalkHandler_caller":
            continue
        bpy.app.handlers.depsgraph_update_pre.remove(item)

    del bpy.types.Scene.bakemaster


if __name__ == "__main__":
    register()
