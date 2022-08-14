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
from .operators import *
from .operator_bake import BM_OT_ITEM_Bake
from .utils import BM_ITEM_Get

class BM_UL_AOL_Item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.8)   

        try:
            context.scene.objects[item.object_pointer.name]

        except KeyError:
            split.label(text=item.object_pointer.name, icon='GHOST_DISABLED')
            split.prop(item, 'use_bake', text="", icon='RESTRICT_RENDER_ON', emboss=False)
            layout.enabled = False

        else:
            split.label(text=item.object_pointer.name, icon='OUTLINER_OB_MESH')

            if item.use_source:
                split.label(text="", icon='FILE_TICK')
            else:
                if item.use_bake:
                    icon = 'RESTRICT_RENDER_OFF'
                else:
                    layout.active = False
                    icon = 'RESTRICT_RENDER_ON'
                split.prop(item, 'use_bake', text="", icon=icon, emboss=False)
            
    def invoke(self, context, event):
        pass

class BM_UL_ITEM_Maps(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text="", icon='IMAGE_DATA')
        layout.prop(item, 'map_type', text="", emboss=False)

        if item.use_bake or item.map_type.find('DISPLACEMENT') != -1 and item.bake_target == 'VERTEX_COLORS':
            icon='RESTRICT_RENDER_OFF'
        else:
            icon='RESTRICT_RENDER_ON'
            layout.active = False
        layout.prop(item, 'use_bake', text="", icon=icon, emboss=False)

    def invoke(self, context, event):
        pass

class BM_PT_MainBase(bpy.types.Panel):
    bl_label = "BakeMaster"
    bl_idname = 'BM_PT_Main'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        row.operator(BM_OT_AOL_Add.bl_idname, text="Add", icon='ADD')
        row.operator(BM_OT_AOL_Remove.bl_idname, text="Remove", icon='REMOVE')
        row.scale_y = 1.15

        refresh = False
        min_rows = 3
        for index, item in enumerate(scene.bm_aol):
            try:
                scene.objects[item.object_pointer.name]
            except KeyError:
                refresh = True
                min_rows = 4
                break

        if len(scene.bm_aol) > min_rows:
            rows = len(scene.bm_aol)
        else:
            rows = min_rows

        row = box.row()
        row.template_list('BM_UL_AOL_Item', "", scene, 'bm_aol', scene.bm_props, 'active_index', rows=rows)
        col = row.column(align=True)
        col.operator(BM_OT_AOL.bl_idname, text="", icon='TRIA_UP').control = 'UP'
        col.operator(BM_OT_AOL.bl_idname, text="", icon='TRIA_DOWN').control = 'DOWN'
        col.separator()

        if refresh:
            col.operator(BM_OT_AOL_Refresh.bl_idname, text="", icon='FILE_REFRESH')
        col.separator()
        col.operator(BM_OT_AOL_Trash.bl_idname, text="", icon='TRASH')

class BM_PT_ItemBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_ItemBase"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (len(context.scene.bm_aol))
    
    def draw_header(self, context):
        item = BM_ITEM_Get(context)

        if item[1]:
            self.layout.label(text="%s settings" % item[0].object_pointer.name, icon='OUTLINER_OB_MESH')
        else:
            self.layout.label(text="Item not found", icon='GHOST_DISABLED')

    def draw(self, context):
        pass

class BM_PT_Item_STTBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_STTBase"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (BM_ITEM_Get(context)[1])
    
    def draw_header(self, context):
        self.layout.label(text="Source to Target")#, icon='FILE_TICK')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        item = BM_ITEM_Get(context)[0]
        col = layout.column()

        if not item.use_source:
            col.prop(item, 'use_target', text="Target")

            if item.use_target:
                col.prop(item, 'source', text="Source")

                if item.source != 'NONE':
                    col.prop(item, 'use_cage', text="Cage")

                    if item.use_cage:
                        col.prop(item, 'cage_object', text="Cage Object")
                        col.prop(item, 'cage_extrusion', text="Extrusion")
                    else:
                        col.prop(item, 'cage_extrusion', text="Ray Distance")

                    if bpy.app.version >= (2, 90, 0):
                        col.prop(item, 'max_ray_distance', text="Max Ray Distance")
        else:
            col.label(text="Source for %s" % item.source_name)

