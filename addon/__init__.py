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

bl_info = {
    "name": "BakeMaster",
    "description":
        "Bake various PBR and other maps fast, with ease and comfort",
    "author": "kemplerart",
    "version": (3, 0, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > BakeMaster",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Material"
}


if "bpy" in locals():
    import importlib

    properties = importlib.reload(properties)
    operators = importlib.reload(operators)
    ui = importlib.reload(ui)
else:
    import bpy

    from . import (
        properties,
        operators,
        ui,
    )

classes = properties.classes + operators.classes + ui.classes


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bakemaster = bpy.props.PointerProperty(
        type=properties.properties.Global)

    bpy.app.handlers.depsgraph_update_pre.append(operators.BM_call_WalkHandler)


def unregister() -> None:
    bpy.ops.bakemaster.helper_free_icons('EXEC_DEFAULT')

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for f in bpy.app.handlers.depsgraph_update_pre:
        if f.__name__ != "BM_call_WalkHandler":
            continue
        bpy.app.handlers.depsgraph_update_pre.remove(f)

    del bpy.types.Scene.bakemaster


if __name__ == "__main__":
    register()
