# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 13:18:38 2024

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
import matplotlib.image as mpimg
import math
import matplotlib.colors as mcolors
from tqdm import tqdm
from scipy.signal import savgol_filter

def crosscorr(datax, datay, lag=0):
    """ Lag-N cross correlation. 
    Parameters
    ----------
    lag : int, default 0
    datax, datay : pandas.Series objects of equal length
    Returns
    ----------
    crosscorr : float
    """
    return datax.corr(datay.shift(lag))

def has_one_common_element(list1, list2):
    common_elements = set(list1) & set(list2)
    return len(common_elements) == 1

# Load the Excel file and select the required rows and columns


#index=0: Experimental id
#index=1: ROI-Name
#index=2: Tubulus ID

all_id=np.arange(1,26)
all_result_intra=[]
masked_results=[]
z_list=[]
corr_list=[]
window_length = 11  # Fenstergröße für den Filter (muss ungerade sein)
polyorder = 3
all_id=all_id[all_id!=14]

z=0

for i in all_id:
    path = r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    path_background=r"C:\Users\wiesbrock\Downloads\all_smmhc BG.xlsx"
    df = pd.read_excel(path, header=None)[0:3]
    names = df.columns[1:]
    df = df[names]
    new_df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    mask = np.zeros((len(new_df.columns), len(new_df.columns)), dtype=bool)
    label = new_df.iloc[2]
    
    for m in range(len(mask)):
        for n in range(len(mask)):  
            common_elements = set(label.iloc[m]) & set(label.iloc[n])
            mask[m, n] = len(common_elements) == 1
            
    path=r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    
    df_bg=pd.read_excel(path_background,skiprows=[3,4,5,6,7,8,9], header=None)

    df=pd.read_excel(path,skiprows=[3,4,5,6,7,8,9], header=None)
    df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    df_bg = df_bg[[col for col in df_bg.columns if df_bg[col].iloc[0] == i]]
    names=df.columns
    df=df[names]


    df=np.array(df)
    df_bg=np.array(df_bg)
    max_diff=12
    cross_corr_array=np.zeros((len(names),len(names)))
    lag_array=np.zeros((len(names),len(names)))

    for k in tqdm(range(len(names))):
        for l in range(len(names)):
            trace_1=df[:,k]
            trace_2=df[:,l]
            trace_1_bg=df_bg[:,k]
            trace_2_bg=df_bg[:,l]
            trace_1=trace_1[3:]
            trace_2=trace_2[3:]
            trace_1_bg=trace_1_bg[3:]
            trace_2_bg=trace_2_bg[3:]
            
            trace_1 = pd.Series(trace_1).fillna(0)
            trace_2 = pd.Series(trace_2).fillna(0)
            trace_1_bg = pd.Series(trace_1_bg).fillna(0)
            trace_2_bg = pd.Series(trace_2_bg).fillna(0)
            trace_1[trace_2==0]=0
            trace_2[trace_1==0]=0
            
            trace_1_bg[trace_2==0]=0
            trace_2_bg[trace_2==0]=0
            
            trace_1=trace_1[trace_1!=0]
            trace_2=trace_2[trace_2!=0]
            
            trace_1_bg=trace_1_bg[trace_1_bg!=0]
            trace_2_bg=trace_2_bg[trace_2_bg!=0]
            
            
            
            
            
            x = np.linspace(0, len(trace_1), len(trace_1))
            baseline_fitter = Baseline(x_data=x)
            trace_1 = np.nan_to_num(trace_1, nan=0)
            trace_1 = trace_1-baseline_fitter.noise_median(trace_1)[0]
            x = np.linspace(0, len(trace_2), len(trace_2))
            baseline_fitter = Baseline(x_data=x)
            trace_2 = np.nan_to_num(trace_2, nan=0)
            trace_2 =trace_2- baseline_fitter.noise_median(trace_2)[0]
            #trace_1 = savgol_filter(trace_1, window_length, polyorder)
            #trace_2 = savgol_filter(trace_2, window_length, polyorder)
                    
            
            trace_1=pd.DataFrame(trace_1)
            trace_2=pd.DataFrame(trace_2)
            trace_1=trace_1.squeeze()
            trace_2=trace_2.squeeze()
            cross_list=np.zeros((max_diff))
            for m in range(max_diff):
                cross_list[m]=crosscorr(trace_1,trace_2,lag=m)
              
            lag_array[k,l]=np.where(cross_list==np.max(cross_list))[0]
            cross_corr_array[k,l]=np.max(cross_list)
            
            
    cross_corr_array[mask==True]=0
    masked_results=np.concatenate(cross_corr_array)
            
    all_result_intra.append(masked_results)
            
    
    print(f"Maske für ID {i}:")
    print(mask)
    
