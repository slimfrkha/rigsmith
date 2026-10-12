"""macOS desktop apps."""

from rigsmith.backends import Cask
from rigsmith.model import Artifact

Artifact(
    id="rectangle",
    help="Window management with keyboard shortcuts and snap areas (⌃⌥← halves, ⌃⌥↩ maximize).",
    sources=[Cask("rectangle", os="darwin")],
    check="test -d /Applications/Rectangle.app",
)
