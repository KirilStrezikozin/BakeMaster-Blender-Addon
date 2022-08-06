.. |empty_list_of_objects| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/choose_objects_page/empty_list_of_objects_254x216.png
    :alt: empty_list_of_objects

.. |adding_objects| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/choose_objects_page/adding_objects_350x320.gif
    :alt: adding_objects

.. |expected_mesh| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/choose_objects_page/expected_mesh_198x23.png
    :alt: expected_mesh

.. |exists_in_list| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/choose_objects_page/exists_in_list_192x25.png
    :alt: exists_in_list

.. |toggle_bake_visibility| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/choose_objects_page/toggle_bake_visibility_350x320.gif
    :alt: toggle_bake_visibility

.. |selecting_objects| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/choose_objects_page/selecting_objects_350x320.gif
    :alt: selecting_objects

==============
Choose Objects
==============

To start settings up maps for the objects you want to bake, you need to add these objects to the BakeMaster List of Objects table.

List of Objects table
=====================

When you first open up the BakeMaster panel in the 3D Viewport, it will appear as an empty table:

|empty_list_of_objects|

To add objects you would like to set up maps for:

1. Select these objects in the scene
2. Press the Add button to add them to the List

|adding_objects|

.. note::
    You can add objects one-by-one or select all of them and add them at once.

Now, objects in the List of Objects can be configured with unique bake settings and an unlimited number of maps to be baked.

List of Objects table Controls
------------------------------

The List of Objects table has several important controls that can be viewed here.

Which objects can be added?
===========================

Only Mesh Objects
-----------------------------------------------------

You can only add objects of type Mesh to the List of Objects. If you are trying to add the object of Non-Mesh type, it will not be added to the List of Objects, add a message will be displayed in the info bar:

|expected_mesh|

If you have multiple objects selected and you are not sure that all of them are meshes, don't worry: BakeMaster will add all the meshes and leave the ones that are not.

Objects holding the same Mesh instance
--------------------------------------

Multiple Objects holding the same Mesh instance cannot be added to the List of Objects. Meaning if you have two selected objects and both of them are linked to the same Mesh, only one of them will be added to the List of Objects.

The following message will appear in the info bar:

|exists_in_list|

The same message will appear if you are trying to add the mesh object that already exists in the list.

Additional Tips
===============

Bake Visibility
---------------

An object can be in the list but excluded from the bake. To do so, click the "📷 Camera" Button to toggle the object's bake visibility.

|toggle_bake_visibility|

Selecting objects
-----------------

If you have a complex scene setup, it might be hard to find the object you have added to the List of Objects. But BakeMaster has a great feature here:

.. tip::
    Click on the object in the list and it will be selected in your current scene.

|selecting_objects|

.. seealso::
    Object Workflow