class BM_PT_Item_UVMapBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_UVMapBase"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        item = BM_ITEM_Get(context)
        return (item[1] and not item[0].use_source)
    
    def draw_header(self, context):
        self.layout.label(text="UV Maps")#, icon='GROUP_UVS')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        item = BM_ITEM_Get(context)[0]
        col = layout.column()

        col.prop(item, 'active_uv', text="UV Map")
        col.prop(item, 'uv_type', text="Type")

        # col active if at least one map bake_target is IMAGE_TEXTURES
        len_maps_to_img = len(list(filter(lambda map: map.bake_target == 'IMAGE_TEXTURES', item.maps)))
        #len_maps_to_vrtx = len(list(filter(lambda map: map.bake_target == 'VERTEX_COLORS', item.maps)))
        if len(item.maps) != 0 and len_maps_to_img == 0:
            col.active = False
        else:
            col.active = True

        if item.uv_type != 'TILED':
            col = layout.column()
            col.prop(item, 'use_islands_pack', text="Include in UV Pack")

            if item.use_islands_pack:
                col.prop(context.scene.bm_props, 'use_islands_rotate', text="Rotate UV islands")
                col.prop(context.scene.bm_props, 'uv_pack_margin', text="Margin", slider=True)

class BM_PT_Item_OutputBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_OutputBase"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        item = BM_ITEM_Get(context)
        return (item[1] and not item[0].use_source)
    
    def draw_header(self, context):
        self.layout.label(text="Output")#, icon='OUTPUT')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        item = BM_ITEM_Get(context)[0]
        
        col = layout.column()
        col.prop(item, 'use_overwrite', text="Overwrite Maps Settings")
        
        if item.use_overwrite:
            if bpy.app.version >= (2, 92, 0):
                col.prop(item, 'overwrite_bake_target', text="Target")

                if item.overwrite_bake_target == 'VERTEX_COLORS':
                    return

            col.prop(item, 'overwrite_file_format', text="File Format")
            col.prop(item, 'overwrite_res_enum', text="Resolution")

            if item.overwrite_res_enum == 'CUSTOM':
                col = layout.column(align=True)
                col.prop(item, 'overwrite_res_height', text="Custom Height")
                col.prop(item, 'overwrite_res_width', text="Custom Width")

            col = layout.column()
            if bpy.app.version >= (3, 1, 0):
                col.prop(item, 'overwrite_margin_type', text="Margin Type")
            col.prop(item, 'overwrite_margin', text="Margin")
            col.prop(item, 'overwrite_use_32bit', text="32 bit Float")
            col.prop(item, 'overwrite_use_alpha', text="Alpha")

            col = layout.column()
            col.active = False if item.use_internal or item.uv_type == 'TILED' else True
            col.prop(item, 'overwrite_use_denoise', text="Denoise")
            
            if item.uv_type == 'TILED':
                col.separator(factor=1.2)
                col = layout.column(align=True)
                col.prop(item, 'overwrite_udim_start_tile', text="Start Tile")
                col.prop(item, 'overwrite_udim_end_tile', text="End Tile")

class BM_PT_Item_MapListBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_Item_MapListBase"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if len(context.scene.bm_aol):
            item = BM_ITEM_Get(context)
            return (item[1] and not item[0].use_source)
        else:
            return False
    
    def draw_header(self, context):
        self.layout.label(text="Map Settings", icon='IMAGE')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        item = BM_ITEM_Get(context)[0]
        box = layout.box()
        row = box.row()

        if len(item.maps) > 3:
            rows = len(item.maps)
        else:
            rows = 3
        
        row.template_list('BM_UL_ITEM_Maps', "", item, 'maps', item, 'maps_active_index', rows = rows)
        col = row.column(align=True)
        col.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='ADD').control = 'ADD'
        col.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='REMOVE').control = 'REMOVE'
        col.separator(factor=1.0)
        col.operator(BM_OT_ITEM_Maps.bl_idname, text="", icon='TRASH').control = 'TRASH'

