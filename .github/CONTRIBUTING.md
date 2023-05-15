<img src="https://raw.githubusercontent.com/KirilStrezikozin/BakeMaster-Blender-Addon/master/.github/images/logos/bakemaster-addon-logo-128.png" alt="bakemaster-logo">

# Contribute Documentation

Needless to say that working as one community for the project's perfectness is the most significant experience in its development. Furthering the idea, you are most welcome to suggest, request, edit, fix, and improve BakeMaster. Whether you'd like to submit a feature request, report an issue, solve a tiny spell mark or a major script bug, the sections below will guide you.

---

## List of Contents

- [Useful Links](#useful-links)
- [Creating a fork](#creating-a-fork)
- [Keep your fork up to date](#keep-your-fork-up-to-date)
- [Write some code](#write-some-code)
- [Contacts](#contacts)

---

## Useful Links

> Rate BakeMaster on [**Blender Market**](https://blendermarket.com/products/bakemaster) or [**Gumroad**](https://kemplerart.gumroad.com/l/bakemaster).

> [**Submit an issue**](https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/issues/new/choose) that you found in the BakeMaster add-on or the documentation.

> BakeMaster news is announced in the [**BakeMaster Chat**](https://discord.gg/2ePzzzMBf4) and the [**Announcements on GitHub**](https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/discussions/categories/announcements).

---

## Creating a fork

Start by forking the BakeMaster repo. Read more on [GitHub Docs](https://docs.github.com/en/get-started/quickstart/fork-a-repo).

1. Clone your fork to your local machine

        $ git clone https://github.com/USERNAME/FORKED-REPO.git

---

## Keep your fork up to date


1. List the current configured remote repository for your fork:

        $ git remote -v
        > origin ... (fetch)
        > origin ... (push)

2. Specify a new remote upstream repository that will be synced with the fork:

        $ git remote add upstream https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git

4. Verify the new upstream repository you've specified for your fork:

        $ git remote -v
        > origin ... (fetch)
        > origin ... (fetch)
        > origin https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git (push)
        > origin https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon.git (push)

5. Update your fork with the latest upstream changes:

        $ git fetch upstream

6. Checkout master branch and merge upstream repo's master branch:
    
        $ git checkout master
        $ git merge upstream/master

---

## Write some code

### Create a branch

Whether it's a bugfix or feature implementation, it's important that you create a new branch. It will help better track progress on your tasks and manage pull requests.

    $ git checkout master
    $ git branch new_branch
    $ git checkout new_branch

We recommend to name your branches in a simple and informative matter. Ideally, consider following these naming conventions:

- `task` - task id or corresponding issue. Example: `issue-#33`
- `name` - short name describing a task. Example: `bugfix-existing-tria-mods-ignored`
- `version` - future version of BakeMaster you expect your work to be released for (it's a good practice to decide that with the origin repo owner). Example: `2.0.3`

        $ git branch task_name_version

    By example:
        
        $ git branch issue-#33_bugfix-tria-mods-ignored_2.0.3

### Code Style guide

#### Existing practices

This repo tries to follow [pep8](https://peps.python.org/pep-0008/) code style conventions for Python while also identifying its own coding style guidelines for ease of readability and maintenance.

#### Long if statements

If your if statement is rather long and complex, use `any()` and `all()` or define logic values as separate variables:

```python
# Correct


if not all([container.get_is_lowpoly(),
            self.data_name == "containers",
            container.get_bm_name(
                bakemaster, self.data_name) == "objects",
            allow_drag_viz,
            container.index == bakemaster.get_drag_to_index(
                self.data_name)]):
    return
```

```python
# Correct


if data is None or any(
        [
            not self.has_multi_selection(
                bakemaster, data, data_name),
            not data.is_selected
        ]):
    ...


# Also correct


is_data_not_in_ms = any([
    not self.has_multi_selection(
        bakemaster, data, data_name),
    not data.is_selected]):

if data is None or is_data_not_in_ms:
    ...
```

#### Nested if statements

Avoid nested if statements and move highly cyclomatic code into separate functions.

```python
# Wrong


def hell_of_if_statements(...) -> result:
    if long_statement:

        if another_long_statement:
            for item in collection:
                if some_statement:
                    # do action
                elif another_statement:
                    if more:
                        # do action
                    else:
                        if ...
                else:
                    continue

        elif another_long_statement:
            # do lots of action

        else:
            if something:
                # do some action
            else:
                if something_else:
                    # do something else
```

```python
# Correct


def some_func() -> result:
    for item in collection:
        if should_continue:
            continue

        if some_statement:
            # do action
        else:
            # do something else


def another_func() -> result:
    ...


def that_is_better(...) -> result:
    if not long_statement:
        return

    if another_long_statement:
        some_func()

    elif another_long_statement:
        another_func()
        # some more action

    else:
        # do some action
```

#### Comments and descriptions

If line is longer than 79 characters because of a comment or description, add `# noqa: E501` to the end of it.

```python
# Wrong commenting

some_v = value #here i explain what it is
some_v2 = diff_value #that's gonna take so much time to explain what it does


# Correct commenting


some_v = value  # here i explain what it is

# Try to make it simple.
informative_name = diff_value
```

- You can explain what function is doing if it isn't obvious by its name and provide a description of parameters
- You can describe what class if for

Example:

```python
def _generic_ticker_Update(self: PropertyGroup, context: Context,
                           walk_data: str, double_click_ot_idname="") -> None:
    """
    Generic ticker property update.

    Parameters:
        self - pointer to prop's PropertyGroup itself.

        context - current data context.

        walk_data - attribute name of Collection Property that
                has uilist walk features.

        double_click_ot - bl_idname of an operator that will be called on
                double click event caught.
    """

    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data
    bakemaster.is_drag_lowpoly_data = False

    walk_data_getter = getattr(bakemaster, "get_active_%s" % walk_data)
    data, containers, attr = walk_data_getter()
    if data is None:
        bakemaster.log("pux0000", walk_data, self)
        return

    ...
```

```python
class BM_OT_Global_WalkData_AddDropped(Operator):
    """
    Add dropped objects to given walk_data data.

    Internal, not used in the UI, invoked from drop_name_Update.
    """

    bl_idname = 'bakemaster.global_walkdata_adddropped'
    bl_label = "New item..."
    bl_description = "Add dropped objects into as new items"
    bl_options = {'INTERNAL', 'UNDO'}


    def remove(self, bakemaster: PropertyGroup):
        bakemaster.wh_remove(self.data, self.walk_data, self.index)

    ...
```

#### Naming conventions

For functions and variables used in a submodule only, add one leading `_` underscore. This specifies their pseudo-privacy.

```python
# Wrong

__ui_pcoll_open = {}

# this function isn't used anywhere except in this submodule
def __load_preview_collections() -> bpy.utils.previews.ImagePreviewCollection:
    ...

# this function also isn't used anywhere except in this submodule
def check_walk_data_safety(data_name: str) -> None:
    ...
```

```python
# Correct

_ui_pcoll_open = {}

def _load_preview_collections() -> bpy.utils.previews.ImagePreviewCollection:
    ...

def _check_walk_data_safety(data_name: str) -> None:
    ...
```

But private methods and variables names in classes should be led by two `_` underscores though.

```python
# Correct

class Global(BM_PropertyGroup_Helper):
    ...

    __preview_collections = {
        "main": _load_preview_collections(),
    }

    def __wh_clear_ms(self, _: typing.Union[None, PropertyGroup],
                      data_name: str) -> None:
        ...
```

#### Type Hints

Consider adding type hints only for function parameters and return values, don't add them for variables or class attributes.

```python
# Correct


def _generic_drag_empty_ticker_Update(self: PropertyGroup, context: Context,
                                      walk_data: str) -> None:
    ...
    bakemaster = context.scene.bakemaster
    bakemaster.walk_data_name = walk_data
    bakemaster.is_drag_lowpoly_data = False
    ...
```

#### License block

Adding `GPL License Block` in the top of the `.py` file is encouraged. An example of it you can find [here](https://github.com/KirilStrezikozin/BakeMaster-Blender-Addon/blob/master/LICENSE.txt).

### Editing Documentation

BakeMaster Documentation is made using [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html) with [Furo](https://github.com/pradyunsg/furo) theme, and hosted with [ReadTheDocs](https://readthedocs.org/). Click on the given hyperlinks to view guides and information.

### Build documentation locally

    > in project root folder
    $ cd docs/
    $ make chtml

    > find html pages in docs/_build/html which you can open in your browser

### Make changes

Documentation files are in `.rst` format. A nice guide can be found [here](https://github.com/DevDungeon/reStructuredText-Documentation-Reference).

---

## Contacts

> [Contacts](https://bakemaster-blender-addon.readthedocs.io/en/latest/pages/more/connect.html#contact-and-chat)

**kemplerart's contacts**

> email: kirilstrezikozin@gmail.com
> telegram: https://t.me/kemplerart
> discord: kemplerart#1586
