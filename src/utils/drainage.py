import requests
import pandas as pd
from pynhd import WaterData

def get_usgs_id_and_drainage(name, lat, lon, radius=0.1):
    """
    Find a USGS monitoring location by waterbody name and coordinates.

    Parameters:
        name (str): Waterbody name (partial match, case-insensitive)
        lat (float): Latitude
        lon (float): Longitude
        radius (float): Bounding box half-width in degrees (default 0.1)

    Returns:
        pd.DataFrame: DataFrame with columns 'USGS_id' and 'drainage_area' for matching locations
    """
    bbox = f"{lon - radius},{lat - radius},{lon + radius},{lat + radius}"

    if not name: # If name unknown, just search by coordinates
        response = requests.get(
            "https://api.waterdata.usgs.gov/ogcapi/v0/collections/monitoring-locations/items",
            params={
                "bbox": bbox,
                "f": "json"
            }
        )
    else:   
        response = requests.get(
            "https://api.waterdata.usgs.gov/ogcapi/v0/collections/monitoring-locations/items",
            params={
                "filter": f"monitoring_location_name ILIKE '%{name}%'",
                "bbox": bbox,
                "f": "json"
            }
        )

    features = response.json().get("features", [])
    if not features:
        return pd.DataFrame(columns=["waterbody_name", "USGS_id", "drainage_area"])
    
    toRet_DF = pd.DataFrame(columns=["waterbody_name", "USGS_id", "drainage_area"])
    for feature in features:
        props = feature.get("properties", {})
        site_id = props.get("monitoring_location_number")
        drainage_area = props.get("drainage_area")
        if site_id and drainage_area: # Ignore sites that don't have a drainage area
            toRet_DF = pd.concat([toRet_DF, pd.DataFrame({
                "waterbody_name": [name],
                "USGS_id": [site_id],
                "drainage_area": [drainage_area]
            })], ignore_index=True)


    return toRet_DF


def km2_to_mi2(km2):
    """Convert square kilometers to square miles."""
    return km2 * 0.386102


def get_drainage_area_by_comid(comids):
    """
    Get the drainage area of waterbodies using their COMIDs via pynhd WaterData.
    Fetches all COMIDs in a single request.

    Parameters:
        comids (list): List of COMIDs (int or str).

    Returns:
        dict: Mapping of comid (str) -> drainage area in square miles, or None if not found.
    """
    comid_strs = [str(int(c)) for c in comids]
    drain_map = {c: None for c in comid_strs}

    wd = WaterData("nhdflowline_network")
    result = wd.byid("comid", comid_strs)

    if result.empty:
        return drain_map

    # totdasqkm is the total upstream drainage area in NHDPlus
    for _, row in result.iterrows():
        comid_key = str(int(row["comid"]))
        if comid_key in drain_map and pd.notna(row.get("totdasqkm")):
            drain_map[comid_key] = round(km2_to_mi2(row["totdasqkm"]), 2)

    return drain_map

def get_drainage_area_by_coords(lat, lon, distance=100):
    """
    Get the drainage area of the nearest NHD flowline by coordinates.

    Parameters:
        lat (float): Latitude
        lon (float): Longitude
        distance (int): Search radius in meters (default 100)

    Returns:
        float: Total upstream drainage area in square miles, or None if not found.
    """
    wd = WaterData("nhdflowline_network")
    result = wd.bydistance(coords=(lon, lat), distance=distance)

    if result.empty:
        return None

    # Pick the closest flowline (first result) and return its total drainage area
    area_km2 = result["totdasqkm"].iloc[0]
    return round(km2_to_mi2(area_km2), 2)

