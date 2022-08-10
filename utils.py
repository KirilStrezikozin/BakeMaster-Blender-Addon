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

import bpy
from .labels import BM_Labels

def BM_ActiveIndexUpdate(self, context):
    if len(context.scene.bm_aol):
        item = context.scene.bm_aol[context.scene.bm_props.active_index].object_pointer
        try:
            context.scene.objects[item.name]
        except (KeyError, UnboundLocalError):
            pass
        else:
            if not item.visible_get():
                return

            for ob in context.scene.objects:
                ob.select_set(False)

            item.select_set(True)
            context.view_layer.objects.active = item

def BM_ITEM_Get(context):
    item = [context.scene.bm_aol[context.scene.bm_props.active_index], True] 
    try:
        context.scene.objects[item[0].object_pointer.name]
    except (KeyError, UnboundLocalError):
        item[1] = False
    return item

def BM_ITEM_UVLayers(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index].object_pointer.data
    uv_layers = []

    if len(item.uv_layers):
        for uv_layer in item.uv_layers:
            uv_layers.append((str(uv_layer.name), uv_layer.name, ""))
    else:
        uv_layers.append(('NONE_AUTO_CREATE', "Auto Unwrap", ""))
    return uv_layers

def BM_ITEM_UVType_Items(self, context):
    if bpy.app.version >= (3, 2, 0):
        items = [('SINGLE', "Single (single tile)", ""), ('TILED', "Tiled (UDIMs)", "")]
    else:
        items = [('SINGLE', "Single (single tile)", "")]
    
    return items

def BM_ITEM_Map_BakeTarget_Items(self, context):
    items = [('IMAGE_TEXTURES', "Image Textures", "Bake to image texture file")]
             #('VERTEX_COLORS', "Vertex Colors", "Bake to vertex color layer")]
             # baking to vertex color layer is not configured
    
    return items

def BM_ITEM_Maps_Items(self, context):
    if bpy.app.version >= (3, 0, 0):
        items = [('', "Material-based", "PBR-based maps to bake from existing material or object data"),
                 ('ALBEDO', "Albedo", "Color image texture containing color without shadows and highlights"),
                 ('METALNESS', "Metalness", "Image texture for determining metal and non-metal parts of the object"),
                 ('ROUGHNESS', "Roughness", "Image texture for determining roughness across the surface of the object"),
                 ('NORMAL', "Normal", "Image texture for simulating high details without changing the number of polygons"),
                 ('DISPLACEMENT', "Displacement", "Height map used for displacing mesh polygons"),
                 ('OPACITY', "Opacity", "Image texture for determining transparent and opaque parts of the object"),
                 ('EMISSION', "Emission", "Image texture for determining emissive parts of the object"),
                 ('', "Node-based", "Special maps for masking and details"),
                 ('AO', "AO", "Ambient Occlusion map contains lightning data"),
                 ('CAVITY', "Cavity", "Image texture map to store small crevice details"),
                 ('CURVATURE', "Curvature", "Image texture map to store object edge data"),
                 ('THICKNESS', "Thickness", "Ambient Occlusion map that casts rays from the surface to the inside. Often used for SSS or masking"),
                 #('MATID', "Material ID", ""),
                 ('XYZMASK', "XYZ Mask", "Contains data of rays casted from particular axis"),
                 ('GRADIENT', "Gradient Mask", "Black and white gradient mask for masking"),
                 ('', "Default Cycles", "Default Cycles map passes"),
                 ('_C_COMBINED', "Combined", "Bakes all materials, textures, and lighting contribution except specularity"),
                 ('_C_AO', "Ambient Occlusion", "Ambient Occlusion map contains lightning data"),
                 ('_C_SHADOW', "Shadow", "Bakes shadows and lighting"),
                 ('_C_POSITION', "Position", "Indicates object parts location in the UV space"),
                 ('_C_NORMAL', "Normal", "Bakes normals to an RGB image"),
                 ('_C_UV', "UV", "Mapped UV coordinates, used to represent where on a mesh a texture gets mapped too"),
                 ('_C_ROUGHNESS', "Roughness", "Bakes the roughness pass of a material"),
                 ('_C_EMIT', "Emit", "Bakes Emission, or the Glow color of a material"),
                 ('_C_ENVIRONMENT', "Environment", "Bakes the environment (i.e. the world surface shader defined for the scene) onto the selected object(s) as seen by rays cast from the world origin."),
                 ('_C_DIFFUSE', "Diffuse", "Bakes the diffuse pass of a material"),
                 ('_C_GLOSSY', "Glossy", "Bakes the glossiness pass of a material"),
                 ('_C_TRANSMISSION', "Transmission", "Bakes the transmission pass of a material")]
    else:
        items = [('', "Material-based", "PBR-based maps to bake from existing material or object data"),
                 ('ALBEDO', "Albedo", "Color image texture containing color without shadows and highlights"),
                 ('METALNESS', "Metalness", "Image texture for determining metal and non-metal parts of the object"),
                 ('ROUGHNESS', "Roughness", "Image texture for determining roughness across the surface of the object"),
                 ('NORMAL', "Normal", "Image texture for simulating high details without changing the number of polygons"),
                 ('DISPLACEMENT', "Displacement", "Height map used for displacing mesh polygons"),
                 ('OPACITY', "Opacity", "Image texture for determining transparent and opaque parts of the object"),
                 ('EMISSION', "Emission", "Image texture for determining emissive parts of the object"),
                 ('', "Node-based", "Special maps for masking and details"),
                 ('AO', "AO", "Ambient Occlusion map contains lightning data"),
                 ('CAVITY', "Cavity", "Image texture map to store small crevice details"),
                 ('CURVATURE', "Curvature", "Image texture map to store object edge data"),
                 ('THICKNESS', "Thickness", "Ambient Occlusion map that casts rays from the surface to the inside. Often used for SSS or masking"),
                 #('MATID', "Material ID", ""),
                 ('XYZMASK', "XYZ Mask", "Contains data of rays casted from particular axis"),
                 ('GRADIENT', "Gradient Mask", "Black and white gradient mask for masking"),
                 ('', "Default Cycles", "Default Cycles map passes"),
                 ('_C_COMBINED', "Combined", "Bakes all materials, textures, and lighting contribution except specularity"),
                 ('_C_AO', "Ambient Occlusion", "Ambient Occlusion map contains lightning data"),
                 ('_C_SHADOW', "Shadow", "Bakes shadows and lighting"),
                 ('_C_NORMAL', "Normal", "Bakes normals to an RGB image"),
                 ('_C_UV', "UV", "Mapped UV coordinates, used to represent where on a mesh a texture gets mapped too"),
                 ('_C_ROUGHNESS', "Roughness", "Bakes the roughness pass of a material"),
                 ('_C_EMIT', "Emit", "Bakes Emission, or the Glow color of a material"),
                 ('_C_ENVIRONMENT', "Environment", "Bakes the environment (i.e. the world surface shader defined for the scene) onto the selected object(s) as seen by rays cast from the world origin."),
                 ('_C_DIFFUSE', "Diffuse", "Bakes the diffuse pass of a material"),
                 ('_C_GLOSSY', "Glossy", "Bakes the glossiness pass of a material"),
                 ('_C_TRANSMISSION', "Transmission", "Bakes the transmission pass of a material")]

    return items

