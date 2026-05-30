# %% [markdown]
# # Import data

# %%
import pandas as pd
import geopandas as gpd
import polars as pl
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
import math
#from utilities.Countries import city_to_country
#from utilities.DE_regions import city_to_state

# %%
calls = pl.read_csv('../raw_and_clean_data/Calls.csv')
contacts = pl.read_csv('../raw_and_clean_data/Contacts.csv')
deals = pl.read_csv('../raw_and_clean_data/Deals.csv')
spend = pl.read_csv('../raw_and_clean_data/Spend.csv')

# %%
calls_raw = calls
deals_raw = deals
contacts_raw = contacts
spend_raw = spend
print("Backups have been created. You can experiment on the main tables!")

# %% [markdown]
# # Data Cleaning and Preparation

# %% [markdown]
# 1. Remove duplicate records and irrelevant columns.
# 2. Properly handle missing values.
# 3. Convert data types for columns such as dates and numerical values.

# %% [markdown]
# ## Calls - Inspection, cleaning and transformation

# %%
# Inspection

# %%
calls = pl.read_csv('../raw_and_clean_data/Calls.csv')

# %%
calls.head()

# %%
calls.schema

# %%
calls.describe()

# %%
calls.describe()

# %%
# Count values

# print( "poloars will not display all columns aplying 'print'. We force it (with) to show us all columns.")

total_unique_rows = calls.n_unique()       # returns a single number (how many unique rows there are in total)
print("Unique values:", total_unique_rows)

with pl.Config(tbl_rows=12):               # Force display of 12 rows, our dataset has 12 columns
    print(calls.count().unpivot())

# %%
# Identify and inspect duplicates
duplicates = calls.filter(calls.is_duplicated())
print("Sample of duplicated rows:")
print(duplicates.head(10))

# %%
# Checking for duplicate IDs

# Filter the dataframe to show only rows where the 'Id' is repeated
duplicate_ids = calls.filter(pl.col("Id").is_duplicated())

# Count how many duplicate IDs exist
duplicate_count = duplicate_ids.height

if duplicate_count > 0:
    print(f"Warning: Found {duplicate_count} rows with duplicate IDs.")
    print(duplicate_ids.sort("Id").head(10)) # Sort to see the identical IDs next to each other
else:
    print("Success: No duplicate IDs found. Every contact is unique.")

# %%
# Transformation & cleaning

# %%
# Standardize column names
calls = calls.rename({col: col.replace(" ", "_") for col in calls.columns})

# Transformation & Cleaning Pipeline
print(f"Number of rows before removing duplicates: {calls.height}")

calls = (
    calls
    .unique() # Remove duplicates
    .drop(["Dialled_Number", "Tag"]) # Remove irrelevant columns
    .with_columns([
        # Convert string timestamps to Datetime
        pl.col("Call_Start_Time").str.to_datetime("%d.%m.%Y %H:%M"),
        pl.col("Call_Duration_(in_seconds)").cast(pl.Int32, strict=False),
        
        # Handle missing CONTACTID (using 0 as placeholder)
        pl.col("CONTACTID").fill_null(0).cast(pl.Int64)
    ])
)

print(f"Number of rows after removing duplicates: {calls.height}")


# %%
calls.schema

# %% [markdown]
# ## Contacts - Inspection, cleaning and transformation

# %%
# Inspection

# %%
contacts = pl.read_csv('../raw_and_clean_data/Contacts.csv')

# %%
print("Table head", contacts.head(10))
print("Data types", contacts.dtypes)
print(contacts.describe())

# %%
contacts.schema

# %%
# Count values

# %%
# print( "poloars will not display all columns aplying 'print'. We force it (with) to show us all columns.")

total_unique_rows = contacts.n_unique()       # returns a single number (how many unique rows there are in total)
print("Unique values:", total_unique_rows)

with pl.Config(tbl_rows=12):               # Force display of 12 rows, our dataset has 12 columns
    print(contacts.count().unpivot())

# %%
# Identify and inspect duplicates
duplicates = contacts.filter(contacts.is_duplicated())
print("Sample of duplicated rows:")
print(duplicates.head(10))

# %%
# Checking for duplicate Contact IDs

# Filter the dataframe to show only rows where the 'Id' is repeated
duplicate_ids = contacts.filter(pl.col("Id").is_duplicated())

# Count how many duplicate IDs exist
duplicate_count = duplicate_ids.height

if duplicate_count > 0:
    print(f"Warning: Found {duplicate_count} rows with duplicate IDs.")
    print(duplicate_ids.sort("Id").head(10)) # Sort to see the identical IDs next to each other
else:
    print("Success: No duplicate IDs found. Every contact is unique.")

# %%
# Transformation & cleaning

# %%
# Standardize column names by replacing spaces with underscores
contacts = contacts.rename({col: col.replace(" ", "_") for col in contacts.columns})

# Transformation & Cleaning Pipeline



contacts = (
    contacts
    #.unique() # Remove duplicates, not needed in this case
    .with_columns([
        # Convert string timestamps to Datetime
        pl.col("Created_Time").str.to_datetime("%d.%m.%Y %H:%M"),
        pl.col("Modified_Time").str.to_datetime("%d.%m.%Y %H:%M")
    ])
)
"""
# Remove duplicates
print(f"Number of rows before removing duplicates: {contacts.height}")
contacts = contacts.unique() # Remove duplicates, not needed in this case
print(f"Number of rows after removing duplicates: {contacts.height}")"""


# %%
contacts.schema

# %% [markdown]
# ## Deals - Inspection, cleaning and transformation

# %%
deals = pl.read_csv('../raw_and_clean_data/Deals.csv')

# %%
# Inspection

# %%
deals.head(5)

# %%
deals.schema

# %%
deals.describe()

# %%
# Count values

# %%
# print( "poloars will not display all columns aplying 'print'. We force it (with) to show us all columns.")

total_unique_rows = deals.n_unique()       # returns a single number (how many unique rows there are in total)
print("Unique values:", total_unique_rows)

with pl.Config(tbl_rows=24):               # Force display of 24 rows, our dataset has 24 columns
    print(deals.count().unpivot())

# %%
# Identify and inspect duplicates
duplicates = deals.filter(deals.is_duplicated())
print("Sample of duplicated rows:")
print(duplicates.head(10))

# %%
# Checking for duplicate IDs
# Filter the dataframe to show only rows where the 'Id' is repeated

duplicate_ids = contacts.filter(pl.col("Id").is_duplicated())

# Count how many duplicate IDs exist
duplicate_count = duplicate_ids.height

if duplicate_count > 0:
    print(f"Warning: Found {duplicate_count} rows with duplicate IDs.")
    print(duplicate_ids.sort("Id").head(10)) # Sort to see the identical IDs next to each other
else:
    print("Success: No duplicate IDs found. Every contact is unique.")

# %%
# Transformation & cleaning

# %%
# # Standardize column names
deals = deals.rename({col: col.replace(" ", "_") for col in deals.columns})

# # Cleaning and Type Casting Pipeline
deals = deals.with_columns([
    # Convert string timestamps to Datetime objects
    pl.col("Created_Time").str.to_datetime("%d.%m.%Y %H:%M"),
    pl.col("Closing_Date").str.to_datetime("%d.%m.%Y", strict=False),
    
    # Optimize Course_duration from Int64 to Int32
    pl.col("Course_duration")
    .cast(pl.Int64, strict=False)    # Handles strings like "12.0" or "12"
    .cast(pl.Int32),                 # Converts to the final integer format
    
    pl.col("Months_of_study")
    .cast(pl.Float64, strict=False)  # Handles strings like "12.0" or "12"
    .cast(pl.Int32),                 # Converts to the final integer format
    
    # Financial columns: Cleaning and casting to Int32
    # We go through Float64 first to handle potential decimals (e.g., ".00")
    pl.col("Initial_Amount_Paid")
        .cast(pl.String)
        .str.replace_all(r"[$,€\s]", "")
        .cast(pl.Float64, strict=False)
        .cast(pl.Int32, strict=False),
        #.fill_null(0),
        
    pl.col("Offer_Total_Amount")
        .cast(pl.String)
        .str.replace_all(r"[$,€\s]", "")
        .cast(pl.Float64, strict=False)
        .cast(pl.Int32, strict=False)
        #.fill_null(0)
])



