import SimpleITK as sitk

def get_rigid_parameter_map():
        
    parameterMap = sitk.GetDefaultParameterMap("rigid")
    
    #parameterMap["FinalGridSpacingInVoxels"] =[ "64"]

    if "FinalGridSpacingInPhysicalUnits" in parameterMap:
        del parameterMap["FinalGridSpacingInPhysicalUnits"]       
    parameterMap["FixedInternalImagePixelType"] =[ "float"]
    parameterMap["MovingInternalImagePixelType"] =[ "float"]
    parameterMap["UseDirectionCosines"] =[ "true"]

    parameterMap["Registration"] =[ "MultiResolutionRegistration"]
    parameterMap["Interpolator"] =[ "BSplineInterpolator"]
    parameterMap["ResampleInterpolator"] =[ "FinalBSplineInterpolator"]
    parameterMap["Resampler"] =[ "DefaultResampler"]
    
    parameterMap["FixedImagePyramid"] =[ "FixedRecursiveImagePyramid"]
    parameterMap["MovingImagePyramid"] =[ "MovingRecursiveImagePyramid"]
    
    parameterMap["Optimizer"] =[ "AdaptiveStochasticGradientDescent"]
    parameterMap["Transform"] =[ "EulerTransform"]
    #parameterMap["Metric"] =[ "AdvancedMattesMutualInformation"]
    parameterMap["Metric"] =[ "AdvancedNormalizedCorrelation"]
    
    parameterMap["AutomaticScalesEstimation"] =[ "true"]
    parameterMap["AutomaticTransformInitialization"] =[ "true"]
    parameterMap["HowToCombineTransforms"] =[ "Compose"]
    parameterMap["NumberOfHistogramBins"] =[ "32"]
    parameterMap["ErodeMask"] =[ "false"]
    parameterMap["NumberOfResolutions"] =[ "6"]
    #parameterMap["GridSpacingSchedule"] = ["128.0", "64.0", "32.0", "16.0", "8.0", "1.0"]
    parameterMap["MaximumNumberOfIterations"] =[ "1000"]
    parameterMap["NumberOfSpatialSamples"] =[ "2048"]
    parameterMap["NewSamplesEveryIteration"] =[ "true"]
    #parameterMap["ImageSampler"] =[ "FullSampler"]
    parameterMap["BSplineInterpolationOrder"] =[ "1"]
    parameterMap["FinalBSplineInterpolationOrder"] =[ "3"]
    parameterMap["DefaultPixelValue"] =["0"]
    parameterMap["WriteResultImage"] =["true"]
    parameterMap["ResultImagePixelType"] =["unsigned short"]
    parameterMap["ResultImageFormat"] =["tif"]

    return parameterMap


