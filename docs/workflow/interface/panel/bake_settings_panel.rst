.. |item_bake_settings| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/bake_settings_page/bake_settings_350x320.gif
    :alt: item_bake_settings

.. |bake_controls| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/interface/bake_settings_panel_page/bake_controls_227x438.png
    :alt: bake_controls

.. |bake_settings| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/workflow/interface/bake_settings_panel_page/bake_settings_227x438.png
    :alt: bake_settings

===================
Bake Settings Panel
===================

Object Bake Settings Panel
==========================

|bake_settings|

Each object in the List of Objects can have the following unique Bake Settings that impact the duration of baking and its quality, as well as directory and files arrangement:

**Create Material**
    Automatic Material creation for the object with all baked maps.
**Internal/External output**
    Toggle to choose whether to save baked images to the disk or pack them into the Blender file.
**Output directory**
    | If saving externally, specify the output directory path. 
    | Set the Output directory path to be ``//`` to save images to the Blender file location.
**Subfolder creation**
    If saving externally, there is an option to create a subfolder in the specified output directory path.
**Subfolder name**
    If the subfolder creation option is enabled, you can specify the name of the subfolder.
**Maps Batch naming**
    Configure map naming pattern using the keywords.
**Bake device**
    CPU, GPU - depends on the system
**Sampling**
    | Output samples count.
    | Adaptive sampling is supported too.

|item_bake_settings|

Bake Controls
=============

Bake Controls
=============

|bake_controls|

Inside the Bake Settings panel, there are the following Bake Control Buttons:

**Reset BakeMaster option**
    Reset BakeMaster after the bake.
**Bake This Button**
    Bake maps only for the current item in the List.
**Bake All Button**
    Bake maps for all items.

There is also an embossed field called "Bake Instruction". When you hover over it, you will see Baking process information and keyboard controls.

Full and detailed information regarding each control can be viewed by following its hyperlink.