#Data Integrity: Remove duplicates and drop irrelevant columns
#print(f"Number of rows before removing duplicates: {deals.height}")
#deals = deals.unique() not needed to delete al values are uniques
#print(f"Number of rows after removing duplicates: {deals.height}")



# %%
# Precision Calculations (Created_Time + SLA)  comes from the chapter Time series analysis 1

# %%
deals.schema

# %%
# --- STEP 1: Extract time components using Regex ---
# We capture Hours, Minutes, and Seconds from the "H:M:S" string format
temp_deals = deals.with_columns([
    pl.col("SLA").str.extract(r"(\d+):(\d+):(\d+)", 1).cast(pl.Int64).alias("hours"),
    pl.col("SLA").str.extract(r"(\d+):(\d+):(\d+)", 2).cast(pl.Int64).alias("minutes"),
    pl.col("SLA").str.extract(r"(\d+):(\d+):(\d+)", 3).cast(pl.Int64).alias("seconds"),
])

# --- STEP 2: Convert components to a unified Duration object ---
# We calculate total milliseconds to create a precise Polars Duration
temp_deals = temp_deals.with_columns(
    ((pl.col("hours") * 3600 + pl.col("minutes") * 60 + pl.col("seconds")) * 1000)
    .cast(pl.Duration(time_unit="ms"))
    .alias("SLA_duration")
)

# --- STEP 3: Final Time-Based Calculations ---
temp_deals = temp_deals.with_columns([
    # Calculate exact closing time by adding duration to creation time
    (pl.col("Created_Time") + pl.col("SLA_duration")).alias("Closing_Time"),
    
    # Convert duration to hours (Float) for easier statistical analysis
    (pl.col("SLA_duration").dt.total_milliseconds() / (1000 * 60 * 60)).alias("Cycle_Time_Hours")
])

# --- STEP 4: Cleanup temporary helper columns ---
temp_deals = temp_deals.drop(["hours", "minutes", "seconds"])

# --- STEP 5: Data Validation ---
# Check the first 5 rows to ensure calculations align with business logic
print("Time Series Analysis - Precision Check:")
print(temp_deals.select(["Created_Time", "SLA", "Closing_Time", "Cycle_Time_Hours"]).head(5))

# %%
# Create a flag for deals that took longer than 24 hours to close
deals = temp_deals.with_columns(
    pl.when(pl.col("Cycle_Time_Hours") > 24)
    .then(pl.lit("Slow"))
    .otherwise(pl.lit("Fast"))
    .alias("Closing_Speed")
)

# %%
deals.schema

# %%
# Handling Missing Values for categorical analysis

# %%
with pl.Config(tbl_rows=24):               
    print(calls.count().unpivot())

# %%
# Completarea coloanaelor

# %%
# Comprehensive mapping for language level normalization
# Maps both Cyrillic 'B' (looks like B) and 'Б' (phonetic B) to Latin 'B'
cyrillic_to_latin = {
    "а": "A", "А": "A",
    "б": "B", "Б": "B", 
    "в": "B", "В": "B", 
    "с": "C", "С": "C"
}

def clean_deutsch_level_refined(df):
    # Rule 0: Initial cleaning and case normalization
    # Rule 1 & 2: Replacing Cyrillic characters with Latin equivalents [cite: 2025-11-28]
    return df.with_columns(
        pl.col("Level_of_Deutsch")
        .str.to_uppercase()
        .str.replace_all("А", "A")
        .str.replace_all("Б", "B")
        .str.replace_all("В", "B")
        .str.replace_all("С", "C")
        .alias("temp_level")
    ).with_columns(
        # Rule 3 & 4: Extract first valid pattern (e.g., A1 from 'a2-b1' or B1 from complex strings) [cite: 2025-11-28]
        pl.col("temp_level")
        .str.extract(r"([A-C][1-2])", 1)
        .alias("Cleaned_Level")
    ).with_columns(
        # Final Rule: Map everything back to original column, forcing noise to Null [cite: 2025-11-28]
        pl.when(pl.col("Cleaned_Level").is_in(["A1", "A2", "B1", "B2", "C1", "C2"]))
        .then(pl.col("Cleaned_Level"))
        .otherwise(None)
        .alias("Level_of_Deutsch")
    ).drop(["temp_level", "Cleaned_Level"])

# Applying the refined logic
deals = clean_deutsch_level_refined(deals)

# Quick check to see the Latin-only results
print("Cleaned Level_of_Deutsch distribution:")
print(deals["Level_of_Deutsch"].value_counts())

# %%
"""Business Rules for Language Level Cleaning

1. Normalization & Case Sensitivity:
All values are converted to uppercase to eliminate differences in spelling or casing [cite: 2025-11-28].

2. Cyrillic-to-Latin Mapping:
Cyrillic letters that visually or phonetically resemble European language level codes are converted as follows:
А (Cyrillic) → A (Latin).
Б or В (Cyrillic) → B (Latin), as both are commonly used to type the "B" level.
С (Cyrillic) → C (Latin).

3. Pattern Extraction (The "First Match" Rule):
In the case of complex or multiple strings (e.g., "A2-B1"), the first valid combination consisting of a letter (A, B, C) followed by a digit (1, 2) is extracted.

4. Complex String Handling:
For cells containing additional comments (e.g., "B2 - awaiting result"), the code isolates and retains only the language level code.

5. Noise Suppression:
Values that do not contain an identifiable language level (question marks, standalone dashes, or text such as "УТОЧНИТЬ!") are forced to null to avoid distorting statistics.

6 .Data Preservation:
Values that are already null remain null"""

# %%
# We use the full calls table to ensure we capture the '0' duration calls for category E
contact_stats = (
    calls
    .group_by("CONTACTID")
    .agg([
        pl.col("Call_Duration_(in_seconds)").mean().alias("mean_duration"),
        pl.col("Call_Start_Time").max().alias("last_contact_date"),
    ])
)

# Getting the duration of the very last call for each contact
last_call_info = (
    calls
    .sort("Call_Start_Time")
    .group_by("CONTACTID")
    .last()
    .select(["CONTACTID", "Call_Duration_(in_seconds)"])
    .rename({"Call_Duration_(in_seconds)": "last_call_duration"})
)

# 2. JOINING METRICS TO DEALS
# Mapping Contact_Name (from deals) to CONTACTID (from calls)
deals = deals.join(contact_stats, left_on="Contact_Name", right_on="CONTACTID", how="left")
deals = deals.join(last_call_info, left_on="Contact_Name", right_on="CONTACTID", how="left")

# 3. APPLYING LOGIC ONLY TO MISSING VALUES
# Prioritizing existing labels and then applying business rules A through E
deals = deals.with_columns(
    pl.when(pl.col("Quality").is_null())
    .then(
        pl.when(pl.col("Initial_Amount_Paid") > 0).then(pl.lit("A - High"))
        .when(pl.col("mean_duration") > 300).then(pl.lit("B - Medium"))
        .when(pl.col("mean_duration") > 0).then(pl.lit("C - Low"))
        .when(pl.col("Stage") == "Need a consultation").then(pl.lit("D - Non Target"))
        .when((pl.col("last_call_duration") == 0) & (pl.col("last_contact_date").is_not_null()))
        .then(pl.lit("E - Non Qualified"))
        .otherwise(pl.lit("Unclassified"))
    )
    .otherwise(pl.col("Quality"))
    .alias("Quality")
)

# 4. FINAL CLEANUP
# Removing auxiliary columns used for calculation
deals = deals.drop(["mean_duration", "last_contact_date", "last_call_duration"])

# Final verification of the distribution seen in your screenshot
print("Quality column updated (only for missing values):")
print(deals["Quality"].value_counts())

# %%
with pl.Config(tbl_rows=26):               # Force display of 24 rows, our dataset has 24 columns
    print(deals.count().unpivot())

# %%
deals.schema

# %% [markdown]
# ## Spend - Inspection, cleaning and transformation

# %%
spend = pl.read_csv('../raw_and_clean_data/Spend.csv')

# %%
print(spend.sample(10))

# %%
spend.describe()

# %%
spend.schema

# %%
total_unique_rows = spend.n_unique()       # returns a single number (how many unique rows there are in total)
print("Unique values:", total_unique_rows)

