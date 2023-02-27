# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (version 3.0.0)
# Copyright (C) 2023 Kiril Strezikozin aka kemplerart
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

from bpy.types import (
    PropertyGroup,
)
from bpy.props import (
    CollectionProperty,
    IntProperty,
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
)


class BM_PROPS_Local_object(PropertyGroup):


class BM_PROPS_Local_redolastaction_object(PropertyGroup):
    name: StringProperty(
        name="Object name",
        default="")

    bm_object_index: IntProperty(default=-1)

    use_affect: BoolProperty(
        name="Apply",
        description="Apply property for this object",
        default=True)


class BM_PROPS_Local_redolastaction_map(PropertyGroup):
    name: StringProperty(
        name="Map name",
        default="")

    bm_object_index: IntProperty(default=-1)

    bm_map_index: IntProperty(default=-1)

    use_affect: BoolProperty(
        name="Apply",
        description="Apply property for this map",
        default=True)


class BM_PROPS_Local_bakegroup(PropertyGroup):
    name: StringProperty(
        name="Object name",
        default="")

    is_lowpoly: BoolProperty(
        name="Inlcude as Lowpoly",
        description="Include this object as a regular or Lowpoly Object in new Artificial Container",  # noqa: E501
        default=False,
        update=BM_CAUC_Object_use_include_Update)

    is_highpoly: BoolProperty(
        name="Include as Highpoly",
        description="Include this object as a Highpoly Object in new Artificial Container",  # noqa: E501
        default=False,
        update=BM_CAUC_Object_is_highpoly_Update)

    is_cage: BoolProperty(
        name="Include as Cage",
        description="Include this object as a Highpoly Object in new Artificial Container",  # noqa: E501
        default=False,
        update=BM_CAUC_Object_is_cage_Update)


class BM_PROPS_Local_matchres(PropertyGroup):
    image_name: StringProperty(
        name="Image Texture name",
        default="Image")

    socket_and_node_name: StringProperty(
        name="Plugged into",
        default="*Not plugged*")

    image_res: StringProperty(
        name="Resolution",
        default="")

    image_height: IntProperty(default=1)
    image_width: IntProperty(default=1)


class BM_PROPS_Local_texset_object_subitems(PropertyGroup):
    name: StringProperty(
        name="Container's Lowpoly Object")

    index: IntProperty(default=-1)

    texset_object_index: IntProperty(default=-1)

    texset_index: IntProperty(default=-1)

    object_index: IntProperty(default=-1)

    use: BoolProperty(
        name="Include/Exclude from Texture Set",
        description="Include/Exclude Container's Lowpoly Object from the current Texture Set",  # noqa: E501
        default=True)


class BM_PROPS_Local_texset_object(PropertyGroup):
    name: EnumProperty(
        name="Choose Object",
        description="Object from the current Bake Job Objects to inlcude in the current Texture Set.\nIf Container's chosen, all its lowpoly objects will be added to the Texture Set",  # noqa: E501
        items=BM_TEXSET_OBJECT_PROPS_global_object_name_Items,
        update=BM_TEXSET_OBJECT_PROPS_global_object_name_Update)

    index: IntProperty(default=-1)

    texset_index: IntProperty(default=-1)

    object_index: IntProperty(default=-1)

    name_old: StringProperty(default='-1')

    name_include: StringProperty(default="")

    subitems: CollectionProperty(type=BM_PROPS_Local_texset_object_subitems)

    subitems_active_index: IntProperty(name="Container's Lowpoly Object")

    subitems_len: IntProperty(default=0)


