```python
# Import the libraries
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import contextily as ctx
import rasterio
```


```python
# Parameters
output_file = "potential_sites.gpkg"
green_penalty_weight = 0.4
church_penalty_weight = 0.2
noise_penalty_weight = 0.3
senior_penalty_weight = 0.1
```


```python
# Hard constraints
min_plot_area = 3500 #sqm
max_plot_area = 7500 #sqm
min_shape_index = 0.6
max_distance_to_road = 10 #m
```


```python
# Read the data
plots = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/2261_dzialki_egib_wfs_gml.gml")
buildings = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/2261_budynki_egib_wfs_gml.gml")
roads = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/2261_ulice_egib_wfs_gml.gml")
local_plans = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/ZbiorAPP_MPZP_Gdansk.gml", layer="AktPlanowaniaPrzestrzennego")
churches = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/churches.gpkg")
green_areas = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/green_areas.gpkg")
noise_map = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/noise/noise_map.gpkg")
neighborhoods = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/rejony_transportowe.gpkg")
city_boundary = gpd.read_file("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/city_boundary2180.gpkg")

city_boundary.to_crs("EPSG:2177", inplace=True)
plots.set_crs("EPSG:2177", inplace=True)
```

    /Users/michaldeja/Documents/GitHub/archestra/venv/lib/python3.12/site-packages/pyogrio/raw.py:198: UserWarning: Measured (M) geometry types are not supported. Original type 'Measured 3D MultiPolygon' is converted to 'MultiPolygon Z'
      return ogr_read(
    /Users/michaldeja/Documents/GitHub/archestra/venv/lib/python3.12/site-packages/pyogrio/raw.py:198: UserWarning: Measured (M) geometry types are not supported. Original type 'Measured 3D MultiPolygon' is converted to 'MultiPolygon Z'
      return ogr_read(





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>gml_id</th>
      <th>coordinates</th>
      <th>ID_DZIALKI</th>
      <th>NUMER_DZIALKI</th>
      <th>NAZWA_OBREBU</th>
      <th>NUMER_OBREBU</th>
      <th>NUMER_JEDNOSTKI</th>
      <th>NAZWA_GMINY</th>
      <th>GRUPA_REJESTROWA</th>
      <th>DATA</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>dzialki.446690</td>
      <td>6539425.910000,6028445.960000 6539485.590000,6...</td>
      <td>226101_1.0042.652/12</td>
      <td>652/12</td>
      <td>042</td>
      <td>42</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6539485.59 6028457.91, 6539485.34 60...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>dzialki.404111</td>
      <td>6540330.740000,6028934.900000 6540338.040000,6...</td>
      <td>226101_1.0043.159/6</td>
      <td>159/6</td>
      <td>043</td>
      <td>43</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6540338.04 6028950.66, 6540331.69 60...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>dzialki.527661</td>
      <td>6531808.490000,6028335.660000 6531866.710000,6...</td>
      <td>226101_1.0003.412</td>
      <td>412</td>
      <td>Klukowo</td>
      <td>3</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6531866.71 6028385.32, 6531823.47 60...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>dzialki.529749</td>
      <td>6538886.610000,6022524.810000 6539095.060000,6...</td>
      <td>226101_1.0075.138/193</td>
      <td>138/193</td>
      <td>Ujeścisko</td>
      <td>75</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6539095.06 6022574.89, 6539071.08 60...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>dzialki.505284</td>
      <td>6558026.700000,6023183.330000 6558170.880000,6...</td>
      <td>226101_1.0141.117/36</td>
      <td>117/36</td>
      <td>Komary</td>
      <td>141</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6558055.86 6023220.3, 6558027.7 6023...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>92155</th>
      <td>dzialki.448952</td>
      <td>6538585.330000,6024643.180000 6538604.240000,6...</td>
      <td>226101_1.0064.704/1</td>
      <td>704/1</td>
      <td>064</td>
      <td>64</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>1</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6538604.24 6024646.82, 6538585.33 60...</td>
    </tr>
    <tr>
      <th>92156</th>
      <td>dzialki.306264</td>
      <td>6536285.160000,6027558.090000 6536292.560000,6...</td>
      <td>226101_1.0028.380</td>
      <td>380</td>
      <td>028</td>
      <td>28</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>1</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6536292.56 6027558.39, 6536292.4 602...</td>
    </tr>
    <tr>
      <th>92157</th>
      <td>dzialki.494343</td>
      <td>6536258.810000,6022259.150000 6536263.830000,6...</td>
      <td>226101_1.0048.182/1</td>
      <td>182/1</td>
      <td>Szadółki</td>
      <td>48</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6536263.83 6022299.05, 6536259.3 602...</td>
    </tr>
    <tr>
      <th>92158</th>
      <td>dzialki.46783</td>
      <td>6537537.690000,6028852.570000 6537545.050000,6...</td>
      <td>226101_1.0030.21/3</td>
      <td>21/3</td>
      <td>030</td>
      <td>30</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>1</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6537545.05 6028852.57, 6537540.98 60...</td>
    </tr>
    <tr>
      <th>92159</th>
      <td>dzialki.516361</td>
      <td>6530214.140000,6032825.060000 6530244.490000,6...</td>
      <td>226101_1.0001.1640</td>
      <td>1640</td>
      <td>Osowa</td>
      <td>1</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>POLYGON ((6530214.14 6032837.1, 6530232.59 603...</td>
    </tr>
  </tbody>
</table>
<p>92160 rows × 11 columns</p>
</div>



## Filter the plots according to the hard constraints



```python
# Area constraint
print(f"Total number of plots: {len(plots)}")
plots["area"] = plots.area
sized_plots = plots[(plots["area"] > min_plot_area) & (plots["area"] < max_plot_area)]
print(f"Plots after size filtering: {len(sized_plots)}")

# Regular shape constraint
def calculate_shape_index(geometry):
    area = geometry.area
    perimeter = geometry.length
    return 4 * np.pi * area / (perimeter ** 2)

sized_plots['shape_index'] = sized_plots['geometry'].apply(calculate_shape_index)
shaped_plots = sized_plots[sized_plots['shape_index'] > min_shape_index]
print(f"Plots after shape filtering: {len(shaped_plots)}")

# No local plan constraint
area_with_local_plan = local_plans.dissolve(by="przestrzenNazw")
plots_with_plans = gpd.sjoin(
    shaped_plots, 
    area_with_local_plan, 
    how='inner'
)

shaped_plots_without_plan = shaped_plots[~shaped_plots.index.isin(plots_with_plans.index)]
print(f"Plots after local plan filtering: {len(shaped_plots_without_plan)}")
# No residential buildings constraint
residential_buildings = buildings[buildings['RODZAJ'] == 'm']


# Find plots that intersect with residential buildings
plots_with_buildings = gpd.sjoin(
    shaped_plots_without_plan,
    residential_buildings,
    how='inner'
)

# Keep only plots that didn't match any residential buildings
empty_plots_without_plan = shaped_plots_without_plan[
    ~shaped_plots_without_plan.index.isin(plots_with_buildings.dropna().index)
]

print(f"Plots after residential buildings filtering: {len(empty_plots_without_plan)}")

road_plots = gpd.sjoin(plots, roads, how='inner', predicate='intersects', rsuffix='road')


potential_sites = gpd.sjoin(empty_plots_without_plan, road_plots, how='inner', predicate='touches')
potential_sites = potential_sites.drop_duplicates(subset='gml_id')
print(f"Plots after public road accessibility filtering: {len(potential_sites)}")

# Save the potential sites to a file
potential_sites.to_file(output_file)
print(f"Potential sites saved to {output_file}")
```

    Total number of plots: 92160
    Plots after size filtering: 23416
    Plots after shape filtering: 10708


    /Users/michaldeja/Documents/GitHub/archestra/venv/lib/python3.12/site-packages/geopandas/geodataframe.py:1819: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      super().__setitem__(key, value)


    Plots after local plan filtering: 2237
    Plots after residential buildings filtering: 1330
    Plots after public road accessibility filtering: 797
    Potential sites saved to potential_sites.gpkg


## Calculate the metrics for retirement home location


```python
def normalize(series):
    # For metrics where lower is better (like noise, distance)
    normalized = (series - series.min()) / (series.max() - series.min())
    return normalized

def compute_distance_to_nearest_target(centroid, target_gdf):
    distances = [centroid.distance(target_geom) for target_geom in target_gdf.geometry.values]
    return round(min(distances))
potential_sites
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>gml_id</th>
      <th>coordinates</th>
      <th>ID_DZIALKI_left</th>
      <th>NUMER_DZIALKI_left</th>
      <th>NAZWA_OBREBU_left</th>
      <th>NUMER_OBREBU_left</th>
      <th>NUMER_JEDNOSTKI_left</th>
      <th>NAZWA_GMINY_left</th>
      <th>GRUPA_REJESTROWA_left</th>
      <th>DATA_left</th>
      <th>...</th>
      <th>gml_id_road</th>
      <th>coordinates_road</th>
      <th>nazwa_gminy</th>
      <th>id_gminy</th>
      <th>nazwa_miejscowosci</th>
      <th>id_miejscowosci</th>
      <th>nazwa_ulicy</th>
      <th>id_ulicy</th>
      <th>data_uchwaly</th>
      <th>nr_uchwaly</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>60</th>
      <td>dzialki.451949</td>
      <td>6542223.180000,6021527.400000 6542331.360000,6...</td>
      <td>226101_1.0125.50/2</td>
      <td>50/2</td>
      <td>125</td>
      <td>125</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.329bc416-e781-4370-b509-91a98306c065</td>
      <td>6542290.510000,6021349.490000 6542443.210000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Poleska</td>
      <td>16989</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>952</th>
      <td>dzialki.259792</td>
      <td>6536704.370000,6023719.910000 6536754.540000,6...</td>
      <td>226101_1.0049.150/98</td>
      <td>150/98</td>
      <td>Jasień</td>
      <td>49</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>8</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.4f1b22f2-848e-4c93-8948-7faea5140143</td>
      <td>6536427.170000,6023442.050000 6536760.880000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Pólnicy</td>
      <td>17414</td>
      <td>1992-11-24 00:00:00</td>
      <td>LV/395/92</td>
    </tr>
    <tr>
      <th>958</th>
      <td>dzialki.278865</td>
      <td>6529806.740000,6025214.970000 6529883.730000,6...</td>
      <td>226101_1.0035.155/34</td>
      <td>155/34</td>
      <td>Kokoszki</td>
      <td>35</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.ea671efc-1ae3-4fb1-aa2f-7fdd32fcead7</td>
      <td>6529821.840000,6025216.110000 6530070.640000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Czaplewska</td>
      <td>39595</td>
      <td>2007-05-31 00:00:00</td>
      <td>X/216/07</td>
    </tr>
    <tr>
      <th>1201</th>
      <td>dzialki.516978</td>
      <td>6540461.540000,6028907.100000 6540521.070000,6...</td>
      <td>226101_1.0044.454</td>
      <td>454</td>
      <td>044</td>
      <td>44</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>5</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.a92114c4-aaf0-42ac-8246-0e83795459ef</td>
      <td>6540412.910000,6027520.180000 6541283.260000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Mikołaja Reja</td>
      <td>18565</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1273</th>
      <td>dzialki.246429</td>
      <td>6532201.450000,6023636.540000 6532264.560000,6...</td>
      <td>226101_1.0036.174/9</td>
      <td>174/9</td>
      <td>Kiełpino Górne</td>
      <td>36</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.320bfbe7-e7b1-444d-9bfc-ed61fe672c2a</td>
      <td>6532024.180000,6023205.030000 6532391.610000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Bieszkowicka</td>
      <td>44990</td>
      <td>2012-11-29 00:00:00</td>
      <td>XXXII/665/12</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>91591</th>
      <td>dzialki.354964</td>
      <td>6540500.700000,6026739.460000 6540659.900000,6...</td>
      <td>226101_1.0055.627</td>
      <td>627</td>
      <td>055</td>
      <td>55</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>5</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.9b2ead2c-dac0-4c56-a8f9-731307fcb3e6</td>
      <td>6539450.930000,6026483.030000 6540940.670000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Romualda Traugutta</td>
      <td>22965</td>
      <td>1953-11-06 00:00:00</td>
      <td>23/53</td>
    </tr>
    <tr>
      <th>91717</th>
      <td>dzialki.303714</td>
      <td>6541345.390000,6016258.650000 6541386.690000,6...</td>
      <td>226101_1.0313.38</td>
      <td>38</td>
      <td>313S</td>
      <td>313</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.ae69628e-7d2b-44d6-b8fd-65029520ea4d</td>
      <td>6541048.960000,6016342.370000 6541633.830000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Batalionów Chłopskich</td>
      <td>868</td>
      <td>1954-02-24 00:00:00</td>
      <td>Bez numeru</td>
    </tr>
    <tr>
      <th>91720</th>
      <td>dzialki.278193</td>
      <td>6545561.440000,6020910.210000 6545658.720000,6...</td>
      <td>226101_1.0129.115/2</td>
      <td>115/2</td>
      <td>129</td>
      <td>129</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.b8fb9f14-2703-4545-a205-be10ec2dd51a</td>
      <td>6542187.660000,6020642.960000 6545984.860000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Olszyńska</td>
      <td>15027</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>91900</th>
      <td>dzialki.385380</td>
      <td>6529366.120000,6025193.280000 6529423.610000,6...</td>
      <td>226101_1.0024.505/21</td>
      <td>505/21</td>
      <td>Bysewo</td>
      <td>24</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.49263419-c027-41f2-9d95-0f15f845c7a4</td>
      <td>6529162.530000,6025144.630000 6529863.720000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Grzybowa</td>
      <td>6341</td>
      <td>1977-04-19 00:00:00</td>
      <td>XIX/49/77</td>
    </tr>
    <tr>
      <th>91907</th>
      <td>dzialki.492213</td>
      <td>6540327.580000,6026396.910000 6540408.270000,6...</td>
      <td>226101_1.0066.1/26</td>
      <td>1/26</td>
      <td>066</td>
      <td>66</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>3</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>ulice.af5aa6e2-cfea-4101-a0ff-5db83d21229b</td>
      <td>6540713.460000,6026009.730000 6540962.390000,6...</td>
      <td>Gdańsk</td>
      <td>226101_1</td>
      <td>Gdańsk</td>
      <td>933016</td>
      <td>Dębinki</td>
      <td>3799</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
<p>797 rows × 36 columns</p>
</div>




```python
potential_sites['centroid'] = potential_sites.centroid


potential_sites["distance_to_nearest_church"] = potential_sites.apply(
    lambda row: compute_distance_to_nearest_target(
        row['centroid'], 
        churches
    ),
    axis=1
)

potential_sites["church_penalty"] = normalize(potential_sites["distance_to_nearest_church"])

```


```python
potential_sites["distance_to_nearest_green"] = potential_sites.apply(
    lambda row: compute_distance_to_nearest_target(
        row['centroid'],
        green_areas
    ),
    axis=1
)

potential_sites["green_penalty"] = normalize(potential_sites["distance_to_nearest_green"])

```


```python
# Calculate noise level at each potential site using polygon intersection
# First get all intersecting noise polygons for each site
intersections = gpd.sjoin(
    potential_sites[['geometry']],
    noise_map[['geometry', 'min_noise']],
    predicate='intersects'
)
# Group by the index from potential_sites and take the mean noise level
mean_noise = intersections.groupby(level=0)['min_noise'].mean()
potential_sites["noise_level"] = mean_noise

# Replace NaN values in noise_level with 50 dB
potential_sites["noise_level"] = potential_sites["noise_level"].fillna(50)

potential_sites["noise_penalty"] = normalize(np.log(potential_sites["noise_level"]))
```


```python
# Calculate senior density at each potential site
# Open the raster file
with rasterio.open("/Users/michaldeja/Documents/GitHub/archestra/data/GIS/old_heatmap.tif") as src:
    # Get the raster values at each centroid
    potential_sites['senior_density'] = [
        round(list(src.sample([(geom.x, geom.y)]))[0][0], 1)
        for geom in potential_sites['centroid']
    ]

potential_sites["senior_penalty"] = 1 - normalize(potential_sites["senior_density"])
```


```python
# Calculate a combined score for each site
potential_sites['combined_score'] = (
    potential_sites['green_penalty'] * green_penalty_weight + 
    potential_sites['church_penalty'] * church_penalty_weight +
    potential_sites['noise_penalty'] * noise_penalty_weight +
    potential_sites['senior_penalty'] * senior_penalty_weight
)

best_sites = potential_sites.nsmallest(9, 'combined_score').copy()
best_sites
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>gml_id</th>
      <th>coordinates</th>
      <th>ID_DZIALKI_left</th>
      <th>NUMER_DZIALKI_left</th>
      <th>NAZWA_OBREBU_left</th>
      <th>NUMER_OBREBU_left</th>
      <th>NUMER_JEDNOSTKI_left</th>
      <th>NAZWA_GMINY_left</th>
      <th>GRUPA_REJESTROWA_left</th>
      <th>DATA_left</th>
      <th>...</th>
      <th>centroid</th>
      <th>distance_to_nearest_church</th>
      <th>church_penalty</th>
      <th>distance_to_nearest_green</th>
      <th>green_penalty</th>
      <th>noise_level</th>
      <th>noise_penalty</th>
      <th>senior_density</th>
      <th>senior_penalty</th>
      <th>combined_score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>33489</th>
      <td>dzialki.32856</td>
      <td>6538177.370000,6032213.550000 6538217.490000,6...</td>
      <td>226101_1.0015.342</td>
      <td>342</td>
      <td>015</td>
      <td>15</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>2</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6538198.23 6032237.824)</td>
      <td>664</td>
      <td>0.181743</td>
      <td>15</td>
      <td>0.009091</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>39.400002</td>
      <td>0.255198</td>
      <td>0.065505</td>
    </tr>
    <tr>
      <th>55603</th>
      <td>dzialki.490123</td>
      <td>6536098.100000,6023717.530000 6536155.140000,6...</td>
      <td>226101_1.0049.222/4</td>
      <td>222/4</td>
      <td>Jasień</td>
      <td>49</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6536127.117 6023732.469)</td>
      <td>351</td>
      <td>0.095422</td>
      <td>14</td>
      <td>0.008485</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>23.900000</td>
      <td>0.548204</td>
      <td>0.077299</td>
    </tr>
    <tr>
      <th>41637</th>
      <td>dzialki.244196</td>
      <td>6540350.200000,6021508.890000 6540451.900000,6...</td>
      <td>226101_1.0303.737/4</td>
      <td>737/4</td>
      <td>303S</td>
      <td>303</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6540403.908 6021533.123)</td>
      <td>423</td>
      <td>0.115279</td>
      <td>0</td>
      <td>0.000000</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>21.600000</td>
      <td>0.591682</td>
      <td>0.082224</td>
    </tr>
    <tr>
      <th>20528</th>
      <td>dzialki.386962</td>
      <td>6540365.890000,6021482.360000 6540451.650000,6...</td>
      <td>226101_1.0303.738/1</td>
      <td>738/1</td>
      <td>303S</td>
      <td>303</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6540413.914 6021498.631)</td>
      <td>459</td>
      <td>0.125207</td>
      <td>0</td>
      <td>0.000000</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>21.000000</td>
      <td>0.603025</td>
      <td>0.085344</td>
    </tr>
    <tr>
      <th>31470</th>
      <td>dzialki.227138</td>
      <td>6537262.970000,6025209.860000 6537377.790000,6...</td>
      <td>226101_1.0052.89</td>
      <td>89</td>
      <td>052</td>
      <td>52</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6537320.365 6025239.318)</td>
      <td>545</td>
      <td>0.148924</td>
      <td>102</td>
      <td>0.061818</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>35.900002</td>
      <td>0.321361</td>
      <td>0.086648</td>
    </tr>
    <tr>
      <th>91480</th>
      <td>dzialki.307675</td>
      <td>6539387.390000,6026753.080000 6539448.540000,6...</td>
      <td>226101_1.0054.198</td>
      <td>198</td>
      <td>054</td>
      <td>54</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6539412.223 6026783.062)</td>
      <td>502</td>
      <td>0.137066</td>
      <td>24</td>
      <td>0.014545</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>24.400000</td>
      <td>0.538752</td>
      <td>0.087107</td>
    </tr>
    <tr>
      <th>67922</th>
      <td>dzialki.238458</td>
      <td>6536237.640000,6023858.990000 6536286.400000,6...</td>
      <td>226101_1.0049.162/2</td>
      <td>162/2</td>
      <td>Jasień</td>
      <td>49</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>7</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6536261.798 6023882.791)</td>
      <td>390</td>
      <td>0.106178</td>
      <td>72</td>
      <td>0.043636</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>26.500000</td>
      <td>0.499055</td>
      <td>0.088596</td>
    </tr>
    <tr>
      <th>34797</th>
      <td>dzialki.348182</td>
      <td>6539155.650000,6026464.200000 6539199.150000,6...</td>
      <td>226101_1.0054.194</td>
      <td>194</td>
      <td>054</td>
      <td>54</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>4</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6539178.753 6026483.37)</td>
      <td>750</td>
      <td>0.205461</td>
      <td>0</td>
      <td>0.000000</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>26.700001</td>
      <td>0.495274</td>
      <td>0.090620</td>
    </tr>
    <tr>
      <th>15299</th>
      <td>dzialki.491427</td>
      <td>6537363.140000,6025200.520000 6537416.190000,6...</td>
      <td>226101_1.0052.42/56</td>
      <td>42/56</td>
      <td>052</td>
      <td>52</td>
      <td>01_1</td>
      <td>M.Gdańsk</td>
      <td>5</td>
      <td>2024-10-15 21:30:16</td>
      <td>...</td>
      <td>POINT (6537390.516 6025218.93)</td>
      <td>510</td>
      <td>0.139272</td>
      <td>156</td>
      <td>0.094545</td>
      <td>50.0</td>
      <td>0.0</td>
      <td>37.099998</td>
      <td>0.298677</td>
      <td>0.095540</td>
    </tr>
  </tbody>