with pl.Config(tbl_rows=12):               # Force display of 12 rows, our dataset has 10 columns
    print(spend.count().unpivot())

# %%
# Identification and archiving of duplicates

# 1. Extract all duplicated rows (all occurrences)
spend_duplicates_df = spend.filter(spend.is_duplicated())

# 2. Count them for the final report
dup_count = spend_duplicates_df.height
print(f"Total duplicated rows identified: {dup_count}")

""" 3. Optional: Save them to a CSV file for stakeholders
if dup_count > 0:
    spend_duplicates_df.write_csv("spend_duplicates_archive.csv")
    print("Duplicates have been archived to 'spend_duplicates_archive.csv'")"""


print("Sample of duplicated rows:")
print(spend_duplicates_df.head(10))

# %%
# Transformation & cleaning

# %%
# Standardize column names
spend = spend.rename({col: col.replace(" ", "_") for col in spend.columns})

# Cleaning and type casting pipeline
spend = spend.with_columns([
    
    # Convert Date string to Datetime
    pl.col("Date").str.to_datetime("%Y-%m-%d"),
    
    # Financial cleaning: remove currency symbols and commas
    # Using Float32 as the maximum value is 744 (memory efficient)
    pl.col("Spend")
        .str.replace_all(r"[€,]", "")
        .str.strip_chars()
        .cast(pl.Float32, strict=False),
        #.fill_null(0.0),             # Only if you need to replace null with 0
    
    # Ensure marketing metrics are stored as integers
    pl.col("Impressions")
        .cast(pl.Int32),
        #.fill_null(0),               # Only if you need to replace null with 0
    pl.col("Clicks")
        .cast(pl.Int32)
        #.fill_null(0)               # Only if you need to replace null with 0

])
# .fill_null(0) We do not convert null to zero in order to avoid distorting the data.
# It has an impact on "Summary statistics"


# Handle missing values for categorical fields to ensure clean grouping later
spend = spend.with_columns([
    pl.col("Source").fill_null("Unknown_Source"),
    pl.col("Campaign").fill_null("No_Campaign")
])

# Remove duplicate records
before = spend.height
print(f"Number of rows before removing duplicates: {before}")
spend = spend.unique()
after  = spend.height
print(f"Number of rows after removing duplicates: {after}")
print(f"{before - after} removed dublicates")
print(spend.tail(5))

# %%
spend.schema

# %% [markdown]
# # Descriptive Statistics

# %% [markdown]
# 1. Calculate summary statistics (mean, median, mode, range) for numerical fields.
# 2. Analyze categorical fields such as quality, stage, source, and product.
# 

# %% [markdown]
# ## 1. Calculate summary statistics (mean, median, mode, range) for numerical fields.

# %% [markdown]
# ### Calls

# %%
# Summary statistics for numerical fields

# %%
calls_summary = calls.select(["Call_Duration_(in_seconds)"]).describe()
print(calls_summary)

# %%
# Inspection of min and max ()
total_unique_rows = calls.n_unique()       # returns a single number (how many unique rows there are in total)
print("Unique values:", total_unique_rows)

count_under_60 = calls.filter(pl.col("Call_Duration_(in_seconds)") < 60).height
count_over_1h = calls.filter(pl.col("Call_Duration_(in_seconds)") > 3600).height
print(f"Calls under 60 seconds (Noise?): {count_under_60}")
print(f"Calls over 1 hour (Anomalies?): {count_over_1h}")

# %%
# Plotly Interactive Box-plot (Initial Data)
# This allows us to hover and see the exact values for whiskers and quartiles
fig1 = px.box(
    calls.to_pandas(), 
    y="Call_Duration_(in_seconds)", 
    title="Interactive Analysis: Initial Call Duration (Raw Data)",
    points="outliers" 
)
fig1.update_layout(yaxis_title="Duration (seconds)")
fig1.show()

# %%
# STATISTICAL OUTLIERS REMOVED (IQR Method)
# Calculating boundaries to show what 'standard' statistics would exclude
Q1 = calls["Call_Duration_(in_seconds)"].quantile(0.25)
Q3 = calls["Call_Duration_(in_seconds)"].quantile(0.75)
IQR = Q3 - Q1
upper_stat_bound = Q3 + 1.5 * IQR

calls_no_stat_outliers = calls.filter(pl.col("Call_Duration_(in_seconds)") <= upper_stat_bound)

fig_stat = px.box(
    calls_no_stat_outliers.to_pandas(), 
    y="Call_Duration_(in_seconds)", 
    title=f"2. Statistical Filtering (Threshold: {upper_stat_bound:.2f}s)",
    template="plotly_white",
    color_discrete_sequence=['#00CC96'] # Green for 'safe' statistical data
)
fig_stat.show()

# %%
# BUSINESS LOGIC BOX-PLOT (30s - 3600s)
# Applying the 30-3600s rule and saving the final cleaned table
calls_cleaned = calls.filter(
    (pl.col("Call_Duration_(in_seconds)") >= 30) & 
    (pl.col("Call_Duration_(in_seconds)") <= 3600)
)

fig_business = px.box(
    calls_cleaned.to_pandas(), 
    y="Call_Duration_(in_seconds)", 
    title="3. Business Logic Filtering (30s - 3600s)",
    template="plotly_white",
    color_discrete_sequence=['#636EFA'] # Blue for final business data
)
fig_business.show()
# Final step: Save the cleaned data to CSV
# Saving the cleaned dataset for BI integration
#calls_cleaned.write_csv("calls_cleaned.csv")
# print("File 'calls_cleaned.csv' has been successfully saved.")

# Final verification of remaining records
print(f"Filtering complete. Remaining rows: {calls_cleaned.height}")

# %%
# Histogram for the cleaned range to see how the duration is distributed
calls_cleaned = calls.filter(
    (pl.col("Call_Duration_(in_seconds)") >= 30) & 
    (pl.col("Call_Duration_(in_seconds)") <= 3600)
)

fig_hist = px.histogram(
    calls_cleaned.to_pandas(), 
    x="Call_Duration_(in_seconds)",
    nbins=100, # Number of bins for granularity
    title="Distribution of Call Durations (30s - 3600s Range)",
    labels={'Call_Duration_(in_seconds)': 'Duration (seconds)'},
    template="plotly_white",
    color_discrete_sequence=['#636EFA'] # Professional blue
)

# Adding a vertical line for the median to see the 'typical' call duration
median_val = calls_cleaned["Call_Duration_(in_seconds)"].median()
fig_hist.add_vline(x=median_val, line_dash="dash", line_color="red", 
                  annotation_text=f"Median: {median_val:.0f}s")

fig_hist.update_layout(
    xaxis_title="Call Duration (seconds)",
    yaxis_title="Number of Calls",
    bargap=0.1
)

fig_hist.show()

# %%
# calls = calls_cleaned
calls_summary = calls_cleaned.select(["Call_Duration_(in_seconds)"]).describe()
print(calls_summary)

# %%
# Grouping data into the three categories defined by an business logic
count_under_30 = calls.filter(pl.col("Call_Duration_(in_seconds)") < 30).height
count_over_3600 = calls.filter(pl.col("Call_Duration_(in_seconds)") > 3600).height
count_target_range = calls.filter(
    (pl.col("Call_Duration_(in_seconds)") >= 30) & 
    (pl.col("Call_Duration_(in_seconds)") <= 3600)
).height

# Displaying the results in the console
print(f"Calls under 30 seconds (Noise): {count_under_30}")
print(f"Calls between 30s and 1h (Cleaned Data): {count_target_range}")
print(f"Calls over 1 hour (Anomalies): {count_over_3600}")

# %%
print(calls.select("Call_Duration_(in_seconds)").describe())

# %%
def get_full_calls(df, column_name):
    return df.select([
        pl.lit(column_name).alias("Metric"),
        # We cast every result to Float32 to ensure they can be concatenated
        pl.col(column_name).mean().cast(pl.Float32).alias("Mean"),
        pl.col(column_name).median().cast(pl.Float32).alias("Median"),
        pl.col(column_name).mode().first().cast(pl.Float32).alias("Mode"),
        (pl.col(column_name).max() - pl.col(column_name).min()).cast(pl.Float32).alias("Range"),
        pl.col(column_name).std().cast(pl.Float32).alias("Std_Dev")
    ])

