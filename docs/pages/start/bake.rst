.. |open_blender_console| image:: ../../_static/images/pages/start/bake/open_blender_console_310x285.png
    :alt: How to open Blender Console

.. |bake_progress| image:: ../../_static/images/pages/start/bake/bake_progress_bar_484x24.gif
    :alt: Bake Progress

========
Hit Bake
========

Start the Bake
==============

.. raw:: html

    <div class="slideshow" id="slideshow-0">
        <div class="content-wrapper">
            <div class="content row active">
                <img src="../../_static/images/pages/start/bake/bake_overwrite_350x210.png" alt="Overwrite">
                <div class="slideshow-description">
                    <b>Overwrite</b>
                    <p>If checked, old bake files in the output directory will be overwritten by the new ones if they have the same name.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/bake/bake_reset_350x210.png" alt="Reset BakeMaster">
                <div class="slideshow-description">
                    <b>Reset BakeMaster</b>
                    <p>Remove baked objects from BakeMaster Table of Objects after the bake.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/bake/bake_this_350x210.png" alt="Bake This Button">
                <div class="slideshow-description">
                    <b>Bake This</b>
                    <p>Bake maps only for the current object or container.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/bake/bake_all_350x210.png" alt="Bake All Button">
                <div class="slideshow-description">
                    <b>Bake All</b>
                    <p>Bake maps for all objects added.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/bake/bake_alep_350x210.png" alt="Apply Lastly Edited Setting">
                <div class="slideshow-description">
                    <b>Apply Lastly Edited Setting</b><a href="../advanced/savetime.html#apply-lastly-edited-setting"> (read more)</a>
                    <p>Select maps or objects to apply value of lastly edited property for.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/bake/bake_job_350x210.png" alt="Bake Job">
                <div class="slideshow-description">
                   <b>Create Bake Job Group</b><a href="../advanced/nolimits.html#create-a-bake-job-group"> (read more)</a>
                    <p>Group objects into a Bake Job Container, where all settings can be set at once for all.</p>
                </div>
            </div>
            <div class="content row">
                <img src="../../_static/images/pages/start/bake/bake_instruction_350x210.png" alt="Bake Instruction">
                <div class="slideshow-description">
                    <b>Bake Instruction</b><a href="./bake.html#while-waiting"> (read more)</a>
                    <p>Short Bake Instruction.</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId('slideshow-0', -1)" onselectstart="return false">&#10094;</a>
            <div class="controls">
                <span class="dot active" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 0)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 1)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 2)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 3)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 4)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 5)"></span>
                <span class="dot inactive" onclick="slideshow_setSlideByAbsoluteId('slideshow-0', 6)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-0', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>

BakeMaster Bake won't block anything, so you can continue creating while it's doing its magic.

While waiting
=============

|bake_progress|

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