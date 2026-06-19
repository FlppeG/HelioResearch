#python nombre_de_tu_script.py ./data --umbral 0.5 -o resultados_finales.csv

import glob
import subprocess
import argparse
import os
import pandas as pd
import numpy as np
from skimage.measure import label, regionprops
from sunpy.map import Map
from hpxy2lonlat import hpxy2lonlat

def parse_args():
    parser = argparse.ArgumentParser(description="FITS processing, detects sun spots and generate a trayectory.")
    parser.add_argument('directorio', type=str, help='Route to the .fits.fz folder')
    parser.add_argument('--umbral', type=float, default=0.4, help='Umbral factor (default: 0.4)')
    parser.add_argument('-o', '--output', type=str, default='carrington_trayectory.csv', help='Name of the CSV output')
    return parser.parse_args()

def obtener_centroide_mancha(map_input, factor_umbral):
    # Usamos el factor que viene del parser
    umbral = np.nanmedian(map_input.data) * factor_umbral
    mascara = map_input.data < umbral
    etiquetas = label(mascara)
    regiones = regionprops(etiquetas)
    
    if not regiones:
        return None, None
    
    mancha_principal = max(regiones, key=lambda r: r.area)
    y_pix, x_pix = mancha_principal.centroid
    hpc_x, hpc_y = map_input.pixel_to_world(x_pix, y_pix)
    return hpc_x, hpc_y

if __name__ == '__main__':
    args = parse_args()
    
    if not os.path.isdir(args.directorio):
        print(f"Error: Directory '{args.directorio}' does not exist.")
        exit(1)

    archivos_fz = glob.glob(os.path.join(args.directorio, '*.fits.fz'))
    datos_trayectoria = []

    print(f"Uncompressing {len(archivos_fz)} ...")
    for archivo_fz in archivos_fz:
        subprocess.run(['funpack', '-E', '1', '-v', archivo_fz], check=True)

    archivos_fits = glob.glob(os.path.join(args.directorio, '*.fits'))
    print(f"Processing {len(archivos_fits)} FITS...")

    for archivo in sorted(archivos_fits):
        try:
            m = Map(archivo)
            hpx, hpy = obtener_centroide_mancha(m, args.umbral)
            
            if hpx is not None:
                lon, lat = hpxy2lonlat(m, hpx, hpy)
                datos_trayectoria.append({
                    'fecha_obs': m.date.iso,
                    'lon_carrington': lon.value,
                    'lat_carrington': lat.value
                })
        except Exception as e:
            print(f"Error processing {archivo}: {e}")

    df = pd.DataFrame(datos_trayectoria)
    df.to_csv(args.output, index=False)
    print(f"Done! Saved in: {args.output}")