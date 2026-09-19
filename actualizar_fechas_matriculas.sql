-- ============================================================
-- Script MEJORADO: distribución con días 10, 20 y 30
-- dentro de cada mes de forma cíclica por id_matricula
-- ============================================================

BEGIN TRANSACTION;

UPDATE MAT_Matriculas
SET fecha_matricula = CASE
    -- Mes según (id_matricula % 12) + ajuste de grupo
    -- Día según (id_matricula % 3): 0 -> 10, 1 -> 20, 2 -> 30
    WHEN ((id_matricula - 1) / 3) % 12 = 0 THEN  -- Enero: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-01-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-01-20'
             ELSE '2026-01-30' END
    WHEN ((id_matricula - 1) / 3) % 12 = 1 THEN  -- Febrero: días 10,20 (no 30)
        CASE WHEN (id_matricula % 2) = 1 THEN '2026-02-10'
             ELSE '2026-02-20' END
    WHEN ((id_matricula - 1) / 3) % 12 = 2 THEN  -- Marzo: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-03-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-03-20'
             ELSE '2026-03-30' END
    WHEN ((id_matricula - 1) / 3) % 12 = 3 THEN  -- Abril: días 10,20 (max 30)
        CASE WHEN (id_matricula % 2) = 1 THEN '2026-04-10'
             ELSE '2026-04-20' END
    WHEN ((id_matricula - 1) / 3) % 12 = 4 THEN  -- Mayo: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-05-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-05-20'
             ELSE '2026-05-30' END
    WHEN ((id_matricula - 1) / 3) % 12 = 5 THEN  -- Junio: días 10,20 (max 30)
        CASE WHEN (id_matricula % 2) = 1 THEN '2026-06-10'
             ELSE '2026-06-20' END
    WHEN ((id_matricula - 1) / 3) % 12 = 6 THEN  -- Julio: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-07-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-07-20'
             ELSE '2026-07-30' END
    WHEN ((id_matricula - 1) / 3) % 12 = 7 THEN  -- Agosto: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-08-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-08-20'
             ELSE '2026-08-30' END
    WHEN ((id_matricula - 1) / 3) % 12 = 8 THEN  -- Septiembre: días 10,20 (max 30)
        CASE WHEN (id_matricula % 2) = 1 THEN '2026-09-10'
             ELSE '2026-09-20' END
    WHEN ((id_matricula - 1) / 3) % 12 = 9 THEN  -- Octubre: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-10-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-10-20'
             ELSE '2026-10-30' END
    WHEN ((id_matricula - 1) / 3) % 12 = 10 THEN  -- Noviembre: días 10,20 (max 30)
        CASE WHEN (id_matricula % 2) = 1 THEN '2026-11-10'
             ELSE '2026-11-20' END
    WHEN ((id_matricula - 1) / 3) % 12 = 11 THEN  -- Diciembre: días 10,20,30
        CASE WHEN (id_matricula % 3) = 1 THEN '2026-12-10'
             WHEN (id_matricula % 3) = 2 THEN '2026-12-20'
             ELSE '2026-12-30' END
END;

-- Verificar distribución final
PRINT '=== DISTRIBUCION DE FECHAS DE MATRICULA ===';
SELECT 
    DATENAME(MONTH, fecha_matricula) AS mes_nombre,
    MONTH(fecha_matricula)           AS mes_num,
    DAY(fecha_matricula)             AS dia,
    COUNT(*)                         AS cantidad_matriculas
FROM MAT_Matriculas
GROUP BY MONTH(fecha_matricula), DAY(fecha_matricula), DATENAME(MONTH, fecha_matricula)
ORDER BY mes_num, dia;

PRINT '=== TOTAL POR MES ===';
SELECT 
    DATENAME(MONTH, fecha_matricula) AS mes,
    MONTH(fecha_matricula)           AS mes_num,
    COUNT(*)                         AS total_mes
FROM MAT_Matriculas
GROUP BY MONTH(fecha_matricula), DATENAME(MONTH, fecha_matricula)
ORDER BY mes_num;

COMMIT TRANSACTION;
