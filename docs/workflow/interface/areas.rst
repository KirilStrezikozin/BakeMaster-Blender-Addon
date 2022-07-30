=====
Areas
=====

The Blender Windows is divided into areas. Read more about areas in the Blender Manual.

UI Panel
========

BakeMaster add-on Panel (aka the add-on's UI organization unit) holds all the menus, properties, buttons, and controls for the user to manipulate.

The Panel can be accessed in the 3D Viewport Workspace.
Hit the ``N`` key on your keyboard and the right UI sidebar will pop up. Then navigate to the BakeMaster Tab, where you will see the add-on:

.. image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-accessing.gif 
    :alt: bakemaster-addon-accessing

Editors
=======

BakeMaster results and workflow is connected with several editing workspaces:

- 3D Viewport
- UV Editor
- Image Editor

3D Viewport
-----------

While baking, BakeMaster will configure the baking process by scripts. For bake to proceed properly, objects will be automatically selected, and materials with UV maps will be automatically configured. The add-on leaves Blender Interface unfrozen to see the baking progress and leaves the ability for the user to continue working in Blender while baking is active.

Below is the list of expected Interface freezes that might occur:

- Preparing multires data for Displacement bake (depends on subdivisions number)
- Mesh UV-unwrapping (when UV Packing or unwrapping the mesh with no UV Layers)
- Denoising a baked image.

UV Editor
---------

UV Unwrapping and packing, as well as UDIM tiles and properties, will be configured in the UV Editor. If there is no UV Editor available, BakeMaster will set the current active area to be the one. 

Status Bar
==========

Baking progress, info messages, warnings, and errors will be displayed in the bottom status bar of your Blender file.

.. image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-item-baking-progress.gif
    :alt: bakemaster-addon-item-baking-progress

.. note:: 
    While baking, the BakeMaster Status bar message updates every 2 seconds.