#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Fish.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class comp_weight(gr.sync_block):
    """
    pov: ur a nerd and ur reading documentation
    """
    def __init__(self, vector_len = 1024, mag = [1,1,1,1], phase = [0,0,0,0]):
        gr.sync_block.__init__(self,
            name="comp_weight",
            in_sig=[(np.complex64, vector_len)] * len(mag),
            out_sig=[(np.complex64, vector_len)] + len(mag) * [(np.complex64, vector_len)]
                               
        )
        
        self.vector_len = vector_len
        self.mag = mag
        self.phase = phase
        self.in_num = len(self.mag)
        
        self.empty_input = [[] for _ in range(self.in_num)]


    def work(self, input_items, output_items):
        n_vectors = len(input_items[0])
        inputs = self.empty_input
        
        for x in range(self.in_num):
            stream_data = [input_items[x][i] for i in range(n_vectors)]
            concatenated_stream = np.concatenate(stream_data)
            inputs[x] = concatenated_stream

        inputs = np.array(inputs, dtype=np.complex64)
        inputs_contiguous = np.ascontiguousarray(inputs)
        
        mag, phase = self.parse_weights()
                        
        phase_factors = np.exp(1j * np.radians(phase))      
        weighted_signals = inputs_contiguous * mag[:, np.newaxis] * phase_factors[:, np.newaxis]
        final_combined = np.sum(weighted_signals, axis=0).astype(np.complex64)

        final_combined_vectors = final_combined.reshape((n_vectors, self.vector_len))
        output_items[0][:n_vectors] = final_combined_vectors
        
        weighted_signals_vectors = weighted_signals.reshape((self.in_num, n_vectors, self.vector_len))
        for i in range(self.in_num):
            output_items[i+1][:n_vectors] = weighted_signals_vectors[i]

        return n_vectors


    def parse_weights(self):
        mag = list(self.mag)
        phase = list(self.phase)
        
        if len(mag) > self.in_num:
            mag = mag[:self.in_num]

        elif len(mag) < self.in_num:
            mag += [0] * (self.in_num - len(mag))

        if len(phase) > self.in_num:
            phase = phase[:self.in_num]
            
        elif len(phase) < self.in_num:
            phase += [0] * (self.in_num - len(phase))

        return np.array(mag), np.array(phase)
    
    def set_mag(self, mag):
        self.mag = mag
        
    def set_phase(self, phase):
        self.phase = phase

