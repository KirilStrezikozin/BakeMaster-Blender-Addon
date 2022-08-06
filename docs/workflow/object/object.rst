======
Object
======

.. py:class:: object

.. note::
    This page contains all Object properties references and short descriptions, and the Object definition itself.

    Each section has a code block with a script reference and another code block with a Blender Python Data Path to access the value in Python. ``__item_index__`` is an index of a key in the List of Objects.

BakeMaster Object (Item can be also mentioned) is a BakeMaster List of Objects class unit. The Object is a Property Group that holds child properties and Map classes.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    class BM_Item(PropertyGroup):
        ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__]

List of Objects
===============

.. py:class:: objects

List of Objects is a ``bpy_prop_collection_idprop`` collection class that contains keys. The key is the Object Property Group class.

.. code-block:: python
    :caption: init.py
    :emphasize-lines: 2

    ...
    bpy.types.Scene.bm_aol = bpy.props.CollectionProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol

Object Pointer
==============

.. py:property:: object.object_pointer

Each Object class has a pointer to an existing mesh object data block in the Blender file scene. Object Pointer is assigned when this object is added to the List of Objects. Because Object Pointer stores a pointer to an object and not a full data block, its properties are changed along with the original object.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    object_pointer : PointerProperty()
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].object_pointer

Use Bake
========

.. py:property:: object.use_bake

``use_bake`` defines whether to include the Object in the bake. If ``False``, then the Object is excluded and appears greyed out in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_bake : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_bake

Source to Target Related Properties
===================================

Use Target
----------

.. py:property:: object.use_target

Set this item as a bake target object. Enables Source to Target settings in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_target : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_target

Use Source
----------

.. py:property:: object.use_source

``True`` when the object is a source. Not used in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_source : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_source

Source
------

.. py:property:: object.source

Index of a key in the List of Objects that is a source for the object. Not used in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    source : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].source

Source Name
-----------

.. py:property:: object.source_name

If an Object is a source, ``source_name`` is equal to the name of the target object. Not used in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    source_name : bpy.props.StringProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].source_name

Use Cage
--------

.. py:property:: object.use_cage

Enable casting rays to an active item from a cage.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_cage : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_cage

Cage Extrusion
--------------

.. py:property:: object.cage_extrusion

Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cage_extrusion : bpy.props.FloatProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].cage_extrusion

Max Ray Distance
----------------

.. py:property:: object.max_ray_distance

The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    max_ray_distance : bpy.props.FloatProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].max_ray_distance

Cage Object
-----------

.. py:property:: object.cage_object

Object to use as cage instead of calculating the cage from the active object with cage extrusion.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    cage_object : bpy.props.PointerProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].cage_object

UV Settings Related Properties
==============================

Active UV Layer
---------------

.. py:property:: object.active_uv

Choose an active UVMap layer among created to use in the bake. If the mesh has got no UV layers, auto UV unwrap will be proceeded.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    active_uv : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].active_uv

UV Type
-------

.. py:property:: object.uv_type

UVMap type in Single (Single Tile) or UDIMs (Tiled). Set to ``UDIMs`` when baking to UDIM tiles is desired, otherwise - ``Single``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    uv_type : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].uv_type

Use UV Islands Packing
----------------------

.. py:property:: object.use_islands_pack

Items UVs with 'Pack' turned on will be packed before the bake. Those items will share the same baked image. Available if the UV Type is Single.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_islands_pack : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_islands_pack

Overwrite Maps Output Related Properties
========================================

Use Overwrite Map Output Settings
---------------------------------

.. py:property:: object.use_overwrite

Set output settings for all item maps at once.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_overwrite : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_overwrite

Overwrite Bake Target
---------------------

.. py:property:: object.overwrite_bake_target

Overwrite maps bake target, in Image Textures or Vertex Colors. Currently, only Image Textures are supported.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_bake_target : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_bake_target

Overwrite Map Output Denoising
------------------------------

.. py:property:: object.overwrite_use_denoise

Overwrite maps output denoising use. If ``True``, all Object's maps will be denoised and despeckled.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_use_denoise : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_use_denoise

Overwrite File Format
---------------------

.. py:property:: object.overwrite_file_format