</table>
<p>9 rows × 46 columns</p>
</div>




```python
# Plot the results
fig, ax = plt.subplots(figsize=(12, 8))


# Plot the city boundary
city_boundary.plot(ax=ax, edgecolor='black', linewidth=1, alpha=0.5)

# Plot the centroids of the 10 best sites
best_sites['centroid'].plot(
    ax=ax,
    color='red',
    marker='*', 
    markersize=50,
    label='Top 9 Sites'
)

# Add labels with ranking
for idx, site in best_sites.iterrows():
    rank = best_sites.index.get_loc(idx) + 1
    ax.annotate(
        f'#{rank}',
        xy=(site.centroid.x, site.centroid.y),
        xytext=(5, 5),
        textcoords='offset points',
        color='black',
        fontweight='bold'
    )
ctx.add_basemap(ax, crs=2177)
ax.set_axis_off()

plt.title('Top 9 Sites Based on Combined Criteria')
plt.legend()
```




    <matplotlib.legend.Legend at 0x16a03a660>




    
![png](output_13_1.png)
    


### Zoom to the best sites


```python
buffer_distance = 300

fig, axes = plt.subplots(3, 3, figsize=(12, 12))
axes = axes.flatten()

for idx in range(len(best_sites)):
    ax = axes[idx]
    site_polygon = best_sites.geometry.iloc[idx]

    # Create buffer
    buffer = site_polygon.buffer(buffer_distance+100)
    
    # Filter and plot background features
    noise_map_in_view = noise_map[noise_map.intersects(buffer)]
    plots_in_view = plots[plots.intersects(buffer)]
    buildings_in_view = buildings[buildings.intersects(buffer)]
    green_areas_in_view = green_areas[green_areas.intersects(buffer)]
    pow_in_view = churches[churches.intersects(buffer)]
    best_sites_in_view = best_sites[best_sites.intersects(buffer)]
    
    # Plot layers
    noise_map_in_view.plot(ax=ax, cmap='Reds', alpha=0.3)
    plots_in_view.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.3)
    buildings_in_view.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.3)
    green_areas_in_view.plot(ax=ax, color='green', alpha=0.3)
    if len(pow_in_view) > 0:
        pow_in_view.plot(ax=ax, color='blue', marker='+', markersize=100)
    best_sites_in_view.plot(ax=ax, facecolor='red', alpha=0.3)
    
    # Highlight the site
    site_gdf = gpd.GeoDataFrame(geometry=[site_polygon], crs=2177)
    site_gdf.plot(ax=ax, facecolor='red', edgecolor='black', alpha=0.7, linewidth=2)
    
    # Set bounds
    ax.set_xlim(buffer.bounds[0], buffer.bounds[2])
    ax.set_ylim(buffer.bounds[1], buffer.bounds[3])
    
    ax.set_title(f'Site {idx+1}\nArea: {site_polygon.area:.1f} m²')
    ax.set_axis_off()

plt.tight_layout()
plt.legend()
```

    /var/folders/j5/0qh0dgj5607fhs9231nrxjww0000gn/T/ipykernel_2136/1328023580.py:42: UserWarning: No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
      plt.legend()





    <matplotlib.legend.Legend at 0x175a66690>




    
