# ##### BEGIN GPL LICENSE BLOCK #####
#
# "BakeMaster" Add-on (3.0.0)
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


def get_uilist_rows(len_of_idprop, min_rows: int, max_rows: int):
    return min(max_rows, max(min_rows, len_of_idprop))


def get_active_bakejob_and_object(context):
    try:
        bakejob = context.scene.bakemaster.bakejobs[
                context.scene.bakemaster.bakejobs_active_index]
        object = bakejob.objects[bakejob.objects_active_index]
    except (IndexError, AttributeError):
        return None, None
    else:
        return bakejob, object


def are_object_props_drawable(bakejob, object):
    if bakejob is None or object is None:
        return False

    if any([object.nm_is_lc, object.hl_is_highpoly, object.hl_is_cage]):
        return False
    if object.nm_is_detached:
        return True
    if object.nm_is_uc:
        return object.nm_uc_is_global
    return not bakejob.objects[object.nm_uc_index].nm_uc_is_global


def is_mapsettings_active(object, map):
    uv_container = object
    if object.uv_use_unique_per_map:
        uv_container = map

    if uv_container.uv_bake_target == 'VERTEX_COLORS':
        if map.map_type != 'VERTEX_COLOR_LAYER':
            return False
        elif all([map.map_type == 'NORMAL',
                  map.map_normal_data == 'MULTIRES']):
            return False
        elif all([map.map_type == 'DISPLACEMENT',
                  map.map_displacement_data in ['HIGHPOLY', 'MULTIRES']]):
            return False
    if map.map_type == 'DECAL' and object.bake_save_internal:
        return False
    return True


def ui_draw_hl(layout, bakemaster, bakejob, object, hl_container,
               bpy_app_version):
    box = layout.box()
    box.use_property_split = True
    box.use_property_decorate = False

    # hl header
    header = box.row(align=True)
    header.use_property_split = False
    header.emboss = 'NONE'
    icon = 'TRIA_DOWN'
    if bakemaster.local_is_hl_panel_expanded:
        icon = 'TRIA_RIGHT'
    header.prop(bakemaster, 'local_is_hl_panel_expanded', text="",
                icon=icon)
    header.emboss = 'NORMAL'
    if object.hl_use_unique_per_map:
        header.label(text="Map High to Lowpoly")
    else:
        header.label(text="High to Lowpoly")
    BM_PT_HL_Presets.draw_panel_header(header)

    if not bakemaster.local_is_hl_panel_expanded:
        return

    # hl body
    split = box.split(factor=0.4)
    split.column()
    col = split.column()
    label = "Highpoly"
    if hl_container.hl_highpolies_len > 1:
        label = "Highpolies"
    col.label(text=label)
    row = col.column().row()
    rows = get_uilist_rows(hl_container.hl_highpolies_len, 1, 5)
    row.template_list('BM_UL_Table_of_Maps_Item_Highpoly', "",
                      hl_container, 'hl_highpolies', hl_container,
                      'hl_highpolies_active_index', rows=rows)
    col = row.column(align=True)
    col.operator(BM_OT_MAP_Highpoly_Table_Add.bl_idname,
                 text="", icon='ADD')
    col.operator(BM_OT_MAP_Highpoly_Table_Remove.bl_idname,
                 text="", icon='REMOVE')

    if hl_container.hl_highpolies_len == 0:
        return

    col = box.column(align=True)
    h_object_index = -1
    try:
        highpoly = hl_container.hl_highpolies[
                hl_container.hl_highpolies_active_index]
        h_object_index = highpoly.object_index
    except IndexError:
        pass
    if h_object_index != -1:
        col.prop(bakejob.objects[h_object_index], 'hl_is_decal')
    col.prop(object, 'hl_decals_use_separate_texset')
    if object.hl_decals_use_separate_texset:
        col.prop(object, 'hl_decals_separate_texset_prefix')

    # cage
    label = "Extrusion"
    if hl_container.hl_use_cage:
        label = "Cage Extrusion"
    col = box.column(align=True)
    col.prop(hl_container, 'hl_cage_type')
    if hl_container.hl_cage_type == 'SMART':
        col.prop(hl_container, 'hl_cage_extrusion', text="Extrusion")
    else:
        col.prop(hl_container, 'hl_cage_extrusion', text=label)
        if bpy_app_version >= (2, 90, 0):
            col.prop(hl_container, 'hl_max_ray_distance')
        col.prop(hl_container, 'hl_use_cage')
        if hl_container.hl_use_cage:
            col.prop(hl_container, 'hl_cage')


