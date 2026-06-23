def templates():
    from .toolbutton_with_dialog.plugin_template import ToolbuttonWithDialogPluginTemplate
    from .toolbutton_with_dockwidget.plugin_template import ToolbuttonWithDockWidgetPluginTemplate
    from .processing_provider.plugin_template import ProcessingProviderPluginTemplate
    return [
        ToolbuttonWithDialogPluginTemplate(),
        ToolbuttonWithDockWidgetPluginTemplate(),
        ProcessingProviderPluginTemplate()
    ]
