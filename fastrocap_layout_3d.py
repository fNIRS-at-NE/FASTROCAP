# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% FASTROCAP layout(s) 3D

% TUM, NEL, 16/02/2021
% Fabian Schober
"""

# 3D plot for channel positions
import os.path as op

import mne
from mne.datasets import eegbci
from mne.datasets import fetch_fsaverage
from plot_positions import plot_alignment_eeg, plot_alignment_fnirs
# from mne.viz import set_3d_view

# Download fsaverage files
fs_dir = fetch_fsaverage(verbose=True)
data_path = mne.datasets.sample.data_path()
subjects_dir = data_path + '/subjects'

# The files live in:
subject = 'fsaverage'
trans = mne.read_trans(data_path + '/MEG/sample/sample_audvis_raw-trans.fif')
src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')

raw_fname, = eegbci.load_data(subject=1, runs=[6])
raw = mne.io.read_raw_edf(raw_fname, preload=True)

ch_eeg = ['Fp1', 'Fp2', 'F7', 'Fz', 'F8', 'FC1', 'FC2',
          'T7', 'C3', 'Cz', 'C4', 'T8', 'M1', 'CP5',
          'CP1', 'CPz', 'CP2', 'CP6', 'M2', 'P3', 'Pz',
          'P4', 'O1', 'O2']

ch_eeg_custom1 = ['Fp1', 'Fp2', 'F7', 'Fz', 'F8', 'FC1', 'FC2',
          'T7', 'C3', 'Cz', 'C4', 'T8', 'CP5', 'FC5', 'FC6',
          'CP1', 'CPz', 'CP2', 'CP6', 'P3', 'Pz',
          'P4', 'O1', 'O2']

ch_eeg_custom2 = ['Fp1', 'Fp2', 'F7', 'Fz', 'F8', 'FC1', 'FC2',
          'T7', 'C3', 'Cz', 'C4', 'T8', 'CP5', 'F3', 'F4',
          'CP1', 'CPz', 'CP2', 'CP6', 'P3', 'Pz',
          'P4', 'O1', 'O2']

ch_eeg_custom3 = ['AF3', 'AF4', 'F7', 'Fz', 'F8', 'FC1', 'FC2',
          'T7', 'C3', 'Cz', 'C4', 'T8', 'CP5', 'F3', 'F4',
          'CP1', 'CPz', 'CP2', 'CP6', 'P3', 'Pz',
          'P4', 'O1', 'O2']

ch_eeg_custom4 = ['AF3', 'AF4', 'F7', 'F1', 'F8', 'FC1', 'FC2',
          'T7', 'C3', 'Fpz', 'C4', 'T8', 'CP5', 'F3', 'F4',
          'CP1', 'F2', 'CP2', 'CP6', 'P3', 'FCz',
          'P4', 'O1', 'O2']

ch_fnirs24_left = ['FFC5', 'FFC3', 'FT7h', 'FC5h', 'FC3h',
                   'FCC5', 'FCC3', 'T7h', 'C5h', 'C3h',
                   'CCP5', 'CCP3']

ch_fnirs24_right = ['FFC4', 'FFC6', 'FC4h', 'FC6h', 'FT8h',
                   'FCC4', 'FCC6', 'C4h', 'C6h', 'T8h',
                   'CCP4', 'CCP6']

ch_fnirs24 = ch_fnirs24_left + ch_fnirs24_right

ch_fnirs54_left = ['FFC5', 'FFC3', 'FT7h', 'FC5h', 'FC3h',
                   'FTT7', 'FCC5', 'FCC3', 'T9h', 'T7h', 
                   'C5h', 'C3h', 'TTP7', 'CCP5', 'CCP3',
                   'TP9h','TP7h', 'CP5h', 'CP3h','TPP7',
                   'CPP5', 'CPP3', 'P7h', 'P3', 'P1',
                   'PPO5h', 'PPO1']

ch_fnirs54_right = ['FFC4', 'FFC6', 'FC4h', 'FC6h', 'FT8h',
                   'FCC4', 'FCC6', 'FTT8', 'C4h', 'C6h', 'T8h',
                   'T10h', 'CCP4', 'CCP6', 'TTP8', 'CP4h',
                   'CP6h', 'TP8h', 'TP10h', 'CPP4', 'CPP6',
                   'TPP8', 'P2', 'P4', 'P8h', 'PPO2', 'PPO6h']

ch_fnirs54 = ch_fnirs54_left + ch_fnirs54_right

ch_all_54 = ch_eeg + ch_fnirs54

info_eeg = mne.create_info(ch_names=ch_eeg ,sfreq=250, ch_types='eeg')
montage = mne.channels.make_standard_montage('standard_1005')
info_eeg.set_montage(montage)

info_fnirs24 = mne.create_info(ch_names=ch_fnirs24, sfreq=250, ch_types='eeg')
montage = mne.channels.make_standard_montage('standard_1005')
info_fnirs24.set_montage(montage)

info_fnirs54 = mne.create_info(ch_names=ch_fnirs54,sfreq=250, ch_types='eeg')
montage = mne.channels.make_standard_montage('standard_1005')
info_fnirs54.set_montage(montage)

subjects_dir = mne.datasets.sample.data_path() + '/subjects'

fig = plot_alignment_eeg(info_eeg, subject = 'sample', trans = trans,
                      eeg=['original', 'projected'], meg=False, subjects_dir=subjects_dir)
plot_alignment_fnirs(info_fnirs24, subject = 'sample', trans = trans,
                      eeg=['original', 'projected'], meg=False, subjects_dir=subjects_dir, fig=fig)