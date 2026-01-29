import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.stats import gaussian_kde


# PLOTTING FUNCTIONS

def add_panel_label(ax, label, loc='top left', offset=2/(1/25.4), **kwargs):
    """
    Add a panel label to the corner of a figure. 
    """
    
    fig = ax.get_figure()
    px = offset * fig.dpi  # convert inches to pixels

    loc = loc.lower().replace(' ', '')
    loc_dict = {
        'topleft':     dict(xy=(0, 1), text=(px, -px), ha='left',  va='top'),
        'topright':    dict(xy=(1, 1), text=(-px, -px), ha='right', va='top'),
        'bottomleft':  dict(xy=(0, 0), text=(px, px), ha='left',  va='bottom'),
        'bottomright': dict(xy=(1, 0), text=(-px, px), ha='right', va='bottom'),
    }
    cfg = loc_dict[loc]
    
    # Place in pixel coordinates relative to axis
    ax.annotate(
        label,
        xy=cfg['xy'], xycoords='axes fraction',
        xytext=cfg['text'], textcoords='offset points',
        ha=cfg['ha'], va=cfg['va'],
        **kwargs,
    )


# TIME-SERIES AGGREGATION FUNCTIONS


def get_aggregate_data(gdf, datatype, year, relative_to_drainage):
    """
    Get all observations from all crevasses/lakes into a single pandas dataframe.
    """

    df_strain_list = []
    df_racmo_list = []
    
    for _, row in tqdm(gdf.iterrows()):
    
        i = row.label
        # print(i)
    
        df_strain = pd.read_csv(f'../data/timeseries/{datatype}/{i}/timeseries_strain.csv')
        df_strain = df_strain[['mid_date', 'date_dt', 'acquisition_date_img1', 'acquisition_date_img2', 'vel_frac_500', 'e_1_500', 'e_2_500', 'e_lon_500']]
        df_strain['mid_date'] = pd.to_datetime(df_strain['mid_date'], format='ISO8601')
        df_strain = df_strain[df_strain.mid_date.dt.year == year]
        df_strain = df_strain[df_strain['vel_frac_500']>=0.8] # Filter only to velcoity cover with 80% data cover
        
        df_strain['date_dt'] = pd.to_timedelta(df_strain['date_dt'])
        df_strain['acquisition_date_img1'] = pd.to_datetime(df_strain['acquisition_date_img1'], format='ISO8601')
        df_strain['acquisition_date_img2'] = pd.to_datetime(df_strain['acquisition_date_img2'], format='ISO8601')
        df_strain['date_dt'] = pd.to_timedelta(df_strain['date_dt'])
        
        df_strain['crevasse_field'] = i
        df_strain['day_of_year'] = df_strain.mid_date.dt.dayofyear
        
        df_racmo = pd.read_csv(f'../data/timeseries/{datatype}/{i}/timeseries_racmo.csv')
        df_racmo['date'] = pd.to_datetime(df_racmo['date'])
        df_racmo = df_racmo[df_racmo.date.dt.year == year]
    
        df_racmo['crevasse_field'] = i
        df_racmo['day_of_year'] = df_racmo.date.dt.dayofyear
        
        if relative_to_drainage == True:
            drainage_date = row['2019_max_water']
            
            df_strain['drainage_date_delta'] = df_strain.mid_date - drainage_date
            df_strain['delta_days'] = df_strain['drainage_date_delta'].dt.total_seconds() / 86400
    
            df_racmo['drainage_date_delta'] = df_racmo.date - drainage_date
            df_racmo['delta_days'] = df_racmo['drainage_date_delta'].dt.total_seconds() / 86400
    
        df_strain_list.append(df_strain)
        df_racmo_list.append(df_racmo)

    df_strain_list = pd.concat(df_strain_list).reset_index(drop=True)
    df_racmo_list = pd.concat(df_racmo_list).reset_index(drop=True)

    return df_strain_list, df_racmo_list



def get_gaussian_densities(df, datatype, y_column, relative_days=True, vrange=0.1):
    """
    Get a gaussian distribution of strain/runoff through time.
    """
    
    if relative_days==True:
        x = df['delta_days'].values
    else:
        x = df['day_of_year'].values
    
    y = df[y_column].values
    
    x = x[~np.isnan(y)]

    if datatype=='strain':
        xerr = (df['date_dt'] / np.timedelta64(1, 'D')).values / 2
        xerr = xerr[~np.isnan(y)]
        
    y = y[~np.isnan(y)]
    
    if relative_days==True:
        target_days = np.linspace(-50, 100, 151)
    else: 
        target_days = np.linspace(100, 250, 151)

    if datatype=='strain':
        y_vals = np.linspace(-vrange, vrange, 1001)
    elif datatype=='racmo':
        y_vals = np.linspace(0, 80, 801)
    else:
        raise ValueError("`datatype` must be one of 'strain' or 'racmo'")

    heatmap_days = []
    heatmap = []
    modes = []

    for day in tqdm(target_days):

        if datatype=='strain':
            mask = (x - xerr <= day) & (x + xerr >= day)
        else:
            mask = x == day
            
        y_subset = np.array(y[mask])
        
        if (len(y_subset) > 1) and ~np.all(y_subset==0):
                kde = gaussian_kde(y_subset)
                density = kde(y_vals)
        else:
            density = np.zeros_like(y_vals)

        mode = y_vals[np.argmax(density)]

        # print(f'day {day}', mode)
        
        heatmap.append(density)
        modes.append(mode)

    heatmap = np.array(heatmap)  # shape: [len(target_days), len(y_vals)]

    return target_days, y_vals, heatmap, modes

