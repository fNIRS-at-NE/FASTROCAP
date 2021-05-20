# -*- coding: utf-8 -*-
"""
%% Project: FASTROCAP 
% Master Thesis

% Filter module for EEG stream
% Taken from: Mentalab explorepy

% TUM, NEL, 18/03/2021
% Fabian Schober
"""

import copy
import numpy as np
from scipy.signal import butter, lfilter, iirfilter, cheby2

class ExGFilter:
    """Filter class for ExG signals"""
    def __init__(self, cutoff_freq, filter_type, s_rate, n_chan, order=5):
        """
        Args:
            cutoff_freq (Union[float, tuple]): cutoff frequency (frequencies) for the filter
            filter_type (str): Fitler type ['lowpass', 'highpass', 'bandpass', 'notch']
            s_rate (Union[float, int]): sampling rate of the signal
            order (int): Filter order (default value: 5)
            n_chan (int): Number of channels
        """
        self.s_rate = np.float(s_rate)
        nyq_freq = self.s_rate / 2.
        self.filter_type = filter_type
        self.filter_param = None
        if filter_type == 'lowpass':
            hc_freq = cutoff_freq / nyq_freq
            b, a = butter(order, hc_freq, btype='lowpass')
            zi = np.zeros((n_chan, order))

        elif filter_type == 'highpass':
            lc_freq = cutoff_freq / nyq_freq
            b, a = butter(order, lc_freq, btype='highpass')
            zi = np.zeros((n_chan, order))

        elif filter_type == 'butter_bandpass':
            if cutoff_freq[0] >= cutoff_freq[1]:
                raise ValueError("High cutoff frequency must be larger than low cutoff frequency.")
            lc_freq = cutoff_freq[0] / nyq_freq
            hc_freq = cutoff_freq[1] / nyq_freq
            # if lc_freq <= 0.003:
                # raise ValueError('Transient band for low cutoff frequency is too narrow. Please try with larger values.')
            b, a = butter(order, [lc_freq, hc_freq], btype='band')
            zi = np.zeros((n_chan, order * 2))
            
        elif filter_type == 'cheby2_bandpass':
            if cutoff_freq[0] >= cutoff_freq[1]:
                raise ValueError("High cutoff frequency must be larger than low cutoff frequency.")
            lc_freq = cutoff_freq[0] / nyq_freq
            hc_freq = cutoff_freq[1] / nyq_freq
            # if lc_freq <= 0.003:
                # raise ValueError('Transient band for low cutoff frequency is too narrow. Please try with larger values.')
            b, a = cheby2(N=order, rs=25, Wn=[lc_freq, hc_freq], btype='bandpass')
            zi = np.zeros((n_chan, order * 2))

        elif filter_type == 'notch':
            lc_freq = (cutoff_freq - 2) / nyq_freq
            hc_freq = (cutoff_freq + 2) / nyq_freq
            b, a = iirfilter(5, [lc_freq, hc_freq], btype='bandstop', ftype='butter')
            zi = np.zeros((n_chan, 10))
        else:
            raise ValueError('Unknown filter type: {}'.format(filter_type))
        self.filter_param = {'a': a, 'b': b, 'zi': zi}

    def apply(self, input_data, in_place=True):
        """Apply filter
        Args:
            input_data (np.ndarray): raw data to be filtered
            in_place (bool): Whether apply filter in-place
        Returns:
            filtered data array
        """
        if not in_place:
            temp_data = copy.deepcopy(input_data)
        else:
            temp_data = input_data
        return self._apply_to_raw_data(raw_data=temp_data)

    def _apply_to_raw_data(self, raw_data):
        if len(raw_data.shape) < 2:
            raw_data = np.array(raw_data)[np.newaxis, :]
        filtered_data, self.filter_param['zi'] = lfilter(self.filter_param['b'],
                                                         self.filter_param['a'],
                                                         raw_data,
                                                         zi=self.filter_param['zi'])
        return filtered_data