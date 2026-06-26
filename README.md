This repostory is the codebase for the publication "Cell type specific Ca2 signals govern mouse seminiferous tubule physiology" by Justine A. Fischoeder, David Fleck, Jerome Schröer, Christopher Wiesbrock, Lina
Kenzler, Christoph Weber-Hamacher, Ilian Schröder, Melissa Franke, Stefanie Kurth, Martin Strauch, Guiscard Seebohm4, Johannes Stegmaier, Naofumi Uesaka6, Jennifer Spehr, Marc Spehr

## Fiji/ImageJ Macro

This Fiji/ImageJ macro was developed to generate transient-enhanced GCaMP image stacks, create maximum-intensity projections, and identify non-rigid motion artifacts during two-photon calcium imaging.

### Purpose

The macro performs optic-flow-based motion detection to identify image regions or frames containing local tissue movement (e.g., contractions of individual tubules during acquisition). These regions are subsequently excluded from calcium signal quantification and from the generation of maximum-intensity projections, thereby reducing motion-induced artifacts.

### Prerequisites

Before running the macro:

* A **2-channel ImageJ stack** must be open with the expected window title:

  * `2PStack_GCaMP.tif`
* The channels must be organized as follows:

  * **Channel 1 (C1):** Red structural/reference channel (deep-interpolated two-photon signal).
  * **Channel 2 (C2):** GCaMP6f fluorescence channel.
* The **Stowers** and **BIG-EPFL** Fiji update sites must be enabled, as they provide the required `StackRegJ_` plugin used for image registration.

### Processing Pipeline

The macro performs the following steps:

1. Registers the two-channel image stack using the structural reference channel.
2. Computes optic-flow-based motion maps from the GCaMP channel to detect localized non-rigid movement.
3. Generates binary motion masks representing detected motion regions.
4. Produces a transient-enhanced GCaMP activity stack.
5. Excludes detected motion regions from downstream maximum-intensity projections and signal quantification.
6. Creates visualization overlays for quality control.

### Outputs

The following images are generated:

| Output                               | Description                                                                                        |
| ------------------------------------ | -------------------------------------------------------------------------------------------------- |
| `Movement_Detection`                 | Binary motion mask (`0/255`) generated from optic-flow analysis of the GCaMP channel.              |
| `GCaMP_transient_enhanced`           | Transient-enhanced calcium activity stack.                                                         |
| `GCaMP_transient_MAX`                | Maximum-intensity projection generated after excluding detected motion regions.                    |
| `GCaMP_transient_with_MotionOverlay` | Composite visualization displaying the motion mask (red) over the GCaMP signal (grayscale).        |
| `2PStack_GCaMP_registeredMerged`     | Registered two-channel image stack containing the aligned structural (C1) and GCaMP (C2) channels. |


# MATLAB Utilities

This directory contains several MATLAB scripts used for image analysis preprocessing, nearest-neighbor analysis, and mask conversion workflows.

## `nearest_neighbours_and_volumina2`

This script processes object coordinates exported from **Imaris** and computes nearest-neighbor statistics.

### Requirements

* The script must be located in the same directory as the Imaris-generated `.xls` result files.
* Each Excel file must contain a worksheet named **`Center of Homogeneous Mass`**, which stores the object centroid coordinates (`x`, `y`, `z`).
* Object volumes are also extracted from the input files, although they are not used in the associated publication analyses.

### Functionality

For every object (e.g., nucleus), the script computes the average Euclidean distance to its:

* 3 nearest neighbors
* 5 nearest neighbors
* 7 nearest neighbors
* 9 nearest neighbors

Nearest-neighbor searches are performed using MATLAB's `knnsearch` function.

In addition, dataset-level summary statistics are calculated for each neighborhood size.

### Output

Three tables are generated and exported:

1. **Per-object nearest-neighbor distances** for every nucleus.
2. **Mean nearest-neighbor distances** for each dataset.
3. **Median nearest-neighbor distances** for each dataset.

---

## `export_as_tiff`

This script exports segmentation masks created in the MATLAB **Image Segmenter** app as TIFF images.

### Intended use

The script was originally developed to generate training data for **Cellpose** from manually created binary masks.

### Workflow

1. Open the source `.tiff` image in the MATLAB **Image Segmenter** app.
2. Create segmentation masks manually.
3. Export the segmentation results to the MATLAB workspace.
4. The exported variables are expected to have the default names:

   * `maskedImage`
   * `BW`
