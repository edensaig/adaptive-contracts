import numpy as np
import pandas as pd
import scipy.stats

import os
import functools
import itertools
from glob import glob

import matplotlib.pyplot as plt
import matplotlib
plt.rcParams.update({
    'text.usetex': True,
    'text.latex.preamble': r'''
    \usepackage{amsmath,amsfonts,amssymb,bm}
    \newcommand{\bq}{\mathbf{q}}
    \newcommand{\bp}{\mathbf{p}}
    ''',
})

import matplotlib_inline
matplotlib_inline.backend_inline.set_matplotlib_formats('retina')

background_line_style = {
    'color': 'lightgray',
    'linestyle': ':',
    'zorder': -100,
}

import contract_optimization