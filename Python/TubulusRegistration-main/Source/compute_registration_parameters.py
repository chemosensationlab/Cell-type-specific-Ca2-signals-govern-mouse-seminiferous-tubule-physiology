# import dependencies
import SimpleITK as sitk
import os
import time
import re
from utils.utils import normalize, read_image, save_image
import numpy as np
import registration_parameters as rp
from parfor import parfor


def perform_registration_parallel(input_image, output_name, output_folder_frames, output_folder_transformations, method='rigid', perform_normalization=False, use_mask=False, pre_norm_thresh_low=0.0, pre_norm_thresh_high=65535.0, reference_frame=0, intermediate_results=True, num_threads=-1):
    
    # create output folders if they don't exist yet
    if intermediate_results:
        os.makedirs(output_folder_frames, exist_ok=True)


    # set num threads
    if num_threads < 0:
        num_threads = sitk.ProcessObject_GetGlobalDefaultNumberOfThreads()

    #sitk.ProcessObject_SetGlobalDefaultNumberOfThreads(1)

    print('Global number of threads for SITK is set to %i and using parfor with %i threads' % (sitk.ProcessObject_GetGlobalDefaultNumberOfThreads(), num_threads))

    os.makedirs(output_folder_transformations, exist_ok=True)

    # get number of frames and initialize result image
    num_frames = input_image.shape[0]
    result_image_stack = np.zeros_like(input_image)

    # get the fixed image (either the first one or the specified reference frame)
    fixed_image = np.squeeze(input_image[np.max((0, np.min((reference_frame, num_frames)))),...])

    # perform normalization if enabled
    if (perform_normalization):
        fixed_image = normalize(fixed_image.astype(np.float32), lower_boundary=1.0, upper_boundary=99.0, pre_norm_thresh_low=pre_norm_thresh_low, pre_norm_thresh_high=pre_norm_thresh_high)

    # convert image to ITK image for further processing
    fixed_image = sitk.GetImageFromArray(fixed_image)
    fixed_image = sitk.Cast(fixed_image, sitk.sitkFloat32)
    fixed_image.SetSpacing((1,1))

    num_iterations = int(np.floor(num_frames / num_threads))

     # Calculate the start time
    start_time = time.time()

    for i in range(0,num_iterations):
    
        start_index = i*num_threads
        end_index = int(np.min((start_index + num_threads, num_frames)))

        @parfor(range(start_index, end_index), ((input_image, fixed_image, method, output_folder_frames, intermediate_results), ), n_processes=num_threads)
        def register_image_pair(moving_index, input_tuple):

            moving_image = np.squeeze(input_tuple[0][moving_index, ...])
            fixed_image = input_tuple[1]
            method = input_tuple[2]
            output_folder_frames = input_tuple[3]
            intermediate_results = input_tuple[4]

            result_image = fixed_image

            try:
                # normalize the moving image if enabled
                if (perform_normalization):
                    moving_image = normalize(moving_image.astype(np.float32), lower_boundary=1.0, upper_boundary=99.0)

                moving_image = sitk.GetImageFromArray(moving_image)
                moving_image = sitk.Cast(moving_image, sitk.sitkFloat32)
                moving_image.SetSpacing((1,1))

                elastix_image_filter = sitk.ElastixImageFilter()
                elastix_image_filter.SetFixedImage(fixed_image)
                elastix_image_filter.SetMovingImage(moving_image)

                if (method == 'rigid'):
                    elastix_image_filter.SetParameterMap(rp.get_rigid_parameter_map())
                elif (method == 'affine'):
                    elastix_image_filter.SetParameterMap(rp.get_affine_parameter_map())
                elif (method == 'bspline'):
                    elastix_image_filter.SetParameterMap(rp.get_bspline_parameter_map())

                elastix_image_filter.Execute()

                transform_parameter_map = elastix_image_filter.GetTransformParameterMap()

                output_file_name = os.path.basename(output_folder_frames)
                output_file_name = output_file_name.replace(".tiff", "")
                output_file_name = output_file_name.replace(".tif", "")

                # Save transformation parameters to a text file
                sitk.WriteParameterFile(transform_parameter_map[0], os.path.join(output_folder_transformations, "%s_%s_%04d.txt" % (output_file_name, method, moving_index)))

                result_image = elastix_image_filter.GetResultImage()
                result_image = sitk.GetArrayFromImage(result_image)

                if perform_normalization:
                    result_image = result_image * 65535
                    result_image[result_image <= 0] = 0.0
                    result_image[result_image > 65535] = 65535.0
                    result_image = result_image.astype(np.uint16)
                else:
                    if input_image.dtype == np.uint16:
                        result_image[result_image <= 0] = 0
                        result_image[result_image > 65535] = 65535
                    else:
                        result_image[result_image <= 0] = 0
                        result_image[result_image > 255] = 255

                    result_image = result_image.astype(input_image.dtype)

                if intermediate_results:
                    sitk.WriteImage(sitk.GetImageFromArray(result_image), os.path.join(output_folder_frames, "%s_%s_%04d.tif" % (output_file_name, method, moving_index)))

            except:
                result_image = fixed_image
                if intermediate_results:
                    sitk.WriteImage(sitk.GetImageFromArray(result_image), os.path.join(output_folder_frames, "%s_%s_%04d_ERROR.tif" % (output_file_name, method, moving_index)))

            return result_image
    
        result_list = register_image_pair

        # process all frames
        for j in range(0, len(result_list)):
            result_image_stack[start_index+j, ...] = result_list[j]

        # Calculate the end time and time taken
        end_time = time.time()
        length = (end_time - start_time) / 60.0
        time_per_frame = length / end_index

        print("Finished processing %i / %i frames (elapsed time: %f min, est. remaining time: %f min)... " % (end_index, num_frames, length, time_per_frame*num_frames - length))

    sitk.WriteImage(sitk.GetImageFromArray(result_image_stack[:,0,0,...]), output_name)

        #if (use_mask):
        #    sitk.WriteImage(fixed_mask, os.path.join(output_folder, "%s_mask_registered_image_%03d.tif" % (method, i+1)))


