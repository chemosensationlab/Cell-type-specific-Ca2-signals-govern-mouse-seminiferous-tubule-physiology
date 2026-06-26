# -*- coding: utf-8 -*-
"""
Created on Thu May  2 18:12:55 2024

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
#from read_roi import read_roi_zip
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

path=r"C:\Users\wiesbrock\Desktop\Projekte\all_smmhc v2.xlsx"

df=pd.read_excel(path, skiprows=[0,1,2,3,4,5,6,7,8],header=None)
names=df.columns
names=names[1:]
df=df[names]

start_frame=pd.read_excel(path,skiprows=5,nrows=1,usecols=range(1,df.shape[1]+1), header=None)
stop_frame=pd.read_excel(path,skiprows=6,nrows=1,usecols=range(1,df.shape[1]+1), header=None)

start_unique=np.unique(start_frame)
stop_unique=np.unique(stop_frame)


df=np.array(df)
max_diff=10
cross_corr_array=np.zeros((len(names),len(names)))
lag_array=np.zeros((len(names),len(names)))

z_list=[]
corr_list=[]

z=0

window_length = 11  # Fenstergröße für den Filter (muss ungerade sein)
polyorder = 3

for k in tqdm(range(len(names))):
    for l in range(len(names)):
        trace_1=df[:,k]
        trace_2=df[:,l]
        trace_1=trace_1[3:]
        trace_2=trace_2[3:]

        
        trace_1 = pd.Series(trace_1).fillna(0)
        trace_2 = pd.Series(trace_2).fillna(0)
        trace_1[trace_2==0]=0
        trace_2[trace_1==0]=0
        

        
        trace_1=trace_1[trace_1!=0]
        trace_2=trace_2[trace_2!=0]
        

        
        
        
        
        if len(trace_1)>10:
                if len(trace_2)>10:
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
                    if len(np.where(cross_list==np.max(cross_list))[0])==1:
                        lag_array[k,l]=np.where(cross_list==np.max(cross_list))[0]
                    else:
                        lag_array[k,l]=np.where(cross_list==np.max(cross_list))[0][0]
                    cross_corr_array[k,l]=np.max(cross_list)
                    

plt.style.use("dark_background")  
start=0
stop=9
plt.figure(dpi=300)    
plt.title('Crosscorrelation')
plt.imshow(cross_corr_array[start:stop,start:stop],vmin=0,vmax=1)
plt.colorbar()
plt.savefig('Exp1.svg')
plt.figure(dpi=300)    
plt.title('Lag')
plt.imshow(lag_array[start:stop,start:stop],vmin=0,vmax=10)
plt.colorbar()
plt.savefig(r'Lag1.svg')

plt.figure(dpi=300)    
plt.title('Lag')
plt.imshow(lag_array)
plt.colorbar()
#plt.savefig(r'Y:\File transfer\Jerome_transfer\von_Christopher\lag_overall.svg')



for i in range(25):
    a=np.random.randint(15,180)
    b=a+15
    np.mean(cross_corr_array[a:b, b:b+15][cross_corr_array[a:b, b:b+15] != 1])
    
    
for i in range(len(start_unique)):
    plt.style.use("default")  
    start=start_unique[i]
    stop=stop_unique[i]+1
    plt.figure(dpi=300)    
    plt.title('Crosscorrelation')
    plt.imshow(cross_corr_array[start:stop,start:stop], cmap='YlOrRd',vmin=0,vmax=1)
    plt.colorbar()
    plt.savefig('SMMHC_heatmaps\Exp'+str(i)+'.svg')
    plt.savefig('SMMHC_heatmaps\Exp'+str(i)+'.png')
    plt.figure(dpi=300)    
    plt.title('Lag')
    #lag_array=lag_array/2.3
    plt.imshow(lag_array[start:stop,start:stop],vmin=0,vmax=5)
    plt.colorbar()
    plt.savefig(r'Lag'+str(i)+'.svg')

plt.figure(dpi=300) 
plt.title('Crosscorrelation')   
plt.imshow(cross_corr_array[0:25,150:175],cmap='YlOrRd', vmin=0,vmax=1)
plt.colorbar()
plt.savefig('SMMHC_heatmaps\Exp_control.svg')
plt.savefig('SMMHC_heatmaps\Exp_control.png')

import random
plt.figure(dpi=300)    
plt.title('Lag')
plt.imshow(lag_array[0:25,150:175],vmin=0,vmax=5)
plt.colorbar()
plt.savefig('Lag_control.svg')

# Flach das 2D-Array in eine 1D-Liste umwandeln
flattened_array = cross_corr_array.flatten()

# 2.000 zufällige Werte aus der flachen Liste auswählen
random_samples = random.sample(list(flattened_array), 2000)

# Jetzt enthält random_samples 2.000 zufällig ausgewählte Werte

               