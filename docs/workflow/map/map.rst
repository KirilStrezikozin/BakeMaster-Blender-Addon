.. |ao| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/AO.png
    :width: 250 px
    :alt: ao

.. |albedo| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Albedo.png
    :width: 250 px
    :alt: albedo

.. |cavity| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Cavity.png
    :width: 250 px
    :alt: cavity

.. |curvature| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Curvature.png
    :width: 250 px
    :alt: curvature

.. |gradient| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Gradient.png
    :width: 250 px
    :alt: gradient

.. |metalness| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Metalness.png
    :width: 250 px
    :alt: metalness

.. |normal| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Normal.png
    :width: 250 px
    :alt: normal

.. |position| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Position.png
    :width: 250 px
    :alt: position

.. |shadow| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Shadow.png
    :width: 250 px
    :alt: shadow

.. |thickness| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/Thickness.png
    :width: 250 px
    :alt: thickness

.. |uv| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/UV.png
    :width: 250 px
    :alt: uv

.. |xyzmask| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/map/map_page/XYZMask.png
    :width: 250 px
    :alt: xyzmask

===
Map
===

.. py:class:: map

.. note:: 
    This page contains all Map properties references and short descriptions, and the Map definition itself.

    Each section has a code block with a script reference and another code block with a Blender Python Data Path to access the value in Python. The ``map`` class can be accessed by the following expression, where ``__item_index__`` is an index of a key in the List of Objects, ``__map_index__`` is an index of a key in the List of Maps, :

    .. code-block:: python
        :caption: Accessing the Map class

        map = bpy.context.scene.bm_aol[__item_index__].maps[__map_index__]

    Further, the ``map`` will be mentioned as a reference to the initial Object's Map class.

BakeMaster Map is a BakeMaster List of Maps class unit. The Map is a Property Group holding child properties that are accessed in the Bake Operator.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    class BM_Item_Map(bpy.types.PropertyGroup):
        ...

.. code-block:: python
    
    map

List of Maps Active Index
=========================

.. py:property:: object.maps_active_index

Active List of Maps key index is stored in this value. Not used in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    maps_active_index : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].maps_active_index

List of Maps
============

.. py:class:: maps
    
List of Maps is a ``bpy_prop_collection_idprop`` collection class that contains keys. The key is the Map Property Group class.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    maps : bpy.props.CollectionProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].maps

Use Bake
========

.. py:property:: map.use_bake

``use_bake`` defines whether to include the Map in the bake. If ``False``, then the Map is excluded and appears greyed out in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_bake : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.use_bake

Map Type
========

Type of the Map Pass as a map bake type. There are 25 different map pass types available and listed in the table below:

PBR-based
---------

+---------------------+------------------------------------------------------------------------------------+
| * Albedo            | Color image texture containing color without shadows and highlights                |
+---------------------+------------------------------------------------------------------------------------+
| * Metalness         | Image texture for determining metal and non-metal parts of the object              |
+---------------------+------------------------------------------------------------------------------------+
| * Roughness         | Image texture for determining roughness across the surface of the object           |
+---------------------+------------------------------------------------------------------------------------+
| * Normal            || Image texture for simulating high details without changing the                    |
|                     || number of polygons                                                                |
+---------------------+------------------------------------------------------------------------------------+
| * Displacement      | Height map used for displacing mesh polygons                                       |
+---------------------+------------------------------------------------------------------------------------+
| * Opacity           | Image texture for determining transparent and opaque parts of the object           |
+---------------------+------------------------------------------------------------------------------------+
| * Emission          | Image texture for determining emissive parts of the object                         |
+---------------------+------------------------------------------------------------------------------------+

Special Masks
-------------

