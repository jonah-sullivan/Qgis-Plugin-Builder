NOTE
====

**QGIS 4 development now takes place in master branch.**

QGIS Plugin Builder
===================

.. image:: https://github.com/jonah-sullivan/Qgis-Plugin-Builder/workflows/Tests/badge.svg
   :target: https://github.com/jonah-sullivan/Qgis-Plugin-Builder/actions

.. image:: https://img.shields.io/badge/License-GPL_v2-blue.svg
   :target: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html

.. image:: https://img.shields.io/badge/QGIS-Plugin_Repository-brightgreen
   :target: https://plugins.qgis.org/plugins/plugin_builder/

.. figure:: help/source/images/wizard_required_info.png

This is a QGIS plugin that generates a QGIS plugin template for use in
creating custom plugins.

Walkthrough
-----------

**1. Install Plugin Builder**

Open QGIS and go to **Plugins → Manage and Install Plugins**. Search for
*Plugin Builder* and install it.

**2. Open Plugin Builder**

Go to **Plugins → Plugin Builder → Plugin Builder**. The wizard opens.

**3. Fill in the required fields**

On the first page enter:

- **Class name** — CamelCase Python class name (e.g. ``MyPlugin``)
- **Module name** — snake_case file name (e.g. ``my_plugin``)
- **Plugin name** — human-readable title shown in QGIS menus
- **Description** — one-line summary of what the plugin does
- **Version** — starting version number (e.g. ``0.1``)
- **Minimum QGIS version** — minimum compatible version (required; defaults to ``4.0``)
- **Maximum QGIS version** — maximum compatible version (required; defaults to ``4.99``)
- **Author** and **Email**

On the second page enter a longer **About** description.

**4. Choose a template**

On the template page select one of:

- **Tool button with dialog** — toolbar button that opens a modal dialog
- **Tool button with dock widget** — toolbar button that opens a dock panel
- **Processing provider** — adds an algorithm to the Processing toolbox

**5. Set publication info (optional)**

Enter URLs for your bug tracker, home page, and repository. Add tags to
help users find the plugin on the QGIS Plugin Repository.

**6. Choose additional components**

Check the components you want included:

- **Internationalization** — stub i18n setup for adding translated strings
- **Help** — a Sphinx documentation project in ``help/``
- **Unit tests** — a pytest test suite wired to ``pytest-qgis``
- **Helper scripts** — scripts for publishing to plugins.qgis.org and managing translations
- **Makefile** — a GNU Makefile for building and deploying
- **pb_tool** — a ``pb_tool.cfg`` for the ``pb_tool`` command-line deploy tool

**7. Generate the plugin**

Click **Generate**, choose an output directory, and click **Generate** again.
Plugin Builder writes all the files into a new directory named after your module.

Resource file compilation is optional. It is best practice to reference
resources such as icons and images using ``os.path`` rather than Qt's resource
system::

    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    icon = QIcon(icon_path)

This avoids the need to run ``rcc`` at build time and keeps your assets visible
as ordinary files. If you do use a ``.qrc`` file, compile it with::

    rcc -g python resources.qrc -o resources.py

**8. Deploy and test**

Use ``pb_tool`` to deploy the generated plugin to your QGIS plugin directory::

    cd my_plugin
    pip install pb_tool
    pb_tool deploy

Then open QGIS, enable the plugin in **Plugins → Manage and Install Plugins**,
and run it to confirm it loads correctly.

**9. Start developing**

The generated plugin is a working stub. Open the source files in your editor,
implement your logic, and use ``pb_tool deploy -q`` to redeploy quickly as you
iterate.

Documentation
-------------

See the `help`_ documentation for full details on each wizard field and
deployment option.

.. _help: https://jonah-sullivan.github.io/Qgis-Plugin-Builder/

Contributing
------------

New plugin templates can be added by creating a subdirectory below ``plugin_templates`` and registering the template in ``plugin_templates/__init__.py``
