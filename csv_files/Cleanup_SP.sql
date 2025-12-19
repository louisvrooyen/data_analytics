DROP PROCEDURE IF EXISTS sp_clean_incident_records;
DELIMITER $$

CREATE PROCEDURE sp_clean_incident_records()
BEGIN

    /* -----------------------------------------------------------
       1. Clean symbols (@ ? a, 0 ? o, ^ ? i, # ? e)
    ----------------------------------------------------------- */
    UPDATE incident_records
    SET 
        str_name = REPLACE(REPLACE(REPLACE(REPLACE(str_name, '@','a'),'0','o'),'^','i'),'#','e'),
        suburb   = REPLACE(REPLACE(REPLACE(REPLACE(suburb, '@','a'),'0','o'),'^','i'),'#','e')
    WHERE str_name REGEXP '[@0^#]' OR suburb REGEXP '[@0^#]';


    /* -----------------------------------------------------------
       2. Expand suffixes (regex whole-word)
    ----------------------------------------------------------- */
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\srd\\.?\\b', ' Road');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sst(r)?\\b', ' Street');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\save\\.?\\b', ' Avenue');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scl\\b', ' Close');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ster(race)?\\b', ' Terrace');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scr(escent)?\\b', ' Crescent');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scir(cle)?\\b', ' Circle');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ssq(uare)?\\b', ' Square');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sblvd\\b', ' Boulevard');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sla(ne)?\\b', ' Lane');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sdr\\.?\\b', ' Drive');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sext(ension)?\\b', ' Extension');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\spl(ace)?\\b', ' Place');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\swk\\b', ' Walk');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sct\\b', ' Court');
    UPDATE incident_records SET str_name = REGEXP_REPLACE(str_name, '(?i)\\slne\\b', ' Lane');


    /* -----------------------------------------------------------
       3. ProperCase
    ----------------------------------------------------------- */
    UPDATE incident_records
    SET 
        str_name = ProperCase(str_name),
        suburb   = ProperCase(suburb);


    /* -----------------------------------------------------------
       4. Prefix fixes (St., Dr., Mt.)
    ----------------------------------------------------------- */
    UPDATE incident_records
    SET str_name = CASE
        WHEN LEFT(str_name, 3) = 'St.' THEN CONCAT('St.', UPPER(SUBSTRING(str_name,4,1)), SUBSTRING(str_name,5))
        WHEN LEFT(str_name, 3) = 'Dr.' THEN CONCAT('Dr.', UPPER(SUBSTRING(str_name,4,1)), SUBSTRING(str_name,5))
        WHEN LEFT(str_name, 3) = 'Mt.' THEN CONCAT('Mt.', UPPER(SUBSTRING(str_name,4,1)), SUBSTRING(str_name,5))
        ELSE str_name
    END;


    /* -----------------------------------------------------------
       5. Literal “Funnies”
    ----------------------------------------------------------- */
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(m','(M');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(n','(N');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(r','(R');

    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M1O)','(M10)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Rio2)','(R102)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R1o2)','(R102)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R1O2)','(R102)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R31O)','(R310)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M17O)','(M170)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi8)','(M18)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M1o)','(M10)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi7o)','(M170)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Rd (','Road (');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M6i)','(M61)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M17o)','(M170)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R31o)','(R310)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'N2/m3','N2/M3');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi7)','(M17)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mio)','(M10)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'D.f.malan','DF Malan');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'H.l.de Villiers','HL de Villiers Road');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M6o)','(M60)');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R3io)','(R310)');

    /* Stormvoël encoding fix */
    UPDATE incident_records
    SET Str_Name = REPLACE(Str_Name, 'StormvoÃ«l', CONCAT('Stormvo', CHAR(235), 'l'))
    WHERE Str_Name LIKE '%StormvoÃ«l%';


    /* -----------------------------------------------------------
       6. Ordinal fixes (1st, 10th, 11th, 50th, etc.)
    ----------------------------------------------------------- */
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'i4th','14th');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'I4th','14th');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'I6th','16th');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'1oth','10th');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Iith','11th');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'5ist','51st');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'1ith','11th');
    UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'5oth','50th');

    /* I + digit ? 1 + digit */
    UPDATE incident_records
    SET Str_Name = CONCAT('1', SUBSTRING(Str_Name,2))
    WHERE HEX(Str_Name) REGEXP '^49[30-39]';

    /* Ist ? 1st */
    UPDATE incident_records
    SET Str_Name = '1st Avenue'
    WHERE HEX(Str_Name) LIKE '497374%';

    /* Iith ? 11th */
    UPDATE incident_records
    SET Str_Name = '11th Avenue'
    WHERE HEX(Str_Name) LIKE '49697468%';

    /* Ioth ? 10th */
    UPDATE incident_records
    SET Str_Name = '10th Avenue'
    WHERE HEX(Str_Name) LIKE '496F7468%';


    /* -----------------------------------------------------------
       7. Suburb: Belhar Ext cleanup
    ----------------------------------------------------------- */
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I','Belhar Ext 1') WHERE Suburb LIKE 'Belhar Ext I%';
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext 1i','Belhar Ext 11');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext 1o','Belhar Ext 10');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext 2i','Belhar Ext 21');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext 2o','Belhar Ext 20');

    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I1','Belhar Ext 11');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I2','Belhar Ext 12');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I3','Belhar Ext 13');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I4','Belhar Ext 14');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I5','Belhar Ext 15');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I6','Belhar Ext 16');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I7','Belhar Ext 17');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I8','Belhar Ext 18');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext I9','Belhar Ext 19');

    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext Ii','Belhar Ext 11');
    UPDATE incident_records SET Suburb = REPLACE(Suburb,'Belhar Ext Io','Belhar Ext 10');

END$$

DELIMITER ;