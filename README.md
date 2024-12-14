# Overview

mpr2csv saves timing data from LFS multiplayer replay to a csv file, one line per player per lap.

Contains a copy of [pyinsim9](https://github.com/KingOfIce77/pyinsim9) by KingOfIce and Alex McBride.
For documentation refer to [LFSManual](https://en.lfsmanual.net/wiki/InSim) and excellent documentation at [brunsware.de](https://www.brunsware.de/insim06b/index.html)

# Requirements

Python version <= 3.11, due to deprecated `asyncore` dependency in Python 3.12 and above.

# Running

1. Run LFS, type `/insim 29999`
2. Run mpr2csv.py
3. Load and start a multiplayer race replay
4. A new .csv file will be created in the current folder, laps will be appended as the replay gets played

# Note

Sector times are not exactly as they are in the game.