all_result_intra=np.concatenate(all_result_intra)
all_result_intra=all_result_intra[all_result_intra<0.99]
all_result_intra=all_result_intra[all_result_intra!=0]
all_result_intra=all_result_intra/0.81
plt.figure(dpi=300)
sns.histplot(all_result_intra,stat='percent', kde=True)
sns.despine()
plt.title('Intra-Tubular')

all_id=np.arange(1,26)
all_result_inter=[]
masked_results=[]
all_id=all_id[all_id!=14]



for i in all_id:
    path = r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    path_background=r"C:\Users\wiesbrock\Downloads\all_smmhc BG.xlsx"
    df = pd.read_excel(path, header=None)[0:3]
    names = df.columns[1:]
    df = df[names]
    new_df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    mask = np.zeros((len(new_df.columns), len(new_df.columns)), dtype=bool)
    label = new_df.iloc[2]
    
    for m in range(len(mask)):
        for n in range(len(mask)):  
            common_elements = set(label.iloc[m]) & set(label.iloc[n])
            mask[m, n] = len(common_elements) == 1
            
    path=r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    
    df_bg=pd.read_excel(path_background,skiprows=[3,4,5,6,7,8,9], header=None)

    df=pd.read_excel(path,skiprows=[3,4,5,6,7,8,9], header=None)
    df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    df_bg = df_bg[[col for col in df_bg.columns if df_bg[col].iloc[0] == i]]
    names=df.columns
    df=df[names]


    df=np.array(df)
    df_bg=np.array(df_bg)
    max_diff=12
    cross_corr_array=np.zeros((len(names),len(names)))
    lag_array=np.zeros((len(names),len(names)))

    for k in tqdm(range(len(names))):
        for l in range(len(names)):
            trace_1=df[:,k]
            trace_2=df[:,l]
            trace_1_bg=df_bg[:,k]
            trace_2_bg=df_bg[:,l]
            trace_1=trace_1[3:]
            trace_2=trace_2[3:]
            trace_1_bg=trace_1_bg[3:]
            trace_2_bg=trace_2_bg[3:]
            
            trace_1 = pd.Series(trace_1).fillna(0)
            trace_2 = pd.Series(trace_2).fillna(0)
            trace_1_bg = pd.Series(trace_1_bg).fillna(0)
            trace_2_bg = pd.Series(trace_2_bg).fillna(0)
            trace_1[trace_2==0]=0
            trace_2[trace_1==0]=0
            
            trace_1_bg[trace_2==0]=0
            trace_2_bg[trace_2==0]=0
            
            trace_1=trace_1[trace_1!=0]
            trace_2=trace_2[trace_2!=0]
            
            trace_1_bg=trace_1_bg[trace_1_bg!=0]
            trace_2_bg=trace_2_bg[trace_2_bg!=0]
            
            
            
            
            
            x = np.linspace(0, len(trace_1), len(trace_1))
            baseline_fitter = Baseline(x_data=x)
            trace_1 = np.nan_to_num(trace_1, nan=0)
            trace_1 = trace_1-baseline_fitter.noise_median(trace_1)[0]
            x = np.linspace(0, len(trace_2), len(trace_2))
            baseline_fitter = Baseline(x_data=x)
            trace_2 = np.nan_to_num(trace_2, nan=0)
            trace_2 =trace_2- baseline_fitter.noise_median(trace_2)[0]
            #trace_1 = savgol_filter(trace_1, window_length, polyorder)
            #trace_2 = savgol_filter(trace_2, window_length, polyorder)
                    
            
            trace_1=pd.DataFrame(trace_1)
            trace_2=pd.DataFrame(trace_2)
            trace_1=trace_1.squeeze()
            trace_2=trace_2.squeeze()
            cross_list=np.zeros((max_diff))
            for m in range(max_diff):
                cross_list[m]=crosscorr(trace_1,trace_2,lag=m)
              
            lag_array[k,l]=np.where(cross_list==np.max(cross_list))[0]
            cross_corr_array[k,l]=np.max(cross_list)
                
              

            
    cross_corr_array[mask==False]=0
    masked_results=np.concatenate(cross_corr_array)
            
    all_result_inter.append(masked_results)
            
    
    print(f"Maske für ID {i}:")
    print(mask)
    
