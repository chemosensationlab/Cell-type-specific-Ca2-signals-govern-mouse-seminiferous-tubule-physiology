# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 13:58:49 2024

@author: wiesbrock
"""

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import scipy.stats as stats
from scipy.signal import find_peaks
from pybaselines import Baseline
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

# Laden der DataFrames
path = r'C:\Users\wiesbrock\Desktop\Projekte\AMH\ROIs_Traces_for_Christopher\merged_output.xlsx'
df_trace = pd.read_excel(path, skiprows=1)
names_ = pd.read_excel(r"C:\Users\wiesbrock\Desktop\Projekte\AMH\Activity pattern AMH Ctrl.xlsx")
pattern_class = names_['Pattern class']
names_ = names_['ROI']
#names_ = names_[pattern_class == 1]

threshold = [4]
results = []
all_detected_peaks = {name: [] for name in names_}
peak_metrics = []
peaks_diff_list=[]
peak_diff_mean=[]
def calculate_fwhm(x, y, left_border, right_border):
    # Slice the x and y arrays within the borders
    x_slice = x[left_border:right_border+1]
    y_slice = y[left_border:right_border+1]

    # Find the maximum value and its index within the slice
    max_val = np.max(y_slice)
    max_idx = np.argmax(y_slice)
    
    # Calculate half maximum
    half_max = max_val / 2.0
    
    # Find the left index where y_slice crosses half maximum
    left_idx = np.where(y_slice[:max_idx] < half_max)[0]
    if len(left_idx) > 0:
        left_idx = left_idx[-1]
    else:
        left_idx = 0
    
    # Find the right index where y_slice crosses half maximum
    right_idx = np.where(y_slice[max_idx:] < half_max)[0]
    if len(right_idx) > 0:
        right_idx = right_idx[0] + max_idx
    else:
        right_idx = len(y_slice) - 1
    
    # Calculate FWHM
    fwhm = x_slice[right_idx] - x_slice[left_idx]
    return fwhm

def calculate_rise_time(x, y, left_idx, peak_idx):
    baseline = np.mean(y[left_idx:peak_idx])
    rise_time_idx = np.where(y[left_idx:peak_idx] >= (baseline + (y[peak_idx] - baseline) / 2))[0]
    if rise_time_idx.size > 0:
        rise_time_idx = rise_time_idx[-1] + left_idx
    else:
        rise_time_idx = left_idx
    rise_time = x[peak_idx] - x[rise_time_idx]
    return rise_time, rise_time_idx

def calculate_20_80_rise_time(x, y, left_border, right_border):
    # Slice the x and y arrays within the borders
    x_slice = x[left_border:right_border+1]
    y_slice = y[left_border:right_border+1]
    
    # Find the baseline in the region (mean of the sliced y array)
    baseline = np.mean(y_slice)
    
    # Calculate the 20% and 80% levels from the baseline to the peak
    peak_val = np.max(y_slice)
    twenty_percent_level = baseline + 0.2 * (peak_val - baseline)
    eighty_percent_level = baseline + 0.8 * (peak_val - baseline)
    
    # Find the index where y_slice crosses the 20% level
    twenty_percent_idx = np.where(y_slice >= twenty_percent_level)[0]
    if len(twenty_percent_idx) > 0:
        twenty_percent_idx = twenty_percent_idx[0]
    else:
        twenty_percent_idx = 0  # In case no index is found, set it to the start
    
    # Find the index where y_slice crosses the 80% level
    eighty_percent_idx = np.where(y_slice >= eighty_percent_level)[0]
    if len(eighty_percent_idx) > 0:
        eighty_percent_idx = eighty_percent_idx[0]
    else:
        eighty_percent_idx = len(y_slice) - 1  # In case no index is found, set it to the end
    
    # Calculate the 20-80 rise time
    rise_time_20_80 = x_slice[eighty_percent_idx] - x_slice[twenty_percent_idx]
    
    # Return the rise time and the actual indices (adjusted to the original x and y arrays)
    return rise_time_20_80, left_border + twenty_percent_idx, left_border + eighty_percent_idx

def exp_decay(x, a, tau, y0):
    return a * np.exp(-x / tau) + y0

def calculate_tau(x, y, peak_idx, right_idx):
    x_decay = x[peak_idx:right_idx] - x[peak_idx]
    y_decay = y[peak_idx:right_idx]

    if len(x_decay) < 2:  # Ensure there are enough points to fit
        return np.nan
    
    try:
        popt, _ = curve_fit(exp_decay, x_decay, y_decay, p0=(y_decay[0], 1, y_decay[-1]))
        tau = popt[1]
    except (RuntimeError, ValueError):
        tau = np.nan
    
    return tau

def detect_peaks_with_derivative(trace, threshold):
    x = np.linspace(0, len(trace), len(trace))
    baseline_fitter = Baseline(x_data=x)
    #trace = trace.fillna(df_trace[names].mean())
    trace = stats.zscore(trace)
    smoothed_trace = gaussian_filter1d(trace, sigma=20)
    
    trace = trace - baseline_fitter.noise_median(trace)[0]
    
    first_derivative = np.diff(smoothed_trace)
    
    peaks, _ = find_peaks(trace, prominence=threshold)
    left_border=find_peaks(trace,prominence=threshold)[0]
    right_border=find_peaks(trace,prominence=threshold)[0]
    
    left_border_list = left_border
    right_border_list = right_border
    '''
    for peak in peaks:
        left_border = np.where(first_derivative[:peak] <= 0)[0]
        
        right_border = np.where(first_derivative[peak:] >= 0)[0]

        
        if left_border.size > 0:
            left_border = left_border[-1]
        else:
            left_border = 0
        
        if right_border.size > 0:
            right_border = right_border[0] + peak
        else:
            right_border = len(smoothed_trace) - 1
        '''
            

        
        #left_border_list.append(left_border)
        #right_border_list.append(right_border)
    
    return smoothed_trace, peaks, left_border_list, right_border_list

fwhm_list = []
events_min_list=[]
z=0
for thresholds in threshold:
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for names, files in zip(names_, df_trace.columns):
        print(names)
        x = np.linspace(0, len(df_trace[names]), len(df_trace[names]))
        df_trace[names] = df_trace[names].fillna(df_trace[names].mean())
        df_trace[names] = stats.zscore(df_trace[names])
        
        trace = df_trace[names]
        original_fs = 2.3  # Hz
        desired_fs = 10.0  # Hz

        original_time = np.arange(len(trace)) / original_fs
        desired_time = np.arange(0, original_time[-1], 1 / desired_fs)

        interpolator = interp1d(original_time, trace, kind='linear')
        resampled_trace = interpolator(desired_time)
        x = np.linspace(0, len(resampled_trace), len(resampled_trace))
        
        smoothed_trace,peaks, left_border_list, right_border_list = detect_peaks_with_derivative(resampled_trace, thresholds)
        if len(peaks)>1:
            active_length=peaks[-1]-peaks[0]
            active_length_min=(active_length/10)/60
            events_min=len(peaks)/active_length_min
            events_min_list.append(events_min)
        else:
            active_length_min=len(smoothed_trace)
            events_min=len(peaks)/active_length_min
            events_min_list.append(0)
        
        peaks_diff=np.diff(peaks)
        peaks_diff=peaks_diff/10
        peak_diff_mean.append(np.nanmean(peaks_diff))
        peaks_diff_list.append(np.std(peaks_diff)/np.nanmean(peaks_diff))
        
        left_border_list=left_border_list-60
        right_border_list=right_border_list+60
        
        left_border_list[left_border_list<0]=0 
        right_border_list[right_border_list>len(smoothed_trace)]=len(smoothed_trace)-1
        
        all_detected_peaks[names].append(peaks)

        for peak, left_border, right_border in zip(peaks, left_border_list, right_border_list):
            
            amplitude = resampled_trace[peak]
            fwhm = calculate_fwhm(x, resampled_trace, left_border, right_border)
            rise_time, rise_time_idx = calculate_rise_time(x, resampled_trace, left_border, peak)
            rise_time_20_80, twenty_percent_idx, eighty_percent_idx = calculate_20_80_rise_time(x, resampled_trace, left_border, peak)
            #tau = calculate_tau(x, resampled_trace, peak, right_border)
            tau=1
            fwhm_list.append(fwhm)

            peak_metrics.append({
                'file': files,
                'trace': names,
                'peak_index': peak,
                'amplitude': amplitude,
                'fwhm': fwhm,
                'rise_time': rise_time,
                'rise_time_20_80': rise_time_20_80,
                'tau': tau
            })
        
        #plt.figure(dpi=300)
        #z=z+1
        #plt.title(str(z))
        #plt.plot(x,resampled_trace,'k-')
        #plt.plot(x[peaks],resampled_trace[peaks],'ro')
        #plt.plot(x,smoothed_trace)
        #plt.plot(x[left_border_list],resampled_trace[left_border_list],'bo')
        #plt.plot(x[right_border_list],resampled_trace[right_border_list], 'yo')
        #plt.savefig(r'C:\Users\wiesbrock\Desktop\Projekte\AMH\sprocadic\\'+str(names)+'.png')
            
        

    results.append({
        'threshold': thresholds,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    })

for result in results:
    print(f"Threshold: {result['threshold']}")
    print(f"True Positives: {result['true_positives']}")
    print(f"False Positives: {result['false_positives']}")
    print(f"False Negatives: {result['false_negatives']}")
    print('-' * 30)

output_path = r"C:\Users\wiesbrock\Downloads\Detected_Peaks.xlsx"

max_length = max(len(peaks) for peaks in all_detected_peaks.values())
df_peaks = pd.DataFrame({name: peaks + [None] * (max_length - len(peaks)) for name, peaks in all_detected_peaks.items()})

df_peaks.to_excel(output_path, index=False)

metrics_df = pd.DataFrame(peak_metrics)
metrics_df.to_excel(r"C:\Users\wiesbrock\Downloads\Peak_Metrics.xlsx", index=False)

# Histograms
import seaborn as sns
plt.figure(dpi=300)
sns.histplot(metrics_df['fwhm'].dropna()/10, bins=20, stat="probability")
sns.despine()
plt.title('Distribution of FWHM')
plt.xlabel('FWHM [s]')
plt.ylabel('Frequency')
plt.savefig(r'C:\Users\wiesbrock\Downloads\FWHM_Histogram.png')

rise_times=metrics_df['rise_time_20_80'].dropna()
#rise_times=rise_times[rise_times<10]

plt.figure(dpi=300)
sns.histplot(data=rise_times/10, bins=20, stat="probability")
sns.despine()
plt.title('Distribution of Rise Time')
plt.xlabel('Rise Time [s]')
plt.ylabel('Frequency')
plt.savefig(r'C:\Users\wiesbrock\Downloads\Rise_Time_Histogram.png')

plt.figure(dpi=300)
plt.hist(metrics_df['tau'].dropna(), bins=20, edgecolor='black')
plt.title('Distribution of Tau')
plt.xlabel('Tau')
plt.ylabel('Frequency')
plt.savefig(r'C:\Users\wiesbrock\Downloads\Tau_Histogram.png')

#import ace_tools as tools; tools.display_dataframe_to_user(name="Peak Metrics", dataframe=metrics_df)

plt.figure(dpi=300)
plt.plot(events_min_list,peaks_diff_list, 'o')

events_min_list=np.array(events_min_list)
peaks_diff_list=np.array(peaks_diff_list)
fwhm_list=np.array(fwhm_list)/10
rise_times=rise_times/10

fwhm_list=fwhm_list[rise_times<3]
rise_times=rise_times[rise_times<3]

rise_times=rise_times[fwhm_list<12]
fwhm_list=fwhm_list[fwhm_list<12]


