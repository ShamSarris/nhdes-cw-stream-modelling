# NHDES Cold Water Wadeable Stream Modelling

## Overview
The goal of this effort is to classify 1st - 4th order (wadeable) streams as cold water based on data from NHDES EMD (Environmental Monitoring Database) and other. Based on the 2007 paper from NHDES using Logistic regression, can we build a more accurate and inference-able model for this effort?

## Data Organization + Cleaning

**NHDES EMD Assemblage Records**
From the NHDES EMD the following data is used  from electro-fishing sampling efforts(see [20260316_Fish_Data.xlsx](NHDES Fish Assemblage Data)):
- EMD Station ID (where the sampling took place)
- Collection Date
- Stream Order
- Lattitude / Longitude of site
- Fish Species 
- Number of Fish Species collected

The original 2007 model used the following filters on the available assemblage data: 
- Only 1st-4th order streams
- Lattitude and Longitude of sites
- Only samples of Slimy Sculpin (SS) and Eastern Brooke Trout (EBT) (Cold water specialists)
- Only records where there were at least 30 SS and/or EBT

Notes for our process:
1) We want to attempt to include strict warm water specialists to add data points
2) We want to use cross validation to determine if we can included sites that had < 30 SS/EBT
3) Since these are wadeable steams, do we need to consider deep holes for cold water fish? A detractor of IBIs. 

**Drainage Area**
We attempted 2 methods of identifying the drainage/watershed area of each sampling site. The first method was to use the USGS NHD api with the known NHD COMID for each site. This provided the drainage area of each site easily and reliably. Note that the USGS NHD is no longer being maintained as of 2023. Since the data under review is previous to that time, this is a reliable API. The second method was to use shapefiles provided by the NHDES of the watershed area of each sampling site, and calculating the area of each watershed shape. The area from each method for each site was compared and the mean difference was 0.8 square miles. *What to choose?*

**National Land Cover Database (NLCD)**
In the original 2007 paper, 37 of the sampling sites were excluded due to "significant human disturbances based on objective criteria". In attempts to best match the original model, we are using the NLCD data from each year of sampling to determine if the areas of collection had much human activity. We will use CV to determine what % land development signifies "significant human disturbance" and if more or less % will affect the model. 