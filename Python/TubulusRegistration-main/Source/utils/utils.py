import os
import numpy as np
import pathlib
from os import listdir
from os.path import isfile, join
from pathlib import Path
from skimage import segmentation


import tifffile
import json

def standardize_metadata(metadata : dict):
    key_map = {
        "spacing": ["spacing"],
        "PhysicalSizeX": ["PhysicalSizeX", "physicalsizex", "physical_size_x"],
        "PhysicalSizeY": ["PhysicalSizeY", "physicalsizey", "physical_size_y"],
        "PhysicalSizeZ": ["PhysicalSizeZ", "physicalsizez", "physical_size_z"],
        "unit": ["unit"],
        "axes": ["axes"],
        "channels": ["channels", "SizeC", "sizec"],
        "slices": ["slices", "SizeZ", "sizez"],
        "frames": ["frames", "SizeT", "sizet"],
        "study": ["study"],
        "SizeT": ["sizet", "SizeT"],
        "SizeZ": ["sizez", "SizeZ"],
        "SizeC": ["sizec", "SizeC"],
        "SizeY": ["sizey", "SizeY"],
        "SizeX": ["sizex", "SizeX"]
    }

    # Normalize metadata by looking up possible keys
    standardized_metadata = {}
    for standard_key, possible_keys in key_map.items():
        for key in possible_keys:
            if key in metadata:
                standardized_metadata[standard_key] = metadata[key]
                break  # Stop once we find the first available key

    return standardized_metadata



def read_image(location, end_point_image=False): # WARNING IMAGE DATA EN ZYX
    import tifffile
    # Read the TIFF file and get the image and metadata
    with tifffile.TiffFile(location) as tif:

        #image_data = tif.asarray() # Extract image array data
        #return image_data, None
    
        image_data = tif.asarray() # Extract image array data

        if tif.shaped_metadata is not None:
            shp_metadata = tif.shaped_metadata[0]
            metadata = standardize_metadata(shp_metadata)

            return image_data, metadata
        else:
            if tif.imagej_metadata is not None:
                shape = list(image_data.shape)
                imgj_metadata = tif.imagej_metadata
                imgj_metadata['shape'] = shape
                metadata = standardize_metadata(imgj_metadata)

                if 'slices' not in metadata:
                    metadata['slices'] = 1

                if 'channels' not in metadata:
                    metadata['channels'] = 1

                if 'frames' not in metadata:
                    metadata['frames'] = 1

                if len(shape) == 4:
                    if not end_point_image:
                        if shape[1] == 2:
                            image_data = np.expand_dims(image_data, axis=1)
                        else:
                            image_data = np.expand_dims(image_data, axis=2)
                    else:
                        image_data = np.expand_dims(image_data, axis=0)
                if len(shape) == 3:
                    if end_point_image:
                        if shape[0] == 2:
                            image_data = np.expand_dims(image_data, axis=0)
                            image_data = np.expand_dims(image_data, axis=0)
                        else:
                            image_data = np.expand_dims(image_data, axis=1)
                            image_data = np.expand_dims(image_data, axis=0)
                    else:
                        image_data = np.expand_dims(image_data, axis=1)
                        image_data = np.expand_dims(image_data, axis=1)
                
                if len(shape) > 2:
                    shape = image_data.shape
                    metadata['frames'] = shape[0]
                    metadata['slices'] = shape[1]
                    metadata['channels'] = shape[2]                
                    metadata['shape'] = shape

                ## TODO!!!
                #myimage = create_standardized_image(image_data, metadata)

                return image_data, metadata

            else:
                return image_data, None


def create_standardized_image(image_data, metadata):

    num_slices = 1
    num_frames = 1
    num_channels = 1
    height = image_data.shape[-2]
    width = image_data.shape[-1]
    image_shape = image_data.shape
    image_dim = len(image_shape)

    if len(image_shape) == 5:
        return image_data

    if 'frames' in metadata:
        num_frames = metadata['frames']

    if 'slices' in metadata:
        num_slices = metadata['slices']

    if 'channels' in metadata:
        num_channels = metadata['channels']

    result_image = np.zeros((num_frames, num_slices, num_channels, height, width))

    for f in range (0, num_frames):
        for s in range (0, num_slices):
            for c in range (0, num_channels):

                if image_dim == 4 and num_frames > 1:
                    result_image[f, s, c, ...] = image_data[f, c, ...]
                elif image_dim == 4 and num_slices > 1:
                    result_image[f, s, c, ...] = image_data[s, c, ...]
                elif image_dim == 3 and num_frames > 1:
                    result_image[f, s, c, ...] = image_data[f, ...]
                elif image_dim == 3 and num_slices > 1:
                    result_image[f, s, c, ...] = image_data[s, ...]
                elif image_dim == 3 and num_channels > 1:
                    result_image[f, s, c, ...] = image_data[c, ...]
                elif image_dim == 2:
                    result_image[f, s, c, ...] = image_data

    return result_image