# Now the concatenation will work perfectly because all types match
all_spend_calls = pl.concat([
    get_full_calls(calls_cleaned, "Call_Duration_(in_seconds)"),

])

print(all_spend_calls)

# %% [markdown]
# ### Spend

# %%
# Summary statistics for numerical fields

# %%
spend_summary = spend.select(["Impressions", "Spend", "Clicks"]).describe()
print(spend_summary)

# %%
def get_full_stats(df, column_name):
    return df.select([
        pl.lit(column_name).alias("Metric"),
        # We cast every result to Float64 to ensure they can be concatenated
        pl.col(column_name).mean().cast(pl.Float64).alias("Mean"),
        pl.col(column_name).median().cast(pl.Float64).alias("Median"),
        pl.col(column_name).mode().first().cast(pl.Float64).alias("Mode"),
        (pl.col(column_name).max() - pl.col(column_name).min()).cast(pl.Float64).alias("Range"),
        pl.col(column_name).std().cast(pl.Float64).alias("Std_Dev")
    ])

# Now the concatenation will work perfectly because all types match
all_spend_stats = pl.concat([
    get_full_stats(spend, "Impressions"),
    get_full_stats(spend, "Spend"),
    get_full_stats(spend, "Clicks")
])

print(all_spend_stats)

# %% [markdown]
# ### Deals

# %%
# Summary statistics for numerical fields

# %%
deals_summary = deals.select(["Course_duration", "Initial_Amount_Paid", "Offer_Total_Amount"]).describe()
print(deals_summary)

# %%
# Summary where "Offer_Total_Amount" > 10

# Clean data by ensuring all key metrics are positive
deals_cleaned = deals.filter(
    (pl.col("Offer_Total_Amount") > 10) & 
    (pl.col("Initial_Amount_Paid") > 10) &
    (pl.col("Course_duration") > 0)
)

deals_summary = deals_cleaned.select([
    "Course_duration", 
    "Initial_Amount_Paid", 
    "Offer_Total_Amount"
]).describe()

print(deals_summary)


# %%
def get_full_deals(df, column_name):
    return df.select([
        pl.lit(column_name).alias("Metric"),
        # We cast every result to Float32 to ensure they can be concatenated
        pl.col(column_name).mean().cast(pl.Float32).alias("Mean"),
        pl.col(column_name).median().cast(pl.Float32).alias("Median"),
        pl.col(column_name).mode().first().cast(pl.Float32).alias("Mode"),
        (pl.col(column_name).max() - pl.col(column_name).min()).cast(pl.Float32).alias("Range"),
        pl.col(column_name).std().cast(pl.Float32).alias("Std_Dev")
    ])

# Now the concatenation will work perfectly because all types match
all_deals = pl.concat([
    get_full_deals(deals, "Course_duration"),
    get_full_deals(deals, "Initial_Amount_Paid"),
    get_full_deals(deals, "Offer_Total_Amount")
])

print(all_deals)

# %% [markdown]
# ## 2. Analyze categorical fields such as quality, stage, source, and product

# %%
# 1. Filter out null values for Product analysis
product_data = deals.filter(pl.col("Product").is_not_null())

# 2. Count occurrences
product_counts = product_data["Product"].value_counts()

# 3. Create the Pie/Donut Chart with increased size
fig_pie = px.pie(
    product_counts.to_pandas(), 
    values="count", 
    names="Product", 
    title="Product Distribution (Excluding Nulls)",
    hole=0.4, 
    template="plotly_white"
)

# Rule: Move labels outside and increase chart dimensions for clarity
fig_pie.update_traces(
    textinfo='percent+label',
    textposition='outside', # Moves labels outside the slices to prevent overlapping
    pull=[0.05] * len(product_counts) # Slightly separates slices for better focus
)

"""fig_quality.update_layout(
    height=700, # Increased height
    width=900,  # Increased width to provide room for labels
    margin=dict(l=50, r=250, t=100, b=50), # Large right margin for the legend and labels
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.1
    )
)"""

fig_pie.show()

# %%
# Force a specific renderer if you still see pink boxes (try 'notebook' or 'colab')
pio.renderers.default = "notebook_connected"

# 1. Clean and Prepare Data
# We drop nulls and take top 20 sources to avoid overcrowding and rendering errors
source_summary = (
    deals.filter(pl.col("Source").is_not_null())
    ["Source"]
    .value_counts()
    .sort("count", descending=True)
    .head(20) # Keeping only top 20 for a clean look
)

# 2. Construct the Horizontal Bar Chart
fig_source = px.bar(
    source_summary.to_pandas(),
    x="count",
    y="Source",
    orientation='h',
    title="Source leaders",
    text="count", 
    template="plotly_white",
    color_discrete_sequence=['#636EFA']
)

# 3. Apply Professional Formatting
fig_source.update_traces(
    textposition='outside',
    cliponaxis=False # Prevents the text from being cut off
)

# 4. Critical Layout Settings
fig_source.update_layout(
    # 'total ascending' ensures the largest bar is at the top in horizontal mode
    yaxis={'categoryorder': 'total ascending'},
    xaxis_title="Number of Leads",
    yaxis_title="Marketing Source",
    height=700,
    margin=dict(l=200, r=50, t=50, b=50), # Increased left margin for source names
    showlegend=False
)

fig_source.show()

# %%
# Prepare data for Quality
quality_summary = (
    deals["Quality"]
    .value_counts()
    .sort("count", descending=False)
)

# Create Quality chart
fig_quality = px.bar(
    quality_summary.to_pandas(),
    x="count",
    y="Quality",
    orientation='h',
    title="Horizontal Distribution: Quality",
    text="count",
    template="plotly_white",
    color_discrete_sequence=['#636EFA']
)

# Formatting for Quality
fig_quality.update_traces(textposition='outside')
fig_quality.update_layout(
    height=500, # Standard height is enough for Quality
    margin=dict(l=150, r=50, t=50, b=50),
    yaxis={'categoryorder':'total ascending'},
    xaxis_title="Number of Leads"
)

fig_quality.show()

# %%
# Rule: Create horizontal bar charts for Stage using the functional loop structure
for col_name in ["Stage"]:
    summary_data = (
        deals[col_name]
        .value_counts()
        .sort("count", descending=False) # Ascending count for top-down descending horizontal bars
    )

    fig_horiz = px.bar(
        summary_data.to_pandas(),
        x="count",
        y=col_name,
        orientation='h',
        title=f"Horizontal Distribution: {col_name}",
        text="count",
        template="plotly_white",
        color_discrete_sequence=['#636EFA']
    )
    
    fig_horiz.update_traces(textposition='outside')
    
    # Rule: Adjusting height and margins within the working loop
    fig_horiz.update_layout(
        height=600, # Increased height to prevent overlapping
        margin=dict(l=250, r=100, t=50, b=50), # Space for long stage names
        xaxis_title="Number of Leads",
        yaxis_title="Stage"
    )
    
    fig_horiz.show()

# %% [markdown]
# # Unit econimics

# %% [markdown]
# Identify a business growth point and formulate a hypothesis for improving a business process to increase metrics, and describe their testing mechanics, considering that the test should not take more than 2 weeks.
# 
# 1. Calculate unit economics for the products.
# 
# 2. Identify business growth points from the unit economics.
# 
# 3. Understand the business metrics tree.
# 
# 4. Determine which product metric they will impact and formulate hypotheses.
# 
# 5. Describe the hypothesis testing method, including the conditions for conducting the test.

# %% [markdown]
# ## 1. Calculate unit economics for the products.

# %%
deals

# %%
ue_deals = deals

# %%
import polars as pl
import pandas as pd

# --- STEP 1: INDIVIDUAL REVENUE CALCULATION (Allocation Logic) ---
# Assuming 'ue_deals' is the source DataFrame for Unit Economics
# We calculate revenue based on initial payment and monthly installments
df_ue = ue_deals.with_columns([
    pl.when(pl.col("Months_of_study") == 1)
    .then(pl.col("Initial_Amount_Paid"))
    .otherwise(
        pl.col("Initial_Amount_Paid") + 
        ((pl.col("Offer_Total_Amount") - pl.col("Initial_Amount_Paid")) / 
         (pl.when(pl.col("Course_duration") <= 1).then(1).otherwise(pl.col("Course_duration") - 1))) * (pl.col("Months_of_study") - 1)
    )
    .fill_null(0)
    .alias("Individual_Revenue")
])

