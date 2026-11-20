"""Lets the test suite run against an alternative implementation.

Set DECODER to a module path (e.g. variants.v01_index_loop) and that
module is imported in place of `decoder`.
"""

import importlib
import os
import sys

_target = os.environ.get("DECODER")
if _target and _target != "decoder":
    sys.modules["decoder"] = importlib.import_module(_target)