class BM_PT_Item_MapBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_Item_MapBase"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if len(context.scene.bm_aol):
            item = BM_ITEM_Get(context)
            return (item[1] and not item[0].use_source and len(item[0].maps))
        else:
            return False
    
    def draw_header(self, context):
        item = BM_ITEM_Get(context)[0]
        label =  item.maps[item.maps_active_index].map_type.lower().capitalize()
        if label.find('_c_') != -1:
            label = "Cycles " + label[3:]
        self.layout.label(text=f"{label} settings")#, icon='IMAGE_DATA')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        item = BM_ITEM_Get(context)[0]
        map = item.maps[item.maps_active_index]
        stt_affect = True
        stt_affect_used = False
        use_output_sep = True
        col = layout.column()

        # Cycles maps
        if map.map_type == '_C_NORMAL':
            col.prop(map, 'normal_space', text="Space")

            sub = col.column(align=True)
            sub.prop(map, 'normal_r', text="Swizzle R")
            sub.prop(map, 'normal_g', text="G")
            sub.prop(map, 'normal_b', text="B")

        elif map.map_type == '_C_COMBINED':
            row = col.row(align=True)
            row.use_property_split = False
            row.prop(map, 'cycles_use_pass_direct', toggle=True)
            row.prop(map, 'cycles_use_pass_indirect', toggle=True)

            flow = col.grid_flow(row_major = False, columns = 0, even_columns = False, even_rows = False, align=True)

            flow.active = map.cycles_use_pass_direct or map.cycles_use_pass_indirect
            flow.prop(map, 'cycles_use_pass_diffuse')
            flow.prop(map, 'cycles_use_pass_glossy')
            flow.prop(map, 'cycles_use_pass_transmission')
            if bpy.app.version < (3, 0, 0):
                flow.prop(map, 'cycles_use_pass_ambient_occlusion')
            flow.prop(map, 'cycles_use_pass_emit')

        elif map.map_type in {'_C_DIFFUSE', '_C_GLOSSY', '_C_TRANSMISSION'}:
            row = col.row(align=True)
            row.use_property_split = False
            row.prop(map, 'cycles_use_pass_direct', toggle=True)
            row.prop(map, 'cycles_use_pass_indirect', toggle=True)
            row.prop(map, 'cycles_use_pass_color', toggle=True)
        ###

        elif map.map_type == 'NORMAL':
            col.prop(map, 'normal_space', text="Space")
            sub = col.column(align=True)
            sub.prop(map, 'normal_r', text="Swizzle R")
            sub.prop(map, 'normal_g', text="G")
            sub.prop(map, 'normal_b', text="B")
            col.prop(map, 'use_smooth_normals', text="Bake Smooth Normals")
            if map.use_smooth_normals:
                col.prop(map, 'normal_cage', text="Ray Distance")
                stt_affect = False

        elif map.map_type == 'DISPLACEMENT':
            if item.use_target and item.source != 'NONE' and map.use_source_target:
                col.prop(map, 'displacement_subdiv_levels', text="Subdiv Levels")
                face_count = len(item.object_pointer.data.polygons) * 4 ** map.displacement_subdiv_levels #future face count
                col.label(text="Face count while baking: " + str(face_count))
            else:
                use_output_sep = False

        #elif map.map_type == 'EMISSION':
        #    col.prop(map, 'emission_use_mask', text="Mask")

        elif map.map_type == 'AO':
            col.prop(map, 'ao_use_preview', text="Preview")
            col.prop(map, 'ao_use_default', text="Default")
            if not map.ao_use_default:
                col.prop(map, 'ao_samples', text="Samples", slider=True)
                col.prop(map, 'ao_distance', text="Distance")
                col = layout.column(align=True)
                col.prop(map, 'ao_black_point', text="Blacks", slider=True)
                col.prop(map, 'ao_white_point', text="Whites", slider=True)
                col = layout.column(align=True)
                col.prop(map, 'ao_brightness', text="Brightness")
                col.prop(map, 'ao_contrast', text="Contrast")
                col.prop(map, 'ao_opacity', text="Opacity", slider=True)
                col = layout.column()
                col.prop(map, 'ao_use_local', text="Only Local")
                col.prop(map, 'ao_use_invert', text="Invert", slider=True)

        elif map.map_type == 'CAVITY':
            col.prop(map, 'cavity_use_preview', text="Preview")
            col.prop(map, 'cavity_use_default', text="Default")
            if not map.cavity_use_default:
                col = layout.column(align=True)
                col.prop(map, 'cavity_black_point', text="Blacks", slider=True)
                col.prop(map, 'cavity_white_point', text="Whites", slider=True)
                col = layout.column()
                col.prop(map, 'cavity_power', text="Power")
                col.prop(map, 'cavity_use_invert', text="Invert", slider=True)

        elif map.map_type == 'CURVATURE':
            col.prop(map, 'curv_use_preview', text="Preview")
            col.prop(map, 'curv_use_default', text="Default")
            if not map.curv_use_default:
                col.prop(map, 'curv_samples', text="Samples", slider=True)
                col.prop(map, 'curv_radius', text="Radius")
                col = layout.column(align=True)
                col.prop(map, 'curv_edge_contrast', text="Edge")
                col.prop(map, 'curv_body_contrast', text="Body")
                col = layout.column()
                col.prop(map, 'curv_use_invert', text="Invert", slider=True)

        elif map.map_type == 'THICKNESS':
            col.prop(map, 'thick_use_preview', text="Preview")
            col.prop(map, 'thick_use_default', text="Default")
            if not map.thick_use_default:
                col.prop(map, 'thick_samples', text="Samples", slider=True)
                col.prop(map, 'thick_distance', text="Distance")
                col = layout.column(align=True)
                col.prop(map, 'thick_black_point', text="Blacks", slider=True)
                col.prop(map, 'thick_white_point', text="Whites", slider=True)
                col = layout.column(align=True)
                col.prop(map, 'thick_brightness', text="Brightness")
                col.prop(map, 'thick_contrast', text="Contrast")
                col = layout.column()
                col.prop(map, 'thick_use_invert', text="Invert", slider=True)

        #elif map.map_type == 'MATID':
            #col.prop(map, 'matid_source', text="Source")
            #col.prop(map, 'matid_algorithm', text="Algorithm")

        elif map.map_type == 'XYZMASK':
            col = layout.column(align=True)
            col.prop(map, 'xyzmask_use_x', text="X")
            col.prop(map, 'xyzmask_use_y', text="Y")
            col.prop(map, 'xyzmask_use_z', text="Z")
            col.prop(map, 'xyzmask_use_preview', text="Preview")     
            col.prop(map, 'xyzmask_use_default', text="Default")
            if not map.xyzmask_use_default:
                col = layout.column(align=True)
                col.prop(map, 'xyzmask_coverage', text="Coverage")
                col.prop(map, 'xyzmask_saturation', text="Saturation")
                col = layout.column()
                col.prop(map, 'xyzmask_opacity', text="Opacity", slider=True)
                col.prop(map, 'xyzmask_use_invert', text="Invert", slider=True)

        elif map.map_type == 'GRADIENT':
            col.prop(map, 'gmask_use_preview', text="Preview")
            col.prop(map, "gmask_type", text="Type")
            col = layout.column(align=True)
            col.prop(map, "gmask_location_x", text="Location X")
            col.prop(map, "gmask_location_y", text="Location Y")
            col.prop(map, "gmask_location_z", text="Location Z")
            col = layout.column(align=True)
            col.prop(map, "gmask_rotation_x", text="Rotation X")
            col.prop(map, "gmask_rotation_y", text="Rotation Y")
            col.prop(map, "gmask_rotation_z", text="Rotation Z")
            col = layout.column()
            col.prop(map, 'gmask_use_default', text="Default")
            if not map.gmask_use_default: 
                col = layout.column(align=True)
                col.prop(map, "gmask_scale_x", text="Scale X")
                col.prop(map, "gmask_scale_y", text="Scale Y")
                col.prop(map, "gmask_scale_z", text="Scale Z")
                col = layout.column(align=True)
                col.prop(map, 'gmask_coverage', text="Coverage")
                col.prop(map, 'gmask_contrast', text="Contrast")
                col = layout.column(align=True)
                col.prop(map, 'gmask_saturation', text="Saturation")
                col.prop(map, 'gmask_opacity', text="Opacity", slider=True)
                col.prop(map, 'gmask_use_invert', text="Invert", slider=True)
        
        else:
            use_output_sep = False

        if stt_affect and item.use_target and item.source != 'NONE':
            if use_output_sep:
                col.separator(factor=2.0)
            col.prop(map, 'use_source_target', text="Affect by Source")
            stt_affect_used = True

        # Map Output Settings
        if use_output_sep or stt_affect_used:
            col.separator(factor=2.0)

        col = layout.column()
        if bpy.app.version >= (2, 92, 0):
            col.prop(map, 'bake_target', text="Target")

            if map.bake_target == 'VERTEX_COLORS':
                return

        col.prop(map, 'file_format', text="File Format")
        col.prop(map, 'res_enum', text="Resolution")

        if map.res_enum == 'CUSTOM':
            col = layout.column(align=True)
            col.prop(map, 'res_height', text="Custom Height")
            col.prop(map, 'res_width', text="Custom Width")

        col = layout.column()
        if bpy.app.version >= (3, 1, 0):
            col.prop(map, 'margin_type', text="Margin Type")
        col.prop(map, 'margin', text="Margin")
        col.prop(map, 'use_32bit', text="32 bit Float")
        col.prop(map, 'use_alpha', text="Alpha")

        col = layout.column()
        col.active = False if item.use_internal or item.uv_type == 'TILED' else True
        col.prop(map, 'use_denoise', text="Denoise")

        if item.uv_type == 'TILED':
            col.separator(factor=1.2)
            col = layout.column(align=True)
            if item.uv_type == 'TILED':
                col.prop(map, 'udim_start_tile', text="Start Tile")
                col.prop(map, 'udim_end_tile', text="End Tile")

