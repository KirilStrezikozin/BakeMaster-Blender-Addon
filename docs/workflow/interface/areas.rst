.. |accessing| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/install/install_page/accessing_350x320.gif
    :alt: accessing

.. |image_editor| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/about/introduction_page/image_editor_350x320.gif
    :width: 320 px
    :alt: image_editor

.. |baking_progress| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/bake_process_page/baking_progress_350x320.gif
    :alt: baking_progress

.. |static_baking_progress| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/areas_page/static_progress_bar_1049x49.png
    :width: 900 px
    :alt: static_baking_progress

=====
Areas
=====

The Blender Windows is divided into areas. Read more about areas in the Blender Manual.

UI Panel
========

BakeMaster add-on Panel (aka the add-on's UI organization unit) holds all the menus, properties, buttons, and controls for the user to manipulate.

The Panel can be accessed in the 3D Viewport Workspace.
Hit the ``N`` key on your keyboard and the right UI sidebar will pop up. Then navigate to the BakeMaster Tab, where you will see the add-on:

|accessing|

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

UV Unwrapping and packing, as well as UDIM tiles and properties, will be configured in the UV Editor. If there is no UV Editor available, BakeMaster will set the current active area to be one. 

Image Editor
------------

Before bake, BakeMaster creates image files to save the baked result. Baked image textures can be viewed in the Image Editor.

|image_editor|

Status Bar
==========

Baking progress, info messages, warnings, and errors will be displayed in the bottom status bar of your Blender file.

|baking_progress|

|static_baking_progress|

.. note:: 
    While baking, the BakeMaster Status bar message updates every 2 seconds.