def ui_draw_uv(layout, bakemaster, object, uv_container):
    box = layout.box()
    box.use_property_split = True
    box.use_property_decorate = False

    # uv header
    header = box.row(align=True)
    header.use_property_split = False
    header.emboss = 'NONE'
    icon = 'TRIA_DOWN'
    if bakemaster.local_is_uv_panel_expanded:
        icon = 'TRIA_RIGHT'
    header.prop(bakemaster, 'local_is_uv_panel_expanded',
                text="", icon=icon)
    header.emboss = 'NORMAL'
    if object.uv_use_unique_per_map:
        header.label(text="Map UVs and Layers")
    else:
        header.label(text="UVs and Layers")
    BM_PT_UV_Presets.draw_panel_header(header)

    if not bakemaster.local_is_uv_panel_expanded:
        return

    # uv body
    col = box.column(align=True)
    col.prop(uv_container, 'uv_bake_data')
    col.prop(uv_container, 'uv_bake_target')
    if uv_container.uv_bake_target != 'IMAGE_TEXTURES':
        return

    col = box.column(align=True)
    col.prop(uv_container, 'uv_active_layer')
    col.prop(uv_container, 'uv_type')
    col.prop(uv_container, 'uv_snap_islands_to_pixels')
    col = box.column(align=True)
    if object.uv_active_layer != 'NONE_AUTO_CREATE':
        col.prop(object, 'uv_use_auto_unwrap')
    if any([object.uv_active_layer == 'NONE_AUTO_CREATE',
            object.uv_use_auto_unwrap]):
        col.prop(object, 'uv_auto_unwrap_angle_limit')
        col.prop(object, 'uv_auto_unwrap_island_margin')
        col.prop(object, 'uv_auto_unwrap_use_scale_to_bounds')


