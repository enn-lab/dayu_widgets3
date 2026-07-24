"""
Trae Theme for dayu_widgets

A dark theme inspired by Trae IDE (Vibe Coding IDE).
Features near-black backgrounds with teal/cyan accents.

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
            #08080c  editor / deepest background
            #0c0c12  sidebar / panels
            #14141c  cards / elevated surfaces
            #1c1c24  hover / active states

        Text hierarchy (lightest -> darkest):
            #ffffff  titles / primary
            #a0a0a8  body / secondary
            #686870  hints / disabled

        Accent:
            #00d9a0  teal primary
            #00b386  teal dark
            #33ffbd  teal light

        Border:
            #1a1a22  subtle dividers
    """

    # Trae accent color (teal/cyan)
    teal = "#00d9a0"
    teal_dark = "#00b386"
    teal_light = "#33ffbd"

    def __init__(self):
        super(MTraeTheme, self).__init__(theme="dark", primary_color=MTraeTheme.teal)

    def _dark(self):
        """Override dark theme colors with Trae palette."""
        # Text colors (light on dark)
        self.title_color = "#ffffff"
        self.primary_text_color = "#a0a0a8"
        self.secondary_text_color = "#686870"
        self.disable_color = "#404048"

        # Border & dividers
        self.border_color = "#1a1a22"
        self.divider_color = "#1a1a22"
        self.header_color = "#08080c"

        # Icon color
        self.icon_color = "#606068"

        # Background hierarchy (darkest to lightest)
        self.background_color = "#08080c"
        self.background_selected_color = "#1c1c24"
        self.background_in_color = "#0c0c12"
        self.background_out_color = "#14141c"
        self.mask_color = utils.fade_color(self.background_color, "90%")
        self.toast_color = "#1c1c24"


def apply_trae_theme(widget):
    """Convenience function to apply Trae theme to a widget.

    :param widget: QWidget instance to apply the theme.
    :return: None
    """
    theme = MTraeTheme()
    theme.apply(widget)
