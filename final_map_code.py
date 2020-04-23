# Make sure these libraries are installed
# !conda install branca
# !conda install -c conda-forge folium
# pip install geocoder

#########################################################

# from IPython.display import IFrame
# documentation = IFrame(src='https://python-visualization.github.io/folium/', width=500, height=300)
# display(documentation)

# import the necessary packages
import folium
import folium.plugins
import pandas as pd
import requests
from folium import *
import datetime
import seaborn as sns

# create map object
folium.Map()

# change up the location and zoom_start to find the proper location
m = folium.Map(location=[42.3484, -83.0777], zoom_start=15, tiles='openstreetmap', width=1500, height=700, control_scale=True)
folium.TileLayer('stamen toner').add_to(m)
folium.TileLayer('stamen terrain').add_to(m)
m.save('final_map.html')

# read in the raw data
conditions = pd.read_csv('datasets/residential_condition.csv')
conditions.head(1)
conditions.groupby(['condition']).size()


# To return more accurate coordinates, we need to append zipcode, city and state the ending to the addresses
conditions["Address"] = conditions["Address"] + " Detroit, MI 48201"
# conditions.head(3)


# create new columns so that for loop works properly
conditions['lat'] = 0
conditions['lng'] = 0

# Get latitude and longitude of addresses using Google Maps API
url = 'https://maps.googleapis.com/maps/api/geocode/json'
api_key = 'AIzaSyD4JECdDVlDrDtxY241OddCX1CxvYznoqo'
for i in range(len(conditions)):
    params = {'address': conditions.iloc[i]['Address'], 'key': api_key}
    r = requests.get(url, params=params)
    results = r.json()['results']
    coordinate = results[0]['geometry']['location']
    conditions.loc[i,'lat'] = coordinate['lat']
    conditions.loc[i,'lng'] = coordinate['lng']

#  Write compiled coordinates to new csv to speed up code running
conditions.to_csv("datasets/residential_condition_coor.csv", index=False)


# HOUSING CONDITION
conditions_new = pd.read_csv('datasets/residential_condition_coor.csv')

# Next Step: go through the rows in the data frame and add a marker at each location

# Create groups for different housing conditions
condition_layer = folium.FeatureGroup(name="1) Housing Condition Layer")
m.add_child(condition_layer)

good_group = folium.plugins.FeatureGroupSubGroup(condition_layer,'Condition: Good (Green)')
fair_group = folium.plugins.FeatureGroupSubGroup(condition_layer,'Condition: Fair (Orange)')
poor_group = folium.plugins.FeatureGroupSubGroup(condition_layer,'Condition: Poor (Red)')
other_group = folium.plugins.FeatureGroupSubGroup(condition_layer,'Condition: Suggest Demolition (Black)')

# Looping through each row to add a marker at each location
for i in range(len(conditions_new)):
    if conditions_new.iloc[i]['condition'] == 'good':
        good_group.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=conditions_new.iloc[i]['Address'], tooltip='click', icon=folium.Icon(icon='home', color='green')))
    elif conditions_new.iloc[i]['condition'] == 'fair':
        fair_group.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=conditions_new.iloc[i]['Address'], tooltip='click', icon=folium.Icon(icon='home', color='orange')))
    elif conditions_new.iloc[i]['condition'] == 'poor':
        poor_group.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=conditions_new.iloc[i]['Address'], tooltip='click', icon=folium.Icon(icon='home', color='red')))
    else:
        other_group.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=conditions_new.iloc[i]['Address'], tooltip='click', icon=folium.Icon(icon='home', color='black')))

# add the groups to the map
m.add_child(good_group)
m.add_child(fair_group)
m.add_child(poor_group)
m.add_child(other_group)


# PROPERTY TYPES
# 4 types - column: (occupancy) : unoccupied, partial, occupied, maybe
# or column (units): 1 unit, 2-3 units, 4+ units, single, apartments, multi, garage


type_layer = folium.FeatureGroup(name="2) Type of Housing Layer", show=False)
m.add_child(type_layer)
apartment = folium.plugins.FeatureGroupSubGroup(type_layer, name='Type: Apartment (Light Blue)') #apartments
single = folium.plugins.FeatureGroupSubGroup(type_layer, name='Type: Single (Blue)') # 1 unit, or single
multiunit = folium.plugins.FeatureGroupSubGroup(type_layer, name='Type: Multi-unit (Dark Blue)') #multi, 2-3 units, 4+ units

for i in range(len(conditions_new)):
    if conditions_new.iloc[i]['units'] == 'apartments':
        apartment.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=[conditions_new.iloc[i]['Address'], conditions_new.iloc[i]['units']], tooltip='click', icon=folium.Icon(icon='home', color='lightblue')))
    elif (conditions_new.iloc[i]['units'] == '1 unit') | (conditions_new.iloc[i]['units'] == 'single'):
        single.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=[conditions_new.iloc[i]['Address'], conditions_new.iloc[i]['units']], tooltip='click', icon=folium.Icon(icon='home', color='blue')))
    elif (conditions_new.iloc[i]['units'] == 'multi') | (conditions_new.iloc[i]['units'] == '2-3 units') | (conditions_new.iloc[i]['units'] == '4+ units'):
        multiunit.add_child(Marker([conditions_new.iloc[i]['lat'], conditions_new.iloc[i]['lng']],
        popup=[conditions_new.iloc[i]['Address'], conditions_new.iloc[i]['units']], tooltip='click', icon=folium.Icon(icon='home', color='darkblue')))


