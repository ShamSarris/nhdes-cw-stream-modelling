import geopandas as gpd

gdf = gpd.read_file("./src/data/Shapefiles/All_Watersheds_wJoin.zip")

# Project to UTM zone 19N (covers New Hampshire/Vermont area) for accurate area calculation
projected = gdf.to_crs(epsg=32619)

# Calculate area in square miles (1 sq meter = 3.86102e-7 sq miles)
SQ_M_TO_SQ_MI = 3.86102e-7
projected["area (sq mi)"] = projected.geometry.area * SQ_M_TO_SQ_MI

# Copy the new column back to the original GDF (drop geometry for CSV export)
gdf["area (sq mi)"] = projected["area (sq mi)"]

output_df = gdf.drop(columns="geometry")
output_df.to_csv("./src/data/watersheds_with_area_based-on-shp.csv", index=False)

print(f"Saved {len(output_df)} records to watersheds_with_area_based-on-shp.csv")
print(output_df[["Name", "Unique_ID", "area (sq mi)"]].head(10))