#!/usr/bin/env python3
"""Screenshots of the workbench's Game screen under different screen filter settings.

Start melonDS with the API, the workbench and a test scene, for example:
    melonDS --api -wo --state 3 game.nds
then:
    filter_shots.py OUTDIR NAME:SETTING=VALUE,... [NAME:...]

Each NAME:... sets the listed filter settings (as filter.set: mode=off|lcd|crt, CrtSignal, CrtCable,
CrtDecoder, CrtBeamMin, GridDarkness...; see filter.get) and saves OUTDIR/NAME.png of the Game screen.
The game is paused first, so every shot shows the same frame. A NAME with no settings shoots as is.
Example:
    filter_shots.py /tmp/shots plain:mode=off off:mode=crt,CrtSignal=4 blur:mode=crt,CrtSignal=0
"""

import base64
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "python"))
from dswb.client import Client  # noqa: E402


def parse(arg):
    name, _, rest = arg.partition(":")
    settings = {}
    for item in filter(None, rest.split(",")):
        key, _, value = item.partition("=")
        settings[key] = value if key == "mode" else float(value)
    return name, settings


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    shots = [parse(a) for a in sys.argv[2:]]
    c = Client.connect()
    c.execution_control("pause")
    for name, settings in shots:
        if settings:
            c.filter_set(settings=settings)
        time.sleep(0.5)     # the filter thread filters the paused frame again, then the panel repaints
        img = c.ui_capture(panel="game", max_width=0)
        path = os.path.join(out, name + ".png")
        with open(path, "wb") as f:
            f.write(base64.b64decode(img.png))
        print(f"{path}  {img.width}x{img.height}  {settings or '(as is)'}")


if __name__ == "__main__":
    main()