5. Run the script to save the exported masks as `.tif` files in the current working directory.

---

## `converter`

This script converts binary MATLAB masks into instance-labeled masks compatible with **Cellpose**.

### Background

Masks generated in MATLAB typically use:

* `0` → background
* `1` → foreground

In contrast, Cellpose expects:

* `0` → background
* A unique positive integer label for every individual object (cell)

The script therefore relabels connected components into separate object instances.

### Implementation details

* The output directory is specified by the `folder` variable near the beginning of the script.
* The input directory is currently hard-coded (around line 8) and should be adjusted manually as needed.
* The `for` loop range is also hard-coded to match the number of mask files and may require modification for other datasets.
* Connected components are labeled using MATLAB's `bwlabel` function.
* Before saving, the script automatically determines whether 8-bit storage is sufficient or whether 16-bit output is required to represent all object labels.
* Converted masks are saved as new TIFF files with an appended **`s`** at the end of the original filename, allowing them to be distinguished from the source masks.

## `Kinetics_Analysis_Script`

This Python script performs semi-automated kinetic analysis of calcium imaging time series. It detects transient events, extracts temporal and amplitude-based parameters, and exports the results to Excel spreadsheets. The workflow combines automated signal processing with user-guided quality control for ROI and peak selection.

### Purpose

The script was developed to quantify calcium transient kinetics from fluorescence traces by:

* Correcting baseline drift.
* Detecting calcium events using a statistically defined threshold.
* Allowing manual review and curation of detected events.
* Calculating a comprehensive set of event-specific and dataset-level kinetic parameters.
* Exporting all measurements and curation logs for downstream analysis.

### Input

* A directory containing one or more `.csv` files with fluorescence traces.
* Each column is interpreted as an individual ROI.
* If the first column contains a uniformly sampled time axis, the script automatically estimates the acquisition frame rate. Alternatively, the user may specify a custom frame rate.

### Processing Pipeline

For each dataset and ROI, the script performs the following steps:

1. **Interactive ROI curation**

   * Each fluorescence trace is displayed, allowing the user to accept or discard individual ROIs before analysis.

2. **Baseline correction**

   * Baseline drift is removed using an iterative modified polynomial (`imodpoly`) fitting approach.

3. **Baseline estimation**

   * The user specifies a baseline intensity range from which the mean and standard deviation are calculated.

4. **Peak detection**

   * Candidate events are identified using a threshold of:

   ```
   mean + 3 × standard deviation
   ```

   Peaks are detected as local maxima within contiguous regions exceeding this threshold.

5. **Interactive peak curation**

   * Detected events can be manually removed using user-defined rectangular selection regions.

6. **Peak boundary detection**

   * Event onset and offset are determined from threshold crossings relative to the baseline mean. If no crossing exists between neighboring events, approximate boundaries are estimated from local minima.

7. **Kinetic parameter calculation**

   * A comprehensive set of transient characteristics is calculated for every detected event.

### Calculated Parameters

For each detected calcium transient, the script computes:

* Peak time
* Peak amplitude
* Event onset and offset times
* Signal amplitude
* Full Width at Half Maximum (FWHM)
* Full event duration
* Area Under the Curve (AUC)
* Rise time
* Decay time
* 20–80% rise time
* 20–80% decay time
* Approximate decay constant (τ) based on the 63.2% decay point
* Exponential decay constant (τ) obtained by curve fitting

Additionally, event train statistics are calculated for each ROI:

* Inter-spike intervals (ISI)
* Mean, median, and standard deviation of ISI
* Mean and median event frequency
* Frequency variability
* Periodicity index (defined as SD(ISI) / mean(ISI))

### Outputs

For each processed dataset, the script generates:

| Output                      | Description                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| `<dataset>_results.xlsx`    | Comprehensive table containing all calculated kinetic parameters for every detected event and ROI. |
| `peak_log_<dataset>.xlsx`   | Log file documenting peaks that were manually removed during curation.                             |
| `column_log_<dataset>.xlsx` | Log file documenting ROIs that were excluded from analysis.                                        |

### Notes

* The workflow is intentionally **semi-automated** and includes several user interaction steps for quality control.
* Automatic baseline correction is performed using the `pybaselines` implementation of the iterative modified polynomial (`imodpoly`) algorithm.
* Exponential decay constants are estimated by fitting the decay phase with a single-exponential model using `scipy.optimize.curve_fit`.
* Results are exported as Excel workbooks (`.xlsx`) for downstream statistical analysis.

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

