# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 13:19:50 2023

@author: wiesbrock
"""

import glob
import numpy as np
import pandas as pd
import os
import matplotlib.pylab as plt
from tqdm import tqdm
import seaborn as sns
import scipy.stats as stats
from pybaselines import Baseline
from pybaselines.utils import gaussian
import csv
import numpy as np
import pandas as pd
import scipy.stats as stats
import scipy.signal as signal
import matplotlib.pylab as plt
import seaborn as sns
from pybaselines import Baseline
from pybaselines.utils import gaussian
from sklearn.preprocessing import MinMaxScaler

import openpyxl
from openpyxl import load_workbook

import numpy as np

from scipy.stats import linregress

# Liste zur Speicherung der R-Werte
r_values = []



def linear_fit_and_store_r(x, y):
    """
    Führt eine lineare Regression auf den gegebenen x- und y-Daten durch und speichert den R-Wert.

    Parameters:
    x (array_like): Die x-Koordinaten der Datenpunkte.
    y (array_like): Die y-Koordinaten der Datenpunkte.

    Returns:
    slope (float): Die Steigung der Regressionslinie.
    intercept (float): Der y-Achsenabschnitt der Regressionslinie.
    """
    # Führe die lineare Regression durch
    result = linregress(x, y)
    
    # Speichere den R-Wert in der globalen Liste
    r_values.append(result.rvalue)
    
    # Gib die Steigung und den y-Achsenabschnitt zurück
    return result.slope, result.intercept


def find_number_sequences(zeitreihe):
    
    is_number = ~np.isnan(zeitreihe)
    start_number_seq = np.where(is_number & ~np.roll(is_number, 1))[0]  
    end_number_seq = np.where(is_number & ~np.roll(is_number, -1))[0]  

    return start_number_seq, end_number_seq

def find_nan_sequences(zeitreihe):
    is_nan = np.isnan(zeitreihe)
    start_nan_seq = []
    end_nan_seq = []

    in_nan_seq = False
    for idx, val in enumerate(is_nan):
        if val and not in_nan_seq:
            start_nan_seq.append(idx)
            in_nan_seq = True
        elif not val and in_nan_seq:
            end_nan_seq.append(idx)
            in_nan_seq = False

    # Falls die letzte Sequenz bis zum Ende des Arrays reicht
    if in_nan_seq:
        end_nan_seq.append(len(zeitreihe))

    return np.array(start_nan_seq), np.array(end_nan_seq)





#path=r'X:\Jerome\Las_X_Rohdatein\LASX_RAW_PrintedInvivo_von_SP8\SMMHC\Analysis_SMMHC\ROIs_Results_MaxAverage_RedSub_FG\*'
path=r'C:\Users\wiesbrock\Desktop\Projekte\SMMHC\ROIs_Results_MaxAverage_RedSub_FG\*'
path_pattern=r"C:\Users\wiesbrock\Downloads\Dateiliste SMMHC.xlsx"
#path=r'C:\Users\wiesbrock\Desktop\nan_test\*'
files=glob.glob(path)

list_gre=[]
list_red=[]
list_list_freq=[]
list_list_isi=[]
list_roi_name=[]
list_file_name=[]
#red=background green=signal

for i in files:
    if "RawGre" in i and "binary" not in i:
        list_gre.append(i)
        
for i in files:
    if "RawRed" in i:
        list_red.append(i)
        
for n in tqdm(range(len(list_gre))):
    green_data = pd.read_csv(list_gre[n], encoding='ISO-8859-1')
    print(list_gre[n])
    red_data=pd.read_csv(list_red[n])
    names=green_data.columns
    bin_frame=pd.DataFrame(columns=names)
    names=names[1:]
    peaks=np.zeros((len(names),2))
    nan_array=np.zeros((len(names)))
    results=pd.DataFrame()
    result_dict = {'Column': [], 'Freq_List': []}
    all_results = pd.DataFrame()
    data_dict={}
    csv_data=[]
    indices_frame = pd.DataFrame(columns=names, index=np.arange(200))
    p=0
    save_bin=bin_frame.copy()
    save_peak=pd.DataFrame()
    os.mkdir(list_gre[n][:-3])
    os.chdir(list_gre[n][:-3])
    for m in names:
        list_file_name.append(list_gre[n])
        list_roi_name.append(m)
        
        #factor=np.mean(green_data[m])-np.mean(red_data[m])
        #red_data[m]=red_data[m]+factor
        corrected_data=green_data[m].copy()
        
        corrected_data[0]=np.nan
        
        x = np.linspace(0, len(corrected_data), len(corrected_data))
        baseline_fitter = Baseline(x_data=x)
        

        nan_start_indices, nan_end_indices = find_nan_sequences(corrected_data)

        baseline_data = np.nan_to_num(corrected_data, nan=np.mean(corrected_data))
        baseline_green = baseline_fitter.noise_median(baseline_data)[0]

        complete_data = corrected_data - baseline_green
        curated = complete_data.copy()
        
        
        x=len(corrected_data)
        plt.xlim(0,x)
        nan_start_indices, nan_end_indices = find_nan_sequences(corrected_data)
        
        
        
        for start, end in zip(nan_start_indices, nan_end_indices):
            # Erweiterung der Start- und Endindizes um 20 Frames unter Berücksichtigung der Array-Grenzen
            # extended_start = max(start - 100, 0)
            # extended_end = min(end + 100, len(complete_data))

            # Setzen des erweiterten Bereichs auf NaN
            curated[start - 40:end + 40] = np.nan
        
        start_seq, end_seq = find_number_sequences(curated)

        seq_check = np.ones((len(start_seq))).astype(int)

        for k in range(len(end_seq)):
            if end_seq[k] - start_seq[k] < 200:
                curated[start_seq[k]:end_seq[k] + 1] = np.nan
                seq_check[k] = 0
            if len(end_seq) > 1 and start_seq[k] != 0 and end_seq[k] != len(end_seq):
                curated[start_seq[k] - 5:start_seq[k]] = np.nan
                curated[end_seq[k]:start_seq[k] + 5] = np.nan
                
        corrected_data = np.nan_to_num(curated, nan=0)

        corrected_data = stats.zscore(corrected_data)

        corrected_data[:] = (corrected_data[:] - corrected_data[:].min()) / (
                    corrected_data[:].max() - corrected_data[:].min())
        
        if len(corrected_data[corrected_data>0])>0:
            start_seq = start_seq[np.where(seq_check == 1)[0]]
            end_seq = end_seq[np.where(seq_check == 1)[0]]
        else:
            start_seq,end_seq=0,0

        # max_len = len(end_seq)

        binary = np.zeros((len(corrected_data)))
        peak_indices = signal.find_peaks(corrected_data,prominence=0.27, threshold=0.08)[0] #0.3;0.1 ist gut
        #peak_indices = signal.find_peaks(corrected_data,prominence=m, threshold=0.08)[0] #0.3;0.1 ist gut
        # print(peak_indices)
        #binary[corrected_data>m]=1
        binary[peak_indices] = 1
        start_peak = np.diff(binary)
        start_peak[start_peak != 1] = 0

        peak_series = pd.Series(peak_indices)
        indices_frame[i] = peak_series
        
        save_peak[m]=peak_series
        
        freq_list = []
        x_data=np.linspace(0,len(np.cumsum(binary)),len(np.cumsum(binary)))
        y_data=np.cumsum(binary)
        slope, intercept = linear_fit_and_store_r(x_data, y_data)
        
        
        
        #plt.figure()
        #plt.title(str(m))
        #x=np.linspace(0,len(corrected_data),len(corrected_data))
        #plt.plot(x,corrected_data,'k-')
        #plt.plot(x[peak_indices],corrected_data[peak_indices],'ro')
        #plt.savefig(str(m)+'.svg')
        
        #plt.figure()
        #plt.subplot(311)
        #plt.plot(binary)
        #plt.subplot(312)
        #plt.plot(x_data,y_data,label=r_values[-1])
        #plt.legend()
        #plt.subplot(313)
        #plt.plot(x_data,corrected_data)
        
        
        if np.sum(binary)>0:
        
            try:
                for o in range(len(start_seq)):
                    if np.sum(start_peak[start_seq[o]:end_seq[o]])>1:
                        first_peak=np.where(start_peak[start_seq[o]:end_seq[o]]==1)[0][0]
                        last_peak=np.where(start_peak[start_seq[o]:end_seq[o]]==1)[0][-1]
                        peak_num=np.sum(start_peak[start_seq[o]:end_seq[o]])
                        minutes=(last_peak - first_peak) / 2.3 / 60
                    freq_list.append(peak_num/minutes)

            except:
                first_peak=start_seq
                last_peak=end_seq
                peak_num=np.sum(start_peak[start_seq[o]:end_seq[o]])
                minutes=(last_peak - first_peak) / 2.3 / 60
                freq_list.append(peak_num/minutes)

                
        if np.sum(binary)==0:
            freq_list.append(0)
            
        
         
        distances = []
        
        if np.sum(binary)>0:
            

        # Durchlaufe alle Sequenzen
            for o in range(len(start_seq)):
                # Betrachte nur den relevanten Teil des Arrays
                segment = start_peak[start_seq[o]:end_seq[o] + 1]
            
                # Überprüfe, ob mehr als eine 1 im Segment vorhanden ist
                if np.sum(segment) > 1:
                    # Finde die Indizes aller Einsen im Segment
                    peak_indices = np.where(segment == 1)[0]
            
                    # Berechne die Abstände zwischen aufeinanderfolgenden Einsen
                    segment_distances = np.diff(peak_indices)
            
                    # Füge die Abstände zur Hauptliste hinzu
                    distances.append(segment_distances)
        
            
        
        
        save_bin[m]=binary

        #data_dict[m] = freq_list

        # plt.figure()
        # plt.plot(x,y)

        #corrected_data = green_data[i]
        
        indices_frame.to_excel(r'C:\Users\wiesbrock\Desktop\Projekte\Ground-Truth-SMMHC\peaks.xlsx')
        try:        
            max_len = len(end_seq)
        except:
            max_len=1
            
        data_dict[m] = freq_list
        list_list_freq.append(freq_list)
        list_list_isi.append(distances)
        
    save_bin.to_excel(list_gre[n]+'_binary.xlsx')
    save_peak.to_excel(list_gre[n]+'_peaks.xlsx')
        


# Erstelle einen DataFrame, wobei jede Liste eine Spalte im DataFrame ist
df = pd.DataFrame(list_list_freq).transpose()
distance_df=pd.DataFrame(list_list_isi)
all_distance=[item for sublist in distance_df.values.flatten() if sublist is not None for item in sublist]
all_distance=np.array(all_distance)
all_distance=all_distance/2.3

# Speichere den DataFrame in einer Excel-Datei
df.to_excel("output.xlsx", index=False, header=False)

print("Excel-Datei wurde erfolgreich erstellt!")
'''
all_data=df.values.ravel()
all_data=all_data[all_data>0]
plt.figure(dpi=300)
sns.violinplot(data=all_data, cut=0)
sns.despine()
plt.ylabel('Events/Min')
plt.savefig('Events_vio.svg')
plt.figure(dpi=300)
sns.swarmplot(data=all_data)
sns.despine()
plt.ylabel('Events/Min')
plt.savefig('Events_sc.svg')

plt.figure(dpi=300)
sns.violinplot(data=all_distance, cut=0)
sns.despine()
plt.ylabel('ISI[s]')
plt.savefig('ISI_vio.svg')
plt.figure(dpi=300)
sns.swarmplot(data=all_distance)
sns.despine()
plt.ylabel('ISI[s]')
plt.savefig('ISI_sc.svg')

# Erstelle einen Plot
plt.figure(figsize=(10, 6))  # Größe des Plots anpassen

# Zeichne jede Spalte im DataFrame
for column in df.columns:
    df[column].dropna().plot()  # Ignoriere NaNs und zeichne die Linie

# Füge Legende hinzu
#plt.legend()

# Titel und Achsenbeschriftungen hinzufügen
plt.title('Time effects')
plt.xlabel('')
plt.ylabel('Frequency')
                
r_values=np.array(r_values)

plt.figure()
sns.violinplot(data=r_values, cut=0)
'''

mean_freqs = [np.nanmean(sublist) for sublist in list_list_freq]
list_mean=[[np.mean(array) for array in sublist] for sublist in list_list_isi]
list_sd = [[np.std(array) for array in sublist] for sublist in list_list_isi]
mean_sd=[np.nanmean(sublist) for sublist in list_sd]
list_mean=[np.nanmean(sublist) for sublist in list_mean]


mean_sd=np.array(mean_sd)
mean_freqs=np.array(mean_freqs)
list_mean=np.array(list_mean)

mean_sd=mean_sd[mean_freqs>0.]
mean_freqs=mean_freqs[mean_freqs>0.]
list_mean=list_mean[list_mean>0.]

        






       
        
        
        
        