class BM_PROPS_Local_texset(PropertyGroup):
    name: StringProperty(
            name="Texture Set Name.\nTexture Set is a set of objects that share the same image texture file for each map",  # noqa: E501
        default="Texture Set")

    index: IntProperty(default=-1)

    syncer_use: BoolProperty(
        name="",
        description="Enable one object to dictate maps, channel packs, and bake settings for all others in the current texture set",  # noqa: E501
        default=False)

    syncer_object_name: EnumProperty(
        name="Sync with",
        description="Choose an object from the ones in the current texture set",  # noqa: E501
        items=BM_TEXSET_OBJECT_PROPS_syncer_Items)

    syncer_use_dictate_bake_output: BoolProperty(
        name="Sync Bake Output Settings",
        description="Channel packs and maps settings are synced with enabling 'Sync with', check this option to sync bake settings as well",  # noqa: E501
        default=True)

    uvp_use_uv_repack: BoolProperty(
        name="UV Repack",
        description="Enable UV Repacking for Texture Set Objects.\nWarning: if Objects have materials that depend on UV Layout, enabling this option might change the result of these materials",  # noqa: E501
        default=False)

    uvp_use_islands_rotate: BoolProperty(
        name="Rotate",
        description="Rotate islands for best fit",
        default=False)

    uvp_pack_margin: FloatProperty(
        name="Margin",
        description="Space between packed islands",
        default=0.01,
        min=0.0,
        max=1.0)

    uvp_use_average_islands_scale: BoolProperty(
        name="Average Islands Scale",
        description="Average the size of separate UV islands, based on their area in 3D space",  # noqa: E501
        default=True)

    naming: EnumProperty(
        name="Naming",
        description="Choose output Image texture naming format",
        default='TEXSET_NAME',
        items=[('EACH_OBJNAME', "Each Object Name", "Include each texture set object name in the output texture set image"),  # noqa: E501
               ('TEXSET_INDEX', "Texture Set Index", "Name output texture set image in the format: TextureSet_index"),  # noqa: E501
               ('TEXSET_NAME', "Texture Set Name", "Output texture name will be as Texture Set name")])  # noqa: E501

    texset_objects: CollectionProperty(type=BM_PROPS_Local_texset_object)

    texset_objects_active_index: IntProperty(
        name="Object in the Texture Set",
        default=0)

    texset_objects_len: IntProperty(default=0)


class BM_PROPS_Local_bakejob(PropertyGroup):
    # Bake Job Props

    name: StringProperty(
        name="Bake Job",
        description="Double click to rename",
        default="Bake Job")

    index: IntProperty(default=-1)

    # TODO: Redo Last Action update
    use_bake: BoolProperty(
        name="Include/Exclude Bake Job from baking",
        default=True)

    objects: CollectionProperty(type=BM_PROPS_Local_object)

    objects_active_index: IntProperty(
        name="Mesh Object to bake maps for",
        default=0,
        update=BM_ActiveIndexUpdate)

    objects_len: IntProperty(default=0)

    use_name_matching: BoolProperty(
        name="Toggle Name Matching",
        description="If on, High, Lowpoly, and Cage objects will be grouped by their matched names.\nProperties like Highpoly object and Cage will be set automatically if possible, maps and other settings can be configured by the top-parent container",  # noqa: E501
        default=False,
        update=BM_SCENE_PROPS_global_use_name_matching_Update)

    use_save_log: BoolProperty(
        name="Save Log",
        description="Save log of time used to bake each map and a short summary of all baked maps for all baked objects into a .txt file",  # noqa: E501
        default=False)

    use_bake_overwrite: BoolProperty(
        name="Overwrite",
        description="If checked, previous bake result will be erased and overwritten by the new one",  # noqa: E501
        default=False)

    texsets: CollectionProperty(type=BM_PROPS_Local_texset)

    texsets_active_index: IntProperty(
        name="Texture Set.\nTexture Set is a set of objects that share the same image texture file for each map",  # noqa: E501
        default=-1)

    texsets_len: IntProperty(default=0)