def perform_registration(input_image, output_name, output_folder_frames, output_folder_transformations, method='rigid', perform_normalization=False, use_mask=False, pre_norm_thresh_low=0.0, pre_norm_thresh_high=65535.0, reference_frame=0, intermediate_results=True, num_threads=-1):
    
    # create output folders if they don't exist yet
    if intermediate_results:
        os.makedirs(output_folder_frames, exist_ok=True)


    # set num threads
    if num_threads > 0:
        sitk.ProcessObject_SetGlobalDefaultNumberOfThreads(num_threads)

    print('Global number of threads for SITK is set to %i' % (sitk.ProcessObject_GetGlobalDefaultNumberOfThreads()))

    os.makedirs(output_folder_transformations, exist_ok=True)

    # get number of frames and initialize result image
    num_frames = input_image.shape[0]
    result_image_stack = np.zeros_like(input_image)

    # get the fixed image (either the first one or the specified reference frame)
    fixed_image = np.squeeze(input_image[np.max((0, np.min((reference_frame, num_frames)))),...])

    # perform normalization if enabled
    if (perform_normalization):
        fixed_image = normalize(fixed_image.astype(np.float32), lower_boundary=1.0, upper_boundary=99.0, pre_norm_thresh_low=pre_norm_thresh_low, pre_norm_thresh_high=pre_norm_thresh_high)

    # convert image to ITK image for further processing
    fixed_image = sitk.GetImageFromArray(fixed_image)
    fixed_image = sitk.Cast(fixed_image, sitk.sitkFloat32)
    fixed_image.SetSpacing((1,1))

    if (use_mask):
        #fixed_mask = getmask(fixed_image)
        fixed_mask.SetSpacing(fixed_image.GetSpacing())

    # process all frames
    for i in range(0, num_frames):

        moving_image = np.squeeze(input_image[i,...])

        # normalize the moving image if enabled
        if (perform_normalization):
            moving_image = normalize(moving_image.astype(np.float32), lower_boundary=1.0, upper_boundary=99.0, pre_norm_thresh_low=pre_norm_thresh_low, pre_norm_thresh_high=pre_norm_thresh_high)

        moving_image = sitk.GetImageFromArray(moving_image)
        moving_image = sitk.Cast(moving_image, sitk.sitkFloat32)
        moving_image.SetSpacing((1,1))

        if (use_mask):
            moving_mask = getmask(moving_image)
            moving_mask.SetSpacing(moving_image.GetSpacing())

        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(fixed_image)
        elastix_image_filter.SetMovingImage(moving_image)

        if (method == 'rigid'):   
            elastix_image_filter.SetParameterMap(rp.get_rigid_parameter_map())
        elif (method == 'affine'):
            elastix_image_filter.SetParameterMap(rp.get_affine_parameter_map())
        elif (method == 'bspline'):
            elastix_image_filter.SetParameterMap(rp.get_bspline_parameter_map())

        elastix_image_filter.LogToConsoleOn()
        elastix_image_filter.LogToFileOn()

        elastix_image_filter.Execute()

        result_image = elastix_image_filter.GetResultImage()
        transform_parameter_map = elastix_image_filter.GetTransformParameterMap()

        if reference_frame < 0:
            fixed_image = result_image
        
        if (use_mask):
            fixed_mask = getmask(fixed_image)

        output_file_name = os.path.basename(output_folder_frames)
        output_file_name = output_file_name.replace(".tiff", "")
        output_file_name = output_file_name.replace(".tif", "")

        # Save transformation parameters to a text file
        sitk.WriteParameterFile(transform_parameter_map[0], os.path.join(output_folder_transformations, "%s_%s_%04d.txt" % (output_file_name, method, i)))

        result_image = sitk.GetArrayFromImage(result_image)

        if perform_normalization:
            result_image = result_image * 65535
            result_image[result_image <= 0] = 0.0
            result_image[result_image > 65535] = 65535.0
            result_image = result_image.astype(np.uint16)
        else:
            if input_image.dtype == np.uint16:
                result_image[result_image <= 0] = 0
                result_image[result_image > 65535] = 65535
            else:
                result_image[result_image <= 0] = 0
                result_image[result_image > 255] = 255

            result_image = result_image.astype(input_image.dtype)

        if intermediate_results:
            sitk.WriteImage(sitk.GetImageFromArray(result_image), os.path.join(output_folder_frames, "%s_%s_%04d.tif" % (output_file_name, method, i)))

        result_image_stack[i, ...] = result_image

    sitk.WriteImage(sitk.GetImageFromArray(result_image_stack[:,0,0,...]), output_name)

        #if (use_mask):
        #    sitk.WriteImage(fixed_mask, os.path.join(output_folder, "%s_mask_registered_image_%03d.tif" % (method, i+1)))


