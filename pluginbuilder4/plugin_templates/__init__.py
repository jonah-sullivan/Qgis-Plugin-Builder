from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin_template import PluginTemplate


def templates() -> list["PluginTemplate"]:
    """Return one instance of each plugin type the wizard offers.

    The list order is the order of the wizard's template drop-down: the
    dialog picks a template by its index in this list.
    """
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