+---------------------+------------------------------------------------------------------------------------+
| * AO                | Ambient Occlusion map contains lightning data                                      |
+---------------------+------------------------------------------------------------------------------------+
| * Cavity            | Image texture map to store small crevice details                                   |
+---------------------+------------------------------------------------------------------------------------+
| * Curvature         | Image texture map to store object edge data                                        |
+---------------------+------------------------------------------------------------------------------------+
|  * Thickness        || Ambient Occlusion map that casts rays from the surface to the inside.             |
|                     || Often used for SSS or masking. Note that Thickness is scale-dependent,            |
|                     || meaning the map will be not visible for small-scale models                        |
+---------------------+------------------------------------------------------------------------------------+
| * XYZ Mask          | Contains data of rays that are casted from a particular axis                       |
+---------------------+------------------------------------------------------------------------------------+
| * Gradient Mask     | Black and white gradient mask for masking                                          |
+---------------------+------------------------------------------------------------------------------------+

Default Cycles
--------------

+---------------------+------------------------------------------------------------------------------------+
| * Combined          | Bakes all materials, textures, and lighting contributions except specularity       |
+---------------------+------------------------------------------------------------------------------------+
| * Ambient Occlusion | Ambient Occlusion map contains lightning data                                      |
+---------------------+------------------------------------------------------------------------------------+
| * Shadow            | Bakes shadows and lighting                                                         |
+---------------------+------------------------------------------------------------------------------------+
| * Position          | Indicates object parts' location in the UV space                                   |
+---------------------+------------------------------------------------------------------------------------+
| * Normal            | Bakes normals to an RGB image                                                      |
+---------------------+------------------------------------------------------------------------------------+
| * UV                || Mapped UV coordinates, used to represent where on a mesh a texture                |
|                     || gets mapped too                                                                   |
+---------------------+------------------------------------------------------------------------------------+
| * Roughness         | Bakes the roughness pass of a material                                             |
+---------------------+------------------------------------------------------------------------------------+
| * Emit              | Bakes Emission, or the Glow color of a material                                    |
+---------------------+------------------------------------------------------------------------------------+
|  * Environment      || Bakes the environment (i.e. the world surface shader defined for the scene)       |
|                     || onto the selected object(s) as seen by rays cast from the world origin.           |
+---------------------+------------------------------------------------------------------------------------+
| * Diffuse           | Bakes the diffuse pass of a material                                               |
+---------------------+------------------------------------------------------------------------------------+
| * Glossy            | Bakes the glossiness pass of a material                                            |
+---------------------+------------------------------------------------------------------------------------+
| * Transmission      | Bakes the transmission pass of a material                                          |
+---------------------+------------------------------------------------------------------------------------+

Baked Maps Examples
-------------------

Below are presented baked maps of some map pass types:

+------------+------------+
| AO         | Albedo     |
+------------+------------+
| |ao|       | |albedo|   |
+------------+------------+
| Cavity     | Curvature  |
+------------+------------+
| |cavity|   | |curvature||
+------------+------------+
| Gradient   | Metalness  |
+------------+------------+
| |gradient| | |metalness||
+------------+------------+
| Normal     | Position   |
+------------+------------+
| |normal|   | |position| |
+------------+------------+
| Shadow     | Thickness  |
+------------+------------+
| |shadow|   | |thickness||
+------------+------------+
| UV         | XYZMask    |
+------------+------------+
| |uv|       | |xyzmask|  |
+------------+------------+


.. tip:: 
    As long as adding a new map pass created a completely new instance of a map class, you can have multiple map classes with the same settings, for example:

.. py:property:: map.map_type

    You can bake an unlimited number of Cavity maps for the Object.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    map_type : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.map_type

Map Output Related Properties
=============================

Bake Target
-----------

.. py:property:: map.bake_target

Map's bake target, in Image Textures or Vertex Colors. Currently, only Image Textures are supported.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    bake_target : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.bake_target

Map Denoising
-------------

.. py:property:: map.use_denoise

Map's output denoising use. If ``True``, all Object's maps will be denoised and despeckled.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_denoise : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.use_denoise

File Format
-----------

.. py:property:: map.file_format

Map's file format, in ``BMP, PNG, JPEG, TIFF, EXR``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    file_format : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.file_format

Resolution
----------

.. py:property:: map.res_enum

Map's output resolution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    res_enum : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.res_enum

Height Resolution
-----------------

.. py:property:: map.res_height

