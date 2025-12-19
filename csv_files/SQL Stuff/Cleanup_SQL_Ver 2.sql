USE incidents;

SET NAMES utf8mb4;

-- 1. Clean symbols
UPDATE incident_records
SET str_name = REPLACE(REPLACE(REPLACE(REPLACE(str_name, '@', 'a'), '0', 'o'), '^', 'i'), '#', 'e'),
    suburb   = REPLACE(REPLACE(REPLACE(REPLACE(suburb, '@', 'a'), '0', 'o'), '^', 'i'), '#', 'e')
WHERE str_name REGEXP '[@0^#]' OR suburb REGEXP '[@0^#]';

-- 2. Expand suffixes (whole-word, only after whitespace, abbreviations + full words + dotted variants)

-- Road
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\srd\\b', ' Road');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\srd\\.\\b', ' Road');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sroad\\b', ' Road');

-- Street
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sst\\b', ' Street');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sstr\\b', ' Street');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sstreet\\b', ' Street');

-- Avenue
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\save\\b', ' Avenue');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\save\\.\\b', ' Avenue');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\savenue\\b', ' Avenue');

-- Close
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scl\\b', ' Close');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sclose\\b', ' Close');

-- Terrace
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ster\\b', ' Terrace');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sterrace\\b', ' Terrace');

-- Crescent
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scr\\b', ' Crescent');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\screscent\\b', ' Crescent');

-- Circle
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scir\\b', ' Circle');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scircle\\b', ' Circle');

-- Square
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ssq\\b', ' Square');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ssquare\\b', ' Square');

-- Boulevard
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sblvd\\b', ' Boulevard');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sboulevard\\b', ' Boulevard');

-- Lane
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sla\\b', ' Lane');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\slane\\b', ' Lane');

-- Drive
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sdr\\b', ' Drive');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sdr\\.\\b', ' Drive');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sdrive\\b', ' Drive');

-- Extension
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sext\\b', ' Extension');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sextension\\b', ' Extension');

-- Place
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\spl\\b', ' Place');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\splace\\b', ' Place');

-- Walk
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\swk\\b', ' Walk');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\swalk\\b', ' Walk');

-- Court
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sct\\b', ' Court');
UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scourt\\b', ' Court');

-- 3. Apply ProperCase last (for overall consistency)
UPDATE incident_records
SET str_name = ProperCase(str_name),
    suburb   = ProperCase(suburb);

-- 4. Fix prefixes (capitalize first word after St., Dr., Mt.) running it here after 3 is when it works
-- First ensure prefix is correct
UPDATE incident_records
SET str_name = CASE
    WHEN LEFT(str_name, 3) = 'St.' THEN CONCAT('St.', UPPER(SUBSTRING(str_name, 4, 1)), SUBSTRING(str_name, 5))
    WHEN LEFT(str_name, 3) = 'Dr.' THEN CONCAT('Dr.', UPPER(SUBSTRING(str_name, 4, 1)), SUBSTRING(str_name, 5))
    WHEN LEFT(str_name, 3) = 'Mt.' THEN CONCAT('Mt.', UPPER(SUBSTRING(str_name, 4, 1)), SUBSTRING(str_name, 5))
    ELSE str_name
END;


-- 5. Update Funnies (literal replacements)
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(m', '(M');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(n', '(N');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(r', '(R');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M1O)', '(M10)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Rio2)', '(R102)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R1o2)', '(R102)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R1O2)', '(R102)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R31O)', '(R310)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M17O)', '(M170)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi8)', '(M18)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M1o)', '(M10)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi7o)', '(M170)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Rd (', 'Road (');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M6i)', '(M61)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M17o)', '(M170)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R31o)', '(R310)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'N2/m3', 'N2/M3');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi7)', '(M17)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mio)', '(M10)');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'D.f.malan', 'DF Malan');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'H.l.de Villiers', 'HL de Villiers Road');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M6o)', '(M60)');
UPDATE incident_records
SET Str_Name = REGEXP_REPLACE(Str_Name, '(?i)De L''hermit Avenue', 'De L''Hermit Avenue') WHERE Str_Name REGEXP '(?i)De L''hermit Avenue';
UPDATE incident_records SET Str_Name = 'O''Okiep Road'WHERE Str_Name = 'O''okiep Road';
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Simon Van Der Strel Freeway (M3)', 'Simon Van Der Stel Freeway (M3)');

