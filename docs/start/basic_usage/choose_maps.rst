===========
Choose Maps
===========

Each object in the List of Objects has a list of added maps. The Map Settings panel has preferences to set everything up.

List of Maps table
==================

At first, the List of Maps will be empty. To add maps you would like to be baked, follow the steps below:

1. Select the object in the List of Objects
2. Expand Map Settings panel
3. Click the "+" button to add a map pass

.. image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-item-add-maps.gif 
    :alt: bakemaster-addon-item-add-maps

Each added map can be selected by clicking it and configured with unique settings.

List of Maps table Controls
---------------------------

The List of Maps table has several important controls that can be viewed here.

The List of Maps table has the following controls:

* Add Button
* Remove Button
* Trash Button

Add Button
**********

To add a new map pass to the List of Maps, click the "Add" Button on the right of the List of Maps table.

Remove Button
*************

A map pass can be removed from the List of Maps by pressing the "Remove" Button. The active map pass in the list will be removed from the table.

Trash Bin Button
****************

To remove all map passes from the List of Maps table, press the "🗑️ Trash Bin" Button. All maps within the list will be removed and their setting will be reset.

Additional Tips
===============

About map types
---------------

Map Pass type can be set by clicking the name of the map in the List of Maps table. You can choose a map pass type within the 25 types available. 

.. note:: 
    An object in the List of Objects can have an unlimited number of maps added.

.. note:: 
    You can add map passes of the same map pass type. For example, you can bake three Albedo maps, each with unique settings.

Bake visibility
---------------

If you have prepared some maps for the future and you don't want to bake them alongside others, click the "📷 Camera" button near the map pass to toggle its "bake visibility". You can then get back to those maps and bake them too.

.. seealso::
    Map Workflow