If the ``res_enum`` value is ``custom``, this property stores custom output image height.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    res_height : bpy.props.IntProperty
    ...

.. code-block:: python

    map.res_height

Width Resolution
----------------

.. py:property:: map.res_width

If the ``res_enum`` value is ``custom``, this property stores the custom output image width.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    res_width : bpy.props.IntProperty
    ...

.. code-block:: python

    map.res_width

Margin
------

.. py:property:: map.margin

Map's margin value as a bake post-processing filter.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    margin : bpy.props.IntProperty
    ...

.. code-block:: python

    map.margin

Margin Type
-----------

.. py:property:: map.margin_type

Map's margin type, in ``ADJACENT_FACES, EXTEND``.

- Adjacent Faces - Use pixels from adjacent faces across UV seams
- Extend - Extend border pixels outwards.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    margin_type : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.margin_type

Use 32bit Float
---------------

.. py:property:: map.use_32bit

Map's 32bit Float color depth usage.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_32bit : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.use_32bit

Use Alpha
---------

.. py:property:: map.use_alpha

Map's Alpha color channel usage.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_alpha : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.use_alpha

Map Source to Target Related Properties
=======================================

Affect by Source to Target Settings
-----------------------------------

.. py:property:: map.use_source_target

If Source to Target settings are configured for the Object, each map will display ``affect by source target`` property. If it is ``True``, Source to Target settings will affect the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_source_target : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.use_source_target

Map UV Settings Related Properties
==================================

UDIM Start Tile
---------------

.. py:property:: map.udim_start_tile

UDIM tile index of UDIM tiles baking range. UDIMs' baking range is used for defining UDIM tiles' baking boundaries. The baked result will only affect a specified range of tiles (Start Tile Index - End Tile Index).

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    udim_start_tile : bpy.props.IntProperty
    ...

.. code-block:: python

    map.udim_start_tile

UDIM End Tile
-------------

.. py:property:: map.udim_end_tile

UDIM tile index of UDIM tiles baking range. UDIMs' baking range is used for defining UDIM tiles' baking boundaries. The baked result will only affect a specified range of tiles (Start Tile Index - End Tile Index).

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    udim_end_tile : bpy.props.IntProperty
    ...

.. code-block:: python

    map.udim_end_tile

Default Cycles Map Related Properties
=====================================

Use Direct Pass
---------------

.. py:property:: map.cycles_use_pass_direct

Add direct lighting contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_direct : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_direct

Use Indirect Pass
-----------------

.. py:property:: map.cycles_use_pass_indirect

Add indirect lighting contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_indirect : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_indirect

Use Color Pass
--------------

.. py:property:: map.cycles_use_pass_color

Color the pass.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_color : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_color

Use Diffuse Pass
----------------

.. py:property:: map.cycles_use_pass_diffuse

Add diffuse contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_diffuse : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_diffuse


Use Glossy Pass
---------------

.. py:property:: map.cycles_use_pass_glossy

Add glossy contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_glossy : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_glossy


Use Transmission Pass
---------------------

.. py:property:: map.cycles_use_pass_transmission

Add transmission contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_transmission : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_transmission


Use Ambient Occlusion Pass
--------------------------

.. py:property:: map.cycles_use_pass_ambient_occlusion

Add Ambient Occlusion contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_ambient_occlusion : bpy.props.
    ...BoolProperty


Use Emit Pass
-------------

.. py:property:: map.cycles_use_pass_emit

Add emit contribution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cycles_use_pass_emit : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cycles_use_pass_emit

Map Normal Settings Related Properties
======================================

Normal Space
------------

.. py:property:: map.normal_space

Choose a normal space for baking in ``Tangent, Object``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    normal_space : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.normal_space

Red Channel Axis
----------------

.. py:property:: map.normal_r

Axis to bake in the red channel in ``+X, +Y, +Z, -X, -Y, -Z``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    normal_r : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.normal_r


Green Channel Axis
------------------

.. py:property:: map.normal_g

Axis to bake in the green channel in ``+X, +Y, +Z, -X, -Y, -Z``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    normal_g : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.normal_g