SET NAMES utf8mb4; -- Even Though I have set it at the beginning of the script it seems that I need to set it again before this update as well
UPDATE incident_records
SET Str_Name = REPLACE(Str_Name, 'Stormvoël', CONCAT('Stormvo', CHAR(235), 'l'))
WHERE Str_Name LIKE '%Stormvoël%';

UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Pres.reitz Street', 'Pres.Reitz Street');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Pres.brand Street', 'Pres.Brand Street');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Pres.steyn Street', 'Pres.Steyn Street');

UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Modderdam Road East-west (M10)', 'Modderdam Road East - West (M10)');

UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R3io)', '(R310)');

UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'i4th', '14th');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'I4th', '14th');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'I6th', '16th');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'1oth', '10th');
UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Iith', '11th');

UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'5ist', '51st');

UPDATE incident_records
SET Str_Name = CONCAT('1', SUBSTRING(Str_Name, 2))
WHERE Str_Name REGEXP '^I[0-9]';

UPDATE incident_records
SET Str_Name = REPLACE(Str_Name, 'Ist', '1st')
WHERE Str_Name LIKE 'Ist%';


-- Fix Ist -> 1st
UPDATE incident_records
SET Str_Name = '1st Avenue'
WHERE HEX(Str_Name) LIKE '497374%';

-- Fix Iith -> 11th
UPDATE incident_records
SET Str_Name = '11th Avenue'
WHERE HEX(Str_Name) LIKE '49697468%';

-- Fix Ioth -> 10th
UPDATE incident_records
SET Str_Name = '10th Avenue'
WHERE HEX(Str_Name) LIKE '496F7468%';

-- General rule: I + digit ordinals (I2th -> 12th, I3th -> 13th, etc.)
UPDATE incident_records
SET Str_Name = CONCAT('1', SUBSTRING(Str_Name, 2))
WHERE HEX(Str_Name) REGEXP '^49[30-39]';

UPDATE incident_records
SET Str_Name = REPLACE(Str_Name, '1ith', '11th')
WHERE Str_Name LIKE '1ith%';

UPDATE incident_records
SET Str_Name = REPLACE(Str_Name, '5oth', '50th');

-- Suburb Anomolies

-- Single I -> 1
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I', 'Belhar Ext 1')
WHERE Suburb LIKE 'Belhar Ext I%';

-- 1i -> 11
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext 1i', 'Belhar Ext 11')
WHERE Suburb LIKE 'Belhar Ext 1i%';

-- 1o -> 10
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext 1o', 'Belhar Ext 10')
WHERE Suburb LIKE 'Belhar Ext 1o%';

-- 2i -> 21
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext 2i', 'Belhar Ext 21')
WHERE Suburb LIKE 'Belhar Ext 2i%';

-- 2o -> 20
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext 2o', 'Belhar Ext 20')
WHERE Suburb LIKE 'Belhar Ext 2o%';

-- I1 -> 11
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I1', 'Belhar Ext 11')
WHERE Suburb LIKE 'Belhar Ext I1%';

-- I2 -> 12
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I2', 'Belhar Ext 12')
WHERE Suburb LIKE 'Belhar Ext I2%';

-- I3 -> 13
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I3', 'Belhar Ext 13')
WHERE Suburb LIKE 'Belhar Ext I3%';

-- I4 -> 14
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I4', 'Belhar Ext 14')
WHERE Suburb LIKE 'Belhar Ext I4%';

-- I5 -> 15
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I5', 'Belhar Ext 15')
WHERE Suburb LIKE 'Belhar Ext I5%';

-- I6 -> 16
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I6', 'Belhar Ext 16')
WHERE Suburb LIKE 'Belhar Ext I6%';

-- I7 -> 17
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I7', 'Belhar Ext 17')
WHERE Suburb LIKE 'Belhar Ext I7%';

-- I8 -> 18
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I8', 'Belhar Ext 18')
WHERE Suburb LIKE 'Belhar Ext I8%';

-- I9 -> 19
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext I9', 'Belhar Ext 19')
WHERE Suburb LIKE 'Belhar Ext I9%';

-- Ii -> 11
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext Ii', 'Belhar Ext 11')
WHERE Suburb LIKE 'Belhar Ext Ii%';

-- Io -> 10
UPDATE incident_records
SET Suburb = REPLACE(Suburb, 'Belhar Ext Io', 'Belhar Ext 10')
WHERE Suburb LIKE 'Belhar Ext Io%';



