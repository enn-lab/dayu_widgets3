"""
Trae Theme for dayu_widgets

A dark theme inspired by Trae IDE (Vibe Coding IDE).
Features deep charcoal backgrounds with teal/cyan accents.

Usage::

    from dayu_widgets.themes.trae import apply_trae_theme
    apply_trae_theme(your_window)

Or use the theme class directly::

    from dayu_widgets.themes.trae import MTraeTheme
    trae_theme = MTraeTheme()
    trae_theme.apply(your_window)
"""

# Import local modules
from dayu_widgets.theme import MTheme
from dayu_widgets import utils


class MTraeTheme(MTheme):
    """Trae-inspired dark theme with teal/cyan accent color.

    Color palette extracted from Trae IDE screenshots::

        Background hierarchy (darkest -> lightest):
            #0d0d12  primary background (editor)
            #16161e  sidebar / panels
            #1e1e28  cards / elevated surfaces
            #2a2a38  hover / active states

        Text hierarchy (lightest -> darkest):
            #e8e8ed  titles / primary
            #a0a0b0  body / secondary
            #6e6e80  hints / disabled

        Accent:
            #00e5a0  teal primary
            #00c48c  teal dark
            #33ffbd  teal light

        Border:
            #2a2a35  subtle dividers
    """

    # Trae accent color (teal/cyan)
    teal = "#00e5a0"
    teal_dark = "#00c48c"
    teal_light = "#33ffbd"

    def __init__(self):
        super(MTraeTheme, self).__init__(theme="dark", primary_color=MTraeTheme.teal)

    def _dark(self):
        """Override dark theme colors with Trae palette."""
        # Text colors (light on dark)
        self.title_color = "#e8e8ed"
        self.primary_text_color = "#a0a0b0"
        self.secondary_text_color = "#6e6e80"
        self.disable_color = "#4a4a5a"

        # Border & dividers
        self.border_color = "#2a2a35"
        self.divider_color = "#2a2a35"
        self.header_color = "#0d0d12"

        # Icon color
        self.icon_color = "#6e6e80"

        # Background hierarchy (darkest to lightest)
        self.background_color = "#0d0d12"
        self.background_selected_color = "#2a2a38"
        self.background_in_color = "#16161e"
        self.background_out_color = "#1e1e28"
        self.mask_color = utils.fade_color(self.background_color, "90%")
        self.toast_color = "#2a2a38"


def apply_trae_theme(widget):
    """Convenience function to apply Trae theme to a widget.

    :param widget: QWidget instance to apply the theme.
    :return: None
    """
    theme = MTraeTheme()
    theme.apply(widget)
