/*
========================================================================
DESCRIPTION (purpose in this study):
This Fiji/ImageJ macro was used to generate transient-enhanced GCaMP stacks and corresponding maximum-intensity projections.
In addition, it performs optic-flow-based motion detection to identify image regions/frames with non–rigid-body motion (e.g., single tubule contractions during acquisition).
Detected motion regions were excluded from amplitude quantification and from maximum-intensity projections of the transient-enhanced Ca2+ activity signal.

Prerequisite / Input:
- A 2-channel ImageJ stack must be open (window title expected: "2PStack_GCaMP.tif").
- Channel 1 (C1): red, deep-interpolated 2P signal (structural/reference channel).
- Channel 2 (C2): GCaMP6f channel.
- NOTE: Before running, ensure the "Stowers" and "BIG-EPFL" update sites are active. needed for "StackRegJ_" Imageregistration


Outputs:
- "Movement_Detection": binary motion mask (0/255) derived from optic flow on GCaMP.
- "GCaMP_transient_enhanced": transient-enhanced Ca2+ activity stack.
- "GCaMP_transient_MAX": max intensity projection excluding moving regions (signal - mask).
- "GCaMP_transient_with_MotionOverlay": composite visualization (motion mask in red over GCaMP in gray).
- "2PStack_GCaMP_registeredMerged": merged 2-channel stack after registration (C1 + C2).

  
CREDITS / CITATION:
- Fiji: Schindelin et al., Nat Methods (2012).
- ImageJ: Schneider, Rasband & Eliceiri, Nat Methods (2012).
- Registration uses StackRegJ_ by Jay Unruh (Stowers Institute),
  based on StackReg/TurboReg by Philippe Thévenaz (BIG, EPFL) and the underlying
  subpixel registration approach by Thévenaz, Ruttimann & Unser, IEEE TIP (1998).
  (Please ensure the Fiji update sites "Stowers" and "BIG-EPFL" are enabled.)
- Additional Fiji commands/plugins used in this macro include:
  "Gaussian Window MSE" (optic flow) and "Calculator Plus" (image arithmetic).
  

LICENSE:
This macro is released under the Creative Commons Attribution-NonCommercial 4.0
International License (CC BY-NC 4.0). You are free to share and adapt the code
for non-commercial purposes, provided appropriate credit is given.
========================================================================
*/

// Required input: a 2-channel time-lapse stack must be open and named "2PStack_GCaMP6.tif".
// Channel 1: reference/structural channel used for rigid-body registration and motion detection.
// Channel 2: raw GCaMP6 signal used for transient (Ca2+) signal enhancement and max-intensity projections.
inputTitle = "2PStack_GCaMP6.tif";
selectWindow(inputTitle);

// (1) Optional: set position and register the full 2-channel stack (rigid body)
Stack.setPosition(1, 1, 1);
//run("StackRegJ_", "transformation=[Rigid Body]");   // "Stowers" and "BIG-EPFL" update sites are active

// (2) Split channels (these are the registered channels if StackReg was run)
run("Split Channels");
ch1Title = "C1-" + inputTitle;   // red structural/reference
ch2Title = "C2-" + inputTitle;   // GCaMP6f

// (3) Motion detection on the registered GCaMP channel (does not modify ch2Title)
Flowtest(ch2Title);

// Rename final motion mask to a publication-friendly name
selectWindow("AResult");
rename("Movement_Detection");

// (4) Transient enhancement on the registered GCaMP channel
// Parameters: XYBlur1 = spatial denoise, XYBlur2 = baseline XY blur, ZBlur = temporal baseline blur
XYBlur1 = 3;
XYBlur2 = 0;
ZBlur   = 20;

transientEnhance(ch2Title, XYBlur1, XYBlur2, ZBlur, "GCaMP_transient_enhanced");

// (4b) Max projection excluding moving regions
// Important: convert signal to 8-bit first to match the 8-bit binary motion mask.
maxProjectWithoutMotion("GCaMP_transient_enhanced", "Movement_Detection", "GCaMP_transient_MAX");

// (5) Visualization overlay: motion mask (red) over transient-enhanced GCaMP (gray)
makeMotionOverlay("Movement_Detection", "GCaMP_transient_enhanced", "GCaMP_transient_with_MotionOverlay");

// (6) Re-merge the split channels back into a 2-channel stack
run("Merge Channels...", "c1=[" + ch1Title + "] c2=[" + ch2Title + "] create");
rename("2PStack_GCaMP_registeredMerged");


// ======================================================================
// Helper functions (small refactors, no change in logic)
// ======================================================================

function to8Bit(title) {
    selectWindow(title);
    run("8-bit");
}

function maxProjectWithoutMotion(signalTitle, maskTitle, outMaxTitle) {
    // Computes (signal - mask) and creates a max intensity projection from the result.
    // Moving pixels (mask=255) are suppressed.
    to8Bit(signalTitle);

    run("Calculator Plus",
        "i1=" + signalTitle + " i2=" + maskTitle +
        " operation=[Subtract: i2 = (i1-i2) x k1 + k2] k1=1 k2=0 create");

    selectWindow("Result");
    run("Z Project...", "projection=[Max Intensity]");
    rename(outMaxTitle);
    run("Grays");

    to8Bit(signalTitle);

    close("Result");
}

