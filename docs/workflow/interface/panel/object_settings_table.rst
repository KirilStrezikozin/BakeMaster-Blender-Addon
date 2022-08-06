.. |settings_panel| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/interface/object_settings_panel_page/object_settings_panel_230x138.png
    :alt: settings_panel

.. |output_panel| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/interface/object_settings_panel_page/output_panel_238x245.png
    :alt: output_panel

.. |source_target_panel| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/interface/object_settings_panel_page/source_to_target_panel_258x301.png
    :alt: source_target_panel

.. |uv_panel| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/interface/object_settings_panel_page/uv_panel_233x183.png
    :alt: uv_panel

=====================
Object Settings Panel
=====================

|settings_panel|

Each object has its prebake settings that are configured in the Object Settings Panel.

Source to Target Panel
======================

|source_target_panel|

Source to Target Panel has settings and preferences related to Source to Target bake. It contains the following controls:

**Use Target Check**
    Set to true if you want to set up the Source to Target setting for the current object in the List of Objects table.
**Source object**
    A dropdown list with available objects that can be set as a source for the current object in the List of Objects table. An object in the List of Objects is available as a source if it is not a source for another object already and it doesn't use Source to Target settings.
**Extrusion**
    Inflate the active object by the specified distance for baking.
**Max Ray Distance**
    The maximum ray distance for matching points between the active and selected objects.
**Cage object**
    Object to use as cage instead of calculating the cage from the active object with cage extrusion. The cage object doesn't need to be in the List of Objects.

.. note:: 
    A Cage Object must be a mesh object and has the same number of polygons as a target object in the list.
    
    A Cage Object is an inflated version of a target object.

UV Maps Panel
=============

|uv_panel|

UV Settings are configured in the UV Maps Panel. There are the following properties:

- UV Type
- Active UV Layer
- UV Packing
    - Use UV Islands Rotate
    - UV Islands margin

UV Type
-------

UV Type is an option to set a correct UV Type for maps to be baked. You can choose between:

* Single (Single tile - baking to a single image)
* Tiles (UDIM tiles - baking to UDIMs)

More information about UV Maps and UDIM tiles can be found in the Blender Manual.

Active UV Layer
---------------

If an object has multiple UV Layers, and you want to specify a particular one to act as an active one while baking, choose the active layer in the Active UV Layer dropdown. The dropdown items are all available UV Layers of the Mesh Object in the list.

.. note:: 
    If the object in the list has no UV Layers, the Active UV Layer will have the "Auto Unwrap" value and the object will be automatically unwrapped before the bake.

UV Packing
----------

To bake multiple items onto one image texture, toggle the "Include in UV Pack". Objects in the List of Objects with "Include in UV Pack" turned on will be packed before the bake.

.. note:: 
    Choose Active UV Layer for the object to specify which UV Layer to use in the Pack.

.. note:: 
    If the object has no UV Layers, it will be unwrapped automatically before the UV Packing.

UV Packing settings can be controlled after enabling "Include in UV Pack":

* Rotate UV islands for best fit
* Packing margin (space between packed islands)

Output Panel
============

|output_panel|

Currently, the Object's Output Panel has Overwrite Maps Settings only.

Overwrite Maps Settings panel
-----------------------------

Enable Overwrite Maps Settings for automatic maps output settings configuration. Controls:

**Target**
    Bake target in Image Textures or Vertex Colors. Currently, only Image Textures bake target is available.
**File Format**
    Output image File Format.
**Resolution**
    Output image Resolution
**Margin Type**
    Algorithm to extend the baked result.
**Use 32bit Float**
    Use 32bit Float image color depth.
**Use Alpha channel**
    Use the Alpha color channel in the output image.
**Denoise image after bake**
    Remove noise and despeckle output image after it has finished baking.