Overwrite maps file format, in ``BMP, PNG, JPEG, TIFF, EXR``.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_file_format : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_file_format

Overwrite Resolution
--------------------

.. py:property:: object.overwrite_res_enum

Overwrite maps output resolution.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_res_enum : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_res_enum

Overwrite Height Resolution
---------------------------

.. py:property:: object.overwrite_res_height

If the ``res_enum`` value is ``custom``, this property stores custom output image height.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_res_height : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_res_height

Overwrite Width Resolution
--------------------------

.. py:property:: object.overwrite_res_width

If the ``res_enum`` value is ``custom``, this property stores the custom output image width.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_res_width : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_res_width

Overwrite Margin
----------------

.. py:property:: object.overwrite_margin

Overwrite maps margin value as a bake post-processing filter.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_margin : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_margin

Overwrite Margin Type
---------------------

.. py:property:: object.overwrite_margin_type

Overwrite maps margin type, in ``ADJACENT_FACES, EXTEND``.

- Adjacent Faces - Use pixels from adjacent faces across UV seams
- Extend - Extend border pixels outwards.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_margin_type : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_margin_type

Overwrite Use 32bit Float
-------------------------

.. py:property:: object.overwrite_use_32bit

Overwrite maps 32bit Float color depth usage.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_use_32bit : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_use_32bit

Overwrite Use Alpha
-------------------

.. py:property:: object.overwrite_use_alpha

Overwrite maps Alpha color channel usage.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_use_alpha : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_use_alpha

Overwrite UDIM Start Tile
-------------------------

.. py:property:: object.overwrite_udim_start_tile

Overwrite UDIM tile index of UDIM tiles baking range. UDIMs' baking range is used for defining UDIM tiles' baking boundaries. The baked result will only affect a specified range of tiles (Start Tile Index - End Tile Index).

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_udim_start_tile : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_udim_start_tile


Overwrite UDIM End Tile
-----------------------

.. py:property:: object.overwrite_udim_end_tile

Overwrite UDIM tile index of UDIM tiles baking range. UDIMs' baking range is used for defining UDIM tiles' baking boundaries. The baked result will only affect a specified range of tiles (Start Tile Index - End Tile Index).

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    overwrite_udim_end_tile : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].overwrite_udim_end_tile

Bake Settings Related Properties
================================

Use Internal
------------

.. py:property:: object.use_internal

If ``True``, save baked images internally. If ``False``, enables Output Directory path and subfolder creation specification.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_internal : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_internal

Output Filepath
---------------

.. py:property:: object.output_filepath

Output Directory file path to save baked images to externally.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    output_filepath : bpy.props.StringProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].output_filepath

Use subfolder Creation
----------------------

.. py:property:: object.use_subfolder

Create a subfolder in the output file path directory. If any image has the same name in the directory as the baked image, it will be overwritten.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_subfolder : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_subfolder

Subfolder Name
--------------

.. py:property:: object.subfolder_name

If subfolder creation is enabled, the subfolder's name can be specified.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    subfolder_name : bpy.props.StringProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].subfolder_name

Batch Naming Pattern
--------------------

.. py:property:: object.batch_name

Format using underscore(_) between keywords:

- ``_index_`` - write the item's index in the list
- ``_item_`` - write the name of the item in the list
- ``_sourcetarget_`` - write 'Target' if the item is a target
- ``_uvpacked_``- write 'Packed' if the item is included in UV Pack
- ``_map_`` - write baked map name
- ``_res_`` - write baked map resolution
- ``_float_`` - write '32bit' if the baked image uses 32bit Float, otherwise write '8bit'
- ``_alpha_`` - write 'Alpha' if the baked image uses Alpha Channel
  
Example ``item_map_res``: Suzanne_ALBEDO_2048; ``map_float_item``: NORMAL_32bit_MyCube.

.. note::
    If the Batch Name value has no _item_ key, it will be added automatically.

    Multiple keys are supported: item_item_map - Monster.001_Monster.001_DISPLACEMENT.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    batch_name : bpy.props.StringProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].batch_name

Use Material Creation
---------------------

.. py:property:: object.use_material

If enabled, create a material after bake including all baked maps for this item.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    use_material : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].use_material

