===========================
Installing the Source Files
===========================

Installing Dependencies
=======================

To build the Documentation locally on your computer, you will need to have installed the following software:

1. `Python <https://www.python.org/>`__
2. `Git <https://git-scm.com/>`__
   
.. note:: 
    The installation process may be different on each operating system, the guides can be found online.

Installing Project Files
========================

1. To install Documentation source files and BakeMaster Demo version scripts, clone the GitHub repo using the command::

    $ git clone https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git

2. List the current configured remote repository for your fork::

    $ git remote -v
    > origin ... (fetch)
    > origin ... (push)

3. Specify a new remote upstream repository that will be synced with the fork::

    $ git remote add upstream https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git

4. Verify the new upstream repository you've specified for your fork::

    $ git remote -v
    > origin ... (fetch)
    > origin ... (fetch)
    > origin https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git (push)
    > origin https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git (push)
