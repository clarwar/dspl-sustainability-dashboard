#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 15:26:18 2026

@author: claranassar
"""

import pandas as pd

# load CSV file
data = pd.read_csv("/Users/claranassar/Desktop/DSPL INDVL CCW/DATASET/WB_EWSA_WIDEF.csv")

#columns that are not needed for the dashboard
columns_to_drop =[
    "FREQ",
    "FREQ_LABEL",
    "DATABASE_ID",
    "DATABASE_ID_LABEL",
    "UNIT_MULT",
    "UNIT_MULT_LABEL",
    "OBS_STATUS",
    "OBS_STATUS_LABEL",
    "OBS_CONF",
    "OBS_CONF_LABEL" ]


#drop the columns
data = data.drop(columns=columns_to_drop)

#check remaining columns
print("\nREMAINING COLUMNS")
print(data.columns)





# check missing values in each column
print("\nMISSING VALUES")
print(data.isna().sum())

# check missing values as percentages
print('\nMISSING PERCENTAGES')
missing_percent= data.isna().mean() * 100
print(missing_percent.sort_values (ascending=False) )

# check missing values in year columns only
print("\nCHECK YEARS")
year_cols =[ str(y) for y in range(1964, 2024) ]

missing_years = data[year_cols].isna().mean() * 100
print("\nYEARS PERCENTAGE")
print(missing_years.sort_values(ascending=False))





# drop years before 2000 and 2023
years_to_drop = [str(year) for year in range(1964, 2000)]+["2023"]

#remove year columns from the dataset
data = data.drop(columns=years_to_drop)

#check columns after dropping years
print("\nCOLUMNS AFTER DROPPING YEARS")
print(data.columns)






# check missing values by indicator
year_cols =[str(year) for year in range(2000, 2023) ]

indicator_missing = data.groupby("INDICATOR_LABEL")[year_cols].apply(
    lambda group: group.isna().mean().mean() * 100)

indicator_missing = indicator_missing.sort_values(ascending=False)

print("\nINDICATOR MISSING\n")
print(indicator_missing)





# list indicators needed for the dashboard
indicators_to_keep = [
    "Water Stress (SDG 6.4.2)",
    "Total renewable water resources per capita",
    "Agricultural water withdrawal as % of total water withdrawal",
    "Total water supply coverage by piped improved facilities (%)"  ]

#keep only those indicators
data = data[data["INDICATOR_LABEL"].isin(indicators_to_keep)]

#check it worked
print("\nINDICATORS KEPT")
print(data["INDICATOR_LABEL"].unique())

#check the shape
print("\nFINAL DATA SHAPE")
print(data.shape)

#final checks before saving
print(data.isna().sum())
print(data.duplicated().sum())
print(data.dtypes)



#save the cleaned file
data.to_csv("/Users/claranassar/Desktop/DSPL INDVL CCW/DATASET/water_security_clean.csv", index=False)