Blue Channel Axis
-----------------

.. py:property:: map.normal_b

Axis to bake in the blue channel in ``+X, +Y, +Z, -X, -Y, -Z``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    normal_b : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.normal_b

Use Smooth Normals Bake
-----------------------

.. py:property:: map.use_smooth_normals

If ``True``, faces smooth normals will be baked. A copy of the object will be made, smooth normals toggled and baked to the object as a Normal map.

.. warning:: 
    Baking smooth normals for a high-resolution object might cause a freeze when copying.

.. DANGER:: 
    There is a known bug for smooth normals baking to crash blender due to ``STACK_OVERFLOW_EXCEPTION``. Please make sure you saved your Blender file before the bake to exclude unexpected data loss.

    If Blender keeps crashing but you want to bake smooth normals, try copying the object you want to bake smooth normals for to the new Blender file and restart the bake there.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_smooth_normals : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.use_smooth_normals

Normal Cage
-----------

.. py:property:: map.normal_cage

Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    normal_cage : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.normal_cage

Map Displacement Settings Related Properties
============================================

Displacement Subdiv Levels
--------------------------

.. py:property:: map.displacement_subdiv_levels

The subdivision level defines the level of details. Keep as low as possible for optimal performance. 

.. warning:: 
    The higher the subdivision level, the longer it will take to subdivide the object when preparing multires data for Displacement Map Bake.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    displacement_subdiv_levels : bpy.props.IntProperty
    ...

.. code-block:: python

    map.displacement_subdiv_levels

Map AO Settings Related Properties
==================================

Use AO Preview
--------------

.. py:property:: map.ao_use_preview

Preview the Map in real-time in the 3D Viewport.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_use_preview : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.ao_use_preview

Use Default AO
--------------

.. py:property:: map.ao_use_default

Bake texture map using default settings.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_use_default : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.ao_use_default

AO Samples
----------

.. py:property:: map.ao_samples

racing samples count. Affects the quality. Keep as low as possible for optimal performance.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_samples: bpy.props.IntProperty
    ...

.. code-block:: python

    map.ao_samples

AO Distance
-----------

.. py:property:: map.ao_distance

Distance up to which other objects are considered to occlude the shading point.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_distance : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_distance

AO Black Point
--------------

.. py:property:: map.ao_black_point

Shadow point location on the map color gradient spectrum.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_black_point : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_black_point

AO White Point
--------------

.. py:property:: map.ao_white_point

Highlight point location on the map color gradient spectrum.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_white_point : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_white_point

AO Brightness
-------------

.. py:property:: map.ao_brightness

Map Color Brightness.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_brightness : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_brightness


AO Contrast
-------------

.. py:property:: map.ao_contrast

Map Color Contrast.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_contrast : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_contrast


AO Opacity
----------

.. py:property:: map.ao_opacity

Map Color Opacity relative to a blank color.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_opacity : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_opacity

AO Use Local
------------

.. py:property:: map.ao_use_local

Only detect occlusion from the object itself, and not others.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_use_local : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.ao_use_local

AO Use Invert
-------------

.. py:property:: map.ao_use_invert

Invert the colors of the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    ao_use_invert : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.ao_use_invert

Map Cavity Settings Related Properties
======================================

Use Cavity Preview
------------------

.. py:property:: map.cavity_use_preview

Preview the Map in real-time in the 3D Viewport.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cavity_use_preview : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cavity_use_preview


Use Default Cavity
------------------

.. py:property:: map.cavity_use_default

Bake texture map using default settings.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cavity_use_default : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.cavity_use_default


Cavity Black Point
------------------

.. py:property:: map.cavity_black_point

Shadow point location on the map color gradient spectrum.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cavity_black_point : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.cavity_black_point


Cavity White Point
------------------

.. py:property:: map.cavity_white_point

Highlight point location on the map color gradient spectrum.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cavity_white_point : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.cavity_white_point

Cavity Power
------------

.. py:property:: map.cavity_power

Cavity map color power value.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cavity_power : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.cavity_power

Cavity Use Invert
-----------------

.. py:property:: map.cavity_use_invert

