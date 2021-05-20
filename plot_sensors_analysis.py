# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Plot sensors for analysis window

% TUM, NEL, 29/03/2021
% Fabian Schober
"""

# -*- coding: utf-8 -*-
"""Utility functions for plotting M/EEG data."""

# Authors: Alexandre Gramfort <alexandre.gramfort@inria.fr>
#          Denis Engemann <denis.engemann@gmail.com>
#          Martin Luessi <mluessi@nmr.mgh.harvard.edu>
#          Eric Larson <larson.eric.d@gmail.com>
#          Mainak Jas <mainak@neuro.hut.fi>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#          Clemens Brunner <clemens.brunner@gmail.com>
#          Daniel McCloy <dan@mccloy.info>
#
# License: Simplified BSD

# from collections import defaultdict
# from contextlib import contextmanager
# from functools import partial
# import difflib
# import webbrowser
# import tempfile
# import math
import numpy as np
# from copy import deepcopy
from distutils.version import LooseVersion
import warnings
# import threading

# from mne.defaults import _handle_default
# from mne.fixes import _get_status
# from mne.io import show_fiff, Info
from mne.io.constants import FIFF
from mne.io.pick import (channel_indices_by_type, _DATA_CH_TYPES_SPLIT, 
                         _contains_ch_type)
# from mne.io.meas_info import create_info
# from mne.rank import compute_rank
# from mne.io.proj import setup_proj
from mne.utils import warn, _check_ch_locs

# from mne.selection import (read_selection, _SELECTIONS, _EEG_SELECTIONS,
                         # _divide_to_regions)
from mne.transforms import apply_trans


_channel_type_prettyprint = {'eeg': "EEG channel", 'grad': "Gradiometer",
                             'mag': "Magnetometer", 'seeg': "sEEG channel",
                             'eog': "EOG channel", 'ecg': "ECG sensor",
                             'emg': "EMG sensor", 'ecog': "ECoG channel",
                             'misc': "miscellaneous sensor"}

def plot_sensors_eeg(info, kind='topomap', ch_type=None, title=None,
                 show_names=False, ch_groups=None, to_sphere=True, axes=None,
                 block=False, show=True, sphere=None, verbose=None):

    ch_indices = channel_indices_by_type(info)
    allowed_types = _DATA_CH_TYPES_SPLIT

    if ch_type is None:
        for this_type in allowed_types:
            if _contains_ch_type(info, this_type):
                ch_type = this_type
                break
    picks = ch_indices[ch_type]
    chs = [info['chs'][pick] for pick in picks]
    if not _check_ch_locs(chs):
        raise RuntimeError('No valid channel positions found')
    dev_head_t = info['dev_head_t']
    pos = np.empty((len(chs), 3))
    for ci, ch in enumerate(chs):
        pos[ci] = ch['loc'][:3]
        if ch['coord_frame'] == FIFF.FIFFV_COORD_DEVICE:
            if dev_head_t is None:
                warn('dev_head_t is None, transforming MEG sensors to head '
                     'coordinate frame using identity transform')
                dev_head_t = np.eye(4)
            pos[ci] = apply_trans(dev_head_t, pos[ci])
    del dev_head_t
    ch_names = np.array([ch['ch_name'] for ch in chs])
    # bads = [idx for idx, name in enumerate(ch_names) if name in info['bads']]
    
    # from matplotlib import rcParams
    # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D
    from mne.viz.topomap import _get_pos_outlines, _draw_outlines
    
    pos, outlines = _get_pos_outlines(info, picks, sphere,
                                          to_sphere=to_sphere)     
    # print(type(pos))
    
    _draw_outlines(axes, outlines)
    
    if show_names:
            if isinstance(show_names, (list, np.ndarray)):  # only given channels
                indices = [list(ch_names).index(name) for name in show_names]
            else:  # all channels
                indices = range(len(pos))
    for idx in indices:
            this_pos = pos[idx]
            axes.text(this_pos[0], this_pos[1], ch_names[idx],
                      ha='center', va='center', fontweight='bold')
    
    colors = [(1.,1.,1.)]*24

    fig = axes.get_figure()
    
    dots = axes.scatter(pos[:, 0], pos[:, 1], picker=True, clip_on=False,
                 c=colors, edgecolors='k', marker='o', s=600, lw=2)
   
    # default channel colored
    dots._facecolors[17] = (0,1,0,1)
    
    def on_pick(event):
        
        if event.ind[0] <= 24:
            dots._facecolors[:24] = (1,1,1,1)
            dots._facecolors[event.ind[0]] = (0,1,0,1)
            fig.canvas.draw()
    
    fig.canvas.draw()

    axes.axis("off")  # remove border around figure
    axes.set(aspect='equal')
    
    fig.canvas.mpl_connect('pick_event', on_pick)


def _close_event(event, fig):
    """Listen for sensor plotter close event."""
    if getattr(fig, 'lasso', None) is not None:
        fig.lasso.disconnect()

def _onpick_sensor(event, fig, ax, pos, ch_names, show_names):
    """Pick a channel in plot_sensors."""
    if event.mouseevent.key == 'control' and fig.lasso is not None:
        for ind in event.ind:
            fig.lasso.select_one(ind)

        return
    if show_names:
        return  # channel names already visible
    ind = event.ind[0]  # Just take the first sensor.
    ch_name = ch_names[ind]

    this_pos = pos[ind]
    ax.texts.pop(0)
    if len(this_pos) == 3:
        ax.text(this_pos[0], this_pos[1], this_pos[2], ch_name)
    else:
        ax.text(this_pos[0], this_pos[1], ch_name)
    fig.canvas.draw()

def plot_sensors_fnirs(info, kind='topomap', ch_type=None, title=None,
                 show_names=False, ch_groups=None, to_sphere=True, axes=None,
                 block=False, show=True, sphere=None, verbose=None):

    ch_indices = channel_indices_by_type(info)
    allowed_types = _DATA_CH_TYPES_SPLIT

    if ch_type is None:
        for this_type in allowed_types:
            if _contains_ch_type(info, this_type):
                ch_type = this_type
                break
    picks = ch_indices[ch_type]
    chs = [info['chs'][pick] for pick in picks]
    if not _check_ch_locs(chs):
        raise RuntimeError('No valid channel positions found')
    dev_head_t = info['dev_head_t']
    pos = np.empty((len(chs), 3))
    for ci, ch in enumerate(chs):
        pos[ci] = ch['loc'][:3]
        if ch['coord_frame'] == FIFF.FIFFV_COORD_DEVICE:
            if dev_head_t is None:
                warn('dev_head_t is None, transforming MEG sensors to head '
                     'coordinate frame using identity transform')
                dev_head_t = np.eye(4)
            pos[ci] = apply_trans(dev_head_t, pos[ci])
    del dev_head_t
    
    from mne.viz.topomap import _get_pos_outlines, _draw_outlines
    
    pos, outlines = _get_pos_outlines(info, picks, sphere,
                                          to_sphere=to_sphere)
    
    _draw_outlines(axes, outlines)
    
    axes.scatter(pos[:24, 0], pos[:24, 1], picker=False, clip_on=False,
                  color=None, edgecolors='k', marker='o', s=300, lw=3)
    
    axes.scatter(pos[24:42, 0], pos[24:42, 1], picker=False, clip_on=False,
                  color='k', edgecolors='k', marker='o', s=600, lw=3)
    
    rxtx = ['Tx2', 'Rx3', 'Tx5', 'Rx1', 'Tx3', 'Rx4', 'Tx1', 'Rx2', 'Tx4',
           'Tx7', 'Rx7', 'Tx10', 'Rx5', 'Tx8', 'Rx8', 'Tx6', 'Rx6', 'Tx9']
    
    names = range(24,42)
    for idx in names:
            this_pos = pos[idx]
            axes.text(this_pos[0], this_pos[1], rxtx[idx-24],
                      ha='center', va='center', fontweight='bold', color='w')
    
    # plot the lines between receivers and transmitters
    axes.plot(pos[(24,25,26), 0], pos[(24,25,26), 1], c='k')
    axes.plot(pos[(27,28,29), 0], pos[(27,28,29), 1], c='k')
    axes.plot(pos[(30,31,32), 0], pos[(30,31,32), 1], c='k')
    axes.plot(pos[(33,34,35), 0], pos[(33,34,35), 1], c='k')
    axes.plot(pos[(36,37,38), 0], pos[(36,37,38), 1], c='k')
    axes.plot(pos[(39,40,41), 0], pos[(39,40,41), 1], c='k')
    axes.plot(pos[(24,27,30), 0], pos[(24,27,30), 1], c='k')
    axes.plot(pos[(25,28,31), 0], pos[(25,28,31), 1], c='k')
    axes.plot(pos[(26,29,32), 0], pos[(26,29,32), 1], c='k')
    axes.plot(pos[(33,36,39), 0], pos[(33,36,39), 1], c='k')
    axes.plot(pos[(34,37,40), 0], pos[(34,37,40), 1], c='k')
    axes.plot(pos[(35,38,41), 0], pos[(35,38,41), 1], c='k')
    
    colors = [(1.,1.,1.)]*24

    fig = axes.get_figure()
    fig.suptitle(title, size='x-large')
    
    dots = axes.scatter(pos[:24, 0], pos[:24, 1], picker=True, clip_on=False,
                            c=colors, marker='o', s=300, zorder=2.5)
    
    # default channels colored
    dots._facecolors[1] = (1,0,0,1)
    dots._facecolors[12] = (0,0,1,1)
    
    def on_pick(event):
        
        if event.ind[0] <= 11:
            dots._facecolors[:12] = (1,1,1,1)
            dots._facecolors[event.ind[0]] = (1,0,0,1)
            fig.canvas.draw()
            
        elif event.ind[0] > 11:
            dots._facecolors[12:24] = (1,1,1,1)
            dots._facecolors[event.ind[0]] = (0,0,1,1)
            fig.canvas.draw()
    
    fig.canvas.draw()

    axes.axis("off")  # remove border around figure
    axes.set(aspect='equal')
    
    fig.canvas.mpl_connect('pick_event', on_pick)
               

def plt_show(show=True, fig=None, **kwargs):
    
    from matplotlib import get_backend
    import matplotlib.pyplot as plt
    if show and get_backend() != 'agg':
      (fig or plt).show(**kwargs)
        
      
warnings.filterwarnings("ignore")
        
class SelectFromCollection(object):

    def __init__(self, ax, collection, ch_names, alpha_other=0.5,
                 linewidth_other=0.5, alpha_selected=1, linewidth_selected=1):
        from matplotlib import __version__
        if LooseVersion(__version__) < LooseVersion('1.2.1'):
            raise ImportError('Interactive selection not possible for '
                              'matplotlib versions < 1.2.1. Upgrade '
                              'matplotlib.')
        from matplotlib.widgets import LassoSelector
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.ch_names = ch_names
        self.alpha_other = alpha_other
        self.linewidth_other = linewidth_other
        self.alpha_selected = alpha_selected
        self.linewidth_selected = linewidth_selected

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        self.ec = collection.get_edgecolors()
        self.lw = collection.get_linewidths()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, self.Npts).reshape(self.Npts, -1)
            self.ec = np.tile(self.ec, self.Npts).reshape(self.Npts, -1)
        self.fc[:, -1] = self.alpha_other  # deselect in the beginning
        self.ec[:, -1] = self.alpha_other
        self.lw = np.full(self.Npts, self.linewidth_other)

        self.lasso = LassoSelector(ax, onselect=self.on_select,
                                   lineprops=dict(color='red', linewidth=0.5))
        self.selection = list()

    def on_select(self, verts):
        """Select a subset from the collection."""
        from matplotlib.path import Path
        if len(verts) <= 3:  # Seems to be a good way to exclude single clicks.
            return

        path = Path(verts)
        inds = np.nonzero([path.contains_point(xy) for xy in self.xys])[0]
        if self.canvas._key == 'control':  # Appending selection.
            sels = [np.where(self.ch_names == c)[0][0] for c in self.selection]
            inters = set(inds) - set(sels)
            inds = list(inters.union(set(sels) - set(inds)))

        self.selection[:] = np.array(self.ch_names)[inds].tolist()
        self.style_sensors(inds)
        self.canvas.callbacks.process('lasso_event')

    def select_one(self, ind):
        """Select or deselect one sensor."""
        ch_name = self.ch_names[ind]
        if ch_name in self.selection:
            sel_ind = self.selection.index(ch_name)
            self.selection.pop(sel_ind)
        else:
            self.selection.append(ch_name)
        inds = np.in1d(self.ch_names, self.selection).nonzero()[0]
        self.style_sensors(inds)
        self.canvas.callbacks.process('lasso_event')

    def select_many(self, inds):
        """Select many sensors using indices (for predefined selections)."""
        self.selection[:] = np.array(self.ch_names)[inds].tolist()
        self.style_sensors(inds)

    def style_sensors(self, inds):
        """Style selected sensors as "active"."""
        # reset
        self.fc[:, -1] = self.alpha_other
        self.ec[:, -1] = self.alpha_other / 2
        self.lw[:] = self.linewidth_other
        # style sensors at `inds`
        self.fc[inds, -1] = self.alpha_selected
        self.ec[inds, -1] = self.alpha_selected
        self.lw[inds] = self.linewidth_selected
        self.collection.set_facecolors(self.fc)
        self.collection.set_edgecolors(self.ec)
        self.collection.set_linewidths(self.lw)
        self.canvas.draw_idle()

    def disconnect(self):
        """Disconnect the lasso selector."""
        self.lasso.disconnect_events()
        self.fc[:, -1] = self.alpha_selected
        self.ec[:, -1] = self.alpha_selected
        self.collection.set_facecolors(self.fc)
        self.collection.set_edgecolors(self.ec)
        self.canvas.draw_idle()