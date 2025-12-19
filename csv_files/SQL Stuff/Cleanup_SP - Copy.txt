DROP PROCEDURE IF EXISTS sp_clean_incident_records;
DELIMITER $$

CREATE PROCEDURE sp_clean_incident_records()
BEGIN
    /* ===========================================================
       GLOBAL DECLARATIONS
    =========================================================== */

    -- Timing
    DECLARE v_start_time      DATETIME(6);
    DECLARE v_end_time        DATETIME(6);

    -- Batching
    DECLARE v_batch_start_id  INT;
    DECLARE v_batch_end_id    INT;
    DECLARE v_max_id          INT;
    DECLARE v_batch_size      INT DEFAULT 500;

    -- Row counters
    DECLARE v_rows            INT DEFAULT 0;
    DECLARE v_phase1_rows     INT DEFAULT 0;
    DECLARE v_phase2_rows     INT DEFAULT 0;
    DECLARE v_phase3_rows     INT DEFAULT 0;
    DECLARE v_phase4_rows     INT DEFAULT 0;
    DECLARE v_phase5_rows     INT DEFAULT 0;
    DECLARE v_phase6_rows     INT DEFAULT 0;
    DECLARE v_phase7_rows     INT DEFAULT 0;

    -- Start timing
    SET v_start_time = NOW(6);

    /* ===========================================================
       INITIALIZE BATCH RANGE
    =========================================================== */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);

    /* ===========================================================
       PHASE 1 — SYMBOL CLEANUP
       (@ ? a, 0 ? o, ^ ? i, # ? e)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO
        
        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        UPDATE incident_records
        SET 
            str_name = REPLACE(REPLACE(REPLACE(REPLACE(str_name, '@','a'),'0','o'),'^','i'),'#','e'),
            suburb   = REPLACE(REPLACE(REPLACE(REPLACE(suburb, '@','a'),'0','o'),'^','i'),'#','e')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND (str_name REGEXP '[@0^#]' OR suburb REGEXP '[@0^#]');

        SET v_rows = ROW_COUNT();
        SET v_phase1_rows = v_phase1_rows + v_rows;

        SET v_batch_start_id = v_batch_end_id + 1;
    END WHILE;

    SELECT 'Phase 1 - Symbol cleanup' AS Phase, v_phase1_rows AS RowsAffected;

    /* Reset batch range for next phase */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);

    /* ===========================================================
       PHASE 2 — SUFFIX EXPANSION
       (Road, Street, Avenue, Lane, Lne, etc.)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO
        
        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        /* ------------------------------
           Road
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\srd\\.?\\b', ' Road')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Street
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sst(r)?\\b', ' Street')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Avenue
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\save\\.?\\b', ' Avenue')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Close
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scl\\b', ' Close')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Terrace
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ster(race)?\\b', ' Terrace')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Crescent
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scr(escent)?\\b', ' Crescent')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Circle
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\scir(cle)?\\b', ' Circle')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Square
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\ssq(uare)?\\b', ' Square')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Boulevard
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sblvd\\b', ' Boulevard')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Lane
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sla(ne)?\\b', ' Lane')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Lne ? Lane (NEW anomaly)
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\slne\\b', ' Lane')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Drive
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sdr\\.?\\b', ' Drive')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Extension
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sext(ension)?\\b', ' Extension')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Place
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\spl(ace)?\\b', ' Place')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Walk
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\swk\\b', ' Walk')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* ------------------------------
           Court
        ------------------------------ */
        UPDATE incident_records
        SET str_name = REGEXP_REPLACE(str_name, '(?i)\\sct\\b', ' Court')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase2_rows = v_phase2_rows + ROW_COUNT();

        /* Move to next batch */
        SET v_batch_start_id = v_batch_end_id + 1;

    END WHILE;

    SELECT 'Phase 2 - Suffix expansion' AS Phase, v_phase2_rows AS RowsAffected;

    /* Reset batch range for next phase */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);

    /* ===========================================================
       PHASE 3 — PROPERCASE
       (Apply ProperCase to str_name and suburb)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO
        
        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        UPDATE incident_records
        SET 
            str_name = ProperCase(str_name),
            suburb   = ProperCase(suburb)
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;

        SET v_rows = ROW_COUNT();
        SET v_phase3_rows = v_phase3_rows + v_rows;

        SET v_batch_start_id = v_batch_end_id + 1;

    END WHILE;

    SELECT 'Phase 3 - ProperCase applied' AS Phase, v_phase3_rows AS RowsAffected;

    /* Reset batch range for next phase */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);

    /* ===========================================================
       PHASE 4 — PREFIX FIXES
       (St., Dr., Mt. — capitalize first letter after prefix)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO
        
        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        UPDATE incident_records
        SET str_name = CASE
            WHEN LEFT(str_name, 3) = 'St.' THEN CONCAT('St.', UPPER(SUBSTRING(str_name, 4, 1)), SUBSTRING(str_name, 5))
            WHEN LEFT(str_name, 3) = 'Dr.' THEN CONCAT('Dr.', UPPER(SUBSTRING(str_name, 4, 1)), SUBSTRING(str_name, 5))
            WHEN LEFT(str_name, 3) = 'Mt.' THEN CONCAT('Mt.', UPPER(SUBSTRING(str_name, 4, 1)), SUBSTRING(str_name, 5))
            ELSE str_name
        END
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;

        SET v_rows = ROW_COUNT();
        SET v_phase4_rows = v_phase4_rows + v_rows;

        SET v_batch_start_id = v_batch_end_id + 1;

    END WHILE;

    SELECT 'Phase 4 - Prefix fixes (St., Dr., Mt.)' AS Phase, v_phase4_rows AS RowsAffected;

    /* Reset batch range for next phase */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);

    /* ===========================================================
       PHASE 5 — LITERAL “FUNNIES”
       (Case fixes, route fixes, Stormvoël, Goldshmidt, Modderdam)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO

        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        /* ------------------------------
           Basic case corrections
        ------------------------------ */
        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(m','(M')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(n','(N')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(r','(R')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();


        /* ------------------------------
           Route number corrections
        ------------------------------ */
        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M1O)','(M10)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Rio2)','(R102)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R1o2)','(R102)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R1O2)','(R102)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R31O)','(R310)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M17O)','(M170)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi8)','(M18)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M1o)','(M10)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi7o)','(M170)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Rd (','Road (')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M6i)','(M61)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M17o)','(M170)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R31o)','(R310)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

      UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(R3io)','(R310)') -- added extra
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

      UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(M4i)','(M41)') -- added extra
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();




        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'N2/m3','N2/M3')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mi7)','(M17)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'(Mio)','(M10)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();


        /* ------------------------------
           Named road corrections
        ------------------------------ */
        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'D.f.malan','DF Malan')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'H.l.de Villiers','HL de Villiers')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();


        /* ------------------------------
           NEW: Goldshmidt fix
        ------------------------------ */
        UPDATE incident_records 
        SET Str_Name = REPLACE(Str_Name,'M.h.goldshmidt','MH.Goldshmidt')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();


        /* ------------------------------
           NEW: Modderdam East-West fix
        ------------------------------ */
        UPDATE incident_records 
        SET Str_Name = REPLACE(Str_Name,'Modderdam Road East-west (M10)',
                                           'Modderdam Road East - West (M10)')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();


        /* ------------------------------
           Stormvoël encoding repair
        ------------------------------ */
        UPDATE incident_records
        SET Str_Name = REPLACE(Str_Name, 'StormvoÃ«l', CONCAT('Stormvo', CHAR(235), 'l'))
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND Str_Name LIKE '%StormvoÃ«l%';
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        /* ------------------------------
           Missing named road corrections
        ------------------------------ */
        UPDATE incident_records 
        SET Str_Name = REPLACE(Str_Name,'Pres.reitz Street','Pres.Reitz Street')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records 
        SET Str_Name = REPLACE(Str_Name,'Pres.brand Street','Pres.Brand Street')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();

        UPDATE incident_records 
        SET Str_Name = REPLACE(Str_Name,'Pres.steyn Street','Pres.Steyn Street')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase5_rows = v_phase5_rows + ROW_COUNT();


        /* Move to next batch */
        SET v_batch_start_id = v_batch_end_id + 1;

    END WHILE;

    SELECT 'Phase 5 - Literal funnies & special fixes' AS Phase, v_phase5_rows AS RowsAffected;

    /* Reset batch range for next phase */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);

    /* ===========================================================
       PHASE 6 — ORDINAL FIXES
       (1st, 10th, 11th, 50th, I?1 patterns, hex-based corrections)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO

        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        /* ------------------------------
           Direct literal ordinal fixes
        ------------------------------ */
        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'i4th','14th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'I4th','14th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'I6th','16th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'1oth','10th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'Iith','11th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'5ist','51st')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'1ith','11th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        UPDATE incident_records SET Str_Name = REPLACE(Str_Name,'5oth','50th')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();


        /* ------------------------------
           General rule:
           I + digit ordinals (I2th ? 12th, I3th ? 13th, etc.)
           Using hex pattern: 49 = 'I'
        ------------------------------ */
        UPDATE incident_records
        SET Str_Name = CONCAT('1', SUBSTRING(Str_Name, 2))
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND HEX(Str_Name) REGEXP '^49[30-39]';
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();


        /* ------------------------------
           Special-case corrections
        ------------------------------ */

        -- Ist ? 1st Avenue
        UPDATE incident_records
        SET Str_Name = '1st Avenue'
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND HEX(Str_Name) LIKE '497374%';
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        -- Iith ? 11th Avenue
        UPDATE incident_records
        SET Str_Name = '11th Avenue'
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND HEX(Str_Name) LIKE '49697468%';
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();

        -- Ioth ? 10th Avenue
        UPDATE incident_records
        SET Str_Name = '10th Avenue'
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND HEX(Str_Name) LIKE '496F7468%';
        SET v_phase6_rows = v_phase6_rows + ROW_COUNT();


        /* Move to next batch */
        SET v_batch_start_id = v_batch_end_id + 1;

    END WHILE;

    SELECT 'Phase 6 - Ordinal fixes' AS Phase, v_phase6_rows AS RowsAffected;

    /* Reset batch range for next phase */
    SET v_batch_start_id = (SELECT MIN(id) FROM incident_records);
    SET v_max_id         = (SELECT MAX(id) FROM incident_records);


    /* ===========================================================
       PHASE 7 — SUBURB ANOMALIES (BELHAR EXT)
    =========================================================== */

    WHILE v_batch_start_id IS NOT NULL AND v_batch_start_id <= v_max_id DO

        SET v_batch_end_id = v_batch_start_id + v_batch_size - 1;

        /* ------------------------------
           Belhar Ext I ? 1
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I','Belhar Ext 1')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id
          AND Suburb LIKE 'Belhar Ext I%';
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           1i ? 11
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext 1i','Belhar Ext 11')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           1o ? 10
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext 1o','Belhar Ext 10')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           2i ? 21
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext 2i','Belhar Ext 21')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           2o ? 20
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext 2o','Belhar Ext 20')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           Ix ? 1x (I1 ? 11, I2 ? 12, … I9 ? 19)
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I1','Belhar Ext 11')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I2','Belhar Ext 12')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I3','Belhar Ext 13')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I4','Belhar Ext 14')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I5','Belhar Ext 15')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I6','Belhar Ext 16')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I7','Belhar Ext 17')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I8','Belhar Ext 18')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext I9','Belhar Ext 19')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           Ii ? 11
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext Ii','Belhar Ext 11')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();

        /* ------------------------------
           Io ? 10
        ------------------------------ */
        UPDATE incident_records
        SET Suburb = REPLACE(Suburb,'Belhar Ext Io','Belhar Ext 10')
        WHERE id BETWEEN v_batch_start_id AND v_batch_end_id;
        SET v_phase7_rows = v_phase7_rows + ROW_COUNT();


        /* Move to next batch */
        SET v_batch_start_id = v_batch_end_id + 1;

    END WHILE;

    SELECT 'Phase 7 - Suburb Belhar Ext cleanup' AS Phase, v_phase7_rows AS RowsAffected;


    /* ===========================================================
       FINAL TIMING SUMMARY
    =========================================================== */

    SET v_end_time = NOW(6);

    SELECT 
        TIMESTAMPDIFF(MICROSECOND, v_start_time, v_end_time) / 1000 AS ExecutionTime_ms,
        v_start_time AS Started,
        v_end_time   AS Finished;


END$$

DELIMITER ;

   SELECT 'Cleanup SP Sucessfully Created' AS Message ;