## `amh_border.py`

This Python script performs automated event detection and kinetic analysis of calcium traces acquired during the AMH experiments. It extracts transient characteristics from individual ROIs and summarizes population-level event statistics.

### Purpose

The script was developed to quantify spontaneous calcium activity by detecting fluorescence transients and calculating event kinetics, including amplitude, duration, rise time, and event frequency.

### Input

* An Excel file containing ROI fluorescence traces.
* An accompanying metadata table containing ROI identifiers and optional pattern classifications.
* One fluorescence trace per ROI.

### Processing Pipeline

For each ROI, the script performs the following operations:

1. **Signal preprocessing**

   * Missing values are replaced by the trace mean.
   * Traces are converted to z-scores.
   * Signals are temporally interpolated to a higher sampling frequency.
   * Gaussian smoothing and baseline correction are applied.

2. **Peak detection**

   * Calcium transients are detected using `scipy.signal.find_peaks` based on a user-defined prominence threshold.

3. **Event characterization**

   * For every detected transient, the script computes:

     * Peak amplitude
     * Full Width at Half Maximum (FWHM)
     * Rise time
     * 20–80% rise time
     * Exponential decay constant (τ, where applicable)

4. **Population statistics**

   * Event rates (events per minute) are estimated.
   * Inter-event interval variability is calculated.
   * Summary distributions of kinetic parameters are generated across all analyzed ROIs.

### Outputs

The script exports:

| Output                    | Description                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| `Detected_Peaks.xlsx`     | Detected peak positions for every ROI.                                                          |
| `Peak_Metrics.xlsx`       | Per-event measurements including amplitude, FWHM, rise time, and additional kinetic parameters. |
| `FWHM_Histogram.png`      | Distribution of event full widths at half maximum.                                              |
| `Rise_Time_Histogram.png` | Distribution of 20–80% rise times.                                                              |
| `Tau_Histogram.png`       | Distribution of fitted decay constants (τ).                                                     |

### Notes

* Signals are standardized (z-score normalized) before analysis.
* Temporal interpolation is performed to improve temporal resolution for kinetic measurements.
* Peak detection relies on prominence-based thresholding rather than simple intensity thresholds.

## `amh_cross_corr_final`

This Jupyter notebook performs pairwise correlation analysis of calcium activity recorded during the AMH experiments in order to quantify functional relationships between ROIs.

### Purpose

The notebook computes pairwise correlations between calcium activity traces and compares correlations between spatially related and unrelated ROI pairs. In addition, spatial information extracted from ROI annotations is incorporated to relate functional connectivity to anatomical organization.

### Input

* ROI fluorescence traces stored as CSV files.
* ROI annotation files (`.zip`) exported from ImageJ/Fiji ROI Manager.
* Datasets organized within a common directory structure.

### Processing Pipeline

For each dataset, the notebook:

1. Loads fluorescence traces and ROI annotations.
2. Extracts ROI identities and geometric properties.
3. Performs signal preprocessing and normalization.
4. Computes pairwise correlation coefficients between ROI activity traces.
5. Associates correlation values with ROI metadata, including:

   * ROI identity
   * ROI area
   * Pairwise spatial distance
6. Separates correlation values into biologically relevant comparison groups (e.g., intra-group versus inter-group ROI pairs).
7. Aggregates results across all processed datasets.

### Outputs

The notebook generates several summary tables and visualizations, including:

| Output                    | Description                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| `corr.xlsx`               | Pairwise correlation coefficients for analyzed ROI pairs.                                         |
| `all_list.xlsx`           | Combined dataset containing ROI metadata, distances, areas, and corresponding correlation values. |
| `file_list.xlsx`          | List of processed input files.                                                                    |
| Histogram plots           | Distribution of correlation coefficients for different ROI pair categories.                       |
| Additional summary tables | Intermediate or control analyses generated during processing.                                     |

### Notes

* ROI annotations are imported directly from ImageJ/Fiji ROI archives.
* Correlation analyses are performed after preprocessing and normalization of fluorescence traces.
* The notebook is intended for exploratory analysis and comparison of spatial and functional relationships between ROIs in the AMH datasets.

## `smmhc_analysis.py`

This Python script performs automated event detection and activity quantification for calcium imaging data acquired in the SMMHC experiments. It preprocesses fluorescence traces, detects calcium transients, and estimates event frequencies and inter-spike intervals for individual ROIs.

### Purpose

