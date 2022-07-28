# BakeMaster Docs

The documentation uses plain text files in reStructuredText format and the Sphinx documentation system.

### Documentation structure:
```
C:.
├───access_modules
├───contribute
├───start
├───versions
├───workflow
│   ├───bake
│   ├───errors
│   ├───interface
│   ├───maps
│   └───objects
├───_static
└───_templates
```

### Create your local build:

A local HTML version can be created using the commands:

- `python -m pip install sphinx` - Sphinx installation
- In the `docs/` directory, use `make html`

HTML pages will sit in `docs/_build/html`.

### Contribute

You can edit documentation by:

- Fork the repo
- Make changes
- Open Pull Request

More information regarding Contributions can be viewed in <a href="">Contributing Guidelines</a>.