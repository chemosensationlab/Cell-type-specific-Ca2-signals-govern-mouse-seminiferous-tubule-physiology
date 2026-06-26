%% Initialisierung
% folderPath = 'D:\Christoph\Fischoeder_et_al\Results'; % Pfad anpassentrt
folderPath = '.';
filePattern = fullfile(folderPath, '*.xls*');
files = dir(filePattern);

% Definition der Nachbarschaften (k-Werte)
kValues = [3, 5, 7, 9];

% Speicher für die Gesamtdatenbank (Tabelle)
dbTable = table();
dbTable2 = table();
dbTable3 = table();
for i = 1:length(files)
    fileName = files(i).name;
    fullFileName = fullfile(folderPath, fileName);
    
    fprintf('Verarbeite Datei: %s...\n', fileName);
    
    % 1. Daten einlesen
    % Center of Homogeneous Mass: Spalten A-C (XYZ)
    try
        coordData = readtable(fullFileName, 'Sheet', 'Center of Homogeneous Mass', 'Range', 'A:C');
        coords = table2array(coordData);
        
        % Volume: Spalte A
        volData = readtable(fullFileName, 'Sheet', 'Volume', 'Range', 'A:A');
        volumes = table2array(volData);
    catch ME
        fprintf('Fehler beim Lesen von %s: %s\n', fileName, ME.message);
        continue;
    end
    
    % Falls die Tabellen unterschiedlich lang sind, kürzen wir auf das Minimum
    numRows = min(size(coords, 1), size(volumes, 1));
    coords = coords(1:numRows, :);
    volumes = volumes(1:numRows, :);
    
    % 2. Nearest Neighbor Berechnung
    tempResults = table(repmat({fileName}, numRows, 1), volumes, 'VariableNames', {'FileName', 'Volume'});
    
    for k = kValues
        % knnsearch gibt Distanzen zurück. 'k+1', weil der Punkt selbst 
        % (Distanz 0) mitgezählt wird, wir wollen aber die echten Nachbarn.
        [~, dists] = knnsearch(coords, coords, 'K', k + 1);
        
        % Berechne den Durchschnitt der Distanzen (ohne die erste Spalte/Null-Distanz)
        meanDists = mean(dists(:, 2:end), 2);
        
        % Spalte zur temporären Tabelle hinzufügen
        colName = sprintf('MeanDist_k%d', k);
        tempResults.(colName) = meanDists;
    end
    
    % 3. Ergebnisse zur Datenbank hinzufügen
    dbTable = [dbTable; tempResults];
    
    % 4. Mittelwerte pro Datei berechnen und in Sheet 2 speichern
    % Wir berechnen den Mittelwert über alle numerischen Spalten dieser Datei
    summaryStats = groupsummary(tempResults, "FileName", "mean", ["Volume", "MeanDist_k3", "MeanDist_k5", "MeanDist_k7", "MeanDist_k9"]);
    dbTable2 = [dbTable2; summaryStats];
    summaryStats = groupsummary(tempResults, "FileName", "median", ["Volume", "MeanDist_k3", "MeanDist_k5", "MeanDist_k7", "MeanDist_k9"]);
    dbTable3 = [dbTable3; summaryStats];


    % In das zweite Sheet der Originaldatei schreiben
    
end

% 5. Globale Datenbank speichern
writetable(dbTable, fullfile(folderPath, 'GesamtDatenbank_Ergebnisse.xls'));
writetable(dbTable2, fullfile(folderPath, 'GesamtDatenbank_Ergebnisse_mean.xls'));
writetable(dbTable3, fullfile(folderPath, 'GesamtDatenbank_Ergebnisse_median.xls'));
fprintf('Fertig! Die Datenbank wurde gespeichert.\n');