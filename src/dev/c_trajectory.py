#python c_trajectory.py ./data --umbral 0.5 -o resultados_finales.csv

import glob
import argparse
import os
import pandas as pd
import numpy as np
from skimage.measure import label, regionprops
from sunpy.map import Map
from astropy import units as u
from hpxy2lonlat import hpxy2lonlat

def parse_args():
    parser = argparse.ArgumentParser(description="FITS processing, detects sun spots and generate a trayectory.")
    parser.add_argument('directory', type=str, help='Path to the FITS files folder')
    parser.add_argument('--umbral', type=float, default=0.4, help='Umbral factor (default: 0.4)')
    parser.add_argument('-o', '--output', type=str, default='carrington_trajectory.csv', help='Name of the CSV output')
    return parser.parse_args()

def sunspot_centroid(map_input, umbral_factor):

    umbral = np.nanmedian(map_input.data) * umbral_factor       # We use the parser default factor
    mask = map_input.data < umbral
    etiquette = label(mask)
    regions = regionprops(etiquette)
    
    if not regions:
        return None, None
    
    principal_sunspot = max(regions, key=lambda r: r.area)
    y_pix, x_pix = principal_sunspot.centroid

    x_input = x_pix * u.pix
    y_input = y_pix * u.pix

    world_coords = map_input.pixel_to_world(x_input, y_input)

    hpc_x = world_coords.Tx
    hpc_y = world_coords.Ty
    
    return hpc_x, hpc_y
    

if __name__ == '__main__':
    args = parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        exit(1)

    trajectory_data = []

    fits_files = glob.glob(os.path.join(args.directory, '*.fits'))
    print(f"Processing {len(fits_files)} FITS...")

    for archivo in sorted(fits_files):
        try:
            m = Map(archivo)
            hpx, hpy = sunspot_centroid(m, args.umbral)
            
            if hpx is not None:
                lon, lat = hpxy2lonlat(m, hpx, hpy)
                trajectory_data.append({
                    'obs_date': m.date.iso,
                    'lon_carrington': lon.value,
                    'lat_carrington': lat.value
                })
        except Exception as e:
            print(f"Error processing {archivo}: {e}")

    df = pd.DataFrame(trajectory_data)
    df.to_csv(args.output, index=False)
    print(f"Saved in: {args.output}")