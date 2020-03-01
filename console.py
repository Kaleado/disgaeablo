#!/usr/bin/env python

import tcod
import tcod.event
import random

# Setup the font.
tcod.console_set_custom_font(
    "terminal10x10_gs_tc.png",
    tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
)

# Initialize the root console in a context.
root_console = tcod.console_init_root(80, 60, order="F")
