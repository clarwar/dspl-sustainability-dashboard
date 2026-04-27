#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Water Security Dashboard
"""

import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt





st.set_page_config(page_title="Water Security Dashboard", layout="wide")





# shorter labels so the dropdowns are easier to read
indicator_names = {
    "Water Stress (SDG 6.4.2)": "Water stress",
    "Total renewable water resources per capita": "Renewable water resources",
    "Agricultural water withdrawal as % of total water withdrawal": "Agricultural water withdrawal",
    "Total water supply coverage by piped improved facilities (%)": "Piped water coverage"}

indicator_units = {
    "Water Stress (SDG 6.4.2)": "%",
    "Total renewable water resources per capita": "m³ per person",
    "Agricultural water withdrawal as % of total water withdrawal": "%",
    "Total water supply coverage by piped improved facilities (%)": "%"}





# load the cleaned dataset
csv_path = os.path.join(os.path.dirname(__file__), "data", "clean", "water_security_clean.csv")
data = pd.read_csv(csv_path)

year_cols = [str(y) for y in range(2000, 2023)]





#helper function for chart style
def style_axes(ax):
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)





#title and intro
st.title("Water Security Dashboard")

st.write(
    "This dashboard explores water security across selected European and Central Asian countries "
    "using World Bank data from 2000 to 2022.")


st.markdown("### What this dashboard shows" )


st.write(
    """
    Water security means having enough safe and reliable water for people, farming, and the environment.

    This dashboard looks at where water pressure is highest, how much renewable water is available,
    how much water is used for agriculture, and whether people have access to piped water.
    """ 
    
    )

st.markdown(
    """
    - **Water stress**: pressure on available freshwater resources.
    - **Renewable water resources**: natural renewable water available per person.
    - **Agricultural water withdrawal**: water taken from natural sources and used for farming.
    - **Piped water coverage**: access to piped improved water in rural and urban areas.
    """
    )




# sidebar filters
st.sidebar.header("Filters")

all_countries = sorted(data["REF_AREA_LABEL"].unique())
all_indicators = sorted(data["INDICATOR_LABEL"].unique())

country = st.sidebar.selectbox("Select country", all_countries)

selected_year = st.sidebar.selectbox(
    "Select year",
    year_cols,
    index=len(year_cols) - 1
    )

st.sidebar.markdown("---")
st.sidebar.subheader("Trend chart options")

trend_indicator = st.sidebar.selectbox(
    "Indicator for trend chart",
    all_indicators,
    format_func=lambda x: indicator_names.get(x, x))

compare_countries = st.sidebar.multiselect(
    "Compare with other countries (optional)",
    [c for c in all_countries if c != country],
    max_selections=4)

year_range = st.sidebar.slider(
    "Year range",
    min_value=2000,
    max_value=2022,
    value=(2000, 2022))

st.sidebar.markdown("---")
st.sidebar.subheader("Comparison chart options")

comp_indicator = st.sidebar.selectbox(
    "Indicator for country comparison",
    all_indicators,
    format_func=lambda x: indicator_names.get(x, x),
    key="comp_indicator" )

comp_order = st.sidebar.radio("Show countries with", ["Highest values", "Lowest values"])





st.markdown("---")





# key figures
st.subheader("Key figures for selected year")

ws = data[
    (data["INDICATOR_LABEL"] == "Water Stress (SDG 6.4.2)") &
    (data["URBANISATION_LABEL"].str.contains("Total", case=False, na=False))
    ][["REF_AREA_LABEL", selected_year]].dropna()

rw = data[
    (data["INDICATOR_LABEL"] == "Total renewable water resources per capita") &
    (data["URBANISATION_LABEL"].str.contains("Total", case=False, na=False))
    ][["REF_AREA_LABEL", selected_year]].dropna()

col1, col2 = st.columns(2)

with col1:
    if ws.empty:
        st.metric("Highest water stress", "No data")
    else:
        ws = ws.sort_values(by=selected_year, ascending=False)
        top_country = ws.iloc[0]["REF_AREA_LABEL"]
        top_value = round(ws.iloc[0][selected_year], 2)
        st.metric("Highest water stress", top_country, f"{top_value}%")

with col2:
    if rw.empty:
        st.metric("Lowest renewable water resources", "No data")
    else:
        rw = rw.sort_values(by=selected_year, ascending=True)
        low_country = rw.iloc[0]["REF_AREA_LABEL"]
        low_value = round(rw.iloc[0][selected_year], 2)
        st.metric(
            "Lowest renewable water resources",
            low_country,
            f"{low_value} m³/person" )





st.markdown("---")





# trend chart
st.subheader("Trend over time")

urb_options = data[
    (data["REF_AREA_LABEL"] == country) &
    (data["INDICATOR_LABEL"] == trend_indicator)
    ]["URBANISATION_LABEL"].unique()

if len(urb_options) == 0:
    st.write("No data available for this country and indicator.")

else:
    trend_urb = st.selectbox("Urbanisation category", sorted(urb_options))

    countries_to_plot =[country]+compare_countries

    start_year, end_year = year_range
    range_cols = [str(y) for y in range(start_year, end_year + 1)]

    fig, ax = plt.subplots(figsize=(9, 4))
    plotted_anything = False

    for c in countries_to_plot:
        row = data[
            (data["REF_AREA_LABEL"] == c) &
            (data["INDICATOR_LABEL"] == trend_indicator) &
            (data["URBANISATION_LABEL"] == trend_urb)]

        if row.empty:
            continue

        chart_data = row[range_cols].T.reset_index()
        chart_data.columns = ["Year", "Value"]
        chart_data["Year"] = chart_data["Year"].astype(int)
        chart_data = chart_data.dropna()

        if not chart_data.empty:
            ax.plot(chart_data["Year"], chart_data["Value"], marker="o", label=c)
            plotted_anything = True

    if not plotted_anything:
        st.write("No values available to plot for this selection.")
    else:
        trend_name = indicator_names.get(trend_indicator, trend_indicator)
        trend_unit = indicator_units.get(trend_indicator, "")

        ax.set_xlabel("Year")
        ax.set_ylabel(f"{trend_name} ({trend_unit})")
        ax.set_title(f"{trend_name} ({start_year}-{end_year})")
        ax.legend()
        style_axes(ax)

        plt.tight_layout()
        st.pyplot(fig)

        st.caption(
            "Use the sidebar to compare up to 4 other countries on the same chart, "
            "or to change the year range." )





st.markdown("---")





# country comparison
st.subheader("Country comparison")

comp_data = data[
    (data["INDICATOR_LABEL"] == comp_indicator) &
    (data["URBANISATION_LABEL"].str.contains("Total", case=False, na=False))
    ][["REF_AREA_LABEL", selected_year]].dropna()

if comp_data.empty:
    st.write("No comparison data available for this year.")
else:
    
    
    if comp_order == "Highest values":
        comp_data = comp_data.sort_values(by=selected_year, ascending=False).head(10)
    else:
        comp_data = comp_data.sort_values(by=selected_year, ascending=True).head(10)

    fig2, ax2 = plt.subplots(figsize=(9, 5))

    colours = ["#1f77b4" if c != country else "#ff7f0e" for c in comp_data["REF_AREA_LABEL"]]
    bars = ax2.barh(comp_data["REF_AREA_LABEL"], comp_data[selected_year], color=colours)

    for bar, value in zip(bars, comp_data[selected_year]):
        ax2.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" {round(value, 1)}",
            va="center",
            fontsize=9 )

    comp_name = indicator_names.get(comp_indicator,comp_indicator)
    comp_unit = indicator_units.get(comp_indicator, "")

    ax2.set_xlabel(f"{comp_name} ({comp_unit})")
    ax2.set_ylabel("Country")
    ax2.set_title(f"{comp_order} for {comp_name} in {selected_year}")
    ax2.invert_yaxis()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig2)

    st.caption(
        f"This chart compares countries for the selected indicator and year. "
        f"Your selected country ({country}) is highlighted in orange if it appears in the chart.")





st.markdown("---")





# rural vs urban chart
st.subheader("Rural vs urban piped water coverage")

st.write("This section compares rural and urban piped water supply coverage for the selected country and year.")

piped_indicator = "Total water supply coverage by piped improved facilities (%)"

access_data = data[
    (data["REF_AREA_LABEL"] == country) &
    (data["INDICATOR_LABEL"] == piped_indicator) &
    (
        data["URBANISATION_LABEL"].str.contains("Rural", case=False, na=False) |
        data["URBANISATION_LABEL"].str.contains("Urban", case=False, na=False) )
    ][["URBANISATION_LABEL", selected_year]].dropna()

if access_data.empty:
    st.write("No rural or urban piped water data available for this country and year.")
else:
    fig3, ax3 = plt.subplots(figsize=(6, 4))

    colours3 = ["#2ca02c" if "Rural" in label else "#1f77b4" for label in access_data["URBANISATION_LABEL"]]
    bars3 = ax3.bar(access_data["URBANISATION_LABEL"], access_data[selected_year], color=colours3)

    for bar, value in zip(bars3, access_data[selected_year]):
        ax3.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{round(value, 1)}%",
            ha="center",
            va="bottom",
            fontsize=10 )

    ax3.set_xlabel("Urbanisation category")
    ax3.set_ylabel("Piped water coverage (%)")
    ax3.set_title(f"{country} in {selected_year}")
    ax3.set_ylim(0, max(access_data[selected_year]) * 1.15)
    style_axes(ax3)

    plt.tight_layout()
    st.pyplot(fig3)

    st.caption("This chart shows whether piped water coverage differs between rural and urban areas.")

    if len(access_data) == 2:
        gap = access_data[selected_year].max() - access_data[selected_year].min()
        gap = round(gap, 2)
        st.write("Rural-urban access gap:", gap, "percentage points")
        
        
        
        
        
        
        
        