def save_image(*, location, array, metadata=None, pixel_size_mu=1.0):

    if metadata is None:
        metadata = {'spacing': 1.0, 'unit': 'microns', 'shape': list(array.shape)}

    if array.dtype == np.int32 or array.dtype == np.float64:
        array = array.astype(np.uint16)

    tifffile.imwrite(
        location,
        array,
        bigtiff=True, #Keep it for 3D images
        resolution=(1. / pixel_size_mu, 1. / pixel_size_mu),
        imagej=True,
        metadata=metadata,
        tile=(128, 128),
        )
    
def save_omnipose_segmentation(*, location, masks, stem_file, metadata=None, pixel_size_mu=1.0, save_tiff=True, original_file_name, flow):

    if metadata is None:
        metadata = {'spacing': 1.0, 'unit': 'microns', 'shape': list(masks.shape)}
    
    output_path = Path(location)

    seg_npy_path = output_path / (stem_file + '_seg.npy')

    outlines = segmentation.find_boundaries(masks, mode='outer').astype(np.uint8)

    np.save(seg_npy_path, {
        'masks': masks,
        'filename': str(original_file_name),
        'metadata': metadata,
        'outlines': outlines, 
        'flows': flow, #[dummy_flow, dummy_prob, dummy_p], 
        'chan_choose': [0, 0],
        'chan_choose2': [0, 0],
        'diam_mean': 0.0,
    })
    print(f"Saved Omnipose segmentation NPY: {seg_npy_path}")




    
def adjust_meta_information(input_path, metadata, pixel_size_mu=1.0):

    input_files = list(pathlib.Path(input_path).rglob('*.tif'))

    for current_file in input_files:
        current_image, current_metadata = read_image(current_file)
        save_image(location=current_file, array=current_image.astype(np.uint16), metadata=metadata, pixel_size_mu=pixel_size_mu)

def read_image_folder(input_folder, extension='.tif'):

    input_files = [f for f in os.listdir(input_folder) if f.endswith(extension)]
    input_files.sort()

    if len(input_files) <= 0:
        return []

    # read first image to get the size information
    input_image, metadata = read_image(os.path.join(input_folder, input_files[0]))

    result_images = np.zeros((len(input_files), input_image.shape[0], input_image.shape[1]))
    for f in range(0, len(input_files)):
        result_images[f, :, :] = tifffile.imread(os.path.join(input_folder, input_files[f]))

    return result_images

def write_image_folder(output_path, output_image):

    num_files = output_image.shape[0]
    
    for f in range(0, num_files):
        output_filename = os.path.join(output_path, 'mask%04d.tif' % (f))
        save_image(location=output_filename, array=output_image[f, ...], metadata=None)


def normalize(image, lower_boundary=0.01, upper_boundary=99.99, pre_norm_thresh_low=0.0, pre_norm_thresh_high=65535.0):

    image_array = image

    image_array[image_array <= pre_norm_thresh_low] = 0
    image_array[image_array >= pre_norm_thresh_high] = 0

    # Get lower and upper quantiles using NumPy
    lower_quantile = np.percentile(image_array[image_array > 0], lower_boundary)  # 1st percentile (lower quantile)
    upper_quantile = np.percentile(image_array[image_array > 0], upper_boundary)  # 99th percentile (upper quantile)

    # Normalize the image
    normalized_image_array = (image_array - lower_quantile) / (upper_quantile - lower_quantile)
    normalized_image_array[normalized_image_array > 1] = 1
    normalized_image_array[normalized_image_array < 0] = 0
    normalized_image_array = normalized_image_array.astype(np.float32)

    return normalized_image_array

#Funciton to read in Parameters from json file
def read_json(json_path):
    if not json_path:
        print("No valid path to parameter file")
        return 

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    except Exception as e:
        print(f"Failed to open json file: {e}")
        return