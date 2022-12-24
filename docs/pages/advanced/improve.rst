================
Get Best Results
================

Tutorials
=========

.. todo:: Embed a YouTube video tutorial

Baking from highpoly
====================

Texture baking as a method to transfer high-resolution mesh details to a low-res model has become a common practice in 3D workflows. Models with loads of geometry require more computer power and are sometimes even useless as some details won't be noticed in the final production. On the other hand, lowpoly model is easier to handle and those high-resolution details can be baked onto it.

.. todo:: Two images side by side showing wireframe overlap of high and lowpoly geometries.

.. todo:: Two images side by side showing render time for those models and no visual difference.

Read more about how you can set up `High to Lowpoly bake in BakeMaster <../start/objects.html#high-to-lowpoly>`__.

Understanding Cages
===================

A Cage is an inflated copy of your base lowpoly model. When baking highpoly details onto a low-res mesh, a Cage is used to limit the distance of shot detail-capturing projection rays.

.. todo:: A kind of gif showing a brief understandable explanation of how cage works.
    
For best results, the Cage should expand far enough to cover all highpoly geometry. Expanding the Cage too far may cause glitches as projection might intersect other meshes in the scene.

.. todo:: Images side by side: 1 - cage not fully covering highpoly - bake glitches, 2 - correct cage - everything is fine.

In BakeMaster, you can choose a Cage object created on your own, or specify the ``Extrusion`` value by which to inflate the lowpoly.

.. todo:: Gifs side by side: 1 - showing how to specify the extrusion, 2 - how to choose a cage object.

Decrease Baking time
====================

Map resolution
--------------

When choosing a higher map resolution, keep in mind whether it'd be noticeable in the output rendered image. Estimate the distance from the camera to that specific model, its relative size in the render, and how many details there'd be seen.

.. todo:: 3 images side by side showing one rendered model that has textures baked at different res (4k, 1k, .5k).

What's the best sample count
----------------------------

Baking time also increases when setting the sample count very high. It'll result in cleaner and smoother bakes, but you can keep them pretty low and use `Denoising <./nolimits.html#denoising-maps>`__ later.

.. todo:: 3 images side by side showing: 1 - low samples, no denoise, 2 - high samples, no denoise, 3 - low samples, denoise

Help system
===========

.. todo:: Slideshow of images showing: some props descriptions and the Help panel buttons.