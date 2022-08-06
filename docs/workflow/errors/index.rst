==============
Error Handling
==============

On this page, you will get the information about all BakeMaster errors, warnings, and messages that are printed to the Blender Console and to the Blender Status bar. In addition, we left a section with tips about what to do if BakeMaster raises an unexpected error.

Contents
========

* :ref:`bakemaster_statuses` - what BakeMaster reports to the Blender status bar
* :ref:`bakemaster_console` - what BakeMaster prints to the Blender Console
* :ref:`bakemaster_errors` - how to deal with unexpected script errors.
  
.. _bakemaster_statuses:

BakeMaster Statuses
===================

As you flow with BakeMaster, you might see several status reports in the Blender Info bar. These statuses indicate the current stage of baking or a problem message that occurred. Statuses are divided into 2 groups: Workflow Statuses (reports sent while configuring BakeMaster) and Baking Statuses (reports sent while the baking process is active).

Workflow Statuses
-----------------

Below are descriptions and report conditions of all handled workflow info status reports that are sent while configuring BakeMaster from the Panel.

- ``Report id`` - how the reported status is labeled
- ``Report condition`` - condition to call the status report
- ``Message`` - message that will be reported

+--------------------------------+------------------------+------------------------------------+
| Report id                      | Report condition       | Message                            |
+--------------------------------+------------------------+------------------------------------+
|| ``INFO_ITEM_EXISTS``          || On adding object to   || Blender Status Bar:               |
||                               || the List of Objects,  || ``Mesh exists in the list``       |
||                               || that already exists   ||                                   |
||                               || in the list.          ||                                   |
+--------------------------------+------------------------+------------------------------------+
|| ``INFO_ITEM_NONMESH``         || On adding object to   || Blender Status Bar:               |
||                               || the List of Objects,  || ``Expected mesh object``          |
||                               || of a non-mesh type.   ||                                   |
+--------------------------------+------------------------+------------------------------------+
|| ``INFO_MAP_PREVIEWNOTCYCLES`` || On switching on the   || Blender Status Bar:               |
||                               || map preview, when the || ``Swith to Cycles Render Engine`` |
||                               || render engine is not  ||                                   |
||                               || Cycles                ||                                   |
+--------------------------------+------------------------+------------------------------------+

Baking Statuses
---------------

Below are descriptions and report conditions of all handled baking info status reports that are sent while the baking process is active.

- ``Report id`` - how the reported status is labeled
- ``Report condition`` - condition to call the status report
- ``Message`` - message that will be reported

+-------------------------------+-----------------------------+-----------------------------------------+
| Report id                     | Report condition            | Message                                 |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``FATAL``                    || On the bake operator       || Blender Status Bar:                    |
|| ``NOT_IN_CYCLES``            || execution, render engine   || ``Swith to Cycles Render Engine``      |
||                              || is not Cycles.             ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``FATAL``                    || On the bake operator       || Blender Status Bar:                    |
|| ``MAP_QUEUE_EMPTY``          || execution, no maps were    || ``No maps to bake``                    |
||                              || eligible to be baked.      ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``FATAL``                    || On the bake operator       || Blender Status Bar:                    |
|| ``ITEM_QUEUE_EMPTY``         || execution, no Objects      || ``No items to bake``                   |
||                              || were eligible to be baked. ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``FATAL``                    || On the baking process      || Blender Status Bar:                    |
|| ``KEYBOARD_INTERRUPT``       || active, the execution      || ``Bake Process Interrupted by user``   |
||                              || was aborted by the user.   || ``- execution aborted``                |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``FATAL``                    || On the baking process      || Blender Status Bar:                    |
|| ``BACKSPACE_EVENT``          || active, the ``BACKSPACE``  || ``Cancelled all next bakes in the``    |
||                              || key was hit and the baking || ``queue``                              |
||                              || queue was emptied.         ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``ENGINE_NONCYCLES``         || active, the current render || ``Current render engine does not``     |
||                              || engine didn't support      || `` support baking``                    |
||                              || baking.                    ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``CAGE_OBJECT_INVALID``      || active, the cage object    || ``Invalid cage object, the cage mesh`` |
||                              || for the current object     || ``must have the same number of faces`` |
||                              || was invalid.               || ``as the active object``               |
||                              ||                            ||                                        |
||                              ||                            || ``Invalid cage object, cage object``   |
||                              ||                            || ``must be a mesh``                     |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``ERROR_MAP_PASSES``         || active, there were no or   || ``No or not enough passes``            |
||                              || not enough passes to bake  ||                                        |
||                              || the map.                   ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``OJECT_INVALID``            || active, the current object || ``Invalid item settings``              |
||                              || was invalid.               ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``ImageDenoiseRuntimeError`` || active, while denoising    || ``Denoising Fatal Error``              |
||                              || baked image, Runtime Error ||                                        |
||                              || was raised.                ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``BAKE_ERROR``               || active, while baking the   || ``Unexpected bake error``              |
||                              || current map, unexpected    ||                                        |
||                              || bake error occurred.       ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``BAKING_PROGRESS``          || On the baking process      || Blender Status Bar:                    |
||                              || active, the current        || ``Baking [ObjectName]:``               |
||                              || baking progress is.        || ``[MapName], map [CurrentMapIndex]``   |
||                              || reported every 2 seconds.  || ``of [Length of Maps]``                |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``BAKING_COMPLETED``         || After the baking process   || Blender Status Bar:                    |
||                              || has completed, this        || ``Bake completed in [Time]``           |
||                              || message is reported.       ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+
|| ``MESSAGE``                  || On the baking process      || Blender Status Bar:                    |
|| ``CHANGED_MATERIALS``        || active, when restoring     || ``Changed materials``                  |
||                              || original materials, an     ||                                        |
||                              || error occurred.            ||                                        |
+-------------------------------+-----------------------------+-----------------------------------------+

