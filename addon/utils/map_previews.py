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
from .getters import *

# Map Preview Configurators
def Map_MapPreview_CustomNodes_Update(self, context, map_tag):
    object_item_full = BM_Object_Get(self, context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    if getattr(BM_Map_Get(self, object_item), "map_%s_use_preview" % map_tag) is False:
        return
    map = BM_Map_Get(self, object_item)

    # collecting objects for which update bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return

    highpolies = map.hl_highpoly_table if object_item.hl_use_unique_per_map else object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])

    # which bm_nodes' values will change
    nodes_names_data = {
        'AO' : [
            'BM_AmbientOcclusion',
            'BM_ValToRGB',
            'BM_MixRGB',
            'BM_BrightContrast',
            'BM_Invert',
        ],
        'CAVITY' : [
            'BM_ValToRGB',
            'BM_Math',
            'BM_Invert',
        ],
        'CURVATURE' : [
            'BM_Value',
            'BM_AmbientOcclusion',
            'BM_AmbientOcclusion.001',
            'BM_ValToRGB',
            'BM_Gamma',
        ],
        'THICKNESS' : [
            'BM_AmbientOcclusion',
            'BM_MapRange',
            'BM_ValToRGB',
            'BM_Invert',
        ],
        'XYZMASK' : [
            'BM_SeparateXYZ',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_VectorMath.002',
            'BM_MapRange',
            'BM_MixRGB',
        ],
        'GRADIENT' : [
            'BM_Mapping',
            'BM_TexGradient',
            'BM_MapRange',
            'BM_MixRGB',
            'BM_HueSaturation',
            'BM_Invert',
        ],
        'EDGE' : [
            'BM_Bevel',
            'BM_MapRange',
            'BM_Invert',
        ],
        'WIREFRAME' : [
            'BM_Value',
            'BM_Invert',
        ],
        'POSITION' : [
        ],
        'VERTEX_COLOR_LAYER' : [
            'BM_Attribute',
        ],
        'VECTOR_DISPLACEMENT' : [
            'BM_Value',
        ],
        'DECAL' : [
            'BM_CombineXYZ',
            'BM_Invert',
            'BM_Invert.001',
            'BM_Invert.002',
            'BM_Emission',
        ],
        'MASK' : [
            'BM_RGB',
            'BM_Invert',
        ],
        'ID' : [
            'BM_Emission',
        ],
    }
    
    map = BM_Map_Get(self, object_item)

    # for id, loop over materials with COLORI in the name
    # because need to calculate size of color stepping
    if map_tag == "ID":
        import colorsys
        
        for object in objects:
            color_mats = []
            for material in object.data.materials:
                if material is None:
                    continue
                if map.map_matid_data in  ['MATERIALS', 'OBJECTS']:
                    color_mats.append(material)
                else:
                    if material.name.find("BM_CustomMaterial_") != -1 and material.name.find("COLOR") != -1:
                        color_mats.append(material)
            if len(color_mats) == 0:
                continue
            
            # getting colors
            colors = []
            if map.map_matid_algorithm == 'GRAYSCALE':
                step = round(1 / (len(color_mats) - 1), 3)
                color = [0.0, 0.0, 1.0]
                for i in range(len(color_mats)):
                    rgb = list(colorsys.hsv_to_rgb(color[0], color[1], color[2]))
                    rgb.append(1.0)
                    colors.append(tuple(rgb))
                    color[2] -= step
            
            if map.map_matid_algorithm == 'HUE':
                step = round(1 / (len(color_mats)), 3)
                color = [1.0, 1.0, 1.0]
                for i in range(len(color_mats)):
                    rgb = list(colorsys.hsv_to_rgb(color[0], color[1], color[2]))
                    rgb.append(1.0)
                    colors.append(tuple(rgb))
                    color[0] -= step
            
            if map.map_matid_algorithm == 'RANDOM':
                # (dev) debug .prefs/rgb_color_scatter.py to see how this works
                # given variables
                Points = len(color_mats) # number of points to scatter aka colors to get, > 0
                SOrbit = 4 # value indicating at what number of scattered points the first Saturation orbit should end, > 0
                VOrbit = 24 # value indicating at what number of scattered points the first Value orbit should end, > 0
                MinOrbit = 2 # minimum on SOrbit = SOrbit / MinOrbit, same for minimum on VOrbit, float > 0

                def get_orbit_size(orbit_capacity, points):
                    n = 1
                    new_points = [1]
                    points_cache = 1
                    while points_cache < points:
                        # minimum n of points on the current V orbit
                        minimum = int(orbit_capacity / MinOrbit)
                        # how many points left in total
                        points_left = points - points_cache
                        can_contain = points_left - ((points_left - orbit_capacity) + minimum)
                        # if left more than orbit can contain, add orbit_capacity
                        if points_left - orbit_capacity >= orbit_capacity:
                            points_cache += orbit_capacity
                            new_points.append(orbit_capacity)
                        elif can_contain >= minimum and can_contain <= points_left:
                            points_cache += can_contain
                            new_points.append(can_contain)
                        else:
                            points_cache += points_left
                            new_points.append(points_left)
                        orbit_capacity *= 2
                        n += 1
                    return n, sorted(new_points)

                n_v, v_points = get_orbit_size(VOrbit, Points)

                if n_v - 1 == 0:
                    v_step = 0
                else:
                    v_step = round(1 / (n_v - 1), 3)

                color = [1.0, 0.0, 0.0]
                for v_orbit_size in v_points:
                    color[1] = 0.0
                    n_s, s_points = get_orbit_size(SOrbit, v_orbit_size)

                    if n_s - 1 == 0:
                        s_step = 0
                    else:
                        s_step = round(1 / (n_s - 1), 3)

                    for s_orbit_size in s_points:
                        color[0] = 1.0
                        if s_orbit_size - 1 == 0:
                            h_step = 0
                        else:
                            h_step = round(1 / s_orbit_size, 3)

                        for i in range(s_orbit_size):
                            rgb = list(colorsys.hsv_to_rgb(color[0], color[1], color[2]))
                            rgb.append(1.0)
                            colors.append(tuple(rgb))
                            color[0] -= h_step
                        
                        color[1] += s_step
                    
                    color[2] += v_step
            
            # jiltering colors
            # (dev) debug and read .prefs/lazy_array_shuffle to see how that works
            # this array_jilter is not very good and results in loads of repitive patterns
            def lazy_array_jilter(array, jilter):
                # time complexity is O(n)
                # in this case jilter will not affect array, so return
                if jilter == 0:
                    return array
                length = len(array)
                if length % jilter == 0:
                    return array

                for i in range(len(array)):
                    new_pos = i + jilter
                    if new_pos >= length:
                        new_pos %= length

                    c = array[i]
                    array[i] = array[new_pos]
                    array[new_pos] = c
                
                return array

            colors = lazy_array_jilter(colors, map.map_matid_jilter)
            # if map.map_matid_jilter != 0:
                # import numpy
                # numpy.random.shuffle(colors)
            
            # loop through needed materials
            for mat_index, material in enumerate(color_mats):
                material.use_nodes = True
                nodes = material.node_tree.nodes
                map_nodes = nodes_names_data[map_tag]
                nodes[map_nodes[0]].inputs[0].default_value = colors[mat_index]

        return

    # looping through materials
    for object in objects:
        for material in object.data.materials:
            if material is None:
                continue

            material.use_nodes = True
            bm_nodes = str([node.name for node in material.node_tree.nodes])
            if bm_nodes.find('BM_') == -1:
                continue
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            map_nodes = nodes_names_data[map_tag]
            # updating nodes inputs and properties
            if map_tag == "AO":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    distance = 1
                    only_local = False
                    black_point = 0
                    white_point = 0.8
                    opacity = 0.67
                    brightness = -0.3
                    contrast = 0.3
                    invert = 0        
                else:
                    samples = map.map_ao_samples
                    distance = map.map_ao_distance
                    only_local = map.map_ao_use_local
                    black_point = map.map_ao_black_point
                    white_point = map.map_ao_white_point
                    opacity = map.map_ao_opacity
                    brightness = map.map_ao_brightness
                    contrast = map.map_ao_contrast
                    invert = map.map_ao_use_invert

                nodes[map_nodes[0]].samples = samples
                nodes[map_nodes[0]].inputs[1].default_value = distance
                nodes[map_nodes[0]].only_local = only_local
                nodes[map_nodes[1]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[1]].color_ramp.elements[1].position = white_point
                nodes[map_nodes[2]].inputs[0].default_value = opacity
                nodes[map_nodes[3]].inputs[1].default_value = brightness
                nodes[map_nodes[3]].inputs[2].default_value = contrast
                nodes[map_nodes[4]].inputs[0].default_value = invert

            if map_tag == "CAVITY":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    black_point = 0
                    white_point = 1
                    power = 2.5
                    invert = 0
                else:
                    black_point = map.map_cavity_black_point
                    white_point = map.map_cavity_white_point
                    power = map.map_cavity_power
                    invert = map.map_cavity_use_invert

                nodes[map_nodes[0]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[0]].color_ramp.elements[1].position = white_point
                nodes[map_nodes[1]].inputs[1].default_value = power
                nodes[map_nodes[2]].inputs[0].default_value = invert

            if map_tag == "CURVATURE":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    radius = 2.2
                    black_point = 0.4
                    mid_point = 0.5
                    white_point = 0.6
                    gamma = 2.2
                else:
                    samples = map.map_curv_samples
                    radius = map.map_curv_radius
                    black_point = map.map_curv_black_point
                    mid_point = map.map_curv_mid_point
                    white_point = map.map_curv_white_point
                    gamma = map.map_curv_body_gamma
                
                nodes[map_nodes[0]].outputs[0].default_value = radius
                nodes[map_nodes[1]].samples = samples
                nodes[map_nodes[2]].samples = samples
                nodes[map_nodes[3]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[3]].color_ramp.elements[1].position = mid_point
                nodes[map_nodes[3]].color_ramp.elements[2].position = white_point
                nodes[map_nodes[4]].inputs[1].default_value = gamma

            if map_tag == "THICKNESS":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    distance = 1
                    black_point = 0
                    white_point = 1
                    brightness = 1
                    contrast = 0
                    invert = 0
                else:
                    samples = map.map_thick_samples
                    distance = map.map_thick_distance
                    black_point = map.map_thick_black_point
                    white_point = map.map_thick_white_point
                    brightness = map.map_thick_brightness
                    contrast = map.map_thick_contrast
                    invert = map.map_thick_use_invert

                nodes[map_nodes[0]].samples = samples
                nodes[map_nodes[0]].inputs[1].default_value = distance
                nodes[map_nodes[1]].inputs[1].default_value = contrast
                nodes[map_nodes[1]].inputs[4].default_value = brightness
                nodes[map_nodes[2]].color_ramp.elements[0].position = black_point
                nodes[map_nodes[2]].color_ramp.elements[1].position = white_point
                nodes[map_nodes[3]].inputs[0].default_value = invert

            if map_tag == "XYZMASK":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    coverage = 0
                    saturation = 1
                    opacity = 1
                    invert = 1
                else:
                    coverage = map.map_xyzmask_coverage
                    saturation = map.map_xyzmask_saturation
                    opacity = map.map_xyzmask_opacity
                    invert = map.map_xyzmask_use_invert

                for i in range(3):
                    nodes[map_nodes[3]].inputs[1].default_value[i] = invert

                nodes[map_nodes[4]].inputs[1].default_value = coverage
                nodes[map_nodes[4]].inputs[4].default_value = saturation
                nodes[map_nodes[5]].inputs[0].default_value = opacity

                if map.map_xyzmask_use_x:
                    links.new(nodes[map_nodes[0]].outputs[0], nodes[map_nodes[1]].inputs[0])
                elif len(nodes[map_nodes[0]].outputs[0].links):
                    links.remove(nodes[map_nodes[0]].outputs[0].links[0])
                if map.map_xyzmask_use_y:
                    links.new(nodes[map_nodes[0]].outputs[1], nodes[map_nodes[1]].inputs[1])
                elif len(nodes[map_nodes[0]].outputs[1].links):
                    links.remove(nodes[map_nodes[0]].outputs[1].links[0])
                if map.map_xyzmask_use_z:
                    links.new(nodes[map_nodes[0]].outputs[2], nodes[map_nodes[2]].inputs[1])
                elif len(nodes[map_nodes[0]].outputs[2].links):
                    links.remove(nodes[map_nodes[0]].outputs[2].links[0])

            if map_tag == "GRADIENT":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    #mapping = [[0, 0, 0], [0, 0, 0], [1, 1, 1]]
                    coverage = 0
                    contrast = 1
                    saturation = 1
                    opacity = 1
                    invert = 0
                else:
                    coverage = map.map_gmask_coverage
                    contrast = map.map_gmask_contrast
                    saturation = map.map_gmask_saturation
                    opacity = map.map_gmask_opacity
                    invert = map.map_gmask_use_invert
                g_type = map.map_gmask_type

                # mapping can be changed no matter the use_default state
                mapping = [
                    [map.map_gmask_location_x, map.map_gmask_location_y, map.map_gmask_location_z],
                    [map.map_gmask_rotation_x, map.map_gmask_rotation_y, map.map_gmask_rotation_z],
                    [map.map_gmask_scale_x, map.map_gmask_scale_y, map.map_gmask_scale_z],
                ]
                for i in range(1, 4):
                    for j in range(3):
                        nodes[map_nodes[0]].inputs[i].default_value[j] = mapping[i - 1][j]

                nodes[map_nodes[1]].gradient_type = g_type
                nodes[map_nodes[2]].inputs[1].default_value = coverage
                nodes[map_nodes[2]].inputs[4].default_value = contrast
                nodes[map_nodes[3]].inputs[0].default_value = opacity
                nodes[map_nodes[4]].inputs[2].default_value = saturation
                nodes[map_nodes[5]].inputs[0].default_value = invert

            if map_tag == "EDGE":
                use_default = getattr(map, "map_%s_use_default" % map_tag)
                if use_default:
                    samples = 16
                    radius = 0.02
                    edge_contrast = 0
                    body_contrast = 1
                    invert = 1
                else:
                    samples = map.map_edgemask_samples
                    radius = map.map_edgemask_radius
                    edge_contrast = map.map_edgemask_edge_contrast
                    body_contrast = map.map_edgemask_body_contrast
                    invert = map.map_edgemask_use_invert

                nodes[map_nodes[0]].samples = samples
                nodes[map_nodes[0]].inputs[0].default_value = radius
                nodes[map_nodes[1]].inputs[1].default_value = edge_contrast
                nodes[map_nodes[1]].inputs[4].default_value = body_contrast
                nodes[map_nodes[2]].inputs[0].default_value = invert

            if map_tag == "WIREFRAME":
                radius = map.map_wireframemask_line_thickness
                invert = map.map_wireframemask_use_invert

                nodes[map_nodes[0]].outputs[0].default_value = radius
                nodes[map_nodes[1]].inputs[0].default_value = invert
                
            # if map_tag == "POSITION":
                
            if map_tag == "VERTEX_COLOR_LAYER":
                layer = map.map_vertexcolor_layer

                nodes[map_nodes[0]].attribute_name = layer

            if map_tag == "VECTOR_DISPLACEMENT":
                value = int(not map.map_vector_displacement_use_negative) - 1

                nodes[map_nodes[0]].outputs[0].default_value = value
            
            if map_tag == "DECAL":
                if map.map_decal_normal_preset == 'CUSTOM':
                    if map.map_decal_normal_custom_preset == 'OPEN_GL':
                        value = 0
                    else:
                        value = 1
                else:
                    if map.map_decal_normal_preset.find('OPENGL') != -1:
                        value = 0
                    elif map.map_decal_normal_preset.find('DIRECTX') != -1:
                        value = 1
                nodes[map_nodes[1]].inputs[0].default_value = value

                nodes[map_nodes[2]].inputs[0].default_value = bool(map.map_decal_height_opacity_invert)
                nodes[map_nodes[3]].inputs[0].default_value = bool(map.map_decal_height_opacity_invert)

                link_from = {
                    'NORMAL' : 0,
                    'HEIGHT' : 2,
                    'OPACITY' : 3,
                }
                index = link_from[map.map_decal_pass_type]
                links.new(nodes[map_nodes[index]].outputs[0], nodes[map_nodes[4]].inputs[0])

            if map_tag == "MASK":
                for i in range(1, 3):
                    if material.name.find("BM_CustomMaterial_") != -1 and material.name.find("COLOR%d" % i) != -1:
                        nodes[map_nodes[0]].outputs[0].default_value = getattr(map, "map_mask_color%d" % i)
                        nodes[map_nodes[1]].inputs[0].default_value = map.map_mask_use_invert