Bake Samples
------------

.. py:property:: object.bake_samples

Number of samples to render per pixel. Keep as low as possible for optimal performance.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    bake_samples : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].bake_samples

Use Adaptive Sampling for the Bake
----------------------------------

.. py:property:: object.bake_use_adaptive_sampling

Automatically reduce the number of samples per pixel based on the estimated noise level.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    bake_use_adaptive_sampling : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].bake_use_adaptive_sampling

Adaptive Threshold
------------------

.. py:property:: object.bake_adaptive_threshold

If Adaptive Sampling for the Bake is enabled, set the Noise level step to stop sampling at, lower values reduce noise at the cost of render time. Zero for automatic setting based on number of AA sampled

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    bake_adaptive_threshold : bpy.props.FloatProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].bake_adaptive_threshold

Adaptive Min Samples
--------------------

.. py:property:: object.bake_min_samples

If Adaptive Sampling for the Bake is enabled, set the minimum number of samples a pixel receives before adaptive sampling is applied. When set to 0 (default), it is automatically set to a value determined by the Noise Threshold.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    bake_min_samples : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].bake_min_samples

Bake Device
-----------

.. py:property:: object.bake_device

Specify the device to use for baking maps for the Object (Depends on the system, if GPU isn't available, choosing it will be displayed grayed out):

- GPU Compute - Use GPU compute device for baking, configured in the system tab in the user preferences
- CPU - Use CPU for baking.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2

    ...
    bake_device : bpy.props.EnumProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_aol[__item_index__].bake_device

BakeMaster Scene Props
======================

Blender file scene context props that are Object class related, but are top-level units.

Object Active Index    
-------------------

.. py:property:: object.active_index

Active List of Objects key index is stored in this value. Not used in the UI.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2
    
    ...
    active_index : bpy.props.IntProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_props.active_index

Use UV Islands Rotation
-----------------------

.. py:property:: object.use_islands_rotate

If ``True``, rotate UV Islands when UV Packing for best fit.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2
    
    ...
    use_islands_rotate : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_props.use_islands_rotate

UV Pack Margin
--------------

.. py:property:: object.uv_pack_margin

UV Pack margin for Islands UV Packing. Defines the packing distance between UV islands.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2
    
    ...
    uv_pack_margin : bpy.props.FloatProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_props.uv_pack_margin

Use BakeMaster Reset
--------------------

.. py:property:: object.use_bakemaster_reset

If ``True``, empty the List of Objects and return all properties to their default values after the bake has completed.

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2
    
    ...
    use_bakemaster_reset : bpy.props.BoolProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_props.use_bakemaster_reset

Bake Instruction
----------------

.. py:property:: object.bake_instruction

Bake Instruction string Property that contains Baking Process control keyboard shortcuts.

- Press ``BACKSPACE`` to cancel baking all next maps
- Press ``ESC`` key to cancel baking current map
- Press ``BACKSPACE + ESC`` to cancel baking
 
If you want to undo the bake, press ``Ctrl + Z`` or ``⌘ Cmd + Z`` (Mac) just after it is finished or canceled.

.. tip::
    Open Blender Console to, if you face an unexpected Blender freeze, press ``Ctrl + C`` or ``⌘ Cmd + C`` (Mac) to abort the bake.

.. warning:: 
    There are expectable Blender freezes when baking Displacement, Denoising baked result, baking item with no UV Map or UV Packing items that have no UV Maps

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2
    
    ...
    bake_instruction : bpy.props.StringProperty
    ...

.. code-block:: python

    bpy.context.scene.bm_props.bake_instruction

Bake Available
--------------

.. py:property:: object.bake_available

``True`` when no BakeMaster baking process is running, ``False`` when the bake is available. Not used in the UI.

.. hint:: 
    If there was a Bake Error and you cannot run the next bake, because the Bake Controls are inactive, write the following expression to the Blender Python Console:

    .. code-block:: python
        :caption: Blender Python Console window

        bpy.context.scene.bm_props.bake_available = True

.. code-block:: python
    :caption: properties.py
    :emphasize-lines: 2
    
    ...
    bake_available : bpy.props.BoolProperty
    ...
