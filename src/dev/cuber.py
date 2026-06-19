import os
import argparse
import numpy as np
from astropy.io import fits

"""
Lee una serie de mapas FITS 2D y los unifica en un verdadero Cubo FITS 3D.
"""

def create_fits_cube(mode, data_dir, output_name):
    """
    Lee una serie de mapas FITS 2D y los unifica en un verdadero Cubo FITS 3D.
    """
    # 1. Definir el filtro según el modo seleccionado
    if mode == 'cutout':
        prefix = 'proc_'
        default_out = 'cutout_cube3d.fits'
    else:  # mode == 'fulldisk'
        prefix = ''
        default_out = 'fulldisk_cube3d.fits'
        
    # Si el usuario no especificó un nombre de salida, usamos el por defecto
    if not output_name:
        output_name = default_out

    # 2. Buscar y ordenar los archivos válidos
    all_files = os.listdir(data_dir)
    
    if mode == 'cutout':
        # Solo archivos que empiezan con 'proc_'
        files = [f for f in all_files if f.endswith('.fits') and f.startswith(prefix)]
    else:
        # Archivos que NO empiezan con 'proc_' ni son cubos generados previamente
        files = [f for f in all_files if f.endswith('.fits') and not f.startswith('proc_') and 'cube3d' not in f]

    files = sorted(files)

    if not files:
        print(f"Error: No se encontraron archivos FITS para el modo '{mode}' en: {data_dir}")
        return

    print(f"Encontrados {len(files)} archivos. Leyendo y apilando...")

    # 3. Leer los datos y extraer el header de referencia
    data_list = []
    header = None
    expected_shape = None
    

    for f in files:
        path = os.path.join(data_dir, f)
        with fits.open(path) as hdul:
            current_data = hdul[0].data

            if current_data is None:
                print(f"⚠️ Corrupted data or gap en {f}")
                continue

            current_shape = current_data.shape
            
            # --- CORRECCIÓN DE SEGURIDAD ---
            # Si por error encuentra un archivo plano que no tiene 2 dimensiones (X, Y), lo salta
            if len(current_shape) != 2:
                continue

            if expected_shape is None:
                expected_shape = current_shape
                header = hdul[0].header.copy()

            if current_shape == expected_shape:
                # Volteamos vertical y horizontalmente usando slices puros de NumPy.
                # Esto mantiene las dimensiones idénticas [Y, X] sin alterar tipos.
                corrected_data = current_data[::-1, ::-1]
                data_list.append(corrected_data)
            else:
                print(f"⚠️ Saltando {f}: Dimensiones {current_shape} no coinciden con las esperadas {expected_shape}")

    if not data_list:
        print("❌ Error: No quedaron archivos válidos para empaquetar.")
        return


    # 4. Crear la matriz 3D (Eje 0 = Tiempo, Eje 1 = Y, Eje 2 = X)
    cube_data = np.stack(data_list, axis=0)

    # Actualizar las dimensiones en el header para que FITS sepa que ahora es 3D
    header['NAXIS'] = 3
    header['NAXIS3'] = len(data_list)  # Dimensión del tiempo

    # 5. Guardar el archivo final
    output_path = os.path.join(data_dir, output_name)
    fits.writeto(output_path, cube_data, header, overwrite=True)
    
    print(f"¡Éxito! cubo 3D guardado en: {output_path}")
    print(f"Para visualizarlo ejecuta: ds9 {output_path} -cmap Viridis -scale mode minmax &")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Unifica series de FITS 2D en un Cubo FITS 3D para DS9.")
    parser.add_argument('mode', choices=['fulldisk', 'cutout'], 
                        help="Modo de empaquetado: 'fulldisk' (originales) o 'cutout' (recortados por c_cube)")
    parser.add_argument('--dir', default='.', 
                        help="Ruta al directorio de los FITS (por defecto el directorio actual)")
    parser.add_argument('--out', default='', 
                        help="Nombre personalizado para el archivo de salida .fits")
    
    args = parser.parse_args()
    create_fits_cube(args.mode, args.dir, args.out)