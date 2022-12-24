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

.. todo:: A kind of gif showing an understandable explanation of how the cage works.
    
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

.. todo:: 3 images side by side showing: 1 - low samples, no denoise, 2 - high samples, no denoise, 3 - low samples, denoise

Help system
===========

.. todo:: Slideshow of images showing: some props descriptions and the Help panel buttons.

.. raw:: html

    <div class="slideshow">
        <div class="content-wrapper">
            <div class="content column active">
                <img src="../../_static/images/pages/setup/installation/access_350x320.gif" alt="access">
                <div class="slideshow-description">
                    <b>Headline</b><br>
                    <p>Hi from slide 1</p>
                </div>
            </div>
            <div class="content">
                <img src="../../_static/images/pages/setup/installation/install_350x320.gif" alt="access">
                <div class="slideshow-description">
                    <b>Headline</b><br>
                    <p>Hi from slide 2</p>
                </div>
            </div>
            <div class="content">
                <img src="../../_static/images/pages/setup/installation/remove_350x320.gif" alt="access">
                <div class="slideshow-description">
                    <b>Headline</b><br>
                    <p>Hi from slide 3</p>
                </div>
            </div>
        </div>
        <div class="footer">
            <a class="prev" onclick="slideshow_setSlideByRelativeId(-1)">&#10094;</a>
            <div class="controls">
                <span class="dot-active" onclick="slideshow_setSlideByAbsoluteId(1)"></span>
                <span class="dot-inactive" onclick="slideshow_setSlideByAbsoluteId(2)"></span>
                <span class="dot-inactive" onclick="slideshow_setSlideByAbsoluteId(3)"></span>
            </div>
            <a class="next" onclick="slideshow_setSlideByRelativeId(1)">&#10095;</a>
        </div>
    </div>