def BM_ITEM_UseTargetUpdate(self, context):
    if not self.use_target:
        for index, item in enumerate(context.scene.bm_aol):
            if item.use_source and item.source_name == self.object_pointer.name:
                self.source = 'NONE'
                item.use_source = False
                item.source_name = ""
                break
    else:
        BM_ITEM_SourceUpdate(self, context)

    #BM_ITEM_RemoveLocalPreviews(self, context)

def BM_ITEM_Source(self, context):
    source = [('NONE', "None", "")]

    for index, item in enumerate(context.scene.bm_aol):
        try:
            context.scene.objects[item.object_pointer.name]
        except KeyError:
            pass
        else:
            if not item.use_target:
                if item.source_name == self.object_pointer.name or not item.use_source:
                    source.append((str(index), item.object_pointer.name, ""))
    return source

def BM_ITEM_SourceUpdate(self, context):
    BM_ITEM_RemoveLocalPreviews(self, context)

    if self.source == '':
        self.source = 'NONE'

    if self.source == 'NONE':
        for index, item in enumerate(context.scene.bm_aol):
            if item.source_name == self.object_pointer.name:
                item.use_source = False
                item.source_name = ""
                break
    else:
        for index, item in enumerate(context.scene.bm_aol):
            if item.use_source and item.source_name == self.object_pointer.name:
                item.use_source = False
                item.source_name = ""
                break

        for index, item in enumerate(context.scene.bm_aol):
            if str(index) == self.source:
                item.use_source = True
                item.source_name = self.object_pointer.name
                break

def BM_ITEM_OverwriteUpdate(self, context):
    if self.use_overwrite:
        for index, map in enumerate(self.maps):
            map.bake_target = self.overwrite_bake_target
            map.use_denoise = self.overwrite_use_denoise
            map.file_format = self.overwrite_file_format
            map.res_enum = self.overwrite_res_enum
            map.res_height = self.overwrite_res_height
            map.res_weight = self.overwrite_res_width
            map.margin = self.overwrite_margin
            map.margin_type = self.overwrite_margin_type
            map.use_32bit = self.overwrite_use_32bit
            map.use_alpha = self.overwrite_use_alpha
            map.udim_start_tile = self.overwrite_udim_start_tile
            map.udim_end_tile = self.overwrite_udim_end_tile

