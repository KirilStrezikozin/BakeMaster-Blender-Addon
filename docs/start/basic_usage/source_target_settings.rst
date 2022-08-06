.. |set_source| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/source_target_page/set_source_350x320.gif
    :alt: set_source

======================
Source-target Settings
======================

Bake shading on the surface of selected objects to the active object. The rays are cast from the low-poly object inwards towards the high-poly object. For more info regarding Source to Target bake, read Selected to Active Render Baking in the Blender Manual.

Choosing a source object
========================

To choose a source object, it should be added to the List of Objects. Follow the steps:

1. Add both low and high-poly models to the List of Objects
2. Select the low-poly in the List
3. Expand the Item Settings panel
4. Expand the Source to Target panel
5. Check "Target"; set "Source" to be the high-poly.

|set_source|

Ray Casting Settings
====================

Source-target Panel includes more settings, configuring which may improve baking results:

* Extrusion
* Max Ray Distance
* Cage object

.. seealso::
    Object Workflow