def ui_draw_out(layout, bakemaster, object, map):
    if object.out_use_unique_per_map:
        label = "Map Format"
        out_container = map
    else:
        label = "Format"
        out_container = object
    if out_container.uv_bake_target != 'VERTEX_COLORS':
        out_box = layout.box()
        out_box.use_property_split = True
        out_box.use_property_decorate = False

        # format header
        out_header = out_box.row()
        out_header.use_property_split = False
        out_header.emboss = 'NONE'
        icon = 'TRIA_DOWN'
        if bakemaster.is_format_panel_expanded:
            icon = 'TRIA_RIGHT'

            # format body
            out_box.prop(object, 'out_use_unique_per_map')
            col = out_box.column(align=True)
            col.prop(out_container, 'out_file_format')
            if out_container.out_file_format == 'PSD':
                col.prop(out_container, 'out_psd_include')
            elif out_container.out_file_format == 'OPEN_EXR':
                col.prop(out_container, 'out_exr_codec')
            elif out_container.out_file_format == 'PNG':
                col.prop(out_container, 'out_compression')
            col = out_box.column(align=True)
            col.prop(out_container, 'out_res', text="Resolution")
            if out_container.out_res == 'CUSTOM':
                col.prop(out_container, 'out_res_height')
                col.prop(out_container, 'out_res_width')
                split = col.split(factor=0.4)
                split.column()
                col = split.column()
                col.operator(BM_OT_ITEM_and_MAP_Format_MatchResolution.bl_idname,
                             icon='FULLSCREEN_ENTER')
            elif out_container.out_res == 'TEXEL':
                col.prop(out_container, 'out_texel_density_value')
                col.prop(out_container, 'out_texel_density_match')
            col = out_box.column(align=True)
            if bpy.app.version >= (3, 1, 0):
                col.prop(out_container, 'out_margin_type')
            col.prop(out_container, 'out_margin')
            col = out_box.column(align=True)
            col.prop(out_container, 'out_use_32bit')
            col.prop(out_container, 'out_use_alpha')
            col.prop(out_container, 'out_use_transbg')
            if out_container.uv_type == 'TILED':
                col = out_box.column(align=True)
                col.prop(out_container, 'out_udim_start_tile',
                         text="Start Tile")
                col.prop(out_container, 'out_udim_end_tile',
                         text="End Tile")
            out_box.prop(out_container, 'out_super_sampling_aa')
            col = out_box.column(align=True)
            col.prop(out_container, 'out_use_adaptive_sampling')
            if out_container.out_use_adaptive_sampling:
                col.prop(out_container, 'out_adaptive_threshold')
                col.prop(out_container, 'out_samples',
                         text="Bake Max Samples")
                col.prop(out_container, 'out_min_samples')
            else:
                col.prop(out_container, 'out_samples')
            col = out_box.column(align=True)
            col.prop(out_container, 'out_use_denoise')
            col.prop(out_container, 'out_use_scene_color_management')
            col.active = not object.bake_save_internal

        out_header.prop(bakemaster, 'is_format_panel_expanded', text="",
                        icon=icon)
        out_header.emboss = 'NORMAL'
        out_header.label(text=label)
        BM_PT_OUT_Presets.draw_panel_header(out_header)


def ui_draw_mapsettings_PASS(context, col, row_mapprev, object, map,
                             bpy_app_version):
    col.prop(map, 'map_pass_type')


def ui_draw_mapsettings_DECAL(context, col, row_mapprev, object, map,
                              bpy_app_version):
    col.prop(map, 'map_decal_pass_type')
    if map.map_decal_pass_type != 'NORMAL':
        col.prop(map, 'map_decal_height_opacity_invert')
    else:
        col.prop(map, 'map_decal_normal_preset')
        if map.map_decal_normal_preset == 'CUSTOM':
            sub = col.column(align=True)
            sub.prop(map, 'map_decal_normal_custom_preset')
            if map.map_decal_normal_custom_preset == 'CUSTOM':
                sub.prop(map, 'map_decal_normal_r', text="Swizzle R")
                sub.prop(map, 'map_decal_normal_g', text="G")
                sub.prop(map, 'map_decal_normal_b', text="B")


def ui_draw_mapsettings_VERTEX_COLOR_LAYER(context, col, row_mapprev, object,
                                           map, bpy_app_version):
    col.prop(map, 'map_vertexcolor_layer')


def ui_draw_mapsettings_C_NORMAL(context, col, row_mapprev, object, map,
                                 bpy_app_version):
    col.prop(map, 'map_normal_space', text="Space")
    sub = col.column(align=True)
    sub.prop(map, 'map_normal_r', text="Swizzle R")
    sub.prop(map, 'map_normal_g', text="G")
    sub.prop(map, 'map_normal_b', text="B")


def ui_draw_mapsettings_C_COMBINED(context, col, row_mapprev, object, map,
                                   bpy_app_version):
    row = col.row(align=True)
    row.use_property_split = False
    row.prop(map, 'map_cycles_use_pass_direct', toggle=True)
    row.prop(map, 'map_cycles_use_pass_indirect', toggle=True)
    flow = col.grid_flow(row_major=False, columns=0,
                         even_columns=False, even_rows=False,
                         align=True)
    flow.active = any([map.map_cycles_use_pass_direct,
                       map.map_cycles_use_pass_indirect])
    flow.prop(map, 'map_cycles_use_pass_diffuse')
    flow.prop(map, 'map_cycles_use_pass_glossy')
    flow.prop(map, 'map_cycles_use_pass_transmission')
    if bpy_app_version < (3, 0, 0):
        flow.prop(map, 'map_cycles_use_pass_ambient_occlusion')
    flow.prop(map, 'map_cycles_use_pass_emit')


