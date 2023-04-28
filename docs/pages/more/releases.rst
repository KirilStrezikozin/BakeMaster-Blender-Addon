========
Releases
========

All BakeMaster Releases and Changelogs are listed on this page. Each new release comes with new features, improvements, or fixes. For clarity, each section has a ``tag`` to identify the changes.

2.0.2 Release
=============

.. admonition:: Tag
    :class: important

    `2.0.2 - April 28th, 2023 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

**Fixes:**

#. Albedo, Metallic, Roughness, and Opacity Maps weren't baked properly from Highpoly (`issue-29 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/29>`__)
#. ID Maps weren't baked if Object had NoneType Materials (`dev-a1a4836 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/a1a4836aa42eae83b6173df147ae63545dff5416>`__)
#. If bake took more than a minute, "Bake completed in ..." didn't show correct time the bake took (`dev-de81454 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/de81454994b1dd73b59fb1167cf0f76bf0011451>`__)
#. Normal map colorspace could not be set (`issue-27 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/27>`__)
#. Normal Map bake with Oject/Materials data outputted raw vectors colors instead of normals (`dev-717cc45 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/717cc4574e985fca7f0617bffd0b195c509f6068>`__)
#. UVMap for bake was set to be the UVMap to bake from (`dev-e4aff4e <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/e4aff4ef30027124ed7270e22f854f10d41de651>`__)
#. Bake could not proceed when objects were hidden at the start (`dev-07ead0b <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/07ead0b3f7716624e098402c2c7990ed08995610>`__)
#. Normal Map bake from multires caused errors (`dev-2c27a29 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/2c27a29c08b20a0d8f95577264e5fcde52997842>`__)

**New Features:**

#. Pack tiled images since Blender 3.5 supports it (`dev-9a954c8 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9a954c8aadd3b086b609676dad4492e588b3abbe>`__)

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.0.2/pages/about.html#key-features>`__.

2.0.1 Release
=============

.. admonition:: Tag
    :class: important

    `2.0.1 - March 8th, 2023 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

**Fixes:**
#. Image format (.png) is occasionally written twice (.png.png) (`issue-22 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/22>`__)
#. Roughness map wasn't added to Baked Material (`dev-9d1a30a <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9d1a30ab757115b1c7c976c20b2c36e0566cb971>`__)
#. Color stepping when baking Displacement from Multires (`dev-9d1a30a <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9d1a30ab757115b1c7c976c20b2c36e0566cb971>`__)
#. Displacement map from material not baking out (`dev-9d1a30a <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon-Dev/commit/9d1a30ab757115b1c7c976c20b2c36e0566cb971>`__)

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.0.1/pages/about.html#key-features>`__.

2.0.0 Release
=============

.. admonition:: Tag
    :class: important

    `2.0.0 - December 29th, 2022 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

Powerful update, refactor of the whole addon.

`Features <https://bakemaster-blender-addon.readthedocs.io/en/2.0.0/pages/about.html#key-features>`__.

1.1.0 Release
=============

.. admonition:: Tag
    :class: important

    `1.1.0 - October 6th, 2022 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

Presets functionality added.

`Features <https://bakemaster-blender-addon.readthedocs.io/en/1.1.0/start/about/introduction.html#key-features>`__.

1.0.0 Release
=============

.. admonition:: Tag
    :class: important

    `1.0.0 - September 12th, 2022 <https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/releases>`__

The first release of BakeMaster Blender Addon.

`Features <https://bakemaster-blender-addon.readthedocs.io/en/1.0.0/start/about/introduction.html#key-features>`__.
    