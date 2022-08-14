# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name" : "BakeMaster",
    "description" : "Bake various PBR-based or Cycles maps with ease and comfort",
    "author" : "kemplerart",
    "version" : (1, 0, 0),
    "blender" : (2, 83, 0),
    "location" : "View3D > Sidebar > BakeMaster",
    "warning" : "",
    "wiki_url": "",
    "tracker_url": "",
    "category" : "Material"
}

if "bpy" in locals():
    from .ui_panel import *
    from .operators import *
    from .properties import *
    from .operator_bake import *

    from . import ui_panel
    from . import operators
    from . import operator_bake
    from . import properties

    import importlib
    importlib.reload(ui_panel)
    importlib.reload(operators)
    importlib.reload(operator_bake)
    importlib.reload(properties)

else:
    from .ui_panel import *
    from .operators import *
    from .properties import *
    from .operator_bake import *
    
import bpy

classes = (
    BM_UL_AOL_Item,
    BM_UL_ITEM_Maps,

    BM_PT_Main,
    BM_PT_Item,
    BM_PT_Item_STT,
    BM_PT_Item_UVMap,
    BM_PT_Item_Output,

    BM_PT_Item_MapList,
    BM_PT_Item_Map,

    BM_PT_Item_MainBake,
    BM_PT_Item_Bake,
    BM_PT_Item_MainBakeSettings,

    BM_PT_Main_Help,

    BM_OT_AOL,
    BM_OT_AOL_Add,
    BM_OT_AOL_Remove,
    BM_OT_AOL_Refresh,
    BM_OT_AOL_Trash,
    BM_OT_ITEM_Maps,
    BM_OT_ITEM_Bake,
    BM_OT_Help,

    BM_Item_Map,
    BM_Item,
    BM_SceneProps)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bm_aol = bpy.props.CollectionProperty(type = BM_Item)
    bpy.types.Scene.bm_props = bpy.props.PointerProperty(type = BM_SceneProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bm_aol
    del bpy.types.Scene.bm_props

if __name__ == "__main__":
    register()