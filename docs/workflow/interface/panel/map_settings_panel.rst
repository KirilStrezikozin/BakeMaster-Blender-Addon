==================
Map Settings Panel
==================

List of Maps table
==================

The List of Maps table has the following controls:

- Bake visibility
- Add Button
- Remove Button
- Trash Button

Bake visibility
---------------

If you have prepared some maps for the future and you don't want to bake them alongside others, click the "📷 Camera" button near the map pass to toggle its "bake visibility". You can then get back to those maps and bake them too.

Add Button
----------

To add a new map pass to the List of Maps, click the "Add" Button on the right of the List of Maps table.

Remove Button
-------------

A map pass can be removed from the List of Maps by pressing the "Remove" Button. The active map pass in the list will be removed from the table.

Trash Bin Button
----------------

To remove all map passes from the List of Maps table, press the "🗑️ Trash Bin" Button. All maps within the list will be removed and their setting will be reset.

Particular Map Settings Panel
=============================

Each added map can have unique settings. They are divided into the following groups:

* Map Pass Type
* Map Output Settings
* Special Map Settings

Map Pass Type
-------------

Map Pass Type is a type of the map to be baked. There are 3 categories:

* PBR-based maps
* Default Cycles maps
* Special mask maps
  
There are 25 map types available in total. Each map pass type bake result is different, as well as its settings. You can read and view all the information about each map pass type and map passes in the Maps Workflow.

Map Pass Type can be set by clicking the name of the map in the List of Maps table.

.. note:: 
    An object in the List of Objects can have an unlimited number of maps added.

.. note:: 
    You can add map passes of the same map pass type. For example, you can bake three Albedo maps, each with unique settings.

Map Output Settings
-------------------

Map Output Settings include:

* File format
* Resolution
* Margin
* Use 32bit float bit depth
* Use Alpha Channel
* Map Denoising
* Affect by Source (apply Source to Target settings for this map pass)
* Other settings that depend on the Blender version you are using

.. image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-item-map-settings.gif
    :alt: bakemaster-addon-item-map-settings

Detailed information about each map output setting can be viewed here.

.. note:: 
    If you want all maps to have identical Output Settings, set up Overwrite Maps Output Settings.

Special Map Settings
--------------------

Some map passes like AO, Thickness, Displacement and others can have special settings. They can be also set inside the Map Pass Settings panel:

* Use Default Special Settings
* Special Settings
* Real-time Map Preview

Accessing Special Settings
**************************

To toggle Special Settings customization, uncheck "Default" in the map settings panel. Below are all possible Special Settings available:

+----------------------+
| **Quality-related**  |
+----------------------+
| - Samples Count      |
+----------------------+
| **Coverage-related** |
+----------------------+
|| - Radius            |
|| - Distance          |
|| - Coverage          |
+----------------------+
| **Transform**        |
+----------------------+
|| - Axis              |
|| - Gradient Type     |
|| - Gradient Location |
|| - Gradient Rotation |
+----------------------+
| **Color adjustment** |
+----------------------+
|| - Edge contrast     |
|| - Body contrast     |
|| - Blacks            |
|| - Whites            |
|| - Brightness        |
|| - Contrast          |
|| - Opacity           |
|| - Saturation        |
|| - Smoothness        |
|| - Power             |
|| - Invert option     |
+----------------------+
| **Other settings**   |
+----------------------+
| - Use only Local     |
+----------------------+

Each settings hyperlink goes to detailed information and how it applies in the usage.

Real-time Map Preview
*********************

Special Maps have a toggle to preview the bake result using Blender Material Shader Nodes. The preview is only available with Cycles Render Engine enabled. 

.. note:: 
    Map Preview will add its custom nodes to preview the map. After toggling off the preview, all of those nodes will be removed without a single touch to the object's initial materials.

.. |image-0| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-item-map-preview-3.gif
    :width: 320 px
    :alt: bakemaster-addon-item-map-preview-3

.. |image-1| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-item-map-preview-2.gif
    :width: 320 px
    :alt: bakemaster-addon-item-map-preview-2

|image-0| |image-1|