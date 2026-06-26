#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:46:20 2020

@author: stegmaier
"""

import os
import glob
import time

from argparse import ArgumentParser
import pathlib
from pathlib import Path

from utils.utils import read_image, save_image, normalize, read_json, adjust_meta_information
import subprocess
import compute_registration_parameters as reg
import numpy as np
import pandas as pd
import json
import sys
import csv


def main(hparams):

    # Calculate the start time
    start_time = time.time()
    

    #input_table = pd.read_excel(hparams.input_table, sheet_name='Sheet1')

    with open(hparams.input_table, newline='') as csvfile:
        input_files = csv.reader(csvfile, delimiter=';')
        for current_row in input_files:
            print("Processing file %s with reference frame set to %i ..." % (current_row[0], int(current_row[1])))

            input_file = current_row[0].replace('\\', '/')
            mean_frame = int(current_row[1])

    # perform focus stacking
            input_image, metadata = read_image(input_file)

            output_name = input_file.replace('.tif', '_Registered.tif')
            output_folder_frames = input_file.replace('.tif', '_Registered')
            output_folder_transformations = input_file.replace('.tif', '_Parameters')

            reg.perform_registration_parallel(input_image, output_name, output_folder_frames, output_folder_transformations, method='bspline', perform_normalization=False, use_mask=False, reference_frame=mean_frame, intermediate_results=hparams.intermediate_results, num_threads=hparams.num_threads)

    # Calculate the end time and time taken
    end_time = time.time()
    length = end_time - start_time

    # Show the results : this can be altered however you like
    print("It took", length, "seconds!")


if __name__ == '__main__':
    # ------------------------
    # TRAINING ARGUMENTS
    # ------------------------
    # these are project-wide arguments

    parent_parser = ArgumentParser(add_help=False)
    
    parent_parser.add_argument(
        '--input_table',
        type=str,
        default=r'/Users/jstegmaier/Programming/Projects/TubulusRegistration/Data/TubulusRegistrationList.csv',
        help='Path to the input table. Expects a csv file with the first column being the absolute file path and the second parameter being the frame with the movement in the middle'
    )

    parent_parser.add_argument(
        '--num_threads',
        type=int,
        default=-1,
        help='Number of threads to be used by SITK. Set to -1 to leave unchanged and use default value.'
    )

    parent_parser.add_argument(
        "--no_intermediate_results",
        dest="intermediate_results",
        action="store_false",
        help="disable intermediate results"
    )

    hyperparams = parent_parser.parse_args()

    # ---------------------
    # RUN TRAINING
    # ---------------------
    main(hyperparams)