def Map_MapPreview_CustomNodes_Add(self, context, map_tag):
    object_item_full = BM_Object_Get(self, context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    if getattr(BM_Map_Get(self, object_item), "map_%s_use_preview" % map_tag) is False:
        return
    map = BM_Map_Get(self, object_item)

    # collecting objects for which add bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return
    highpolies = map.hl_highpoly_table if object_item.hl_use_unique_per_map else object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])

    # nodes data
    nodes_data = {
        'AO' : [
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeValToRGB',
            'ShaderNodeMixRGB',
            'ShaderNodeBrightContrast',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'CAVITY' : [
            'ShaderNodeNewGeometry',
            'ShaderNodeValToRGB',
            'ShaderNodeMath',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'CURVATURE' : [
            'ShaderNodeValue',
            'ShaderNodeMath',
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeInvert',
            'ShaderNodeMixRGB',
            'ShaderNodeValToRGB',
            'ShaderNodeGamma',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'THICKNESS' : [
            'ShaderNodeAmbientOcclusion',
            'ShaderNodeMapRange',
            'ShaderNodeValToRGB',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'XYZMASK' : [
            'ShaderNodeNewGeometry',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeMapRange',
            'ShaderNodeMixRGB',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'GRADIENT' : [
            'ShaderNodeTexCoord',
            'ShaderNodeMapping',
            'ShaderNodeTexGradient',
            'ShaderNodeMapRange',
            'ShaderNodeMixRGB',
            'ShaderNodeHueSaturation',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'EDGE' : [
            'ShaderNodeBevel',
            'ShaderNodeNewGeometry',
            'ShaderNodeVectorMath',
            'ShaderNodeMapRange',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'WIREFRAME' : [
            'ShaderNodeValue',
            'ShaderNodeMath',
            'ShaderNodeWireframe',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'POSITION' : [
            'ShaderNodeTexCoord',
            'ShaderNodeSeparateRGB',
            'ShaderNodeInvert',
            'ShaderNodeCombineRGB',
            'ShaderNodeGamma',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'VERTEX_COLOR_LAYER' : [
            'ShaderNodeAttribute',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'VECTOR_DISPLACEMENT' : [
            'ShaderNodeTexCoord',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeValue',
            'ShaderNodeMapRange',
            'ShaderNodeMapRange',
            'ShaderNodeMapRange',
            'ShaderNodeCombineXYZ',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'DECAL' : [
            'ShaderNodeTexCoord',
            'ShaderNodeVectorTransform',
            'ShaderNodeVectorMath',
            'ShaderNodeVectorMath',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeInvert',
            'ShaderNodeCombineXYZ',
            'ShaderNodeSeparateXYZ',
            'ShaderNodeInvert',
            'ShaderNodeInvert',
            'ShaderNodeRGB',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'MASK' : [
            'ShaderNodeRGB',
            'ShaderNodeInvert',
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
        'ID' : [
            'ShaderNodeEmission',
            'ShaderNodeOutputMaterial',
        ],
    }

    nodes_names_data = {
        'AO' : [
            'BM_AmbientOcclusion',
            'BM_ValToRGB',
            'BM_MixRGB',
            'BM_BrightContrast',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'CAVITY' : [
            'BM_NewGeometry',
            'BM_ValToRGB',
            'BM_Math',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'CURVATURE' : [
            'BM_Value',
            'BM_Math',
            'BM_AmbientOcclusion',
            'BM_AmbientOcclusion.001',
            'BM_Invert',
            'BM_MixRGB',
            'BM_ValToRGB',
            'BM_Gamma',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'THICKNESS' : [
            'BM_AmbientOcclusion',
            'BM_MapRange',
            'BM_ValToRGB',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'XYZMASK' : [
            'BM_NewGeometry',
            'BM_SeparateXYZ',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_VectorMath.002',
            'BM_MapRange',
            'BM_MixRGB',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'GRADIENT' : [
            'BM_TexCoord',
            'BM_Mapping',
            'BM_TexGradient',
            'BM_MapRange',
            'BM_MixRGB',
            'BM_HueSaturation',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'EDGE' : [
            'BM_Bevel',
            'BM_NewGeometry',
            'BM_VectorMath',
            'BM_MapRange',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'WIREFRAME' : [
            'BM_Value',
            'BM_Math',
            'BM_Wireframe',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'POSITION' : [
            'BM_TexCoord',
            'BM_SeparateRGB',
            'BM_Invert',
            'BM_CombineRGB',
            'BM_Gamma',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'VERTEX_COLOR_LAYER' : [
            'BM_Attribute',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'VECTOR_DISPLACEMENT' : [
            'BM_TexCoord',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_VectorMath.002',
            'BM_SeparateXYZ',
            'BM_SeparateXYZ.001',
            'BM_Value',
            'BM_MapRange',
            'BM_MapRange.001',
            'BM_MapRange.002',
            'BM_CombineXYZ',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'DECAL' : [
            'BM_TexCoord',
            'BM_VectorTransform',
            'BM_VectorMath',
            'BM_VectorMath.001',
            'BM_SeparateXYZ',
            'BM_Invert',
            'BM_CombineXYZ',
            'BM_SeparateXYZ.001',
            'BM_Invert.001',
            'BM_Invert.002',
            'BM_RGB',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'MASK' : [
            'BM_RGB',
            'BM_Invert',
            'BM_Emission',
            'BM_OutputMaterial',
        ],
        'ID' : [
            'BM_Emission',
            'BM_OutputMaterial',
        ],
    }

    # adding materials if needed
    for object in objects:
        len_of_mats = len(object.data.materials)
        if len_of_mats == 0 or len([material for material in object.data.materials if material is None]) == len_of_mats:
            new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s" % (object.name, map_tag))
            object.data.materials.append(new_mat)
    
    # adding nodes to object's materials
    for object in objects:
        for material in object.data.materials:
            if material is None:
                continue

            material.use_nodes = True
            location_x = 0
            for index, node_type in enumerate(nodes_data[map_tag]):
                new_node = material.node_tree.nodes.new(node_type)
                new_node.name = nodes_names_data[map_tag][index]
                new_node.location = (location_x, 0)
                location_x += 300

            # setting up added nodes defaults
            nodes = material.node_tree.nodes
            # AO
            if map_tag == "AO":
                nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
                nodes['BM_MixRGB'].inputs[1].default_value = (1, 1, 1, 1)
        
            # CAVITY
            if map_tag == "CAVITY":
                nodes['BM_Math'].operation = 'POWER'
                nodes['BM_OutputMaterial'].target = 'CYCLES'

            # CURVATURE
            if map_tag == "CURVATURE":
                nodes['BM_Math'].operation = 'MULTIPLY'
                nodes['BM_Math'].inputs[1].default_value = 0.01
                nodes['BM_AmbientOcclusion'].inside = True
                nodes['BM_AmbientOcclusion.001'].inside = False
                nodes['BM_AmbientOcclusion.001'].inputs[0].default_value = (0, 0, 0, 1)
                nodes['BM_ValToRGB'].color_ramp.elements[0].color = (0, 0, 0, 1)
                nodes['BM_ValToRGB'].color_ramp.elements[1].color = (1, 1, 1, 1)
                new_element = nodes['BM_ValToRGB'].color_ramp.elements.new(0.5)
                new_element.color = (0.5, 0.5, 0.5, 1)
            
            # THICKNESS
            if map_tag == "THICKNESS":
                nodes['BM_AmbientOcclusion'].inside = True

            # XYZMASK
            if map_tag == "XYZMASK":
                nodes['BM_VectorMath.002'].operation = 'MULTIPLY'
                nodes['BM_MixRGB'].inputs[1].default_value = (0, 0, 0, 0)

            # GRADIENT
            if map_tag == "GRADIENT":
                nodes['BM_MixRGB'].inputs[1].default_value = (0, 0, 0, 0)

            # EDGE
            if map_tag == "EDGE":
                nodes['BM_VectorMath'].operation = 'DOT_PRODUCT'

            # WIREFRAME
            if map_tag == "WIREFRAME":
                nodes['BM_Math'].operation = 'MULTIPLY'
                nodes['BM_Math'].inputs[1].default_value = 0.01

            # POSITION
            if map_tag == "POSITION":
                nodes['BM_Gamma'].inputs[1].default_value = 2.2

            # VERTEX_COLOR_LAYER
            if map_tag == "VERTEX_COLOR_LAYER":
                pass
            
            # VECTOR_DISPLACEMENT
            if map_tag == "VECTOR_DISPLACEMENT":
                nodes['BM_VectorMath'].inputs[1].default_value[0] = -0.5
                nodes['BM_VectorMath'].inputs[1].default_value[1] = -0.5
                nodes['BM_VectorMath'].inputs[1].default_value[2] = -0.5
                nodes['BM_VectorMath.001'].operation = 'MULTIPLY'
                nodes['BM_VectorMath.001'].inputs[1].default_value[0] = 2
                nodes['BM_VectorMath.001'].inputs[1].default_value[1] = 2
                nodes['BM_VectorMath.001'].inputs[1].default_value[2] = 2
                nodes['BM_VectorMath.002'].operation = 'SUBTRACT'
                nodes['BM_MapRange'].clamp = False
                nodes['BM_MapRange.001'].clamp = False
                nodes['BM_MapRange.002'].clamp = False
            
            # DECAL
            if map_tag == "DECAL":
                nodes['BM_VectorTransform'].convert_to = 'CAMERA'
                nodes['BM_VectorMath'].operation = 'MULTIPLY'
                nodes['BM_VectorMath'].inputs[1].default_value = (0.5, 0.5, -0.5)
                nodes['BM_VectorMath.001'].inputs[1].default_value = (0.5, 0.5, 0.5)
                nodes['BM_RGB'].outputs[0].default_value = (1, 1, 1, 1)

            nodes['BM_OutputMaterial'].target = 'CYCLES'

            # linking added nodes
            # shell - [node_from, node_to, out_socket, in_socket]
            links_data = {
                'AO' : [
                    [0, 1, 1, 0],
                    [1, 2, 0, 2],
                    [2, 3, 0, 0],
                    [3, 4, 0, 1],
                    [4, 5, 0, 0],
                    [5, 6, 0, 0],
                ],
                'CAVITY' : [
                    [0, 1, 7, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                ],
                'CURVATURE' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 1],
                    [1, 3, 0, 1],
                    [2, 4, 1, 1],
                    [4, 5, 0, 1],
                    [3, 5, 1, 2],
                    [5, 6, 0, 0],
                    [6, 7, 0, 0],
                    [7, 8, 0, 0],
                    [8, 9, 0, 0],
                ],
                'THICKNESS' : [
                    [0, 1, 1, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                ],
                'XYZMASK' : [
                    [0, 1, 1, 0],
                    [2, 3, 0, 0],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                    [5, 6, 0, 2],
                    [6, 7, 0, 0],
                    [7, 8, 0, 0],
                ],
                'GRADIENT' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 0],
                    [3, 4, 0, 2],
                    [4, 5, 0, 4],
                    [5, 6, 0, 1],
                    [6, 7, 0, 0],
                    [7, 8, 0, 0],
                ],
                'EDGE' : [
                    [0, 2, 0, 0],
                    [1, 2, 1, 1],
                    [2, 3, 1, 0],
                    [3, 4, 0, 1],
                    [4, 5, 0, 0],
                    [5, 6, 0, 0],
                ],
                'WIREFRAME' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                ],
                'POSITION' : [
                    [0, 1, 0, 0],
                    [1, 3, 0, 0],
                    [1, 3, 2, 1],
                    [1, 2, 1, 1],
                    [2, 3, 0, 2],
                    [3, 4, 0, 0],
                    [4, 5, 0, 0],
                    [5, 6, 0, 0],
                ],
                'VERTEX_COLOR_LAYER' : [
                    [0, 1, 0, 0],
                    [1, 2, 0, 0],
                ],
                'VECTOR_DISPLACEMENT' : [
                    [0, 1, 2, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 1],
                    [0, 3, 3, 0],
                    [3, 4, 0, 0],
                    [0, 5, 3, 0],
                    [6, 7, 0, 1],
                    [6, 8, 0, 1],
                    [6, 9, 0, 1],
                    [4, 7, 0, 0],
                    [4, 8, 1, 0],
                    [5, 9, 2, 0],
                    [7, 10, 0, 0],
                    [8, 10, 0, 1],
                    [9, 10, 0, 2],
                    [10, 11, 0, 0],
                    [11, 12, 0, 0],
                ],
                'DECAL' : [
                    [0, 1, 1, 0],
                    [0, 7, 0, 0],
                    [1, 2, 0, 0],
                    [2, 3, 0, 0],
                    [3, 4, 0, 0],
                    [4, 6, 0, 0],
                    [4, 5, 1, 1],
                    [5, 6, 0, 1],
                    [4, 6, 2, 2],
                    [7, 8, 2, 1],
                    [10, 9, 0, 1],
                    [11, 12, 0, 0],
                ],
                'MASK' : [
                    [0, 1, 0, 1],
                    [1, 2, 0, 0],
                    [2, 3, 0, 0],
                ],
                'ID' : [
                    [0, 1, 0, 0],
                ],
            }

            # linking
            map_nodes = nodes_names_data[map_tag]
            for link in links_data[map_tag]:
                out_socket = material.node_tree.nodes[map_nodes[link[0]]].outputs[link[2]]
                in_socket = material.node_tree.nodes[map_nodes[link[1]]].inputs[link[3]]
                material.node_tree.links.new(out_socket, in_socket)

            for node in nodes:
                if node.type != 'OUTPUT_MATERIAL':
                    continue
                node.target = 'ALL'

            material.node_tree.nodes['BM_OutputMaterial'].select = True
            material.node_tree.nodes.active = nodes['BM_OutputMaterial']

    Map_MapPreview_CustomNodes_Update(self, context, map_tag)

def Map_MapPreview_RelinkMaterials_Add(self, context, map_tag):
    object_item_full = BM_Object_Get(self, context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    map = BM_Map_Get(self, object_item)
    if getattr(map, "map_%s_use_preview" % map_tag) is False:
        return

    # collecting objects for which add bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return
    highpolies = map.hl_highpoly_table if object_item.hl_use_unique_per_map else object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []

    select_highpoly = False
    if len(highpolies) != 0:
        select_highpoly = True
    if map.global_map_type == 'DISPLACEMENT':
        if map.map_displacement_data == 'HIGHPOLY':
            select_highpoly = False
        if map.map_displacement_data == 'MULTIRES':
            select_highpoly = False
        elif len(highpolies) != 0:
            select_highpoly = True
    if map.global_map_type == 'NORMAL':
        if map.map_normal_data == 'MULTIRES':
            select_highpoly = False
        if map.map_normal_data == 'MATERIAL':
            select_highpoly = False
        elif len(highpolies) != 0:
            select_highpoly = True

    if select_highpoly:
        for highpoly in highpolies:
            source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
            if len(source_highpoly) == 0:
                continue
            objects.append(source_highpoly[0])
    elif source_object[0] not in objects:
        objects.append(source_object[0])

    map_type_origin = map_tag
    if map_tag == 'PASS':
        map_tag = map.map_pass_type

    # each shaders supports grabbing specified passes,
    # passes keys' values are sockets names
    # passes names and grabbing algo may differ for each map type
    node_getable_data = {
        'ALBEDO' : ['Color', 'Base Color'],
        'METALNESS' : ['Metallic'],
        'ROUGHNESS' : ['Roughness'],
        'DIFFUSE' : ['Color', 'Base Color'],
        'SPECULAR' : ['Specular'],
        'GLOSSINESS' : ['Roughness'],
        'OPACITY' : ['Alpha', 'Opacity'],
        'BASE_COLOR' : ['Base Color'],
        'SS_COLOR' : ['Subsurface Color', 'Color'],
        'METALLIC' : ['Metallic'],
        'ANISOTROPIC' : ['Anisotropic'],
        'SHEEN' : ['Sheen'],
        'CLEARCOAT' : ['Clearcoat'],
        'IOR' : ['IOR'],
        'TRANSMISSION' : ['Transmission'],
        'EMISSION' : ['Emission'],
        'ALPHA' : ['Alpha'],
        'NORMAL' : ['Normal'],
        'DISPLACEMENT' : ['Displacement'],
    }

    def get_socket_default_color_value(socket, socket_name):  
        default_color_data = {
            'Color' : getattr(socket, "default_value"),
            'Base Color' : getattr(socket, "default_value"),
            'Metallic' : [getattr(socket, "default_value")]*3,
            'Roughness' : [getattr(socket, "default_value")]*3,
            'Specular' : [getattr(socket, "default_value")]*3,
            'Alpha' : [getattr(socket, "default_value")]*3,
            'Subsurface Color' : getattr(socket, "default_value"),
            'Anisotropic' : [getattr(socket, "default_value")]*3,
            'Sheen' : [getattr(socket, "default_value")]*3,
            'Clearcoat' : [getattr(socket, "default_value")]*3,
            'IOR' : [getattr(socket, "default_value")]*3,
            'Transmission' : [getattr(socket, "default_value")]*3,
            'Emission' : getattr(socket, "default_value"),
            'Normal' : [0.5, 0.5, 1],
            'Displacement' : [0.0]*3,
        }
        data = list(default_color_data[socket_name])
        if len(data) != 4:
            data.append(1)
        return tuple(data)
    
    ad_map_tag = ""
    map_tag_origin = map_tag
    if map_tag in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
        ad_map_tag = 'METALNESS'
        map_tag = 'DIFFUSE'

    for object in objects:
        if len(object.data.materials) == 0:
            bpy.ops.bakemaster.report_message(message_type='WARNING', message="%s: No Materials" % object.name)
            continue

        for material in object.data.materials:
            if material is None:
                continue

            material.use_nodes = True
            grab_socket = None
            default_value = None
            grab_ad_socket = None
            default_ad_value = None
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            # grabbing socket to preview
            for node in nodes:
                if node.type != 'OUTPUT_MATERIAL':
                    continue
                
                if map_tag == 'DISPLACEMENT':
                    if len(node.inputs[2].links) == 0:
                        continue
                    grab_socket = node.inputs[2].links[0].from_socket
                    input_node = node.inputs[2].links[0].from_node
                    if input_node.type in ['DISPLACEMENT', 'VECTOR_DISPLACEMENT']:
                            if len(input_node.inputs[0].links) == 0:
                                default_value = tuple([input_node.inputs[0].default_value, input_node.inputs[0].default_value, input_node.inputs[0].default_value, 1])
                                grab_socket = None
                                break
                            grab_socket = input_node.inputs[0].links[0].from_socket
                    break
                
                if len(node.inputs[0].links) == 0:
                        continue
                
                # find socket value to grab
                for input_socket in node.inputs[0].links[0].from_node.inputs:
                    if input_socket.name in node_getable_data[map_tag]:
                        if len(input_socket.links) == 0:
                            default_value = get_socket_default_color_value(input_socket, input_socket.name)
                            break
                        grab_socket = input_socket.links[0].from_socket
                        if input_socket.links[0].from_node.type == 'NORMAL_MAP':
                            if len(input_socket.links[0].from_node.inputs[1].links) == 0:
                                default_value = tuple(input_socket.links[0].from_node.inputs[1].default_value)
                                grab_socket = None
                                break
                            grab_socket = input_socket.links[0].from_node.inputs[1].links[0].from_socket
                        break

                if any([grab_socket is not None, default_value is not None]):
                    if ad_map_tag == "":
                        break

                if ad_map_tag == "":
                    continue
                
                # find additional socket value for pbrs previews
                for input_socket in node.inputs[0].links[0].from_node.inputs:
                    if input_socket.name in node_getable_data[ad_map_tag]:
                        if len(input_socket.links) == 0:
                            default_ad_value = get_socket_default_color_value(input_socket, input_socket.name)
                            break
                        grab_ad_socket = input_socket.links[0].from_socket
                        break
                
                if any([grab_ad_socket is not None, default_ad_value is not None]):
                    break
            
            # add out, emission nodes
            new_nodes = ['ShaderNodeEmission', 'ShaderNodeOutputMaterial']
            rgb_node_name_end = ""
            if grab_socket is None:
                new_nodes.append('ShaderNodeRGB')
            if grab_ad_socket is None and map_tag_origin in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeRGB')
                rgb_node_name_end = ".001" if grab_socket is None else ""

            # pbr specular nodes
            if map_tag_origin in ['GLOSSINESS', 'DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeInvert')
            if map_tag_origin in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeMixRGB')
            if map_tag_origin == 'SPECULAR' and map_type_origin != 'PASS':
                new_nodes.append('ShaderNodeValue')
                new_nodes.append('ShaderNodeMixRGB')

            location_x = 0
            for node_type in new_nodes:
                new_node = nodes.new(node_type)
                new_node.name = 'BM_%s' % node_type[10:]
                new_node.location = (location_x, 0)
                location_x += 300

            # nodes values
            default_value = (0, 0, 0, 1) if default_value is None else default_value
            if grab_socket is None:
                nodes['BM_RGB'].outputs[0].default_value = default_value
                value = nodes['BM_RGB'].outputs[0]
            else:
                value = grab_socket

            # additional node values
            default_ad_value = (0, 0, 0, 1) if default_ad_value is None else default_ad_value
            if grab_ad_socket is None and map_tag_origin in ['DIFFUSE', 'SPECULAR'] and map_type_origin != 'PASS':
                nodes['BM_RGB%s' % rgb_node_name_end].outputs[0].default_value = default_ad_value
                ad_value = nodes['BM_RGB%s' % rgb_node_name_end].outputs[0]
            elif map_type_origin != 'PASS':
                ad_value = grab_ad_socket

            # link added nodes and link with grabbed socket
            if map_tag_origin == 'GLOSSINESS':
                nodes['BM_Invert'].inputs[0].default_value = 1.0
                links.new(value, nodes['BM_Invert'].inputs[1])
                links.new(nodes['BM_Invert'].outputs[0], nodes['BM_Emission'].inputs[0])
            elif map_tag_origin == 'DIFFUSE':
                nodes['BM_Invert'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
                links.new(ad_value, nodes['BM_Invert'].inputs[1])
                links.new(nodes['BM_Invert'].outputs[0], nodes['BM_MixRGB'].inputs[2])
                links.new(value, nodes['BM_MixRGB'].inputs[1])
                links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_Emission'].inputs[0])
            elif map_tag_origin == 'SPECULAR' and map_type_origin != 'PASS':
                nodes['BM_Invert'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].inputs[0].default_value = 1.0
                nodes['BM_MixRGB'].blend_type = 'MULTIPLY'
                nodes['BM_MixRGB.001'].blend_type = 'ADD'
                nodes['BM_Value'].outputs[0].default_value = 0.04
                links.new(ad_value, nodes['BM_Invert'].inputs[1])
                links.new(ad_value, nodes['BM_MixRGB'].inputs[2])
                links.new(nodes['BM_Invert'].outputs[0], nodes['BM_MixRGB.001'].inputs[0])
                links.new(value, nodes['BM_MixRGB'].inputs[1])
                links.new(nodes['BM_MixRGB'].outputs[0], nodes['BM_MixRGB.001'].inputs[1])
                links.new(nodes['BM_Value'].outputs[0], nodes['BM_MixRGB.001'].inputs[2])
                links.new(nodes['BM_MixRGB.001'].outputs[0], nodes['BM_Emission'].inputs[0])
            else:
                if grab_socket is None:
                    links.new(nodes['BM_RGB'].outputs[0], nodes['BM_Emission'].inputs[0])
                else:
                    links.new(grab_socket, nodes['BM_Emission'].inputs[0])
            links.new(nodes['BM_Emission'].outputs[0], nodes['BM_OutputMaterial'].inputs[0])

            for node in nodes:
                if node.type != 'OUTPUT_MATERIAL':
                    continue
                node.target = 'ALL'

            material.node_tree.nodes['BM_OutputMaterial'].select = True
            material.node_tree.nodes.active = nodes['BM_OutputMaterial']

def BM_IterableData_GetNewUniqueName_Simple(data, name_starter):
    index = 0
    for d in data:
        if d.name.find(name_starter) != -1:
            index += 1
    return "%s.%d" % (name_starter, index)

def Map_MapPreview_ReassignMaterials_Prepare(self, context, map_tag):
    object_item_full = BM_Object_Get(self, context)
    if any([object_item_full[1] is False, object_item_full[0].nm_is_universal_container, object_item_full[0].nm_is_local_container]):
        return
    object_item = object_item_full[0]
    if len(object_item.global_maps) == 0:
        return
    map = BM_Map_Get(self, object_item)
    if getattr(map, "map_%s_use_preview" % map_tag) is False:
        return

    # collecting objects for which add bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item.global_object_name]
    if len(source_object) == 0:
        return
    highpolies = map.hl_highpoly_table if object_item.hl_use_unique_per_map else object_item.hl_highpoly_table
    objects = [source_object[0]] if len(highpolies) == 0 else []
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])
    
    if len(objects) == 0:
        return

    # deselect all objects
    for ob in context.scene.objects:
        ob.select_set(False)
    bpy.ops.object.mode_set(mode='OBJECT')
                        
    for object in objects:
        # set object as active in the scene
        object.select_set(True)
        context.view_layer.objects.active = object

        # for mask add vertex group containing selection
        map_mask_selection_color1_vrtx_group_index = 0
        if map_tag == 'MASK':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='VERT')

            vrtx_group_name = BM_IterableData_GetNewUniqueName_Simple(object.vertex_groups, "bm_material_backup_COLOR1")
            object.vertex_groups.new(name=vrtx_group_name)
            map_mask_selection_color1_vrtx_group_index = len(object.vertex_groups) - 1

            if map.map_mask_data == 'VERTEX_GROUPS':
                bpy.ops.mesh.select_all(action='DESELECT')
                for vrtx_group_index, vrtx_group in enumerate(object.vertex_groups):
                    object.vertex_groups.active_index = vrtx_group_index
                    if vrtx_group.name.find(map.map_mask_vertex_groups_name_contains) != -1 and vrtx_group.name.lower().find("bm_") == -1:
                        bpy.ops.object.vertex_group_select()

            if map.map_mask_data == 'MATERIALS':
                bpy.ops.mesh.select_all(action='DESELECT')
                for mat_index, material in enumerate(object.data.materials):
                    if material is None:
                        continue
                    if material.name.find(map.map_mask_materials_name_contains) != -1 and material.name.lower().find("bm_") == -1:
                        object.active_material_index = mat_index
                        bpy.ops.object.material_slot_select()

            bpy.ops.object.vertex_group_assign()       

        # enter edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')

        if map_tag == 'ID' and map.map_matid_data in ['MATERIALS']:
            pass
        else:
            for mat_index, material in enumerate(object.data.materials):
                # set current material as active
                object.active_material_index = mat_index

                if material is None:
                    continue

                # add vertex group, deselect mesh, select current material mesh selection, assign it to created vertex group
                vrtx_group_name = BM_IterableData_GetNewUniqueName_Simple(object.vertex_groups, "bm_material_backup_%s" % material.name)
                object.vertex_groups.new(name=vrtx_group_name)

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.material_slot_select()
                bpy.ops.object.vertex_group_assign()
        
            bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.mesh.select_all(action='DESELECT')
        # for mask assign saved selection vertex group to color1 material
        if map_tag == 'MASK':
            # assign mat for color1
            new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s_COLOR1" % (object.name, map_tag))
            object.data.materials.append(new_mat)
            object.active_material_index = len(object.data.materials) - 1
            object.vertex_groups.active_index = map_mask_selection_color1_vrtx_group_index
            bpy.ops.object.vertex_group_select()
            bpy.ops.object.material_slot_assign()
            
            # assign mat for color2
            new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s_COLOR2" % (object.name, map_tag))
            object.data.materials.append(new_mat)
            object.active_material_index = len(object.data.materials) - 1
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.object.material_slot_assign()
        
        # for id
        if map_tag == 'ID':
            # vertex groups - add materials for vertex groups
            if map.map_matid_data == 'VERTEX_GROUPS':
                vrtx_group_for_inverted_selection_index = 0
                vrtx_group_name = BM_IterableData_GetNewUniqueName_Simple(object.vertex_groups, "bm_material_backup_COLOR")
                vrtx_group_for_inverted_selection_index = len(object.vertex_groups) - 1
                object.vertex_groups.new(name=vrtx_group_name)

                for vrtx_group_index, vrtx_group in enumerate(object.vertex_groups):
                    object.vertex_groups.active_index = vrtx_group_index
                    if vrtx_group.name.find(map.map_matid_vertex_groups_name_contains) != -1 and vrtx_group.name.lower().find("bm_") == -1:
                        bpy.ops.object.vertex_group_select()

                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.object.vertex_group_assign()

                tag_index = 0
                for vrtx_group_index, vrtx_group in enumerate(object.vertex_groups):
                    object.vertex_groups.active_index = vrtx_group_index
                    if vrtx_group.name.find(map.map_matid_vertex_groups_name_contains) != -1 and vrtx_group.name.lower().find("bm_") == -1:
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.vertex_group_select()

                        new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s_COLOR%d" % (object.name, map_tag, tag_index))
                        object.data.materials.append(new_mat)
                        object.active_material_index = len(object.data.materials) - 1
                        bpy.ops.object.material_slot_assign()
                        tag_index += 1
                
                bpy.ops.mesh.select_all(action='DESELECT')
                object.vertex_groups.active_index = vrtx_group_for_inverted_selection_index
                bpy.ops.object.vertex_group_select()
                new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s_COLOR%d" % (object.name, map_tag, tag_index))
                object.data.materials.append(new_mat)
                object.active_material_index = len(object.data.materials) - 1
                bpy.ops.object.material_slot_assign()
                tag_index += 1
            
            # materials - no mats to add, current will be used
            if map.map_matid_data == 'MATERIALS':
                pass
            
            # mesh islands - assign material for each saved mesh island
            if map.map_matid_data == 'MESH_ISLANDS':
                # Add all vertices to "unprocessed" list.
                # While (unprocessed verts remain):
                # Deselect all vertices
                # Select any one unprocessed vert
                # Call select_linked
                # assign new material to selection
                # Remove all selected verts from unprocessed list
                tag_index = 0
                vertices_processed = [False]*len(object.data.vertices)
                while True:
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    v_u = -1
                    for index in range(len(vertices_processed)):
                        if vertices_processed[index] is False:
                            v_u = index
                            break
                    if v_u == -1:
                        break
                    object.data.vertices[v_u].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_linked()

                    # add material
                    new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s_COLOR%d" % (object.name, map_tag, tag_index))
                    object.data.materials.append(new_mat)
                    object.active_material_index = len(object.data.materials) - 1
                    bpy.ops.object.material_slot_assign()
                    tag_index += 1

                    # vrtx_group_name = BM_IterableData_GetNewUniqueName_Simple(object.vertex_groups, "bm_material_backup_COLOR%d" % tag_index)
                    # object.vertex_groups.new(name=vrtx_group_name)
                    # bpy.ops.object.vertex_group_assign()
                    # tag_index += 1

                    for index, v in enumerate(object.data.vertices):
                        if v.select:
                            vertices_processed[index] = True

                bpy.ops.object.mode_set(mode='EDIT')

            # highpolies - add material and assign in to the whole object
            if map.map_matid_data == 'OBJECTS':
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_all(action='SELECT')

                # add material
                new_mat = bpy.data.materials.new("BM_CustomMaterial_%s_%s_COLOR" % (object.name, map_tag))
                object.data.materials.append(new_mat)
                object.active_material_index = len(object.data.materials) - 1
                bpy.ops.object.material_slot_assign()

        # exit edit mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)

def Map_MapPreview_ReassignMaterials_Restore(self, context):
    object_item = BM_Object_Get(self, context)
    if any([object_item[1] is False, object_item[0].nm_is_universal_container, object_item[0].nm_is_local_container]):
        return

    # collecting objects from which remove bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item[0].global_object_name]
    if len(source_object) == 0:
        return
    objects = [source_object[0]]
    highpolies = object_item[0].hl_highpoly_table
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])
    for map in object_item[0].global_maps:
        for highpoly in map.hl_highpoly_table:
            source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
            if len(source_highpoly) == 0:
                continue
            objects.append(source_highpoly[0])
    
    if len(objects) == 0:
        return

    # deselect all objects
    for ob in context.scene.objects:
        ob.select_set(False)
    bpy.ops.object.mode_set(mode='OBJECT')
                        
    # no matter what preview with reassignmats,
    # bm_nodes, and bm_custommaterials are removed in Map_MapPreview_CustomNodes_Remove
    # here need restore old materials assignments to mesh parts, stored in object vertex groups
    tag = "bm_material_backup_"
    for object in objects:
        # set object as active in the scene
        object.select_set(True)
        context.view_layer.objects.active = object
        bpy.ops.object.mode_set(mode='EDIT')

        # find backup vrtx_groups
        to_remove = []
        for vrtx_group_index, vrtx_group in enumerate(object.vertex_groups):
            object.vertex_groups.active_index = vrtx_group_index
            if vrtx_group.name.find(tag) == -1:
                continue
            
            for mat_index, material in enumerate(object.data.materials):
                # this vrtx_group is this material backup
                if material.name in vrtx_group.name:
                    object.active_material_index = mat_index
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.vertex_group_select()
                    bpy.ops.object.material_slot_assign()
            to_remove.append(vrtx_group)
        
        # exit edit mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)

        # remove backup vertex groups
        for vrtx_group in to_remove:
            object.vertex_groups.remove(vrtx_group)

def Map_MapPreview_CustomNodes_Remove(self, context):
    object_item = BM_Object_Get(self, context)
    if any([object_item[1] is False, object_item[0].nm_is_universal_container, object_item[0].nm_is_local_container]):
        return

    # collecting objects from which remove bm_nodes   
    source_object = [object for object in context.scene.objects if object.name == object_item[0].global_object_name]
    if len(source_object) == 0:
        return
    objects = [source_object[0]]
    highpolies = object_item[0].hl_highpoly_table
    for highpoly in highpolies:
        source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
        if len(source_highpoly) == 0:
            continue
        objects.append(source_highpoly[0])
    for map in object_item[0].global_maps:
        for highpoly in map.hl_highpoly_table:
            source_highpoly = [object for object in context.scene.objects if object.name == highpoly.global_object_name]
            if len(source_highpoly) == 0:
                continue
            objects.append(source_highpoly[0])

    # removing bm_nodes
    remove_mats = []
    for object in objects:
        mats_to_remove = []
        for mat_index, material in enumerate(object.data.materials):
            if material is None:
                continue
            if material.name.find('BM_CustomMaterial') != -1:
                remove_mats.append(material)
                mats_to_remove.append(mat_index)
                continue

            material.use_nodes = True
            to_remove = []
            for index, node in enumerate(material.node_tree.nodes):
                if node.name.find('BM_') != -1:
                    to_remove.append(index)
            for index in sorted(to_remove, reverse=True):
                material.node_tree.nodes.remove(material.node_tree.nodes[index])
        
        # removing custom bm_materials
        for mat_index in sorted(mats_to_remove, reverse=True):
            object.data.materials.pop(index=mat_index)
    
    # remove custom mats from data too
    for material in remove_mats:
        bpy.data.materials.remove(material)
