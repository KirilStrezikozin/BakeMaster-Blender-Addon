====
Bake
====

.. py:function:: item_bake()

    A BakeMaster Operator to bake image textures.

    :param str control: The type of the baking operation
    :type control: String
    :return: Running status
    :rtype: str
    :raises KeyboardInterrupt: if the baking process is aborted by the user in the console
    :raises RuntimeError: if the bake runtime fails

.. note::
    This page contains all Bake operators' references and short descriptions.

    Each section has a code block with a script reference and another code block with a Blender Python Data Path to access the operator in Python.

The main BakeMaster baking operator that iters through Objects (depending on the ``control`` value), iters through Object's Maps and prepares arguments for the ``bpy.ops.object.bake`` or ``bpy.ops.object.bake_image``, which is used to bake images textures.

- ``bpy.ops.object.bake_image`` is called for baking Displacement map pass type
- ``bpy.ops.object.bake`` is called for baking all other map pass types.

.. code-block:: python
    :caption: operator_bake.py
    :emphasize-lines: 2

    ...
    class BM_OT_ITEM_Bake(bpy.types.Operator):
        ...

.. code-block:: python

    bpy.ops.bakemaster.item_bake()

Bake This
=========

"Bake This" operation will bake image textures for the current active Object in the List of Objects.

.. code-block:: python
    :caption: operator_bake.py
    :emphasize-lines: 2

    ...
    class BM_OT_ITEM_Bake(bpy.types.Operator):
        ...

.. code-block:: python

    bpy.ops.bakemaster.item_bake(control='BAKE_THIS')

Bake All
========

"Bake All" operation will bake image textures for all Objects in the List of Objects.

.. code-block:: python
    :caption: operator_bake.py
    :emphasize-lines: 2

    ...
    class BM_OT_ITEM_Bake(bpy.types.Operator):
        ...

.. code-block:: python

    bpy.ops.bakemaster.item_bake(control='BAKE_ALL')