m.add_child(apartment)
m.add_child(single)
m.add_child(multiunit)

# LENGTH OF OWNERSHIP
# Data from two sources: Property Sales and Parcels
CURRENT_YEAR = 2020
data = pd.read_csv('datasets/Property_Sales.csv')
data.columns

# Extract year from sale date
data['year'] = pd.DatetimeIndex(data['sale_date']).year
data['ownership_length'] = CURRENT_YEAR - pd.DatetimeIndex(data['sale_date']).year
data.head(1)


data2 = pd.read_csv('datasets/residential_condition.csv')
# Filter properties within Woodbridge by comparing with residential_condition dataset
add_list = data2['Address'].tolist()
add_list_upper = [x.upper() for x in add_list]

clean_data = data[data['address'].isin(add_list_upper)]
clean_data.to_csv('datasets/propertysales_cleaned.csv', index=False)

clean_data_new = pd.read_csv('datasets/propertysales_cleaned.csv')
clean_data_new.head(1)
clean_data_new.rename(columns={'X': 'lng', 'Y': 'lat'}, inplace=True)
clean_data_new = clean_data_new[pd.notnull(clean_data_new['lng'])]

# Create groups of markers for different ownership lengths
length_layer = folium.FeatureGroup(name="3) Length of Ownership Layer", show=False)
m.add_child(length_layer)
# Buckets: <1 year, 1-5 years, 5-10 years, 10-20 years, >20 years
thisyear = folium.plugins.FeatureGroupSubGroup(length_layer, name='Length: <1 year (Light Red)')
pastfive = folium.plugins.FeatureGroupSubGroup(length_layer, name='Length: 1-5 years (Pink)')
fiveten = folium.plugins.FeatureGroupSubGroup(length_layer, name='Length: 6-10 years (Purple)')
tentwenty = folium.plugins.FeatureGroupSubGroup(length_layer, name='Length: 11-20 years (Dark Purple)')
greater = folium.plugins.FeatureGroupSubGroup(length_layer, name='Length: >20 years (Dark Red)') # Data set only goes to 2010

# looping through each row to add a marker at each location
for i in range(len(clean_data_new)):
    if clean_data_new.iloc[i]['year'] == CURRENT_YEAR:
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new.iloc[i]['address'], clean_data_new.iloc[i]['ownership_length'], clean_data_new.iloc[i]['grantee'])
        thisyear.add_child(Marker([clean_data_new.iloc[i]['lat'], clean_data_new.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='lightred')))
    elif (clean_data_new.iloc[i]['ownership_length'] >= 1) &  (clean_data_new.iloc[i]['ownership_length'] < 5):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new.iloc[i]['address'], clean_data_new.iloc[i]['ownership_length'], clean_data_new.iloc[i]['grantee'])
        pastfive.add_child(Marker([clean_data_new.iloc[i]['lat'], clean_data_new.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='pink')))
    elif (clean_data_new.iloc[i]['ownership_length'] >= 5) &  (clean_data_new.iloc[i]['ownership_length'] < 10):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new.iloc[i]['address'], clean_data_new.iloc[i]['ownership_length'], clean_data_new.iloc[i]['grantee'])
        fiveten.add_child(Marker([clean_data_new.iloc[i]['lat'], clean_data_new.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='purple')))
    elif (clean_data_new.iloc[i]['ownership_length'] >= 10) &  (clean_data_new.iloc[i]['ownership_length'] <= 20):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new.iloc[i]['address'], clean_data_new.iloc[i]['ownership_length'], clean_data_new.iloc[i]['grantee'])
        tentwenty.add_child(Marker([clean_data_new.iloc[i]['lat'], clean_data_new.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='darkpurple')))
    elif (clean_data_new.iloc[i]['ownership_length'] > 20):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new.iloc[i]['address'], clean_data_new.iloc[i]['ownership_length'], clean_data_new.iloc[i]['grantee'])
        greater.add_child(Marker([clean_data_new.iloc[i]['lat'], clean_data_new.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='darkred')))


parcels = pd.read_csv('datasets/Parcels.csv')
# Convert sale date from string to datetime format
parcels['SALE_DATE'] = pd.to_datetime(parcels['SALE_DATE'],errors='coerce')
parcels['SALE_DATE']
parcels['year'] = pd.DatetimeIndex(parcels['SALE_DATE']).year
parcels['ownership_length'] = CURRENT_YEAR - parcels['year']

# Filter Parcels dataset by Woodbridge zipcodes
woodbridge_filter = parcels[(parcels['ZIP_CODE'] == "48201") | (parcels['ZIP_CODE'] == "48208")]
woodbridge_filter = woodbridge_filter[woodbridge_filter['SALE_DATE'].notna()]
woodbridge_filter['ownership_length'] = woodbridge_filter['ownership_length'].astype(int)
woodbridge_filter.to_csv('datasets/parcels_matched.csv', index=False)


