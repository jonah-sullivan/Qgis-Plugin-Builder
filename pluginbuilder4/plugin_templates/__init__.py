def templates():
    from .processing_provider.plugin_template import ProcessingProviderPluginTemplate
    from .toolbutton_with_dialog.plugin_template import (
        ToolbuttonWithDialogPluginTemplate,
    )
    from .toolbutton_with_dockwidget.plugin_template import (
        ToolbuttonWithDockWidgetPluginTemplate,
    )

    return [
        ToolbuttonWithDialogPluginTemplate(),
        ToolbuttonWithDockWidgetPluginTemplate(),
        ProcessingProviderPluginTemplate(),
    ]
