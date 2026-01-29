# Data supporting "Seasonal ice dynamics control the timing of crevasse drainage at a fast-flowing outlet glacier"

[![EarthArXiv Preprint - 10.31223/X5H45B](https://img.shields.io/badge/EarthArXiv_Preprint-10.31223%2FX5H45B-2ea44f)](https://doi.org/10.31223/X5H45B) [![Zenodo - 10.5281/zenodo.17287272](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.17287272-blue)](https://doi.org/10.5281/zenodo.17287272)

This repository is associated with the manuscript:

> Chudley, T. R., Stokes, C. R., Lea, J. M., Winterbottom, T., Law, R., Clason, C. C., Wytiahlowsky, H. E., and Dechow, J. L. (_submitted_). Seasonal ice dynamics control the timing of crevasse drainage at a fast-flowing outlet glacier. [Preprint DOI: 10.31223/X5H45B](https://doi.org/10.31223/X5H45B)

It contains open data associated with the paper, as well as Jupyter Notebooks necessary to replicate the figures within the paper. Running the Jupyter Notebooks requires the packages included within the `environment.yml` file, which can be installed using `conda` (e.g. `conda env create -f environment.yml`).

The directories contain the following:

## `./data`

This directory contains data necessary to replicate the analysis and figures in the study.

### `./data/dem`

 - `./data/dem/store_arcticdem_mosaic_32m_cog.tif` -- [ArcticDEM](https://www.pgc.umn.edu/data/arcticdem/) v4.1 mosaic of study region at 32 m resolution.

### `./data/masks`

Masks used to crop the data to crevasse fields.

 - `./data/masks/mask_crev.tif` -- Crevasse mask derived from [Chudley (2022)](https://doi.org/10.5281/zenodo.6779088), further processing described within manuscript. `0` = not crevasses, `1` = crevassed.
 - `./data/masks/mask_grimp_ice.tif` -- GrIMP ice mask from [Howat (2017)](https://doi.org/10.5067/B8X58MQBFUPA). `1` = land/ocean, `0` = ice.
 - `./data/masks/mask_laske.tif` -- Lake mask, described within manuscript. `0` = lake, `1` = not lake.
 - `./data/masks/mask_all.tif`: Combination of the three above masks.

### `./data/model_outputs`

LEFM model outputs.

 - `./data/model_outputs/scenario_predicted_depths.csv`. CSV file output of scenarios in Fig. [XX].  Rows 0-999 represent 1000 timesteps through scenarios, columns `1A` - `3C` represent the nine distinct scenarious outlined within the paper. Values represent predicted depth of crevassed with `min` value of `1.0`.
 - `./data/model_outputs/all_predicted_depths.nc`. Multidimensional NetCDF file showing parameter space of Fig. [XX]. Coordinate `r_xx` represents $R_{xx}$ in MPa, $d_w$ represents nominal water depth within crevase in m, and variable `d_s` represents predicted crevasse depth from LEFM modelling. Fixed and modelling are outlined within the manuscript.  

### `./data/outlines`

Outlines of crevasse fields and lakes (production described within the main manuscript) as geopackage files.

 - `./data/outlines/pondedcrevassefields.gpkg`. Vector dataset of all automatically classified contiguous crevasse fields. Contains fields:
   - `label`: a three-digit code correlating to the directories in `./data/timeseries`
   - `valid`: qualitative QA assessment of whether outline representes true ponded crevasse field.
   - `2019_drainage`: whether the field drained in 2019.
   - `2019_max_water`: the date of maximum water extent.
   - `2019_multiple maxima`: whether the field underwent multiple fill-drain-cycled in 2019.
   - `2019_maxima_melt_coincidence`: whether the field drainaed alongside a maxima in melt as observed in RACMO data.
 - `./data/outlines/lakefields.gpkg`. Same of above but for supraglacial lakes rather than crevasse fields. Contains the additional field `2019_rapid_drainage`, further specifying whether the drainage observed was 'rapid' (i.e. majority of water drained in <4 days).
  - `./data/outlines/emptycrevassefields.gpkg`. Manually produced 'empty' crevasse fields. No associated data beyond a `label` field.

### `./data/pixelcounts`

GeoTiff files counting the number of times a pixel was classified as water within the 2016-2022 study period. `count_crevs.tif` counts the raw number of times a pixel was identified as water, and `pred_lake.tif` count the number of times a pixel was identified as water after the lake-identifying morphological operations described in the main manuscript.

 - `count_crevs.tif`
 - `count_lakes.tif`



### `./data/timeseries`

Timeseries of water, strain rates, and RACMO-derived melt within the defined fields. 

Files for each field are structured first directories according the type of field (`pondedcrev`, `lakes`, and `emptycrev`), then into the labels of the individual field as identified in the `./data/outlines` directory, then into individual files for water (`timeseries_water.csv`), strain, (`timeseries_strain.csv`), and RACMO melt (`timeseries_racmo.csv`). The file structure is as follows:

```
timeseries/
├─ pondedcrev/
│  ├─ 000/
│  │  ├─ timeseries_water.csv
│  │  ├─ timeseries_strain.csv
│  │  └─ timeseries_racmo.csv
│  ├─ 001/
│  │  └─ ...
│  └─ ...
├─ lakes/
│  ├─ 000/
│  │  └─ ...
│  └─ ...
└─ emptycrev/
   ├─ 000/
   │  └─ ...
   └─ ...
```

`timeseries_water` files have the following fields:

 - `date`: Date of observation in the format `YYYY-MM-DD`.
 - `field_water_cover_km2`: Area of water observed within the polygon, in km<sup>2</sup>.
 `mask_cover_km2`: Area of masked data observed within the polygon, in km<sup>2</sup>. In the main paper, values `>0` are discarded before presentaiton/analysis.

 `timeseries_strain` files present data derived from ITS_LIVE data. Two strain analysis have been performed, one where $r$ = 250 m and one where $r$ = 500 m. Only 500 m was used in the study, although both are preserved here (see manuscript methods for more information). The fields are as follows:

 - `mid_date`: Mid-date of the acquisition dates of the two images used to construct the velocity field, in ISO 8601 format.
 - `data_dt`: Time difference between the two images, in ISO 8601 duration format.
 - `vx_error`: Reported error in $x$ direction, in m a<sup>-1</sup>.
 - `vy_error`: Reported error in $y$ direction, in m a<sup>-1</sup>.
 - `acquisition_date_img1`: Acqusition date of image 1, in ISO 8601 format.
 - `acquisition_date_img2`: Acqusition date of image 2, in ISO 8601 format.
 - `str_[250/500]_error`: Predicted error following [Poinar and Andrews (2021)](https://doi.org/10.5194/tc-15-1455-2021). NB these are not used in the study as ITS_LIVE Sentinel-2 velocity errors are likely overly conservative (see main manuscript).
 - `vel_[250/500]`: Average velocity within polygon, in m/a. This value is the same for $r$ = 250 m and $r$ = 500 m.
  - `e_1_[250/500]`: First principal strain rate, in a-1.
  - `e_2_[250/500]`: Second principal strain rate, in a-1.
  - `e_zz_[250/500]`: Inferred vertical strain rate (`e_2` - `e_1`), in a-1.
  - `e_lon_[250/500]`: Longitudinal strain rate in a-1, following [Bindschadler _et al._ (1996)](https://doi.org/10.1017/s0022143000003452).
  - `e_shr_[250/500]`: Shear strain rate in a-1, following [Bindschadler _et al._ (1996)](https://doi.org/10.1017/s0022143000003452).
  - `e_trn_[250/500]`: Transverse strain rate in a-1, following [Bindschadler _et al._ (1996)](https://doi.org/10.1017/s0022143000003452).
  - `e_e_[250/500]`: Effective strain rate in a-1.
  - `str_frac_[250/500]`: Fraction of valid strain rate data within polygon.

`timeseries_racmo` contains the following fields:

 - `date`: Date of observation in the format `YYYY-MM-DD`.
 - `mean_runoff_mm_d`: Mean runoff, in mm/d.
 - `total_runoff_m3`: Total runoff within the polygon (mean runoff multiplied by polygon area) in cubic metres.
 - `year`: Year
 - `mean_runoff_cumsum`: Cumulative annual mean runoff, in mm.
 - `total_runoff_cumsum`: Cumulative annual total runoff, in m.

### `./data/visualisation`

Contains `./visualisation/20190601_S2B_MSIL2A_20190601T151809_R068_T22WED_20201005T205636_RGB_8bit.tif`, an 8-bit three-channel (RGB) image of the Sentinel-2 image `20190601_S2B_MSIL2A_20190601T151809_R068_T22WED_20201005T205636`, clipped to the region of interest of the study. Used as background image during visualisations (e.g. Fig. 1 of paper).

## `./notebooks`

Jupyter Notebooks used to produce figures in the main manuscript.

 - `funcs.py`: Plotting functions for use in Notebooks.
 - `lefm.py`: LEFM functions for use in Notebooks.
 - `map_figures.ipynb`: Maps of study areas (Figs 1, S2, S3).
 - `timeseries_figures.ipynb`: Timeseries plots (Figs 2, 3, S5, S8).
 - `lefm_figures.ipynb`: LEFM plotting figures (Figs 4, 5, S6).

## `./figures`

Contains the figure outputs from Jupyter Notebooks in the `./notebooks` directory. Note that two Figures 6, 7, and S1, as well as Animation S1, are produced seperately from the Jupyter Notebooks. They are included in this directory for completeness, but do not have corresponding `.ipynb` source files.