def BM_ITEM_BatchNameUpdate(self, context):
    try:
        if "item" not in self.batch_name:
            self.batch_name = f"item_{self.batch_name}"

        args = ['index',
                'item',
                'sourcetarget',
                'uvpacked',
                'map',
                'res',
                'float',
                'alpha']

        args_used = [arg for arg in args if arg in self.batch_name]
        args_names_starters = [arg[0] for arg in args_used]
        batch_name_new = ""

        for start_index in range(len(self.batch_name)):

            # if the itered string won't start on any of the symbols in args -> skip it to reduce number of iterations
            if self.batch_name[start_index] not in args_names_starters:
                continue

            # to see how the algo works, type print(self.batch_name[start_index:end_index]) here
            for end_index in range(start_index, len(self.batch_name) + 1): # len() + 1, because we need to check the last symbol

                if self.batch_name[start_index:end_index] in args_used: # if itered srting is an arg -> add it to the batch_name_new
                    batch_name_new += "{}_".format(self.batch_name[start_index:end_index])
                    break

        batch_name_new = batch_name_new[:(len(batch_name_new) - 1)] # remove last '_'

        if self.batch_name != batch_name_new:
            self.batch_name = batch_name_new

    except RecursionError:
        pass

def BM_MAP_MaterialUpdate(self, material, map_index):
    pass

def BM_MAP_Preview_SetMaterial(self, context, map_index):
    pass

def BM_MAP_Preview_CleanMaterial(context):
    pass

def BM_MAP_Preview_LocalUpdate(self, context, map_index):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]

    props = ['ao_use_preview', 'cavity_use_preview', 'curv_use_preview',
             'thick_use_preview', 'xyzmask_use_preview', 'gmask_use_preview']
    
    for index, map in enumerate(item.maps):
        for i in range(len(props)):
            if i != map_index:
                setattr(map, props[i], False)

def BM_MAP_Preview_AO(self, context):
    BM_MAP_Preview_CleanMaterial(context)
    if self.ao_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 0) 
        BM_MAP_Preview_SetMaterial(self, context, 0)

def BM_MAP_Preview_Cavity(self, context):
    BM_MAP_Preview_CleanMaterial(context)
    if self.cavity_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 1)
        BM_MAP_Preview_SetMaterial(self, context, 1)

def BM_MAP_Preview_Curvature(self, context):
    BM_MAP_Preview_CleanMaterial(context)
    if self.curv_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 2)
        BM_MAP_Preview_SetMaterial(self, context, 2)

def BM_MAP_Preview_Thickness(self, context):
    BM_MAP_Preview_CleanMaterial(context)
    if self.thick_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 3)
        BM_MAP_Preview_SetMaterial(self, context, 3)

def BM_MAP_Preview_NormalMask(self, context):
    BM_MAP_Preview_CleanMaterial(context)
    if self.xyzmask_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 4)
        BM_MAP_Preview_SetMaterial(self, context, 4)

def BM_MAP_Preview_GradientMask(self, context):
    BM_MAP_Preview_CleanMaterial(context)
    if self.gmask_use_preview:
        BM_MAP_Preview_LocalUpdate(self, context, 5)
        BM_MAP_Preview_SetMaterial(self, context, 5)

def BM_MAP_AO_MaterialUpdate(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]

    if self.ao_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 0)
            
def BM_MAP_Cavity_MaterialUpdate(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.cavity_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 1)         

def BM_MAP_Curvature_MaterialUpdate(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.curv_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 2)
            
def BM_MAP_Thickness_MaterialUpdate(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.thick_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 3)          

def BM_MAP_NormalMask_MaterialUpdate(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.xyzmask_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 4)       

def BM_MAP_GradientMask_MaterialUpdate(self, context):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]
    if item.use_target and item.source != 'NONE' and self.use_source_target:
        item = context.scene.bm_aol[int(item.source)]
        
    if self.gmask_use_preview:
        for mat in item.object_pointer.data.materials:
            if mat is None:
                continue
            BM_MAP_MaterialUpdate(self, mat, 5)

def BM_ITEM_RemoveLocalPreviews(self, context):
    props = ['ao_use_preview', 'cavity_use_preview', 'curv_use_preview',
             'thick_use_preview', 'xyzmask_use_preview', 'gmask_use_preview']

    #for item_index, item in enumerate(context.scene.bm_aol):
    item = context.scene.bm_aol[context.scene.bm_props.active_index]

    for index, map in enumerate(item.maps):
        for i in range(len(props)):
            setattr(map, props[i], False)

def BM_MAP_AffectBySouce_Update(self, context):
    props = ['ao_use_preview', 'cavity_use_preview', 'curv_use_preview',
             'thick_use_preview', 'xyzmask_use_preview', 'gmask_use_preview']

    # if there is any preview True in props -> update it (set false, set true)
    try:
        active_preview = [prop for prop in props if getattr(self, prop) is True][0]
    except:
        return

    setattr(self, active_preview, False)
    setattr(self, active_preview, True)

# auto set subdiv_levels -> not implemented
def BM_MAP_AutoSetSubdivLevels(self, context):
    try:
        item = context.scene.bm_aol[context.scene.bm_props.active_index]
        subdiv_levels = 1

        if item.use_target and item.source != 'NONE' and self.use_source_target:
            item_poly_count = len(item.object_pointer.data.polygons)
            source_poly_count = len(context.scene.bm_aol[int(item.source)].object_pointer.data.polygons)

            while subdiv_levels < 10 and (item_poly_count * 4 ** subdiv_levels) < source_poly_count:
                subdiv_levels += 1

        if self.displacement_subdiv_levels != subdiv_levels:
            self.displacement_subdiv_levels = subdiv_levels

    except RecursionError:
        pass