![png](output_15_2.png)
    



```python
# Print detailed information about each site
print("\nDetailed information for top sites:")
for idx, site in best_sites.iterrows():
    print(f"\nSite {idx}:")
    print(f"Area: {site.area:.0f}m2")
    print(f"Combined Score: {site.combined_score:.3f}")
    print(f"Seniors in area: {site.senior_density:.1f}%")
    print(f"Noise Level: {site.noise_level:.0f} dB")
    print(f"Distance to nearest church: {site.distance_to_nearest_church:.0f}m")
    print(f"Distance to nearest green area: {site.distance_to_nearest_green:.0f}m")

```

    
    Detailed information for top sites:
    
    Site 33489:
    Area: 1164m2
    Combined Score: 0.066
    Seniors in area: 39.4%
    Noise Level: 50 dB
    Distance to nearest church: 664m
    Distance to nearest green area: 15m
    
    Site 55603:
    Area: 1041m2
    Combined Score: 0.077
    Seniors in area: 23.9%
    Noise Level: 50 dB
    Distance to nearest church: 351m
    Distance to nearest green area: 14m
    
    Site 91480:
    Area: 1709m2
    Combined Score: 0.087
    Seniors in area: 24.4%
    Noise Level: 50 dB
    Distance to nearest church: 502m
    Distance to nearest green area: 24m
    
    Site 67922:
    Area: 1011m2
    Combined Score: 0.089
    Seniors in area: 26.5%
    Noise Level: 50 dB
    Distance to nearest church: 390m
    Distance to nearest green area: 72m
    
    Site 15299:
    Area: 1178m2
    Combined Score: 0.096
    Seniors in area: 37.1%
    Noise Level: 50 dB
    Distance to nearest church: 510m
    Distance to nearest green area: 156m
    
    Site 65037:
    Area: 7706m2
    Combined Score: 0.096
    Seniors in area: 11.7%
    Noise Level: 50 dB
    Distance to nearest church: 336m
    Distance to nearest green area: 0m
    
    Site 26489:
    Area: 4760m2
    Combined Score: 0.100
    Seniors in area: 22.3%
    Noise Level: 50 dB
    Distance to nearest church: 292m
    Distance to nearest green area: 107m
    
    Site 54863:
    Area: 1136m2
    Combined Score: 0.102
    Seniors in area: 14.7%
    Noise Level: 50 dB
    Distance to nearest church: 446m
    Distance to nearest green area: 21m
    
    Site 12849:
    Area: 1114m2
    Combined Score: 0.102
    Seniors in area: 14.0%
    Noise Level: 50 dB
    Distance to nearest church: 442m
    Distance to nearest green area: 20m