def ui_draw_mapsettings_C_DIFFUSE_GLOSSY_TRANSMISSION(context, col,
                                                      row_mapprev, object,
                                                      map,
                                                      bpy_app_version):
    row = col.row(align=True)
    row.use_property_split = False
    row.prop(map, 'map_cycles_use_pass_direct', toggle=True)
    row.prop(map, 'map_cycles_use_pass_indirect', toggle=True)
    row.prop(map, 'map_cycles_use_pass_color', toggle=True)


def ui_draw_mapsettings_NORMAL(context, col, row_mapprev, object, map,
                               bpy_app_version):
    if map.map_normal_data != 'MATERIAL' and row_mapprev is not None:
        row_mapprev.active = False
    col.prop(map, 'map_normal_data')
    col.prop(map, 'map_normal_space')
    col.prop(map, 'map_normal_preset')
    if map.map_normal_preset == 'CUSTOM':
        sub = col.column(align=True)
        sub.prop(map, 'map_normal_custom_preset')
        if map.map_normal_custom_preset == 'CUSTOM':
            sub.prop(map, 'map_normal_r', text="Swizzle R")
            sub.prop(map, 'map_normal_g', text="G")
            sub.prop(map, 'map_normal_b', text="B")
    if map.map_normal_data == 'MULTIRES':
        col.prop(map, 'map_displacement_subdiv_levels')
        face_count = BM_MAO_PROPS_map_get_subdivided_face_count(
                context, object, map)
        col.label(text="Face count while baking: " + str(face_count))


def ui_draw_mapsettings_DISPLACEMENT(context, col, row_mapprev, object, map,
                                     bpy_app_version):
    if map.map_normal_data != 'MATERIAL' and row_mapprev is not None:
        row_mapprev.active = False
    col.prop(map, 'map_displacement_data')
    col.prop(map, 'map_displacement_result')
    if map.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
        col.prop(map, 'map_displacement_subdiv_levels')
        face_count = BM_MAO_PROPS_map_get_subdivided_face_count(
                context, object, map)
        col.label(text="Face count while baking: " + str(face_count))
        col.prop(map, 'map_displacement_lowresmesh')


def ui_draw_mapsettings_VDISPLACEMENT(context, col, row_mapprev, object, map,
                                      bpy_app_version):
    col.prop(map, 'map_vector_displacement_use_negative')
    col.prop(map, 'map_vector_displacement_result')


def ui_draw_mapsettings_AO(context, col, row_mapprev, object, map,
                           bpy_app_version):
    if map.map_AO_use_default is False:
        col.prop(map, 'map_ao_samples', slider=True)
        col.prop(map, 'map_ao_distance')
        sub = col.column(align=True)
        sub.prop(map, 'map_ao_black_point', slider=True)
        sub.prop(map, 'map_ao_white_point', slider=True)
        sub = col.column(align=True)
        sub.prop(map, 'map_ao_brightness')
        sub.prop(map, 'map_ao_contrast')
        sub.prop(map, 'map_ao_opacity', slider=True)
        sub = col.column()
        sub.prop(map, 'map_ao_use_local')
        sub.prop(map, 'map_ao_use_invert', slider=True)


def ui_draw_mapsettings_CAVITY(context, col, row_mapprev, object, map,
                               bpy_app_version):
    if map.map_CAVITY_use_default is False:
        sub = col.column(align=True)
        sub.prop(map, 'map_cavity_black_point', slider=True)
        sub.prop(map, 'map_cavity_white_point', slider=True)
        sub = col.column()
        sub.prop(map, 'map_cavity_power')
        sub.prop(map, 'map_cavity_use_invert', slider=True)


