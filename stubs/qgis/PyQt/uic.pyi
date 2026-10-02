from typing import Any

from PyQt6.QtWidgets import QWidget

# PyQt6-stubs has no uic module. The generated widgets and form classes
# are only known at runtime, so they are typed as Any.
def loadUiType(uifile: str) -> tuple[Any, Any]: ...
def loadUi(
    uifile: str, baseinstance: QWidget | None = ..., package: str = ...
) -> Any: ...
