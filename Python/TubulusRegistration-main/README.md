# TubulusRegistration

The software is based on Python and uses SimpleITK and SimpleElastix for the registration. We recommend installing a dedicated python environment, e.g., using [Anaconda/Miniconda](https://www.anaconda.com/download) (scroll to bottom for Miniconda installer). Install the software and start a new Anaconda prompt. All subsequent steps should be executed from within the Anaconda/Miniconda prompt.

## Installation of the Python Environment

First create a new environment, e.g., called `tubulus-registration` (any name is fine, just make sure to remember it).

```
conda create -n tubulus-registration python=3.13
```

Activate the new environment via 

```
conda activate tubulus-registration
```

You should now see an indicator of the environment before the command prompt. Next step is to install the following requirements:

```
conda install numpy
conda install tifffile

conda install matplotlib
conda install pandas
conda install scikit-image
conda install scikit-learn

pip install simpleitk
pip install simpleitk-simpleelastix

pip install parfor
pip install "ray[default]"
```

If all dependencies could be installed properly, you're all set for continuing with the actual processing.

## Preparation of the CSV Input Files
The software requires a structured input file in CSV format saved as plain text (e.g., use Notepad on Windows, VS Code or any other simple text editor). Each line of the CSV file should contain an the absolute path to the video file in `.tif` format to be processed, followed by an integer value that reflects the reference point all frames will be registered to. The reference frame can be any valid frame between 0 and `num_frames-1`. However, to require as little transformations as possible, we recommend to use the frame that represents the half-way movement. For instance if a structure shrinks from 100% at the beginning to a size of 50% in the last frame, you'd pick the frame with a size of about 75%. For instance use Fiji, scroll through time and coarsely identify this half-way frame.

A final CSV file could look as follows:
```
/this/is/the/absolute/path/to/my/images/image1.tif;500
/this/is/the/absolute/path/to/my/images/image2.tif;200
/this/is/the/absolute/path/to/my/images/image3.tif;170
...
```

Each row will be processed separately and on the test machine (MacBook Pro, M4 Max) it took about 1-2h per video sequence.

## Starting the Processing
The main processing script is called `start_tubulus_registration.py` and requires the absolute path to the CSV input file list as input.

```
python start_tubulus_registration.py --input_table="/path/to/my/input_table.csv"
```

Note: On Windows systems, please make sure to use `/` as the folder separator rather than `\` to specify folder names (also for the CSV file!). For instance, a Windows folder could look like `C:/this/is/the/path/to/my/table.csv`.

## Result Description
The result of the abovementioned script are videos of the same size as the input videos where each frame was registered to the selected reference frame. The 3D file is called like the original video with the extension `_Registered.tif`. Moreover, two folders are created (`..._Registered/` and `..._Parameters/`), which contain intermediate result images (the same images that are also part of the final 3D image stack) and the registration text files that contain parameters for transforming the respective moving image to the reference. If you want to disable the intermediate result generation to save some storage space, just add the parameter `--no_intermediate_results` to the python command that starts the processing.

```
python start_tubulus_registration.py --input_table="/path/to/my/input_table.csv" --no_intermediate_results
```

## References
1. https://simpleitk.org/
2. https://simpleelastix.github.io/
3. https://pandas.pydata.org/
4. https://numpy.org/

