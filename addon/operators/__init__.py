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

from . import (
    helpers,
    walkhandler,
    bakejob,
    container,
    subcontainer,
    bake,
)

BM_call_WalkHandler = walkhandler.call_WalkHandler

__all__ = ["classes", "BM_call_WalkHandler"]

classes = (
    helpers.BM_OT_Helper_Free_Icons,
    helpers.BM_OT_Helper_Help,
    helpers.BM_OT_Helper_Help_Config,
    helpers.BM_OT_Helper_UI_Prop_Relinquish,

    walkhandler.BM_OT_WalkHandler,
    walkhandler.BM_OT_Global_WalkData_Move,
    walkhandler.BM_OT_Global_WalkData_Trans,
    walkhandler.BM_OT_Global_WalkData_Move_Lowpoly_Data,
    walkhandler.BM_OT_Global_WalkData_AddDropped,

    bakejob.BM_OT_BakeJob_Add,
    bakejob.BM_OT_BakeJob_Remove,
    bakejob.BM_OT_BakeJob_Trash,
    bakejob.BM_OT_BakeJob_Rename,
    bakejob.BM_OT_BakeJob_Change_Type,
    bakejob.BM_OT_BakeJob_Merge,

    container.BM_OT_Container_Add,
    container.BM_OT_Container_Remove,
    container.BM_OT_Container_Trash,
    container.BM_OT_Container_Rename,
    container.BM_OT_Container_Toggle_Expand,
    container.BM_OT_Container_Group_Set_Icon,
    container.BM_OT_Container_Group_Options,
    container.BM_OT_Container_Group,
    container.BM_OT_Container_Ungroup,

    subcontainer.BM_OT_Subcontainer_Trash,
    subcontainer.BM_OT_Subcontainer_Toggle_Expand,

    bake.BM_OT_Bake_All,
    bake.BM_OT_Bake_One,
    bake.BM_OT_Bake_Toggle_Pause,
    bake.BM_OT_Bake_Stop,
    bake.BM_OT_Bake_Cancel,
    bake.BM_OT_Bake_Config,
    bake.BM_OT_BakeHistory_Remove,
    bake.BM_OT_BakeHistory_Rebake,
    bake.BM_OT_BakeHistory_Config,
)