all_result_inter=np.concatenate(all_result_inter)
all_result_inter=all_result_inter[all_result_inter<0.99]
all_result_inter=all_result_inter[all_result_inter!=0]
all_result_inter=all_result_inter/0.81
plt.figure(dpi=300)
sns.histplot(all_result_inter, stat='percent', kde=True)
sns.despine()
plt.title('Inter-Tubular')
r'''
all_id=np.arange(1,26)
all_result_cluster=[]
masked_results=[]
all_id=all_id[all_id!=14]

for i in all_id:
    path = r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    path_background=r"C:\Users\wiesbrock\Downloads\all_smmhc BG.xlsx"
    df = pd.read_excel(path, header=None)[0:3]
    names = df.columns[1:]
    df = df[names]
    new_df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    mask = np.zeros((len(new_df.columns), len(new_df.columns)), dtype=bool)
    label = new_df.iloc[2]
    
    for m in range(len(mask)):
        for n in range(len(mask)):  
            if label.iloc[m]==label.iloc[n]:
                mask[m, n] = True
            else:
                mask[m, n] = False
            
    path=r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    
    df_bg=pd.read_excel(path_background,skiprows=[3,4,5,6,7,8,9], header=None)

    df=pd.read_excel(path,skiprows=[3,4,5,6,7,8,9], header=None)
    df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    df_bg = df_bg[[col for col in df_bg.columns if df_bg[col].iloc[0] == i]]
    names=df.columns
    df=df[names]


    df=np.array(df)
    df_bg=np.array(df_bg)
    max_diff=12
    cross_corr_array=np.zeros((len(names),len(names)))
    lag_array=np.zeros((len(names),len(names)))

    for k in tqdm(range(len(names))):
        for l in range(len(names)):
            trace_1=df[:,k]
            trace_2=df[:,l]
            trace_1_bg=df_bg[:,k]
            trace_2_bg=df_bg[:,l]
            trace_1=trace_1[3:]
            trace_2=trace_2[3:]
            trace_1_bg=trace_1_bg[3:]
            trace_2_bg=trace_2_bg[3:]
            
            trace_1 = pd.Series(trace_1).fillna(0)
            trace_2 = pd.Series(trace_2).fillna(0)
            trace_1_bg = pd.Series(trace_1_bg).fillna(0)
            trace_2_bg = pd.Series(trace_2_bg).fillna(0)
            trace_1[trace_2==0]=0
            trace_2[trace_1==0]=0
            
            trace_1_bg[trace_2==0]=0
            trace_2_bg[trace_2==0]=0
            
            trace_1=trace_1[trace_1!=0]
            trace_2=trace_2[trace_2!=0]
            
            trace_1_bg=trace_1_bg[trace_1_bg!=0]
            trace_2_bg=trace_2_bg[trace_2_bg!=0]
            
            
            
            
            
            x = np.linspace(0, len(trace_1), len(trace_1))
            baseline_fitter = Baseline(x_data=x)
            trace_1 = np.nan_to_num(trace_1, nan=0)
            trace_1 = trace_1-baseline_fitter.noise_median(trace_1)[0]
            x = np.linspace(0, len(trace_2), len(trace_2))
            baseline_fitter = Baseline(x_data=x)
            trace_2 = np.nan_to_num(trace_2, nan=0)
            trace_2 =trace_2- baseline_fitter.noise_median(trace_2)[0]
            #trace_1 = savgol_filter(trace_1, window_length, polyorder)
            #trace_2 = savgol_filter(trace_2, window_length, polyorder)
                    
            
            
            trace_1=pd.DataFrame(trace_1)
            trace_2=pd.DataFrame(trace_2)
            trace_1=trace_1.squeeze()
            trace_2=trace_2.squeeze()
            cross_list=np.zeros((max_diff))
            for m in range(max_diff):
                cross_list[m]=crosscorr(trace_1,trace_2,lag=m)
              
            lag_array[k,l]=np.where(cross_list==np.max(cross_list))[0]
            cross_corr_array[k,l]=np.max(cross_list)
            

            
    cross_corr_array[mask==False]=0
    masked_results=np.concatenate(cross_corr_array)
            
    all_result_cluster.append(masked_results)
            
    
    print(f"Maske für ID {i}:")
    print(mask)
    
all_result_cluster=np.concatenate(all_result_cluster)
all_result_cluster=all_result_cluster[all_result_cluster<0.99]
all_result_cluster=all_result_cluster[all_result_cluster!=0]
all_result_cluster=all_result_cluster/0.81
plt.figure(dpi=300)
sns.histplot(all_result_cluster,stat='percent', kde=True)
sns.despine()
plt.title('Intra-Tubulus cluster')

plt.figure(dpi=300)
data=all_result_intra,all_result_inter, all_result_cluster
sns.violinplot(data=data)
sns.despine()
plt.xticks([0,1,2],['Intra', 'Inter','Cluster'])
plt.title('Intra vs Inter')

#%% rois
all_id=np.arange(1,26)
all_result_cluster=[]
masked_results=[]
all_id=all_id[all_id!=14]

for i in all_id:
    path = r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    path_background=r"C:\Users\wiesbrock\Downloads\all_smmhc BG.xlsx"
    df = pd.read_excel(path, header=None)[0:3]
    names = df.columns[1:]
    df = df[names]
    new_df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    mask = np.zeros((len(new_df.columns), len(new_df.columns)), dtype=bool)
    label = new_df.iloc[2]
    
    for m in range(len(mask)):
        for n in range(len(mask)):  
            if label.iloc[m]==label.iloc[n]:
                mask[m, n] = True
            else:
                mask[m, n] = False
            
    path=r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"
    
    df_bg=pd.read_excel(path_background,skiprows=[3,4,5,6,7,8,9], header=None)

    df=pd.read_excel(path,skiprows=[3,4,5,6,7,8,9], header=None)
    df = df[[col for col in df.columns if df[col].iloc[0] == i]]
    df_bg = df_bg[[col for col in df_bg.columns if df_bg[col].iloc[0] == i]]
    names=df.columns
    df=df[names]


    df=np.array(df)
    df_bg=np.array(df_bg)
    max_diff=12
    cross_corr_array=np.zeros((len(names),len(names)))
    lag_array=np.zeros((len(names),len(names)))

    for k in tqdm(range(len(names))):
        for l in range(len(names)):
            trace_1=df[:,k]
            trace_2=df[:,l]
            trace_1_bg=df_bg[:,k]
            trace_2_bg=df_bg[:,l]
            trace_1=trace_1[3:]
            trace_2=trace_2[3:]
            trace_1_bg=trace_1_bg[3:]
            trace_2_bg=trace_2_bg[3:]
            
            trace_1 = pd.Series(trace_1).fillna(0)
            trace_2 = pd.Series(trace_2).fillna(0)
            trace_1_bg = pd.Series(trace_1_bg).fillna(0)
            trace_2_bg = pd.Series(trace_2_bg).fillna(0)
            trace_1[trace_2==0]=0
            trace_2[trace_1==0]=0
            
            trace_1_bg[trace_2==0]=0
            trace_2_bg[trace_2==0]=0
            
            trace_1=trace_1[trace_1!=0]
            trace_2=trace_2[trace_2!=0]
            
            trace_1_bg=trace_1_bg[trace_1_bg!=0]
            trace_2_bg=trace_2_bg[trace_2_bg!=0]
            
            
            
            
            
            x = np.linspace(0, len(trace_1), len(trace_1))
            baseline_fitter = Baseline(x_data=x)
            trace_1 = np.nan_to_num(trace_1, nan=0)
            trace_1 = trace_1-baseline_fitter.noise_median(trace_1)[0]
            x = np.linspace(0, len(trace_2), len(trace_2))
            baseline_fitter = Baseline(x_data=x)
            trace_2 = np.nan_to_num(trace_2, nan=0)
            trace_2 =trace_2- baseline_fitter.noise_median(trace_2)[0]
            #trace_1 = savgol_filter(trace_1, window_length, polyorder)
            #trace_2 = savgol_filter(trace_2, window_length, polyorder)
                    
            
            
            trace_1=pd.DataFrame(trace_1)
            trace_2=pd.DataFrame(trace_2)
            trace_1=trace_1.squeeze()
            trace_2=trace_2.squeeze()
            cross_list=np.zeros((max_diff))
            for m in range(max_diff):
                cross_list[m]=crosscorr(trace_1,trace_2,lag=m)
              
            lag_array[k,l]=np.where(cross_list==np.max(cross_list))[0]
            cross_corr_array[k,l]=np.max(cross_list)
            

            
    cross_corr_array[mask==False]=0
    masked_results=np.concatenate(cross_corr_array)
            
    all_result_cluster.append(masked_results)
            
    
    print(f"Maske für ID {i}:")
    print(mask)
    r'''
