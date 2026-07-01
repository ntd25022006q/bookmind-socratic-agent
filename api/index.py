import os
import sys

# Ensure root directory is in sys.path so server.py and other modules can be found
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app
