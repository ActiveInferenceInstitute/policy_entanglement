"""Project-local release gates (library layer).

Subpackage for tested, parameterised gate logic that the thin scripts under
``../../scripts/`` re-export. Currently holds the pipeline regression gate
(see :mod:`gates.regression_gate`). The package name avoids the
``manuscript/validation.py`` namespace already occupied by the manuscript
validators on the bare-import sys.path entries.
"""