def get_affine_parameter_map():
    parameterMap = sitk.GetDefaultParameterMap("affine")
    
    #if "FinalGridSpacingInPhysicalUnits" in parameterMap:
     #   del parameterMap["FinalGridSpacingInPhysicalUnits"]       
    parameterMap["FixedInternalImagePixelType"] =[ "float"]
    parameterMap["MovingInternalImagePixelType"] =[ "float"]
    parameterMap["UseDirectionCosines"] =[ "true"]

    parameterMap["Registration"] =[ "MultiResolutionRegistration"]
    parameterMap["Interpolator"] =[ "BSplineInterpolator"]
    parameterMap["ResampleInterpolator"] =[ "FinalBSplineInterpolator"]
    parameterMap["Resampler"] =[ "DefaultResampler"]
    
    parameterMap["FixedImagePyramid"] =[ "FixedRecursiveImagePyramid"]
    parameterMap["MovingImagePyramid"] =[ "MovingRecursiveImagePyramid"]
    
    parameterMap["Optimizer"] =[ "AdaptiveStochasticGradientDescent"]
    parameterMap["Transform"] =[ "AffineTransform"]
    #parameterMap["Metric"] =[ "AdvancedMattesMutualInformation"]
    parameterMap["Metric"] =[ "AdvancedNormalizedCorrelation"]
    
    parameterMap["AutomaticScalesEstimation"] =[ "true"]
    parameterMap["AutomaticTransformInitialization"] =[ "true"]
    parameterMap["HowToCombineTransforms"] =[ "Compose"]
    parameterMap["NumberOfHistogramBins"] =[ "32"]
    #parameterMap["ErodeMask"] =[ "false"]
    parameterMap["NumberOfResolutions"] =[ "6"]
    #parameterMap["GridSpacingSchedule"] = ["128.0", "64.0", "32.0", "16.0", "8.0", "1.0"]
    parameterMap["MaximumNumberOfIterations"] =[ "1000"]
    parameterMap["NumberOfSpatialSamples"] =[ "2048"]
    parameterMap["NewSamplesEveryIteration"] =[ "true"]
    parameterMap["ImageSampler"] =[ "Random"]
    parameterMap["BSplineInterpolationOrder"] =[ "1"]
    parameterMap["FinalBSplineInterpolationOrder"] =[ "3"]
    parameterMap["DefaultPixelValue"] =["0"]
    parameterMap["WriteResultImage"] =["true"]
    parameterMap["ResultImagePixelType"] =["unsigned short"]
    parameterMap["ResultImageFormat"] =["tif"]

    #parameterMap["FinalGridSpacingInVoxels"] =[ "64"]

    return parameterMap


def get_bspline_parameter_map():
    parameterMap = sitk.GetDefaultParameterMap("bspline")
    
    if "FinalGridSpacingInPhysicalUnits" in parameterMap:
        del parameterMap["FinalGridSpacingInPhysicalUnits"]
            
    parameterMap["FixedInternalImagePixelType"] =[ "float"]
    parameterMap["MovingInternalImagePixelType"] =[ "float"]

    parameterMap["Registration"] =[ "MultiResolutionRegistration"]
    parameterMap["Interpolator"] =[ "BSplineInterpolator"]
    parameterMap["ResampleInterpolator"] =[ "FinalBSplineInterpolator"]
    parameterMap["Resampler"] =[ "DefaultResampler"]

    parameterMap["FixedImagePyramid"] =[ "FixedRecursiveImagePyramid"]
    parameterMap["MovingImagePyramid"] =[ "MovingRecursiveImagePyramid"]

    parameterMap["Optimizer"] =[ "AdaptiveStochasticGradientDescent"]
    parameterMap["Transform"] =[ "BSplineTransform"]
    parameterMap["Metric"] =[ "AdvancedMattesMutualInformation"]
    #parameterMap["Metric"] =[ "AdvancedNormalizedCorrelation"]
    
    
    parameterMap["FinalGridSpacingInVoxels"] =[ "64"]
    
    parameterMap["GridSpacingSchedule"] = ["64.0", "32.0", "16.0", "8.0", "2.0", "1.0"]

    parameterMap["HowToCombineTransforms"] =[ "Compose"]
    parameterMap["NumberOfHistogramBins"] =[ "32"]
    parameterMap["ErodeMask"] =[ "false"]
    parameterMap["NumberOfResolutions"] =[ "6"]
    
    parameterMap["MaximumNumberOfIterations"] =[ "1000"]
    #parameterMap["NumberOfSpatialSamples"] =[ "2048"]
    parameterMap["NumberOfSpatialSamples"] =[ "4096"]
    parameterMap["NewSamplesEveryIteration"] =[ "true"]
    parameterMap["ImageSampler"] =[ "Random"]
    parameterMap["BSplineInterpolationOrder"] =[ "1"]
    parameterMap["FinalBSplineInterpolationOrder"] =[ "3"]
    parameterMap["DefaultPixelValue"] =["0"]
    parameterMap["WriteResultImage"] =["true"]
    parameterMap["ResultImagePixelType"] =["unsigned short"]
    parameterMap["ResultImageFormat"] =["tif"]

    return parameterMap