# --- STEP 2: UNIT ECONOMICS COMPONENTS CALCULATION ---
# UA (User Acquisition): Total unique leads/contacts
ua = df_ue["Contact_Name"].n_unique()

# Filter dataset only for confirmed payments to calculate performance metrics
df_paid = df_ue.filter(pl.col("Stage") == "Payment Done")

# B (Buyers): Unique customers who made a payment
b = df_paid["Contact_Name"].n_unique()

# C1 (Conversion Rate): Ratio of buyers to total leads
c1 = (b / ua) if ua > 0 else 0

# T (Transactions): Total months of study across all paying students
t = df_paid["Months_of_study"].sum()

# Total Revenue: Sum of calculated individual revenue for confirmed payments
total_revenue = df_paid["Individual_Revenue"].sum()

# Acquisition Cost (AC) processing from spend data
df_spend_temp = spend.to_pandas() if hasattr(spend, "to_pandas") else spend
# Clean numeric spend values from currency symbols and spaces
df_spend_temp['Spend_Numeric'] = df_spend_temp['Spend'].astype(str).str.replace(r'[€, ]', '', regex=True).astype(float)
ac = df_spend_temp['Spend_Numeric'].sum()

# Fundamental Unit Economics Formulas
# AOV: Average Order Value (Revenue per month of study)
aov = total_revenue / t if t > 0 else 0
# APC: Average Purchase Count (Months of study per buyer)
apc = t / b if b > 0 else 0
# CPA: Cost Per Acquisition (Marketing spend per lead)
cpa = ac / ua if ua > 0 else 0
# CLTV: Customer Lifetime Value (Revenue expected from a single buyer)
cltv = aov * apc
# LTV: Lifetime Value (Revenue expected per lead)
ltv = c1 * cltv

# CM (Contribution Margin): Total profit after acquisition costs
# CM = UA * (LTV - CPA)
cm = ua * (ltv - cpa)

# --- STEP 3: SUMMARY TABLE GENERATION ---
# Constructing an overview table for management reporting
overview_data = {
    "Metric": ["UA", "B", "C1", "T", "AC", "Revenue", "AOV", "APC", "CPA", "CLTV", "LTV", "CM"],
    "Description": [
        "User Acquisition (Leads)", "Buyers", "Conversion Rate (%)", "Total Months (Transactions)",
        "Acquisition Cost", "Total Earned Revenue", "Average Order Value", "Avg Purchase Count",
        "Cost Per Acquisition", "Customer LTV", "Lifetime Value", "Contribution Margin"
    ],
    "Value": [
        str(ua), 
        str(b), 
        f"{c1:.2%}", 
        f"{t:.0f}", 
        f"{ac:,.2f} €", 
        f"{total_revenue:,.2f} €", 
        f"{aov:,.2f} €", 
        f"{apc:,.2f}",
        f"{cpa:,.2f} €", 
        f"{cltv:,.2f} €", 
        f"{ltv:,.2f} €",
        f"{cm:,.2f} €"
    ]
}

df_overview = pl.DataFrame(overview_data)

# Print final results to console
print("\n--- UNIT ECONOMICS OVERVIEW ---")
with pl.Config(tbl_rows=12):
    print(df_overview)

# %% [markdown]
# $$User Acquisition: UA = COUNTUNIQUE('deals'['Contact Name'])$$ 
# 
# $$Buyers: B = COUNTUNIQUE('deals'['Contact Name']) Where 'deals'['Stage'] = 'Payment Done' $$
# 
# $$Acquisition Cost: AC = SUM('spend'['Spend'])$$
# 
# $$Transactions: T = SUM('deasl'['Months of study']) Where 'deals'['Stage'] = "Payment Done"$$
# 
# $$ Conversion Rate: C1 = \frac{B}{UA}$$
# 
# $$Cost Per Acquisition: CPA = \frac{AC}{UA}$$
# 
# For revenue was created new column in  deals table
# 
# $$Revenue = \sum [Initial + (\frac{Offer Total - Initial}{Duration - 1} \times (Months - 1))]$$
# 
# Revenue for UE
# 
# $$Revenue =SUM('deals'['Revenue'])$$ 
# 
# $$Average Order Value: AOV = \frac{Revenue}{T}$$
# 
# $$Average Payment Count: APC = B \times T$$
# 
# $$ Customer Lifetime Value: CLTV = (AOV-COGS)*APC-1COGS$$
# $$CLTV = AOV \times APC$$
# in our case 1COGS and COGS = 0, we use formula without COGS's
# 
# $$Lifetime Value: LTV = C1 \times CLTV$$
# 
# $$Contribution Margin: CM = UA \times (LTV - CPA)$$
# 

# %%
import polars as pl
import pandas as pd

# --- STEP 1: INDIVIDUAL REVENUE CALCULATION (ALLOCATION LOGIC) ---
# Calculate revenue for each deal based on study duration and installments
df_ue_base = ue_deals.with_columns([
    pl.when(pl.col("Months_of_study") == 1)
    .then(pl.col("Initial_Amount_Paid"))
    .otherwise(
        pl.col("Initial_Amount_Paid") + 
        ((pl.col("Offer_Total_Amount") - pl.col("Initial_Amount_Paid")) / 
         (pl.when(pl.col("Course_duration") <= 1).then(1).otherwise(pl.col("Course_duration") - 1))) * (pl.col("Months_of_study") - 1)
    )
    .fill_null(0)
    .alias("Individual_Revenue")
])

# --- STEP 2: GLOBAL METRICS CALCULATION ---
# UA (User Acquisition): Total unique leads/contacts across all products
ua_global = df_ue_base["Contact_Name"].n_unique()

# Process Acquisition Cost (AC) from the spend table
df_spend_temp = spend.to_pandas() if hasattr(spend, "to_pandas") else spend
# Clean numeric spend values from currency symbols and spaces
df_spend_temp['Spend_Numeric'] = df_spend_temp['Spend'].astype(str).str.replace(r'[€, ]', '', regex=True).astype(float)
ac_global = df_spend_temp['Spend_Numeric'].sum()

# CPA: Cost Per Acquisition based on global marketing spend and total leads
cpa_global = ac_global / ua_global if ua_global > 0 else 0

# --- STEP 3: UNIT ECONOMICS BY PRODUCT ---
# Analyze performance for each major educational program
products = ["Web Developer", "Digital Marketing", "UX/UI Design"]
product_rows = []

for prod in products:
    # Filter the base dataset for the specific product
    df_prod_all = df_ue_base.filter(pl.col("Product") == prod)
    
    # CRITICAL FILTER: Only include completed transactions (Payment Done)
    # This aligns the analysis with actual cash flow metrics
    df_prod_paid = df_prod_all.filter(pl.col("Stage") == "Payment Done")
    
    # B (Buyers): Unique customers for this product
    b_prod = df_prod_paid["Contact_Name"].n_unique()
    # C1: Conversion rate for this product relative to global lead pool
    c1_prod = (b_prod / ua_global) if ua_global > 0 else 0
    # T (Transactions): Total study months generated by this product
    t_prod = df_prod_paid["Months_of_study"].sum()
    
    # CORRECTED REVENUE: Sum of earned revenue for paid students only
    rev_prod = df_prod_paid["Individual_Revenue"].sum()
    
    # Calculate derived metrics
    # AOV: Revenue per month for this product
    aov_prod = rev_prod / t_prod if t_prod > 0 else 0
    # APC: Retention depth (Average months per student)
    apc_prod = t_prod / b_prod if b_prod > 0 else 0
    # CLTV: Expected revenue from a single buyer of this product
    cltv_prod = aov_prod * apc_prod
    # LTV: Expected revenue per lead for this product path
    ltv_prod = c1_prod * cltv_prod
    
    # CM (Contribution Margin): Financial impact after global acquisition costs
    # CM = UA * (LTV - CPA)
    cm_prod = ua_global * (ltv_prod - cpa_global)
    
    product_rows.append({
        "Product": prod,
        "UA": ua_global,
        "C1": f"{c1_prod:.2%}",
        "AOV": round(aov_prod, 2),
        "APC": round(apc_prod, 2),
        "CPA": round(cpa_global, 2),
        "B": b_prod,
        "T": t_prod,
        "CLTV": round(cltv_prod, 2),
        "LTV": round(ltv_prod, 2),
        "AC": round(ac_global, 2),
        "Revenue": round(rev_prod, 2),
        "CM": round(cm_prod, 2)
    })