class BM_PT_Item_MainBakeBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_Item_MainBakeBase"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return len(context.scene.bm_aol)

    def draw_header(self, context):
        self.layout.label(text="Bake Settings", icon='RENDER_STILL')

    def draw(self, context):
        pass

class BM_PT_Item_BakeBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_Item_BakeBase"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if len(context.scene.bm_aol):
            item = BM_ITEM_Get(context)
            return (item[1] and not item[0].use_source)
        else:
            return False

    def draw_header(self, context):
        item = BM_ITEM_Get(context)[0]
        self.layout.label(text="%s Bake Settings" % item.object_pointer.name)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        item = BM_ITEM_Get(context)[0]
        col = layout.column()

        if len(list(filter(lambda map: map.bake_target == 'IMAGE_TEXTURES', item.maps))):
            col.prop(item, 'use_material', text="Material")
            col.prop(item, 'use_internal', text="Internal")

            if not item.use_internal:
                col.prop(item, 'output_filepath', text="")
                col.prop(item, 'use_subfolder', text="Subfolder")
                
                if item.use_subfolder:
                    col.prop(item, 'subfolder_name', text="Subfolder Name")

            col.prop(item, 'batch_name', text="Batch Name")
            col.separator(factor=1.0)
            #col.prop(item, 'use_save_log', text="Save Log")
            col_bd = layout.column()
            col_bd.prop(item, 'bake_device', text="Bake Device")

            col = layout.column()
            col.prop(item, 'bake_use_adaptive_sampling', text="Adaptive Sampling")
            
            if item.bake_use_adaptive_sampling:
                col.prop(item, 'bake_adaptive_threshold', text="Noise Threshold")
                col = layout.column(align=True)
                col.prop(item, 'bake_samples', text="Max Samples")
                col.prop(item, 'bake_min_samples', text="Min Samples")
            else:
                col.prop(item, 'bake_samples', text="Samples")

        else:
            col_bd = layout.column()
            col_bd.prop(item, 'bake_device', text="Bake Device")

        if item.bake_device != 'GPU':
            col_bd.active = True
        else:
            col_bd.active = context.preferences.addons['cycles'].preferences.has_active_device()

