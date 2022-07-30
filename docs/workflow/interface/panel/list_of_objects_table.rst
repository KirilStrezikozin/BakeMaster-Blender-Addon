=====================
List of Objects table
=====================

The List of Objects table is a table that contains all added mesh objects. It has the following controls:

* Bake visibility
* Add Button
* Remove Button
* Baking Order Buttons
* Trash Bin Button
* Refresh Button

Bake Visibility
===============

An object can be in the list but excluded from the bake. To do so, click the "📷 Camera" Button to toggle the object's bake visibility.

Add Button
==========

To add objects selected in the scene to the List of Objects, click the "Add" Button on top of the List of Objects table.

Remove Button
=============

An object can be removed from the List of Objects by pressing the "Remove" Button. The active object in the list will be removed from the table.

Baking Order Buttons
====================

Objects added to the list will be baked from the top one to the bottom one. To change the baking order, select the object within the List of Objects and click Item Priority Buttons:

.. image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/docs/bakemaster-addon-list-item-baking-order.png
    :alt: bakemaster-addon-list-item-baking-order

Trash Bin Button
================

To remove all objects from the List of Objects table, press the "🗑️ Trash Bin" Button. All objects within the list will be removed and their setting will be reset.

.. note::
    Trash Bin Button is equal to resetting BakeMaster. All preferences and settings will return to their default values.

Refresh Button
==============

If an object was in the List of Objects, but you deleted it from your scene, it will appear greyed out. This is done to prevent you from losing all the settings that you have set for this object. 

Press ``Ctrl + Z`` to return the deleted object along with its settings in the BakeMaster panel.
  
If you no longer want this object to appear in the table, press the "🔁 Refresh" Button to remove all greyed-out objects or remove them one-by-one by pressing the "Remove" Button.

.. note:: 
    Refresh Button will only appear if any object within the List of Objects is not found in the scene (deleted).