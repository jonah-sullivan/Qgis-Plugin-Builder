SOURCES += __init__.py \
    plugin_builder.py \
    plugin_builder_dialog.py \
    plugin_specification.py \
    plugin_templates/__init__.py \
    plugin_templates/plugin_template.py \
    plugin_templates/processing_provider/__init__.py \
    plugin_templates/processing_provider/plugin_template.py \
    plugin_templates/shared/plugin_upload.py \
    plugin_templates/shared/test/__init__.py \
    plugin_templates/shared/test/qgis_interface.py \
    plugin_templates/shared/test/test_init.py \
    plugin_templates/shared/test/test_qgis_environment.py \
    plugin_templates/shared/test/test_translations.py \
    plugin_templates/shared/test/utilities.py \
    plugin_templates/toolbutton_with_dialog/__init__.py \
    plugin_templates/toolbutton_with_dialog/plugin_template.py \
    plugin_templates/toolbutton_with_dockwidget/__init__.py \
    plugin_templates/toolbutton_with_dockwidget/plugin_template.py \
    qgis_dirs.py \
    result_dialog.py \
    select_tags_dialog.py

FORMS += plugin_builder_dialog_base.ui \
    plugin_templates/processing_provider/wizard_form_base.ui \
    plugin_templates/toolbutton_with_dialog/wizard_form_base.ui \
    plugin_templates/toolbutton_with_dockwidget/template/module_name_dockwidget_base.ui \
    plugin_templates/toolbutton_with_dockwidget/wizard_form_base.ui \
    results_dialog_base.ui \
    select_tags_dialog_base.ui \
    plugin_templates/toolbutton_with_dialog/template/module_name_dialog_base.ui.tmpl \
    plugin_templates/toolbutton_with_dockwidget/template/module_name_dockwidget_base.ui.tmpl

TRANSLATIONS += i18n/pluginbuilder3_fr.ts
