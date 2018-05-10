"""Settings for the graphs and plots in the PhD"""

import matplotlib as mpl
import matplotlib.pyplot as plt

class PhdPlots():
    def __init__(self):
        mpl.rcParams['font.size'] = 24.
        mpl.rcParams['font.family'] = 'Tahoma'
        mpl.rcParams['axes.labelsize'] = 24.
        mpl.rcParams['xtick.labelsize'] = 24.
        mpl.rcParams['xtick.major.size'] = 10.
        mpl.rcParams['xtick.major.width'] = 1.
        mpl.rcParams['xtick.minor.size'] = 5.
        mpl.rcParams['xtick.minor.width'] = 1.
        mpl.rcParams['ytick.labelsize'] = 24.
        mpl.rcParams['ytick.major.size'] = 10.
        mpl.rcParams['ytick.major.width'] = 1.
        mpl.rcParams['ytick.minor.size'] = 5.
        mpl.rcParams['ytick.minor.width'] = 1.
        mpl.rcParams['ytick.labelsize'] = 24.
        mpl.rcParams['figure.figsize'] = 15, 10
        params = {'mathtext.default': 'regular' }
        plt.rcParams.update(params)