clean_parcels = pd.read_csv('datasets/parcels_matched.csv')

# Remove overlap in addresses already in Property Sales dataset
housing = clean_parcels[clean_parcels['ADDRESS'].isin(add_list_upper)]
add_list_2 = clean_data_new['address'].tolist()
housing_not_in = housing[-housing['ADDRESS'].isin(add_list_2)]

housing_not_in.to_csv('datasets/parcels_matched.csv', index=False)


# Get latitude and longitude of new addresses using Google Maps API
housing_new = pd.read_csv('datasets/parcels_matched.csv')
housing_new['ZIP_CODE'] = housing_new['ZIP_CODE'].astype(str)
housing_new['ADDRESS'] = housing_new["ADDRESS"] + " DETROIT, MI " + housing_new['ZIP_CODE']
housing_new['lat'] = 0
housing_new['lng'] = 0
url = 'https://maps.googleapis.com/maps/api/geocode/json'
api_key = 'AIzaSyD4JECdDVlDrDtxY241OddCX1CxvYznoqo'
for i in range(len(housing_new)):
    params = {'address': housing_new.iloc[i]['ADDRESS'], 'key': api_key}
    r = requests.get(url, params=params)
    results = r.json()['results']
    coordinate = results[0]['geometry']['location']
    housing_new.loc[i,'lat'] = coordinate['lat']
    housing_new.loc[i,'lng'] = coordinate['lng']


housing_new.to_csv('datasets/parcels_matched.csv', index=False)


clean_data_new2 = pd.read_csv('datasets/parcels_matched.csv')

# Add additional markers to the ownership length groups
for i in range(len(clean_data_new2)):
    if clean_data_new2.iloc[i]['year'] == CURRENT_YEAR:
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new2.iloc[i]['ADDRESS'], clean_data_new2.iloc[i]['ownership_length'], clean_data_new2.iloc[i]['OWNER1'])
        thisyear.add_child(Marker([clean_data_new2.iloc[i]['lat'], clean_data_new2.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='lightred')))
    elif (clean_data_new2.iloc[i]['ownership_length'] >= 1) &  (clean_data_new2.iloc[i]['ownership_length'] < 5):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new2.iloc[i]['ADDRESS'], clean_data_new2.iloc[i]['ownership_length'], clean_data_new2.iloc[i]['OWNER1'])
        pastfive.add_child(Marker([clean_data_new2.iloc[i]['lat'], clean_data_new2.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='pink')))
    elif (clean_data_new2.iloc[i]['ownership_length'] >= 5) &  (clean_data_new2.iloc[i]['ownership_length'] < 10):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new2.iloc[i]['ADDRESS'], clean_data_new2.iloc[i]['ownership_length'], clean_data_new2.iloc[i]['OWNER1'])
        fiveten.add_child(Marker([clean_data_new2.iloc[i]['lat'], clean_data_new2.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='purple')))
    elif (clean_data_new2.iloc[i]['ownership_length'] >= 10) &  (clean_data_new2.iloc[i]['ownership_length'] <= 20):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new2.iloc[i]['ADDRESS'], clean_data_new2.iloc[i]['ownership_length'], clean_data_new2.iloc[i]['OWNER1'])
        tentwenty.add_child(Marker([clean_data_new2.iloc[i]['lat'], clean_data_new2.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='darkpurple')))
    elif (clean_data_new2.iloc[i]['ownership_length'] > 20):
        string = 'Address: {}, No. of years owned: {}, Owner: {}'.format(clean_data_new2.iloc[i]['ADDRESS'], clean_data_new2.iloc[i]['ownership_length'], clean_data_new2.iloc[i]['OWNER1'])
        greater.add_child(Marker([clean_data_new2.iloc[i]['lat'], clean_data_new2.iloc[i]['lng']],
        popup=string, tooltip='click', icon=folium.Icon(icon='home', color='darkred')))


m.add_child(thisyear)
m.add_child(pastfive)
m.add_child(fiveten)
m.add_child(tentwenty)
m.add_child(greater)
m.add_child(folium.map.LayerControl())


# ADDITIONAL FEATURES
fullsc = folium.plugins.Fullscreen(
    position='topleft',
    title='Expand me',
    title_cancel='Exit me',
    force_separate_button=True
)
m.add_child(fullsc)

# finally save map as html file
m
m.save('final_map.html')


# TREND VISUALIZATION
graph_data = pd.read_csv('datasets/propertysales_cleaned.csv')

count = graph_data.groupby(['year']).size()
ax = sns.barplot(x=count.index, y=count.values)
ax.set(xlabel="Year", ylabel="Number of properties sold")
for p in ax.patches:
    ax.annotate("%.f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
    ha='center', va='center', fontsize=11, xytext=(0, 20),
    textcoords='offset points')

fig = ax.get_figure()
fig.savefig('num_properties_sold_trend.png')
