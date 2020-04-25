#!/usr/bin/env python

import tcod
import tcod.event
import random

# Setup the font.
# tcod.console_set_custom_font(
#     "terminal10x10_gs_tc_custom.png",
#     tcod.FONT_LAYOUT_TCOD | tcod.FONT_TYPE_GREYSCALE,
# )

tcod.console_set_custom_font(
    "terminal8x8_gs_ro_custom.png",
    tcod.FONT_LAYOUT_ASCII_INROW | tcod.FONT_TYPE_GREYSCALE, 16, 32
)

# Initialize the root console in a context.
root_console = tcod.console_init_root(80, 60, order="F")