Invert the colors of the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cavity_use_invert : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.cavity_use_invert

Map Curvature Settings Related Properties
=========================================

Use Curvature Preview
---------------------

.. py:property:: map.curv_use_preview

Preview the Map in real-time in the 3D Viewport.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_use_preview : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.curv_use_preview


Use Default Curvature
---------------------

.. py:property:: map.curv_use_default

Bake texture map using default settings.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_use_default : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.curv_use_default

Curvature Samples
-----------------

.. py:property:: map.curv_samples

Tracing samples count. Affects the quality. Keep as low as possible for optimal performance.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_samples: bpy.props.IntProperty
    ...

.. code-block:: python

    map.curv_samples

Curvature Radius
----------------

.. py:property:: map.curv_radius

Curvature Edge radius value. Defines how thick the edge is colored.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_radius : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.curv_radius

Curvature Edge Contrast
-----------------------

.. py:property:: map.curv_edge_contrast

Curvature Edge color contrast value.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_edge_contrast : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.curv_edge_contrast


Curvature Body Contrast
-----------------------

.. py:property:: map.curv_body_contrast

Curvature Body color contrast value.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_body_contrast : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.curv_body_contrast


Curvature Use Invert
--------------------

.. py:property:: map.curv_use_invert

Invert the colors of the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    curv_use_invert : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.curv_use_invert

Map Thickness Settings Related Properties
=========================================

Use Thickness Preview
---------------------

.. py:property:: map.thick_use_preview

Preview the Map in real-time in the 3D Viewport.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_use_preview : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.thick_use_preview


Use Default Thickness
---------------------

.. py:property:: map.thick_use_default

Bake texture map using default settings.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_use_default : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.thick_use_default


Thickness Samples
-----------------

.. py:property:: map.thick_samples

Tracing samples count. Affects the quality. Keep as low as possible for optimal performance.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_samples : bpy.props.IntProperty
    ...

.. code-block:: python

    map.thick_samples


Thickness Distance
------------------

.. py:property:: map.thick_distance

Distance up to which other objects are considered to occlude the shading point.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_distance : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.thick_distance

Thickness Black Point
---------------------

.. py:property:: map.thick_black_point

Shadow point location on the map color gradient spectrum.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_black_point : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.thick_black_point


Thickness White Point
---------------------

.. py:property:: map.thick_white_point

Highlight point location on the map color gradient spectrum.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_white_point : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.thick_white_point


Thickness Brightness
--------------------

.. py:property:: map.thick_brightness

Map Color Brightness.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_brightness : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.thick_brightness


Thickness Contrast
------------------

.. py:property:: map.thick_contrast

Map Color Contrast.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_contrast : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.thick_contrast


Thickness Use Invert
--------------------

.. py:property:: map.thick_use_invert

Invert the colors of the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    thick_use_invert : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.thick_use_invert

Map XYZ Mask Settings Related Properties
========================================

Use XYZ Mask Preview
--------------------

.. py:property:: map.xyzmask_use_preview

Preview the Map in real-time in the 3D Viewport.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_use_preview : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.xyzmask_use_preview


Use Default XYZ Mask
--------------------

.. py:property:: map.xyzmask_use_default

Bake texture map using default settings.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_use_default : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.xyzmask_use_default

XYZ Mask Use X
--------------

.. py:property:: map.xyzmask_use_x

Enable/disable X coordinate mask filter. When enabled, each polygon of the object that is visible under the specified Axis Perspective View will be occluded.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_use_x : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.xyzmask_use_x


XYZ Mask Use Y
--------------

.. py:property:: map.xyzmask_use_y

Enable/disable Y coordinate mask filter. When enabled, each polygon of the object that is visible under the specified Axis Perspective View will be occluded.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_use_y : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.xyzmask_use_y


XYZ Mask Use Z
--------------

.. py:property:: map.xyzmask_use_z

Enable/disable Z coordinate mask filter. When enabled, each polygon of the object that is visible under the specified Axis Perspective View will be occluded.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_use_z : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.xyzmask_use_z

XYZ Maks Coverage
-----------------