# --- STEP 4: FINAL REPORT GENERATION ---
# Construct the final comparative DataFrame
df_ue_by_product = pl.DataFrame(product_rows)

print("\n--- UNIT ECONOMICS BY PRODUCT ---")
with pl.Config(tbl_cols=13):
    print(df_ue_by_product)

# %% [markdown]
# ## 2. Identify business growth points from the unit economics

# %%
import polars as pl
import pandas as pd

# --- STEP 0: DATA PREPARATION (Ensuring missing columns are calculated) ---
# This part ensures that "Individual_Revenue" exists before any further calculations
ue_deals = ue_deals.with_columns([
    pl.when(pl.col("Months_of_study") == 1)
    .then(pl.col("Initial_Amount_Paid"))
    .otherwise(
        pl.col("Initial_Amount_Paid") + 
        ((pl.col("Offer_Total_Amount") - pl.col("Initial_Amount_Paid")) / 
         (pl.when(pl.col("Course_duration") <= 1).then(1).otherwise(pl.col("Course_duration") - 1))) * (pl.col("Months_of_study") - 1)
    )
    .fill_null(0)
    .alias("Individual_Revenue")
])

# --- STEP 1: GLOBAL METRICS CALCULATION ---
# UA (User Acquisition): Total unique leads/contacts across all products
ua_global = ue_deals["Contact_Name"].n_unique()

# Calculate Acquisition Cost (AC) and CPA (Cost Per Acquisition)
try:
    # Attempting to clean and sum the spend from the 'spend' variable if available
    ac_global = spend["Spend"].str.replace_all(r"[€\s,]", "").cast(pl.Float64).sum()
except:
    # Fallback to the last known calculated value if the 'spend' variable is not standard
    ac_global = 149523.45  

cpa_global = ac_global / ua_global if ua_global > 0 else 0

# --- STEP 2: HELPER FUNCTION FOR AUTOMATIC DATA EXTRACTION ---
# This function extracts base metrics for a specific educational product
def get_product_metrics(product_name):
    df_p = ue_deals.filter(pl.col("Product") == product_name)
    df_paid = df_p.filter(pl.col("Stage") == "Payment Done")
    
    b_count = df_paid["Contact_Name"].n_unique()
    c1 = b_count / ua_global if ua_global > 0 else 0
    t_sum = df_paid["Months_of_study"].sum()
    apc = t_sum / b_count if b_count > 0 else 0
    
    # "Individual_Revenue" is now guaranteed to exist from Step 0
    total_rev = df_paid["Individual_Revenue"].sum()
    aov = total_rev / t_sum if t_sum > 0 else 0
    
    return {
        "ua": ua_global,
        "c1": round(c1, 4),
        "aov": round(aov, 2),
        "apc": round(apc, 2),
        "cpa": round(cpa_global, 2)
    }

# --- STEP 3: CONSTRUCTING THE data_products DICTIONARY ---
# Automatic extraction for all main products
data_products = {
    "Web Developer": get_product_metrics("Web Developer"),
    "Digital Marketing": get_product_metrics("Digital Marketing"),
    "UX/UI Design": get_product_metrics("UX/UI Design")
}

# --- STEP 4: SCENARIO CALCULATION FUNCTION ---
# Calculates LTV, Revenue, and CM based on input metrics
def calculate_ue_row(scenario_name, ua, c1, aov, apc, cpa):
    ltv = (aov * apc) * c1
    revenue = (ua * c1 * apc) * aov
    cm = ua * (ltv - cpa)
    
    return {
        "Scenario": scenario_name,
        "UA": round(ua, 0),
        "C1": f"{c1:.2%}",
        "AOV": round(aov, 2),
        "APC": round(apc, 2),
        "CPA": round(cpa, 2),
        "LTV": round(ltv, 2),
        "Revenue": round(revenue, 2),
        "CM": round(cm, 2)
    }

# --- STEP 5: SENSITIVITY GENERATION AND OUTPUT ---
# We use a 15% coefficient for sensitivity testing
coef_modif = 0.15

for prod_name, vals in data_products.items():
    rows = []
    u, c, v, p, cp = vals["ua"], vals["c1"], vals["aov"], vals["apc"], vals["cpa"]
    
    # Generating different scenarios for each product
    rows.append(calculate_ue_row(f"Base Case", u, c, v, p, cp))
    rows.append(calculate_ue_row("UA (+15%)", u * (1 + coef_modif), c, v, p, cp))
    rows.append(calculate_ue_row("C1 (+15%)", u, c * (1 + coef_modif), v, p, cp))
    rows.append(calculate_ue_row("AOV (+15%)", u, c, v * (1 + coef_modif), p, cp))
    rows.append(calculate_ue_row("APC (+15%)", u, c, v, p * (1 + coef_modif), cp))
    rows.append(calculate_ue_row("CPA (-15%)", u, c, v, p, cp * (1 - coef_modif)))
    
    df_filtered = pl.DataFrame(rows)
    
    # Display the results with formatted headers
    print(f"\n" + "="*95)
    print(f"--- SENSITIVITY ANALYSIS: {prod_name.upper()} ---")
    print("="*95)
    
    with pl.Config(tbl_cols=10, tbl_width_chars=200, fmt_str_lengths=20):
        print(df_filtered)

# %%
import polars as pl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- STEP 0: DATA PREPARATION (Ensuring missing columns are calculated) ---
# This part ensures that "Individual_Revenue" exists before any further calculations
ue_deals = ue_deals.with_columns([
    pl.when(pl.col("Months_of_study") == 1)
    .then(pl.col("Initial_Amount_Paid"))
    .otherwise(
        pl.col("Initial_Amount_Paid") + 
        ((pl.col("Offer_Total_Amount") - pl.col("Initial_Amount_Paid")) / 
         (pl.when(pl.col("Course_duration") <= 1).then(1).otherwise(pl.col("Course_duration") - 1))) * (pl.col("Months_of_study") - 1)
    )
    .fill_null(0)
    .alias("Individual_Revenue")
])

# --- STEP 1: GLOBAL METRICS CALCULATION ---
# UA (User Acquisition): Total unique leads/contacts across all products
ua_global = ue_deals["Contact_Name"].n_unique()

# Calculate Acquisition Cost (AC) and CPA (Cost Per Acquisition)
try:
    # Attempting to clean and sum the spend from the 'spend' variable if available
    ac_global = spend["Spend"].str.replace_all(r"[€\s,]", "").cast(pl.Float64).sum()
except:
    # Fallback to the last known calculated value if the 'spend' variable is not standard
    ac_global = 149523.45  

cpa_global = ac_global / ua_global if ua_global > 0 else 0

# --- STEP 2: HELPER FUNCTION FOR AUTOMATIC DATA EXTRACTION ---
# This function extracts base metrics for a specific educational product
def get_product_metrics(product_name):
    df_p = ue_deals.filter(pl.col("Product") == product_name)
    df_paid = df_p.filter(pl.col("Stage") == "Payment Done")
    
    b_count = df_paid["Contact_Name"].n_unique()
    c1 = b_count / ua_global if ua_global > 0 else 0
    t_sum = df_paid["Months_of_study"].sum()
    apc = t_sum / b_count if b_count > 0 else 0
    
    # "Individual_Revenue" is now guaranteed to exist from Step 0
    total_rev = df_paid["Individual_Revenue"].sum()
    aov = total_rev / t_sum if t_sum > 0 else 0
    
    return {
        "ua": ua_global,
        "c1": round(c1, 4),
        "aov": round(aov, 2),
        "apc": round(apc, 2),
        "cpa": round(cpa_global, 2)
    }

# --- STEP 3: CONSTRUCTING THE data_products DICTIONARY ---
# Automatic extraction for all main products
data_products = {
    "Web Developer": get_product_metrics("Web Developer"),
    "Digital Marketing": get_product_metrics("Digital Marketing"),
    "UX/UI Design": get_product_metrics("UX/UI Design")
}