class BM_PT_Item_MainBakeSettingsBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = "BM_PT_Item_MainBakeSettingsBase"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        #col.prop(context.scene.bm_props, 'use_background_bake', text="Bake in the Background")
        col.prop(context.scene.bm_props, 'use_bakemaster_reset', text="Reset BakeMaster")

        col = layout.column(align=True)
        sub = col.column()
        sub.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake This", icon='RENDER_STILL').control = 'BAKE_THIS'
        
        # checking if bake_this available
        item = BM_ITEM_Get(context)[0]
        if not item.use_bake or item.use_source:
            sub.enabled = False

        # list of map with True use_bake
        active_maps = list(filter(lambda map: map.use_bake is True, item.maps))
        # enabled if any maps to bake and bake_ot is not running
        sub.enabled = all([len(active_maps) != 0, context.scene.bm_props.bake_available])

        # bake_all will be always enabled and raise OT errors
        sub = col.column()
        sub.operator(BM_OT_ITEM_Bake.bl_idname, text="Bake All", icon='RENDER_STILL').control = 'BAKE_ALL'
        sub.scale_y = 1.5
        sub.enabled = context.scene.bm_props.bake_available

        col = layout.column()
        col.prop(context.scene.bm_props, "bake_instruction", text="", icon='INFO')
        col.enabled = False

class BM_PT_Main_HelpBase(bpy.types.Panel):
    bl_label = " "
    bl_idname = 'BM_PT_Main_HelpBase'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="Help", icon='HELP')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.operator(BM_OT_Help.bl_idname, text="Documentation", icon='HELP')