def ui_draw_mapsettings_CURVATURE(context, col, row_mapprev, object, map,
                                  bpy_app_version):
    if map.map_CURVATURE_use_default is False:
        col.prop(map, 'map_curv_samples', slider=True)
        col.prop(map, 'map_curv_radius')
        sub = col.column(align=True)
        sub.prop(map, 'map_curv_black_point', slider=True)
        sub.prop(map, 'map_curv_mid_point', slider=True)
        sub.prop(map, 'map_curv_white_point', slider=True)
        sub = col.column()
        sub.prop(map, 'map_curv_body_gamma')


def ui_draw_mapsettings_THICKNESS(context, col, row_mapprev, object, map,
                                  bpy_app_version):
    if map.map_THICKNESS_use_default is False:
        col.prop(map, 'map_thick_samples', slider=True)
        col.prop(map, 'map_thick_distance')
        sub = col.column(align=True)
        sub.prop(map, 'map_thick_black_point', slider=True)
        sub.prop(map, 'map_thick_white_point', slider=True)
        sub = col.column(align=True)
        sub.prop(map, 'map_thick_brightness')
        sub.prop(map, 'map_thick_contrast')
        sub = col.column()
        sub.prop(map, 'map_thick_use_invert', slider=True)


def ui_draw_mapsettings_ID(context, col, row_mapprev, object, map,
                           bpy_app_version):
    col.prop(map, 'map_matid_data')
    if map.map_matid_data == 'VERTEX_GROUPS':
        col.prop(map, 'map_matid_vertex_groups_name_contains')
    col.prop(map, 'map_matid_algorithm')
    col.prop(map, 'map_matid_jilter')


def ui_draw_mapsettings_MASK(context, col, row_mapprev, object, map,
                             bpy_app_version):
    col.prop(map, 'map_mask_data')
    if map.map_mask_data == 'VERTEX_GROUPS':
        col.prop(map, 'map_mask_vertex_groups_name_contains')
    elif map.map_mask_data == 'MATERIALS':
        col.prop(map, 'map_mask_materials_name_contains')
    col.prop(map, 'map_mask_color1')
    col.prop(map, 'map_mask_color2')
    col.prop(map, 'map_mask_use_invert', slider=True)


def ui_draw_mapsettings_XYZMASK(context, col, row_mapprev, object, map,
                                bpy_app_version):
    sub = col.column(align=True)
    sub.prop(map, 'map_xyzmask_use_x')
    sub.prop(map, 'map_xyzmask_use_y')
    sub.prop(map, 'map_xyzmask_use_z')
    if not map.map_XYZMASK_use_default:
        sub = col.column(align=True)
        sub.prop(map, 'map_xyzmask_coverage')
        sub.prop(map, 'map_xyzmask_saturation')
        sub = col.column(align=True)
        sub.prop(map, 'map_xyzmask_opacity', slider=True)
        sub.prop(map, 'map_xyzmask_use_invert', slider=True)


def ui_draw_mapsettings_GRADIENT(context, col, row_mapprev, object, map,
                                 bpy_app_version):
    col.prop(map, 'map_gmask_type')
    sub = col.column(align=True)
    sub.prop(map, 'map_gmask_location_x')
    sub.prop(map, 'map_gmask_location_y')
    sub.prop(map, 'map_gmask_location_z')
    sub = col.column(align=True)
    sub.prop(map, 'map_gmask_rotation_x')
    sub.prop(map, 'map_gmask_rotation_y')
    sub.prop(map, 'map_gmask_rotation_z')
    if not map.map_GRADIENT_use_default:
        sub = col.column(align=True)
        sub.prop(map, 'map_gmask_scale_x')
        sub.prop(map, 'map_gmask_scale_y')
        sub.prop(map, 'map_gmask_scale_z')
        sub = col.column(align=True)
        sub.prop(map, 'map_gmask_coverage')
        sub.prop(map, 'map_gmask_contrast')
        sub = col.column(align=True)
        sub.prop(map, 'map_gmask_saturation')
        sub.prop(map, 'map_gmask_opacity', slider=True)
        sub.prop(map, 'map_gmask_use_invert', slider=True)