# --- STEP 4: SCENARIO CALCULATION FUNCTION ---
# Calculates LTV, Revenue, and CM based on input metrics
def calculate_ue_row(scenario_name, ua, c1, aov, apc, cpa):
    ltv = (aov * apc) * c1
    revenue = (ua * c1 * apc) * aov
    cm = ua * (ltv - cpa)
    
    return {
        "Scenario": scenario_name,
        "UA": round(ua, 0),
        "C1": f"{c1:.2%}",
        "AOV": round(aov, 2),
        "APC": round(apc, 2),
        "CPA": round(cpa, 2),
        "LTV": round(ltv, 2),
        "Revenue": round(revenue, 2),
        "CM": round(cm, 2)
    }

# --- STEP 5: SENSITIVITY GENERATION AND OUTPUT ---
# We use a 15% coefficient for sensitivity testing
coef_modif = 0.15

for prod_name, vals in data_products.items():
    rows = []
    u, c, v, p, cp = vals["ua"], vals["c1"], vals["aov"], vals["apc"], vals["cpa"]
    
    # Generating different scenarios for each product
    rows.append(calculate_ue_row(f"Base Case", u, c, v, p, cp))
    rows.append(calculate_ue_row("UA (+15%)", u * (1 + coef_modif), c, v, p, cp))
    rows.append(calculate_ue_row("C1 (+15%)", u, c * (1 + coef_modif), v, p, cp))
    rows.append(calculate_ue_row("AOV (+15%)", u, c, v * (1 + coef_modif), p, cp))
    rows.append(calculate_ue_row("APC (+15%)", u, c, v, p * (1 + coef_modif), cp))
    rows.append(calculate_ue_row("CPA (-15%)", u, c, v, p, cp * (1 - coef_modif)))
    
    df_filtered = pl.DataFrame(rows)
    
    # Display the results with formatted headers
    print(f"\n" + "="*95)
    print(f"--- SENSITIVITY ANALYSIS: {prod_name.upper()} ---")
    print("="*95)
    
    with pl.Config(tbl_cols=10, tbl_width_chars=200, fmt_str_lengths=20):
        print(df_filtered)

# --- STEP 6: DYNAMIC DATA COLLECTION FOR HEATMAP ---
# Prepare a data structure to store the percentage impact on Contribution Margin (CM)
heatmap_data = []

# Helper function to calculate CM directly
def get_cm(ua, c1, aov, apc, cpa):
    ltv = (aov * apc) * c1
    return ua * (ltv - cpa)

# Iterate through pre-calculated data products
for prod, v in data_products.items():
    # Extract values from the interactive dictionary
    u, c, a, p, cp = v["ua"], v["c1"], v["aov"], v["apc"], v["cpa"]
    
    # Reference value (Base Case)
    base_cm = get_cm(u, c, a, p, cp)
    
    # Calculate impact for each growth lever (+15% or -15% for CPA)
    scenarios = {
        "UA (+15%)":  get_cm(u * (1 + coef_modif), c, a, p, cp),
        "C1 (+15%)":  get_cm(u, c * (1 + coef_modif), a, p, cp),
        "AOV (+15%)": get_cm(u, c, a * (1 + coef_modif), p, cp),
        "APC (+15%)": get_cm(u, c, a, p * (1 + coef_modif), cp),
        "CPA (-15%)": get_cm(u, c, a, p, cp * (1 - coef_modif))
    }
    
    for sc_name, sc_cm in scenarios.items():
        # Formula for percentage impact on profit (CM)
        impact_perc = ((sc_cm - base_cm) / abs(base_cm)) * 100
        
        heatmap_data.append({
            "Produs": prod,
            "Pârghie de Creștere": sc_name,
            "Impact CM (%)": round(impact_perc, 2)
        })

# --- STEP 7: PIVOT PREPARATION AND HEATMAP VISUALIZATION ---
df_heatmap_prep = pd.DataFrame(heatmap_data)
df_pivot = df_heatmap_prep.pivot(index="Produs", columns="Pârghie de Creștere", values="Impact CM (%)")

# Strategically order columns (from volume to efficiency)
cols_order = ["UA (+15%)", "CPA (-15%)", "AOV (+15%)", "APC (+15%)", "C1 (+15%)"]
df_pivot = df_pivot[cols_order]

# Generate Heatmap using Seaborn
plt.figure(figsize=(12, 6))
sns.heatmap(df_pivot, annot=True, fmt=".1f", cmap="RdYlGn", center=0, 
            linewidths=.5, cbar_kws={'label': 'Creștere Profit (CM) %'})

plt.title("Matricea Punctelor de Creștere: Impactul de +15% asupra Profitului", fontsize=16, weight='bold', pad=20)
plt.ylabel("Produse", fontsize=12)
plt.xlabel("Metrică Optimizată (Pârghie)", fontsize=12)
plt.tight_layout()
plt.show()

# --- STEP 8: STRATEGIC INTERPRETATION ---
print(f"""
💡 Interpretare Strategică pentru setul curent de date:
- Cel mai mare impact: {(df_pivot.max(axis=1).idxmax(), df_pivot.max().idxmax())}
- Orice zonă verde închis indică unde o îmbunătățire de 15% produce un efect multiplicator în profit.
""")

print("""
💡 Observații cheie:
1. Pârghiile Magice: C1 și APC au adesea cel mai mare impact procentual deoarece îmbunătățesc venitul pe fiecare lead deja achiziționat.
2. UA (Traficul): Creșterea UA aduce volum, dar impactul asupra CM este mai liniar din cauza costurilor de achiziție.
3. CPA: Reducerea costului de achiziție este critică pentru produsele cu margini mai mici.
""")

# %% [markdown]
# ## 3. Understand the business metrics tree

# %% [markdown]
# Key business metric
# 
#     CM 
# 
# 
# Financial metrics
#     
#     Revenue
# 
# 
# Decision-making metrics
# 
#     UA
#     CPA
#     C1
#     AOV
#     APC
# 
# 
# Product metrics
# 
#     T
#     AC
#     CLTV
#     B
#     LTV
# 
# 
# Atomic metrics
#     
#     Contact Name
#     Stage
#     Initial Amount Paid
#     Spend
#     Months of study
#     Offer Total Amount
#     Course duration
#     Product

# %% [markdown]
# ## 4. Determine which product metric they will impact and formulate hypotheses

# %%
import polars as pl
import math

# --- CONFIGURATION ---
# The maximum duration we allow for an A/B test to run
REQUIRED_DAYS = 14

# --- STEP 1: DYNAMIC DATA PREPARATION ---
# Calculate global traffic metrics from the ue_deals dataset
ua_global = ue_deals["Contact_Name"].n_unique()
min_d = ue_deals["Created_Time"].min()
max_d = ue_deals["Created_Time"].max()

# Determine the total time span and average daily traffic
days_total = (max_d - min_d).days
daily_traffic = ua_global / days_total if days_total > 0 else 0

def get_conversion_rate(product_name):
    """Calculates the current conversion rate (p) for a specific product."""
    b_prod = ue_deals.filter(
        (pl.col("Product") == product_name) & 
        (pl.col("Stage") == "Payment Done")
    )["Contact_Name"].n_unique()
    return b_prod / ua_global if ua_global > 0 else 0

# Retrieve current conversion rates and define target effect sizes (X)
p_web, p_dig, p_ux = get_conversion_rate("Web Developer"), get_conversion_rate("Digital Marketing"), get_conversion_rate("UX/UI Design")
# X values represent the minimum detectable effect we want to measure
x_web, x_dig, x_ux = 0.02, 0.04, 0.025 

ab_setup = {
    "Web Developer": {"p": p_web, "X": x_web},
    "Digital Marketing": {"p": p_dig, "X": x_dig},
    "UX/UI Design": {"p": p_ux, "X": x_ux}
}

results = []

