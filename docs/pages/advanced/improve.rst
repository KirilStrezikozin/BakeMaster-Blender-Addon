.. |understandingcage_howcageworks| image:: ../../_static/images/pages/advanced/improve/understandingcage_howcageworks_700x400.gif
    :alt: How Cage works

================
Get Best Results
================

Tutorials
=========

.. todo:: Embed a YouTube video tutorial

Baking from highpoly
====================

Texture baking often includes transferring high-resolution mesh details to a low-res model. Models with loads of geometry require more computer power, and details sometimes aren't even noticed in the final production. On the other hand, lowpoly model is easier to handle, and you can bake high-resolution details onto it.

.. todo:: Two images side by side showing wireframe overlap of high and lowpoly geometries.

.. todo:: Two images side by side showing render time for those models and no visual difference.

Read more about how you can set up `High to Lowpoly bake <../start/objects.html#high-to-lowpoly>`__ in BakeMaster.

Understanding Cages
===================

A Cage is an inflated copy of your base lowpoly model. When baking highpoly details onto a low-res mesh, a Cage limits the distance of shot detail-capturing projection rays.

|understandingcage_howcageworks|
    
The Cage should expand far enough to cover all highpoly geometry for best results. Expanding the Cage too far may cause glitches as projection might intersect other meshes in the scene.

.. todo:: Images side by side: 1 - cage not fully covering highpoly - bake glitches, 2 - correct cage - everything is fine.

In BakeMaster, you can choose a Cage object you created or specify the ``Extrusion`` value to inflate the lowpoly.

.. todo:: Gifs side by side: 1 - showing how to specify the extrusion, 2 - how to choose a cage object.

Decrease Baking time
====================

Map resolution
--------------

When choosing a higher map resolution, consider whether it'd be noticeable in the output rendered image, estimate the distance from the camera to that specific model, its relative size in the render, and how many details would be distinguished.

.. todo:: 3 images side by side showing one rendered model having textures baked at different res (4k, 1k, .5k).

What's the best sample count
----------------------------

Baking time also increases when setting the sample count very high. It'll result in cleaner and smoother bakes, but you can keep them pretty low and use `Denoising <./nolimits.html#denoising-maps>`__ later.

AO fragment, how long the bake took:

.. raw:: html

    <div class="content-gallery">
        <div class="content">
            <img src="../../_static/images/pages/advanced/improve/samples_8_nodenoise.png" alt="8 Samples, not denoised">
            <div class="content-description">
                <p>8 samples, 4k,</p>
                <p>not denoised, 39s</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/improve/samples_128_nodenoise.png" alt="128 Samples, not denoised">
            <div class="content-description">
                <p>128 samples, 4k,</p>
                <p>not denoised, 6m48s</p>
            </div>
        </div>
        <div class="content">
            <img src="../../_static/images/pages/advanced/improve/samples_8_denoise.png" alt="8 Samples, denoised">
            <div class="content-description">
                <p>8 samples, 4k,</p>
                <p>denoised, 1m13s</p>
            </div>
        </div>
    </div>

Help system
===========

The Help panel offers a couple of buttons that will take you to the corresponding pages of BakeMaster's online documentation you're currently reading.

.. raw:: html

    <div class="slideshow" id="slideshow-0">
        <div class="content-wrapper">
            <div class="content column active">
                <img src="../../_static/images/pages/advanced/improve/help_mainpage_385x176.png" alt="Main Page">
                <div class="slideshow-description">
                    <p>Main Page</p>
                </div>
            </div>
            <div class="content column">
                <img src="../../_static/images/pages/advanced/improve/help_howtosetupobjects_385x176.png" alt="How to Setup Objects">
                <div class="slideshow-description">
                    <p>How to Setup Objects</p>
                </div>
            </div>
            <div class="content column">
                <img src="../../_static/images/pages/advanced/improve/help_howtosetupmaps_385x176.png" alt="How to Setup Maps">
                <div class="slideshow-description">
                    <p>How to Setup Maps</p>
                </div>
            </div>
            <div class="content column">
                <img src="../../_static/images/pages/advanced/improve/help_howtobake_385x176.png" alt="How to Bake">
                <div class="slideshow-description">
                    <p>How to Bake</p>
                </div>
            </div>
            <div class="content column">
                <img src="../../_static/images/pages/advanced/improve/help_support_385x176.png" alt="Support">
                <div class="slideshow-description">
                    <p>Support</p>
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
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId('slideshow-0', 1)" onselectstart="return false">&#10095;</a>
        </div>
    </div>