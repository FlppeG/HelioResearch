import os
import argparse
import numpy as np
from astropy.io import fits

"""
    Code structure
    --------------
    Receive a 2D FITS files series and unifies in a 3D FITS cube of data using NumPy.
    It performs a matrix correction to data since indexing in Python (row-major) and FITS 
    standards (column-major) differ.
    
    Parameters
    ----------
    mode:                       -str It can be "fulldisk" (default) or "cutout" depending on your FITS series (if cutout, the FITS files must have the proc_ prefix)
    data_dir:                   -str FITS data folder path
    output_name (optional):     -str Custom filename for the generated cube
"""

def cuber(mode, data_dir, output_name):

    # Define a filter depending on the selected mode
    if mode == 'cutout':
        prefix = 'proc_'
        default_out = 'cutout_cube3d.fits'
    else: 
        prefix = ''
        default_out = 'fulldisk_cube3d.fits'
        
    if not output_name:
        output_name = default_out

    # Search and sort the valid files
    try:
        all_files = os.listdir(data_dir)
    except FileNotFoundError:
        print(f"Error: The directory '{data_dir}' does not exist.")
        return
    
    if mode == 'cutout':
        # Only files with 'proc_' prefix
        files = [f for f in all_files if f.endswith('.fits') and f.startswith(prefix)]
    else:
        # Avoid processing previously generated cubes or processed cutouts
        files = [f for f in all_files if f.endswith('.fits') and not f.startswith('proc_') and 'cube3d' not in f]

    files = sorted(files)

    if not files:
        print(f"Error: There are no FITS files for '{mode}' mode in: {data_dir}")
        return

    print(f"Found {len(files)} files. Converting...")

    # Read the data and extract the reference header
    data_list = []
    header = None
    expected_shape = None
    

    for f in files:
        path = os.path.join(data_dir, f)
        with fits.open(path) as hdul:
            current_data = hdul[0].data

            if current_data is None:
                print(f"Corrupted data or blank data gap found in {f}")
                continue

            current_shape = current_data.shape
            
            # If it finds a plane with less than 2 dimensions, is ommited 
            if len(current_shape) != 2:
                continue

            if expected_shape is None:
                expected_shape = current_shape
                header = hdul[0].header.copy()

            if current_shape == expected_shape:
                # Matrix correction via pure NumPy slices
                corrected_data = current_data[::-1, ::-1]
                data_list.append(corrected_data)
            else:
                print(f"Omitting {f}: Dimensions {current_shape} does not match with the expected {expected_shape}")

    if not data_list:
        print("Error: No valid FITS layers were found to package.")
        return


    # Create the 3D matrix (axis 0 = time/sequence, axis 1 = Y, axis 2 = X
    cube_data = np.stack(data_list, axis=0)

    # Update the dimension metadata on the FITS header 
    header['NAXIS'] = 3
    header['NAXIS3'] = len(data_list)  

    # Save the generated cube 
    output_path = os.path.join(data_dir, output_name)
    fits.writeto(output_path, cube_data, header, overwrite=True)
    
    print(f"3D cube saved in: {output_path}")
    print(f"For visualization run: ds9 {output_path} -cmap Viridis -scale mode minmax &")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Unifies a 2D FITS series in a 3D FITS cube for DS9.")
    parser.add_argument('mode', choices=['fulldisk', 'cutout'], 
                        help="Packaging mode: 'fulldisk' (original) or 'cutout' (cutted by c_cube)")
    parser.add_argument('--dir', default='.', 
                        help="Directory route to FITS data (actual directory for default)")
    parser.add_argument('--out', default='', 
                        help="Custom filename for the generated cube.")
    
    args = parser.parse_args()
    cuber(args.mode, args.dir, args.out)