.. py:property:: map.xyzmask_coverage

Map range of coverage. The higher the coverage value, the larger the occluded area against its initial area.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_coverage : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.xyzmask_coverage

XYZ Mask Saturation
-------------------

.. py:property:: map.xyzmask_saturation

Map color saturation value.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_saturation : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.xyzmask_saturation


XYZ Mask Opacity
----------------

.. py:property:: map.xyzmask_opacity

Map Color Opacity relative to a blank color.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_opacity : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.xyzmask_opacity


XYZ Mask Use Invert
-------------------

.. py:property:: map.xyzmask_use_invert

Invert the colors of the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    xyzmask_use_invert : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.xyzmask_use_invert

Map Gradient Mask Settings Related Properties
=============================================

Use Gradient Mask Preview
-------------------------

.. py:property:: map.gmask_use_preview

Preview the Map in real-time in the 3D Viewport.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_use_preview : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.gmask_use_preview


Use Default Gradient Mask
-------------------------

.. py:property:: map.gmask_use_default

Bake texture map using default settings.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_use_default : bpy.props.BoolProperty
    ...

.. code-block:: python

    map.gmask_use_default


Gradient Mask Type
------------------

.. py:property:: map.gmask_type

Map Style of color blending.

- Linear - Create a linear progression
- Quadratic - Create a quadratic progression
- Easing - Create progression easing from one step to the next
- Diagonal - Create a diagonal progression
- Spherical - Create a spherical progression
- Quadratic Sphere - Create a quadratic progression in the shape of a sphere
- Radial - Create a radial progression

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_type : bpy.props.EnumProperty
    ...

.. code-block:: python

    map.gmask_type

Gradient Mask X Location
------------------------

.. py:property:: map.gmask_location_x

Gradient location by the local axis X.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_location_x : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_location_x


Gradient Mask Y Location
------------------------

.. py:property:: map.gmask_location_y

Gradient location by the local axis Y.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_location_y : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_location_y


Gradient Mask Z Location
------------------------

.. py:property:: map.gmask_location_z

Gradient location by the local axis Z.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_location_z : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_location_z


Gradient Mask X Rotation
------------------------

.. py:property:: map.gmask_rotation_x

Gradient rotation by the local axis X.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_rotation_x : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_rotation_x


Gradient Mask Y Rotation
------------------------

.. py:property:: map.gmask_rotation_y

Gradient rotation by the local axis Y.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_rotation_y : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_rotation_y


Gradient Mask Z Rotation
------------------------

.. py:property:: map.gmask_rotation_z

Gradient rotation by the local axis Z.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_rotation_z : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_rotation_z

Gradient Mask X Scale
---------------------

.. py:property:: map.gmask_scale_x

Gradient scale by the local axis X. The larger the scale, the smoother the gradient.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_scale_x : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_scale_x


Gradient Mask Y Scale
---------------------

.. py:property:: map.gmask_scale_y

Gradient scale by the local axis Y. The larger the scale, the smoother the gradient.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_scale_y : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_scale_y


Gradient Mask Z Scale
---------------------

.. py:property:: map.gmask_scale_z

Gradient scale by the local axis Z. The larger the scale, the smoother the gradient.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_scale_z : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_scale_z


Gradient Maks Coverage
----------------------

.. py:property:: map.gmask_coverage

Map range of coverage. The higher the coverage value, the larger the occluded area against its initial area.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_coverage : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_coverage


Gradient Mask Contrast
----------------------

.. py:property:: map.gmask_contrast

Map Color Contrast.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_contrast : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_contrast


Gradient Mask Saturation
------------------------

.. py:property:: map.gmask_saturation

Map color saturation value.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_saturation : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_saturation


Gradient Mask Opacity
---------------------

.. py:property:: map.gmask_opacity

Map Color Opacity relative to a blank color.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_opacity : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_opacity


Gradient Mask Use Invert
------------------------

.. py:property:: map.gmask_use_invert

Invert the colors of the Map.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    gmask_use_invert : bpy.props.FloatProperty
    ...

.. code-block:: python

    map.gmask_use_invert