def ui_draw_mapsettings_EDGEMASK(context, col, row_mapprev, object, map,
                                 bpy_app_version):
    if map.map_EDGE_use_default is False:
        col.prop(map, 'map_edgemask_samples', slider=True)
        col.prop(map, 'map_edgemask_radius')
        sub = col.column(align=True)
        sub.prop(map, 'map_edgemask_edge_contrast')
        sub.prop(map, 'map_edgemask_body_contrast')
        sub = col.column()
        sub.prop(map, 'map_edgemask_use_invert')


def ui_draw_mapsettings_WIREFRAME(context, col, row_mapprev, object, map,
                                  bpy_app_version):
    col.prop(map, 'map_wireframemask_line_thickness')
    col.prop(map, 'map_wireframemask_use_invert')


def ui_draw_mapsettings(context, col, row_mapprev, object, map,
                        bpy_app_version):
    methods = {
        'PASS': ui_draw_mapsettings_PASS,
        'DECAL': ui_draw_mapsettings_DECAL,
        'VERTEX_COLOR_LAYER': ui_draw_mapsettings_VERTEX_COLOR_LAYER,
        'C_NORMAL': ui_draw_mapsettings_C_NORMAL,
        'C_COMBINED': ui_draw_mapsettings_C_COMBINED,
        'C_DIFFUSE': ui_draw_mapsettings_C_DIFFUSE_GLOSSY_TRANSMISSION,
        'C_GLOSSY': ui_draw_mapsettings_C_DIFFUSE_GLOSSY_TRANSMISSION,
        'C_TRANSMISSION': ui_draw_mapsettings_C_DIFFUSE_GLOSSY_TRANSMISSION,
        'NORMAL': ui_draw_mapsettings_NORMAL,
        'DISPLACEMENT': ui_draw_mapsettings_DISPLACEMENT,
        'VECTOR_DISPLACEMENT': ui_draw_mapsettings_VDISPLACEMENT,
        'AO': ui_draw_mapsettings_AO,
        'CAVITY': ui_draw_mapsettings_CAVITY,
        'CURVATURE': ui_draw_mapsettings_CURVATURE,
        'THICKNESS': ui_draw_mapsettings_THICKNESS,
        'ID': ui_draw_mapsettings_ID,
        'MASK': ui_draw_mapsettings_MASK,
        'XYZMASK': ui_draw_mapsettings_XYZMASK,
        'GRADIENT': ui_draw_mapsettings_GRADIENT,
        'EDGE': ui_draw_mapsettings_EDGEMASK,
        'WIREFRAME': ui_draw_mapsettings_WIREFRAME,
    }
    methods[map.map_type](context, col, row_mapprev, object, map,
                          bpy_app_version)


def BM_UTILS_Highpoly_get_items(self, self_object, objects, include: list):
    items = []
    added = []

    for object in objects:
        # add current chosen high
        if all([any([object.index == self.object_index,
                     object.name in include]), object.index not in added]):
            items.append((str(object.index), object.name,
                          "Highpoly Object"))
            added.append(object.index)
            continue

        # skip the item itself and all cages, lows, highs already
        if any([any([object.hl_is_cage, object.hl_is_lowpoly,
                     object.hl_is_highpoly]),
                object.index == self.object_index]):
            continue

        if any([all([objects[object.nm_lc_index].nm_is_hl_lc,
                object.nm_uni_index == self_object.nm_uni_index]),
                object.nm_is_detached == self_object.nm_is_detached]):
            items.append((str(object.index), object.name,
                          "Highpoly Object"))
            added.append(object.index)

    if len(items) == 0:
        items = [('NONE', "None",
                  "No highpoly available within the Bake Job's Objects")]
    return items


