#!/bin/bash
cd more_overview_stats
zip 2.1.zip __init__.py
mv __init__.py more_overview_stats.py
zip 2.0.zip more_overview_stats.py
mv more_overview_stats.py __init__.py