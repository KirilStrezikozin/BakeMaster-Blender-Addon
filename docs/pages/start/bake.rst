.. |open_blender_console| image:: ../../_static/images/pages/start/bake/open_blender_console_310x285.png
    :alt: How to open Blender Console

========
Hit Bake
========

Start the Bake
==============

.. todo:: Slideshow of gifs showing bake panel controls (bake this, bake all, overwrite, reset).

BakeMaster Bake won't block anything, so you can continue creating while it's doing its magic.

While waiting
=============

Control the baking process from your keyboard or Blender Console. All keybindings are present below and under the ``Bake Instruction`` field in the Bake panel.

.. cssclass:: ul-stylized

    * Press ``BACKSPACE`` to cancel baking all next maps
    * Press ``ESC`` key to cancel baking the current map
    * Press ``BACKSPACE``, ``ESC`` to cancel baking

.. admonition:: Tip: Blender Console
    :class: important

    By opening the Blender Console you'll see more precise bake process feedback and be able to press ``Ctrl + C`` or ``⌘ Cmd + C`` (Mac) to abort the bake.

    |open_blender_console|

.. caution:: 
    Blender freezes are expected when handling meshes with large amounts of geometry, baking map results to modifiers, Denoising baked results, or UV unwrapping and packing. Please be patient, BakeMaster will notify you if any error occurs.