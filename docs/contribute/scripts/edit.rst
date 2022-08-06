==================
Editing the Add-on
==================

Add-on .py files are in the working directory and read by Blender. Below is the structure:

- ``__init__.py`` is used to register add-on classes and modules.
- ``ui_panel.py`` consists of generic ``bpy.types.Panel`` built-in Blender Python API classes. Initializing panels.
- ``ui_panel_base.py`` contains panels' UI bases.
- ``utils.py`` contains utility functions for operations.
- ``operators.py`` contains BakeMaster configuration operators.
- ``operator_bake.py`` for the main baking logic - Bake Operator.
- ``labels.py`` has a ``BM_Labels`` class that contains strings used for properties', operators' and errors' descriptions.

Make sure you updated the version key in the ``bl_info`` dictionary in the :file:`/__init__.py` (increase the 3rd item in the tuple by 1):

.. code-block:: python
    :lineno-start: 17
    :emphasize-lines: 6

    ...
    bl_info = {
        "name" : "BakeMaster",
        "description" : "Bake various PBR-based or Cycles maps with ease and comfort",
        "author" : "kemplerart",
        "version" : (1, 0, 0), # (1, 0, 0) -> (1, 0, 1)
        "blender" : (2, 83, 0),
        "location" : "View3D > Sidebar > BakeMaster",
        "warning" : "",
        "wiki_url": "",
        "tracker_url": "",
        "category" : "Material"
    }
    ...

.. attention:: 
    Remember to follow the **Style Conventions**.