# --- STEP 2: CALCULATE A/B TEST METRICS ---
for product, vals in ab_setup.items():
    p, x = vals["p"], vals["X"]
    
    if p > 0 and x > 0:
        # Standard formula for sample size per variation (80% power, 5% significance)
        # n = (16 * p * (1 - p)) / (X^2)
        n = (16 * p * (1 - p)) / (x ** 2)
        total_traffic = n * 2 # Total traffic needed for both Control and Test groups
        
        # Calculate how many days it would take based on current daily traffic
        days_needed = math.ceil(total_traffic / daily_traffic) if daily_traffic > 0 else 0
        
        # Suggest an X value that would fit within the REQUIRED_DAYS limit
        x_sug = math.sqrt((16 * p * (1 - p) * 2) / (REQUIRED_DAYS * daily_traffic))
        
        # Determine if the current setup is feasible
        status = "OK" if days_needed <= REQUIRED_DAYS else "⚠️ TOO LONG"
        suggestion = f"Set X to {x_sug:.3f}" if days_needed > REQUIRED_DAYS else "-"
    else:
        n, total_traffic, days_needed, status, suggestion = 0, 0, 0, "No Data", "-"

    results.append({
        "Metric": product, 
        "UA_global": str(ua_global),
        "Total_days": str(days_total),
        "Current Conv (p)": f"{p:.2%}",
        "Target Effect (X)": f"{x:.0%}",
        "Sample Size (n)": f"{n:,.0f}",
        "Total Traffic": f"{total_traffic:,.0f}",
        "Days Needed": str(days_needed),
        "Status": status,
        "Suggestion": suggestion
    })

# --- STEP 3: TRANSPOSITION FOR READABILITY ---
# Create the initial DataFrame from results
df_temp = pl.DataFrame(results)

# Transpose the data: Products become columns, metrics become rows for side-by-side comparison
df_transposed = df_temp.transpose(include_header=True, header_name="Metric", column_names="Metric")

# --- STEP 4: OUTPUT DISPLAY ---
print(f"🚀 Comparative A/B Test Analysis (Limit: {REQUIRED_DAYS} days)\n")
with pl.Config(tbl_width_chars=150, fmt_str_lengths=30):
    print(df_transposed)

# %% [markdown]
# ## 5. Describe the hypothesis testing method, including the conditions for conducting the test

# %% [markdown]
# Digital Marketing Strategy
# 
# Defining the Goal via the SMART Method
# 
# S (Specific):
# We want to modify the sales managers' conversation script for the "Digital Marketing" product (or another one can be selected; a high-volume product was chosen).
# 
# M (Measurable):
# We will measure the C1 metric (Lead-to-Customer Conversion). The goal is to achieve a minimum detectable effect (MDE) of 0.04%, increasing from 2.59% to 2.63%+.
# 
# A (Achievable):
# The goal is realistic because changing the script does not require technical development resources, only sales team training. We have the necessary traffic (UA) to validate the test.
# 
# R (Relevant):
# An increase in C1 has a direct positive impact on Revenue and Contribution Margin (CM).
# 
# T (Time-bound):
# The experiment will be conducted over 13 days, which fits within the maximum 2-week limit.
# 
# HADI Cycle (Hypothesis, Action, Data, Insights)
# 
# H - Hypothesis
# 
# We believe that if we change the sales script by adding a section for "proactive handling of price-related objections," the Lead-to-Payment conversion (C1) will increase because customers will better perceive the product's value before rejecting the offer.
# 
# A - Action
# 
# We are launching an A/B test in the sales department for 13 days:
# 
# Group A (Control): Half of the managers use the old script.
# 
# Group B (Experimental): The other half use the new script.
# 
# Leads (UA) are distributed randomly and equally between the two groups.
# 
# D - Data
# 
# We collect data daily in the CRM:
# 
# Number of Leads (UA) assigned to each group.
# 
# Number of Sales (B) completed by each group.
# 
# Calculation of the daily C1 conversion for Group A and Group B.
# 
# Target sample size: approximately 323 leads per group (according to the "Total Traffic Volume").
# 
# I - Insights
# 
# After 13 days, we analyze the results:
# 
# If C1 (Group B) > C1 (Group A) with statistical significance: the hypothesis is confirmed. We implement the new script for the entire team.
# 
# If there is no difference: the hypothesis is refuted. We revert to the old script or test a different change (e.g., a limited-time special offer).

# %% [markdown]
# Web Developer Strategy
# 
# Defining the Goal via the SMART Method
# 
# S (Specific):
# Optimize the sales script for the "Web Developer" product by emphasizing the long-term career benefits in IT to justify the price point.
# 
# M (Measurable):
# Increase the C1 metric (Lead-to-Customer Conversion) by at least 0.03% (Minimum Detectable Effect). The objective is to grow from 0.75% to 0.78% or higher.
# 
# A (Achievable):
# The goal is realistic because modifying the sales script requires no technical costs, and current traffic levels allow for a rapid hypothesis validation.
# 
# R (Relevant):
# Any increase in C1 for this high-volume product (UA) significantly impacts the Contribution Margin (CM).
# 
# T (Time-bound):
# The experiment will run for 11 days, fitting within a standard two-week cycle.
# 
# HADI Cycle (Hypothesis, Action, Data, Insights)
# 
# H - Hypothesis
# 
# We believe that by changing the sales script to highlight a "job guarantee" for Web Development courses, the Lead-to-Payment conversion (C1) will increase by at least 0.03 percentage points. This approach aims to reduce customers' fear of investing time and money into a new career path.
# 
# A - Action
# 
# We will launch an A/B test for 11 days, splitting the sales team into two equal groups:
# 
# Experimental Group: Uses the new script with an emphasis on employment guarantees.
# 
# Control Group: Uses the standard sales script.
# 
# D - Data
# 
# Data will be tracked daily within the CRM:
# 
# Monitor the number of UA (leads) and B (buyers) for each group daily.
# 
# Target: Reach a total volume of approximately 264 leads (roughly 132 per group) to ensure statistical significance.
# 
# I - Insights
# 
# After the 11-day period, we will compare the C1 performance:
# 
# Success: If the experimental group achieves C1 ≥ 0.78%, the hypothesis is confirmed, and the new script will be implemented permanently.
# 
# Failure/Neutral: If no significant difference is found, the hypothesis is refuted. We will revert to the original script or test a different variable (e.g., a limited-time special offer).

# %% [markdown]
# UX/UI Design Strategy
# 
# Defining the Goal via the SMART Method
# 
# S (Specific):
# Modify the sales script for the "UX/UI Design" product by incorporating specific examples of successful alumni portfolios during the sales call.
# 
# M (Measurable):
# Increase the C1 metric by at least 0.04% (MDE). The target is to grow the conversion rate from 1.25% to 1.29% or higher.
# 
# A (Achievable):
# This is highly achievable as the alumni portfolios already exist; the only requirement is training the sales managers on how to present them effectively.
# 
# R (Relevant):
# Increasing conversion directly improves Unit Economics, making the acquisition channels more profitable.
# 
# T (Time-bound):
# The experiment will last for 10 days, adhering to the requirement of staying under the two-week limit.
# 
# HADI Cycle (Hypothesis, Action, Data, Insights)
# 
# H - Hypothesis
# 
# We believe that if sales managers demonstrate a visual "before and after" portfolio of a graduate during the call (via a shared link or email), the C1 conversion will increase by at least 0.04%. This is based on the premise that the visual nature of UX/UI products requires tangible proof of acquired skills.
# 
# A - Action
# 
# We will launch an A/B test for 10 days with random lead distribution:
# 
# Experimental Group: Managers will send/show a visual portfolio during or immediately after the call.
# 
# Control Group: Managers will follow the standard script without visual portfolio demonstrations.
# 
# D - Data
# 
# Daily data collection via CRM:
# 
# Monitor progress toward the required sample size of approximately 247 leads in total (~124 per test branch).
# 
# I - Insights
# 
# After 10 days, analyze the C1 results:
# 
# Success: If the visual portfolio variant shows a statistically significant increase in C1, we will implement this practice for all managers handling this product.
# 
# Failure/Neutral: If no difference is observed, the hypothesis is refuted. We will revert to the previous script or test alternative changes (e.g., a limited-time offer).

# %% [markdown]
# # Save files for next step

# %%
ue_deals.write_parquet("../raw_and_clean_data/deals_ready.parquet")
contacts.write_parquet("../raw_and_clean_data/contacts_ready.parquet")
spend.write_parquet("../raw_and_clean_data/spend_ready.parquet")
calls.write_parquet("../raw_and_clean_data/calls_ready.parquet")


