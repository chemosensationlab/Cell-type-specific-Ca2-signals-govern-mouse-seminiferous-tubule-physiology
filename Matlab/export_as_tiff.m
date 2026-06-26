varsToSave = {maskedImage, BW};
names = {'masked_raw', 'mask'}; 

for i = 1:length(varsToSave)
    fname = [names{i}, '.tif'];
    imwrite(varsToSave{i}, fname);
    fprintf('Saved: %s\n', fname);
end


