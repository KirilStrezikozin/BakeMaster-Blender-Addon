.. |baking_progress| image:: https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/documentation/start/basic_usage/bake_process_page/baking_progress_350x320.gif
    :alt: baking_progress

==============
Baking Process
==============

Starting the Bake
=================

You can start the bake by pressing Bake All or Bake This Buttons. Baking progress will be shown in the bottom info bar of your Blender file:

|baking_progress|

After a bake has finished, a message in the info bar will appear showing the amount of time the bake took. 

.. note:: 
    - If there was any error with the object or map, the BakeMaster will skip baking them.
    - If there was any error connected with the bake itself, it will be canceled.
    - All errors will be shown in the info bar and printed to the Blender Console.

Controlling the bake
====================

While Baking
------------

The baking process can be controlled from your keyboard or Blender Console. All keybindings are presented below and under the `Bake Instruction <https://bakemaster-blender-addon.readthedocs.io/en/latest/workflow/object/object.html#bake-instruction>`__ field inside the Bake Settings panel:

- Press `BACKSPACE` to cancel baking all next maps
- Press `ESC` to cancel baking current map
- Press `BACKSPACE + ESC` to cancel baking

It is also recommended to have the Blender Console opened before baking (how to open it), so if there is a long unexpected freeze, you can easily abort the bake by pressing ``Ctrl + C`` or ``⌘ Cmd + C`` (Mac) in the console window.

Below is the list of expected freezes that might occur:

- Preparing multires data for Displacement bake (depends on subdivisions number)
- Mesh UV-unwrapping (when UV Packing or unwrapping the mesh with no UV Layers)
- Denoising a baked image.

.. note:: 
    If the bake was canceled, the part of the job that has been done will be saved.

Undo the Bake Result
--------------------

Just after the bake has finished or canceled, you can undo its result by pressing ``Ctrl + Z`` or ``⌘ Cmd + Z`` (Mac) on your keyboard.