def apply_transformation(input_folder, output_folder, output_folder_parameters, method='rigid', perform_normalization=False, use_mask=False, pre_norm_thresh_low=0.0, pre_norm_thresh_high=65535.0):
    
    # create output folders if they don't exist yet
    os.makedirs(output_folder, exist_ok=True)

    # load the input image files
    # find . -name ".DS_Store" -delete
    image_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]

    # Sort the image files based on extracted numbers
    image_files.sort()

    for i in range(0, len(image_files)):

        # setup the output file name
        output_file_name = str(image_files[i])
        output_file_name = output_file_name.replace(".tiff", "")
        output_file_name = output_file_name.replace(".tif", "")

        if "c=01" in output_file_name:
            output_file_name = output_file_name.replace("c=01", "c=00")
        else:
            output_file_name = output_file_name.replace("c=00", "c=01")

        # Save transformation parameters to a text file
        transformationParameters = sitk.ReadParameterFile(os.path.join(output_folder_parameters, "%s_%s.txt" % (output_file_name, method)))

        #moving_image = sitk.ReadImage(os.path.join(input_folder, image_files[i]), sitk.sitkUInt16)
        moving_image = read_image(os.path.join(input_folder, image_files[i]))
        moving_image = sitk.GetImageFromArray(moving_image[0])
        moving_image = sitk.Cast(moving_image, sitk.sitkFloat32)
        moving_image.SetSpacing((1,1))

        if (perform_normalization):
            moving_image = normalize(moving_image, lower_boundary=1.0, upper_boundary=99.0, pre_norm_thresh_low=pre_norm_thresh_low, pre_norm_thresh_high=pre_norm_thresh_high)

        transformix_image_filter = sitk.TransformixImageFilter()
        transformix_image_filter.SetMovingImage(moving_image)

        transformix_image_filter.SetTransformParameterMap(transformationParameters)

        transformix_image_filter.LogToConsoleOn()
        transformix_image_filter.LogToFileOn()

        transformix_image_filter.Execute()

        result_image = transformix_image_filter.GetResultImage()

        result_image = sitk.GetArrayFromImage(result_image)
        result_image[result_image <= 0] = 0.0
        result_image[result_image > 65535] = 65535.0
        result_image = result_image.astype(np.uint16)

        sitk.WriteImage(sitk.GetImageFromArray(result_image), os.path.join(output_folder, "%s_%s.tif" % (output_file_name, method)))

        #if (use_mask):
        #    sitk.WriteImage(fixed_mask, os.path.join(output_folder, "%s_mask_registered_image_%03d.tif" % (method, i+1)))