.. _bakemaster_report_classes:

Report Classes
--------------

The first row in the ``Report id`` field is the class of the report. The table below shows which operations these classes touch:

+----------------------+--------------------------------------------------------------------+
| Class                | Description                                                        |
+----------------------+--------------------------------------------------------------------+
| ``FATAL``            | Fatal report usually stops the execution of the bake.              |
+----------------------+--------------------------------------------------------------------+
| ``MESSAGE``          | Message report usually skips the operation it is referred to.      |
+----------------------+--------------------------------------------------------------------+
| ``BAKING_PROGRESS``  | Baking progress is an idle report which shows the baking progress. |
+----------------------+--------------------------------------------------------------------+
| ``BAKING_COMPLETED`` | Baking complete is reported when the bake has been finished.       |
+----------------------+--------------------------------------------------------------------+
|| ``INFO_...``        || Information message is reported when something blocks a specific  |
||                     || process from the full execution.                                  |
+----------------------+--------------------------------------------------------------------+

.. _bakemaster_console:

BakeMaster Console Prints
=========================

Apart from the reports to the Blender Status bar, BakeMaster also prints messages to the Blender Console. BakeMaster can do printing only while baking. Below is the table showing all printed messages, their print conditions and descriptions:

- ``Print id`` - how the print is labeled
- ``Print condition`` - condition to print
- ``Message`` - message that will be printed

+-------------------------------+--------------------------------+---------------------------------------+
| Print id                      | Print condition                | Message                               |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``MESSAGE``                  || On the baking process         || Blender Status Bar:                  |
|| ``SUBFOLDER_ERROR``          || active, an error has been     || ``Subfolder creation error``         |
||                              || raised while creating         ||                                      |
||                              || a subfolder.                  ||                                      |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``INFO``                     || On the baking process         || Blender Status Bar:                  |
|| ``CONTEXT_OVERRIDE``         || active, when overriding       || ``Overriding Context``               |
||                              || ``bpy.context`` for           ||                                      |
||                              || operators' execution.         ||                                      |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``MESSAGE``                  || On the baking process         || Blender Status Bar:                  |
|| ``BAKED_MATERIAL_ABORT``     || active, when creating a       || ``Aborting baked material creation`` |
||                              || material with all baked       || ``for [ObjectName]: no maps to``     |
||                              || maps for the object,          || ``create material from``             |
||                              || there were no maps to         ||                                      |
||                              || create the material from.     ||                                      |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``MESSAGE``                  || On the baking process         || Blender Status Bar:                  |
|| ``OPERATION_INVALID``        || active, all the ``MESSAGE``   || ``[MESSAGE]``                        |
||                              || report classes statuses       ||                                      |
||                              || are also printed.             ||                                      |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``STACK_OVERFLOW``           || On the baking process         || Blender Status Bar:                  |
||                              || active, ``blender.exe``       || ``catching STACK_OVERFLOW, reset``   |
||                              || is catching a                 || ``BakeMaster and restart Blender``   |
||                              || ``STACK_OVERFLOW_EXCEPTION``. ||                                      |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``MESSAGE``                  || On the baking process         || Blender Status Bar:                  |
|| ``ImageDenoiseRuntimeError`` || active, while denoising       || ``Denoising Fatal Error``            |
||                              || baked image, Runtime Error    ||                                      |
||                              || was raised.                   ||                                      |
+-------------------------------+--------------------------------+---------------------------------------+
|| ``FATAL``                    || On the baking process         || Blender Status Bar:                  |
|| ``KEYBOARD_INTERRUPT``       || active, the execution         || ``Bake Process Interrupted by user`` |
||                              || was aborted by the user.      || ``- execution aborted``              |
+-------------------------------+--------------------------------+---------------------------------------+

.. attention::
    :ref:`bakemaster_report_classes` *are also applied to the Console prints.*

.. _bakemaster_errors:

Unexpected BakeMaster Errors
============================

We make our best to test and establish the add-on's stability, but there is little possibility to catch an unexpected error message. Those messages are highly likely to be connected with a source script error, and if you face one, we extremely encourage you to **Report an Unexpected Issue**. The tips below will help you before the error you have reported will have been fixed:

.. admonition:: Tip №1
    :class: tip

    If you are using the BakeMaster add-on in the Blender version it is **not** meant to be **compatible** with, wait for the developers to upgrade BakeMaster to meet its requirements.

.. admonition:: Tip №2
    :class: tip

    Try to **identify** which specific action you do causes the **error**. Avoid doing that action.

.. admonition:: Tip №3
    :class: tip

    If Blender is crashing due to the error, it might be your system **memory** full or a script stack overflow **error**. In these cases, try copying the objects you want to proceed with the bake for into a new Blender file and repeat the bake.

.. admonition:: Tip №4
    :class: tip

    If you have opened a Blender file (created in one Blender version) in the other Blender version, **metadata leak and incompatibility** might cause a BakeMaster crash error. Try running the bake in the Blender version the Blender file was created in.