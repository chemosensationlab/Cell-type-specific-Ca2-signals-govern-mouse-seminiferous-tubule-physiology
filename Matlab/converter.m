%%% initial matlab masks all have the same value. This gives each labeled
%%% object a different value, so cellpose recognizes the different masks


folder = dir();

for i = 3:18
    img = imread("Training_data\masks\"+folder(i).name+"");
    img = double(img);
    img(img == 1) = 255;


binaryMask = img;               
labelMatrix = bwlabel(binaryMask,8);  
numObjects = max(labelMatrix(:));

if numObjects <= 255
    labeledMask = uint8(labelMatrix);
else
    labeledMask = uint16(labelMatrix);
end

    fname = [""+folder(i).name(1:end-4)+"s.tif"];
    imwrite(labeledMask, fname);
end
