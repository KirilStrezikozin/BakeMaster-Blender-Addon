==========================
Building the Documentation
==========================

The Documentation is written in .reStructuredText text files and built using `Sphinx <https://www.sphinx-doc.org/en/master/>`__.

1. To install Sphinx, run the following command::

    $ python -m pip install -U sphinx

2. Navigate to the project working directory, then to the :file:`/docs/` folder
3. To build the documentation, run the command::
   
    $ make html

HTML pages will be in the :file:`/_build/` directory.

4. To view the built documentation locally in your Browser, open the :file:`/_build/html/index.html` in the Browser.