function makeMotionOverlay(maskTitle, signalTitle, outTitle) {
    // Creates a composite visualization: mask in red over signal in grayscale.
    // No duplicates used.
    to8Bit(signalTitle);

    run("Merge Channels...", "c1=[" + maskTitle + "] c2=[" + signalTitle + "] create");
    rename(outTitle);
    run("Make Composite");
    Stack.setChannel(1); run("Red");
    Stack.setChannel(2); run("Grays");
}


// ======================================================================
// Core processing functions
// ======================================================================

function Flowtest(targetTitle) {
    // Motion mask creation using optic flow + transient enhancement of the flow magnitude

    selectWindow(targetTitle);
    nTarget = nSlices;
    width   = getWidth();
    height  = getHeight();

    // Working copy for optic flow (downsampled in time)
    run("Duplicate...", "title=move duplicate");
    run("Size...", "width=" + width + " height=" + height + " depth=" + (nTarget / 16) + " constrain average interpolation=Bicubic");

    // Optic flow computation (creates e.g. "move optic flow" and "*flow vectors")
    run("Gaussian Window MSE", "sigma=1 maximal_distance=3");
    close("*flow vectors");

    selectWindow("move optic flow");
    rename("move_optic_flow");
    run("32-bit");

    // Emphasize fast changes in optic flow (motion transients)
    transientEnhance("move_optic_flow", 10, 0, 8, "Flow_transient");

    // Clean up optic flow image (not needed afterwards)
    selectWindow("move_optic_flow");
    close();

    // Threshold + morphology to create a robust binary motion mask
    selectWindow("Flow_transient");
    run("Make Binary", "method=Huang background=Dark");

    for (i = 0; i < 5; i++)  run("Erode",  "stack");//5;14
    for (i = 0; i < 18; i++) run("Dilate", "stack");//18;45

    // Upsample back to original time resolution
    run("Size...", "width=" + width + " height=" + height + " depth=" + nTarget +
        " constrain average interpolation=Bilinear");

    // Smooth and normalize before final binarization
    run("Gaussian Blur 3D...", "x=8 y=8 z=30");
    run("Enhance Contrast...", "saturated=0.01 normalize process_all use");

    run("32-bit");
    run("Make Binary", "method=Default background=Dark");

    // Optional inversion correction heuristic
    run("32-bit");
    v = valueCheck();
    if (v > 125) {
        run("Multiply...", "value=-1 stack");
        run("Add...", "value=255 stack");
    }

    run("8-bit");
    rename("AResult");

    // Close remaining temporary window(s)
    close("Flow_transient");
    close("move");
}

function transientEnhance(sourceTitle, XYB1, XYB2, ZB, outTitle) {
    // Transient enhancement (high-pass-like):
    // - Work on a temporary copy (keeps the input stack unchanged).
    // - Create a temporally smoothed baseline and subtract it (implemented via invert+add).
    // - Normalize and clip to a defined range.

    selectWindow(sourceTitle);
    run("Duplicate...", "title=__tmp_fast duplicate");
    selectWindow("__tmp_fast");
    run("32-bit");

    // Spatial denoise
    run("Gaussian Blur 3D...", "x=" + XYB1 + " y=" + XYB1 + " z=0");

    // Create slow baseline estimate
    run("Duplicate...", "title=__tmp_slow duplicate");
    selectWindow("__tmp_slow");
    run("Gaussian Blur 3D...", "x=" + XYB2 + " y=" + XYB2 + " z=" + ZB);
    run("Invert", "stack");

    // Combine fast and inverted slow component -> emphasizes fast events
    run("Calculator Plus", "i1=__tmp_fast i2=__tmp_slow operation=[Add: i2 = (i1+i2) x k1 + k2] k1=0.5 k2=0 create");

    close("__tmp_fast");
    close("__tmp_slow");

    selectWindow("Result");
    rename(outTitle);

    // Normalize to a stable display/analysis range
    normalizeChannel("0.01", "0.4", "0", "1");
    run("Multiply...", "value=1.667 stack");
    setMinAndMax(0, 1);
    run("Grays");
}

function normalizeChannel(Sat, Sub, Min, Max) {
    run("Enhance Contrast...", "saturated=" + Sat + " normalize process_all use");
    run("Subtract...", "value=" + Sub + " stack");
    run("Min...", "value=" + Min + " stack");
    run("Max...", "value=" + Max + " stack");
    resetMinAndMax();
}

function valueCheck() {
    // Reduce to 1x1x1 (averaged) and read pixel value
    run("Scale...", "x=- y=- z=- width=1 height=1 depth=1 interpolation=Bilinear average process create title=Pixel");
    v = getPixel(0, 0);
    close("Pixel");
    return v;
}