def BM_UTILS_CageHighpoly_get_include(self_object):
    include_cages = []
    include_highpolies = []
    skip_highpolies = []
    self_map = self_object.maps[self_object.maps_active_index]

    if self_object.hl_use_unique_per_map:
        return include_cages, include_highpolies

    for map in self_object.maps:
        if all([map.hl_use_cage, map.hl_cage_object_index != -1,
                map.hl_cage_name_old not in include_cages,
                map.index != self_map.index]):
            include_cages.append(map.hl_cage_name_old)
        for highpoly in map.hl_highpolies:
            if highpoly.object_index == -1:
                continue
            if map.index == self_map.index:
                skip_highpolies.append(highpoly.name_old)
                continue
            if all([highpoly.name_old not in include_highpolies,
                    highpoly.name_old not in skip_highpolies]):
                include_highpolies.append(highpoly.name_old)
    return include_cages, include_highpolies


def BM_UTILS_Highpoly_Items(self, context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[self.bakejob_index].objects
    self_object = objects[self.object_index]
    _, include = BM_UTILS_CageHighpoly_get_include(self_object)
    return BM_UTILS_Highpoly_get_items(self, self_object, objects, include)


def mark_highpolies(objects, data):
    for highpoly in data.hl_highpolies:
        if highpoly.object_index == -1:
            continue
        objects[highpoly.object_index].hl_is_highpoly = True


def BM_UTILS_Highpoly_EnsureHighpolyMarked(objects):
    for object in objects:
        if object.hl_use_unique_per_map is False:
            mark_highpolies(objects, object)
            continue
        for map in object.maps:
            mark_highpolies(objects, map)


def BM_UTILS_Highpoly_Update(self, context):
    if self.name == self.name_old:
        return

    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[self.bakejob_index].objects
    update_name = False

    if self.name_old == 'NONE':
        update_name = True
    self.name_old = self.name
    if self.object_index != -1:
        objects[self.object_index].hl_is_highpoly = False
        self.object_index = int(self.name_old)
        objects[self.object_index].hl_is_highpoly = True
    self.object_include = objects[self.object_index].name
    if update_name:
        self.name = self.name_old

    BM_UTILS_Highpoly_EnsureHighpolyMarked(objects)


def BM_UTILS_Highpoly_UpdateOnRemove(self, context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[self.bakejob_index].objects
    if self.object_index != -1:
        objects[self.object_index].hl_is_highpoly = False


def BM_UTILS_Highpoly_unset_none(data):
    to_remove = []
    highpoly_index = 0
    for highpoly in data.hl_highpolies:
        if highpoly.object_index == -1:
            to_remove.append(highpoly.index)
            continue
        highpoly.index = highpoly_index
        highpoly_index += 1

    for index in reversed(to_remove):
        data.hl_highpolies.remove(index)
    data.hl_highpoles_active_index = highpoly_index - 1


def BM_UTILS_Highpoly_UpdateOnAddOT(context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[bakemaster.bakejobs_active_index].objects

    for object in objects:
        if object.hl_use_unique_per_map is False:
            BM_UTILS_Highpoly_unset_none(object)
            object.hl_is_lowpoly = len(object.hl_highpoles) != 0
            continue

        len_of_highpolies = 0
        for map in object.maps:
            BM_UTILS_Highpoly_unset_none(map)
            len_of_highpolies += len(map.hl_highpolies)
        object.hl_is_lowpoly = len_of_highpolies != 0


def reset_highpoly_props(data, objects, from_index, to_index):
    for highpoly in data.hl_highpolies:
        if highpoly.object_index == from_index:
            highpoly.object_index = to_index
        elif highpoly.object_index == to_index:
            highpoly.object_index = from_index
        if highpoly.self_object_index == from_index:
            highpoly.self_object_index = to_index
        elif highpoly.self_object_index == to_index:
            highpoly.self_object_index = from_index
        if highpoly.object_index != -1:
            objects[highpoly.object_index].hl_is_highpoly = True
        try:
            highpoly.name_old = str(highpoly.object_index)
            highpoly.name = str(highpoly.object_index)
        except (ValueError, TypeError):
            pass


def BM_UTILS_Highpoly_UpdateOnMoveOT(context, from_index=-2, to_index=-2):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[bakemaster.bakejobs_active_index].objects

    for object in objects:
        if object.hl_use_unique_per_map is False:
            reset_highpoly_props(object, objects, from_index, to_index)
            continue
        for map in object.maps:
            reset_highpoly_props(map, objects, from_index, to_index)
            continue
        for map in object.maps:
            reset_highpoly_props(map)


def getnew_highpoly_object_index(self, objects):
    for object in objects:
        if object.name == self.object_include and not any([object.nm_is_lc,
                                                           object.nm_is_uc]):
            self.self_object_index = object.index
            return object.index
    return -1


def updateHighpolyProps_and_removeNone(data, objects):
    to_remove = []
    highpoly_index = 0
    for highpoly in data.hl_highpolies:
        new_index = getnew_highpoly_object_index(highpoly, objects)
        highpoly.object_index = new_index
        try:
            highpoly.name_old = str(highpoly.object_index)
            highpoly.name = str(highpoly.object_index)
        except (ValueError, TypeError):
            pass

        if highpoly.object_index == -1:
            to_remove.append(highpoly.index)
        else:
            objects[highpoly.object_index].hl_is_highpoly = True
            highpoly.index = highpoly_index
            highpoly_index += 1

    for highpoly_index in reversed(to_remove):
        data.hl_highpolies.remove(highpoly_index)
    if data.hl_highpolies_active_index >= highpoly_index - 1:
        data.hl_highpolies_active_index = highpoly_index - 1
    return not highpoly_index == 0


def BM_UTILS_Highpoly_UpdateAfterRemoveOT(context):
    bakemaster = context.scene.bakemaster
    objects = bakemaster.bakejobs[bakemaster.bakejobs_active_index].objects

    for object in objects:
        leave_lowpoly = False
        if object.hl_use_unique_per_map is False:
            leave_lowpoly = updateHighpolyProps_and_removeNone(object, objects)
            continue
        for map in object.maps:
            leave_lowpoly = updateHighpolyProps_and_removeNone(map, objects)
        object.hl_is_lowpoly = leave_lowpoly


def remove_highpolies(context, data):
    to_remove = []
    for highpoly in data.hl_highpolies:
        BM_UTILS_Highpoly_UpdateOnRemove(highpoly, context)
        to_remove.append(highpoly.index)
    for index in reversed(to_remove):
        data.hl_highpolies.remove(index)


def set_removed_highpoly_to_none(data, removed_index):
    for highpoly in data.hl_highpolies:
        if highpoly.object_index != removed_index:
            continue
        highpoly.object_index = -1
        highpoly.name_old = 'NONE'
        highpoly.object_include = "NONE"


def BM_UTILS_Highpoly_UpdateOnRemoveOT(context, removed_index, type: str):
    bakemaster = context.scene.bakemaster
    bakejob = bakemaster.bakejobs[bakemaster.bakejobs_active_index]
    objects = bakejob.objects

    if type == 'OBJECT':
        object = objects[removed_index]
        if object.hl_is_highpoly is False:
            if object.hl_use_unique_per_map is False:
                remove_highpolies(context, object)
                return
            for map in object.maps:
                remove_highpolies(context, map)
        for object in objects:
            if object.hl_use_unique_per_map is False:
                set_removed_highpoly_to_none(object, removed_index)
                continue
            for map in object.maps:
                set_removed_highpoly_to_none(map, removed_index)
    elif type == 'MAP':
        self_object = objects[bakejob.objects_active_index]
        if self_object.hl_use_unique_per_map is False:
            return
        map = self_object.maps[removed_index]
        remove_highpolies(context, map)