The script was developed to quantify spontaneous calcium activity across multiple ROIs while accounting for interruptions in signal acquisition and baseline drift.

### Input

* Paired CSV files containing:

  * Green fluorescence traces (signal channel)
  * Red fluorescence traces (reference/background channel)
* One column per ROI.

### Processing Pipeline

For each ROI, the script:

1. Performs baseline correction using median-based baseline estimation.
2. Detects invalid or interrupted recording segments (`NaN` regions) and excludes neighboring frames from analysis.
3. Removes short valid recording intervals below a predefined duration threshold.
4. Standardizes the corrected trace using z-score normalization.
5. Rescales the signal to the range `[0,1]`.
6. Detects calcium events using prominence- and threshold-based peak detection (`scipy.signal.find_peaks`).
7. Computes binary event vectors and peak indices.
8. Estimates:

   * Event frequency within continuous recording segments.
   * Inter-spike intervals (ISI).
   * Linear cumulative event trends for quality assessment.

### Outputs

| Output          | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `*_binary.xlsx` | Binary event matrix indicating detected calcium transients for each ROI. |
| `*_peaks.xlsx`  | Peak indices for every analyzed ROI.                                     |
| `output.xlsx`   | Summary table containing calculated event frequencies across datasets.   |

### Notes

* The analysis explicitly accounts for recording interruptions by masking `NaN` regions and excluding neighboring frames.
* Event detection is performed after normalization and baseline correction to improve robustness across ROIs.
* Frequency estimates are calculated separately for continuous recording segments.

## `smmhc_inter.py`

This Python script performs pairwise cross-correlation analysis between ROIs in the SMMHC datasets to compare functional relationships within and between tubules.

### Purpose

The script evaluates temporal synchronization of calcium activity by computing lag-dependent cross-correlations between ROI pairs and separating them into biologically defined comparison groups.

### Input

* Consolidated Excel files containing ROI fluorescence traces.
* Corresponding background traces.
* Metadata assigning ROIs to experimental datasets and tubule identities.

### Processing Pipeline

For each experiment, the script:

1. Loads fluorescence traces and associated background signals.
2. Aligns overlapping recording periods between ROI pairs.
3. Removes baseline drift using median-based baseline estimation.
4. Computes cross-correlation values over multiple temporal lags.
5. Determines the maximum correlation coefficient and corresponding lag for every ROI pair.
6. Uses ROI metadata to classify ROI pairs as:

   * **Intra-tubular** (within the same tubule)
   * **Inter-tubular** (between different tubules)
7. Aggregates correlation values across all experiments for downstream comparison.

### Outputs

The script generates distributions and summary plots of cross-correlation coefficients for different ROI pair categories, enabling comparison of functional coupling within and between tubules.

### Notes

* Cross-correlations are calculated over a limited lag window to account for temporal offsets between calcium events.
* Baseline correction is applied before correlation analysis to reduce low-frequency drift.
* Metadata-derived masks are used to classify ROI pairs into biologically relevant groups.

## `smmhc_overall_correlation.py`

This Python script computes pairwise cross-correlations across all ROIs in the SMMHC datasets and visualizes functional connectivity as correlation and lag heatmaps.

### Purpose

The script provides a global overview of synchronization patterns between calcium activity traces across experiments by generating correlation matrices and corresponding temporal lag maps.

### Input

* A consolidated Excel file containing ROI fluorescence traces and experiment metadata.
* Metadata specifying recording boundaries for individual experiments.

### Processing Pipeline

For every ROI pair, the script:

1. Extracts overlapping recording intervals.
2. Removes baseline drift using median-based baseline estimation.
3. Computes lag-dependent cross-correlations over a predefined lag range.
4. Identifies the maximum correlation coefficient and its associated temporal lag.
5. Stores the resulting values in pairwise correlation and lag matrices.

### Outputs

The script generates:

| Output                      | Description                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------- |
| Correlation heatmaps        | Matrix visualization of maximum pairwise cross-correlation coefficients between ROIs. |
| Lag heatmaps                | Matrix visualization of temporal offsets corresponding to maximal correlations.       |
| Experiment-specific figures | Separate heatmaps for individual recording sessions and selected ROI subsets.         |

### Notes

* Correlations are calculated after baseline correction and exclusion of non-overlapping recording intervals.
* Heatmaps provide an overview of functional connectivity and temporal coordination between ROIs across the complete dataset.
* Maximum correlation values are determined within a restricted lag window rather than at zero lag only.