class BM_PROPS_Global(PropertyGroup):
    # Bake Jobs Props

    bakejobs: CollectionProperty(type=BM_PROPS_Local_bakejob)

    bakejobs_active_index: IntProperty(
        name="Bake Job",
        description="Active Bake Job",
        default=-1)

    bakejobs_len: IntProperty(default=0)

    # Addon Preferences Props

    prefs_use_show_help: BoolProperty(
        name="Show Help buttons",
        description="Allow help buttons in panels' headers",
        default=True)

    prefs_use_pipeline: BoolProperty(
        name="Bake Pipeline",
        description="Enable/disable Bake Pipeline settings (Bake Configs save/load, Atlas Management, Asset Matching)",  # noqa: E501
        default=False)

    prefs_use_hide_notbaked: BoolProperty(
        name="Hide not baked",
        description="Hide all Objects in the scene that won't be baked, as such they won't affect it",  # noqa: E501
        default=True)

    prefs_texsets_matchmaps_type: EnumProperty(
        name="Maps Match type",
        description="Determine map matching for Texture Sets aka how to source maps that should be baked onto the same image texture",  # noqa: E501
        default='MAP_PREFIX',
        items=[('MAP_PREFIX', "Maps Prefixes", "Maps with identical prefixes will be baked onto the same image file"),  # noqa: E501
               ('MAP_TYPE', "Maps Types", "Maps of identical types will be baked onto the same image file"),  # noqa: E501
               ('MAP_PREFIX_AND_TYPE', "Both Type and Prefix", "Maps with identical prefixes will be baked onto the same image file.\nIf no identical prefixes found, BakeMaster will try to match maps of the same type")])  # noqa: E501

    prefs_texsets_use_matching: BoolProperty(
        name="Match TexSets",
        description="When enabling Name Matching, if this option is checked, Objects with TexSet Tag in their names will be auto matched and put into Texture Sets",  # noqa: E501
        default=True)

    prefs_lowpoly_tag: StringProperty(
        name="Lowpoly Tag",
        description="What keyword to search for in Object name to determine it's a Lowpoly Object",  # noqa: E501
        default="low")

    prefs_highpoly_tag: StringProperty(
        name="Highpoly Tag",
        description="What keyword to search for in Object name to determine it's a Highpoly Object",  # noqa: E501
        default="high")

    prefs_cage_tag: StringProperty(
        name="Cage Tag",
        description="What keyword to search for in Object name to determine it's a Cage Object",  # noqa: E501
        default="cage")

    prefs_decal_tag: StringProperty(
        name="Decal Tag",
        description="What keyword to search for in Object name to determine it's a Decal Object",  # noqa: E501
        default="decal")

    prefs_texset_tag: StringProperty(
        name="TexSet Tag",
        description="What keyword to search for in Object name to determine it should be put into Texture Set (If Match TexSets enabled)",  # noqa: E501
        default="texset")

    prefs_bake_uv_layer_tag: StringProperty(
        name="UVMap Tag",
        description="What UVMap name should contain for BakeMaster to higher up its priority in Active UV Layer items",  # noqa: E501
        default="bake")

    # Redo Last Action Props

    redolastaction_prop: StringProperty(default="")
    redolastaction_prop_name: StringProperty(default="")
    redolastaction_prop_value: StringProperty(default="")
    redolastaction_prop_type: StringProperty(default="")
    redolastaction_prop_is_map: BoolProperty(default=False)

    redolastaction_objects: CollectionProperty(type=BM_PROPS_Local_redolastaction_object)  # noqa: E501

    redolastaction_objects_active_index: IntProperty(
        name="Object",
        default=-1)

    redolastaction_maps: CollectionProperty(type=BM_PROPS_Local_redolastaction_map)  # noqa: E501

    redolastaction_maps_active_index: IntProperty(
        name="Map",
        default=-1)

    redolastaction_affect_objects: BoolProperty(
        name="Affect Objects",
        description="Apply property to all maps of chosen objects",
        default=False)

    # Bake Group Props
    bakegroup_objects: CollectionProperty(type=BM_PROPS_Local_bakegroup)

    bakegroup_objects_active_index: IntProperty(
        name="Detached Object",
        default=-1)

    # Math Res Props
    matchres_items: CollectionProperty(type=BM_PROPS_Local_matchres)

    matchres_items_active_index: IntProperty(
        name="Resolution, Image name, Plugged into",
        default=0)

    # Panels UI Props

    is_decal_panel_expanded: BoolProperty(
        name="Expand/Collapse Decal Settings panel",
        default=False)

    is_hl_panel_expanded: BoolProperty(
        name="Expand/Collapse High to Lowpoly Settings panel",
        default=False)

    is_uv_panel_expanded: BoolProperty(
        name="Expand/Collapse UV Settings panel",
        default=False)

    is_matgroups_panel_expanded: BoolProperty(
        name="Expand/Collapse Material Groups panel",
        default=False)

    is_csh_panel_expanded: BoolProperty(
        name="Expand/Collapse Shading Settings panel",
        default=False)

    is_format_panel_expanded: BoolProperty(
        name="Expand/Collapse Format Settings panel",
        default=False)

    is_chnlpack_panel_expanded: BoolProperty(
        name="Expand/Collapse Channel Packing panel",
        default=False)

    is_bakeoutput_panel_expanded: BoolProperty(
        name="Expand/Collapse Bake Output Settings panel",
        default=False)

    is_map_hl_panel_expanded: BoolProperty(
        name="Expand/Collapse High to Lowpoly Settings panel",
        default=False)

    is_map_uv_panel_expanded: BoolProperty(
        name="Expand/Collapse UV Settings panel",
        default=False)

    # Idle Bake Props

    use_bakemaster_reset: BoolProperty(
        name="Reset BakeMaster",
        description="Remove baked objects from BakeMaster Table of Objects after the bake",  # noqa: E501
        default=False)

    bake_instruction: StringProperty(
        name="Bake Operator Instruction",
        default="Short Bake Instruction",
        description=BM_Labels.OPERATOR_ITEM_BAKE_FULL_DESCRIPTION)

    is_bake_available: BoolProperty(
        default=True)
