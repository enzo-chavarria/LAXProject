--count fully null rows
SELECT COUNT(*) AS fully_null_rows
FROM `LAX_data.passenger_combined`
WHERE DataExtractDate IS NULL
  AND ReportPeriod IS NULL
  AND Terminal IS NULL
  AND Arrival_Departure IS NULL
  AND Domestic_International IS NULL
  AND Passenger_Count IS NULL;

--delete fully null rows
DELETE FROM `LAX_data.passenger_combined`
WHERE DataExtractDate IS NULL
  AND ReportPeriod IS NULL
  AND Terminal IS NULL
  AND Arrival_Departure IS NULL
  AND Domestic_International IS NULL
  AND Passenger_Count IS NULL;

--check distinct values in categorical columns
SELECT DISTINCT Terminal FROM `LAX_data.passenger_combined` ORDER BY Terminal;
SELECT DISTINCT Arrival_Departure FROM `LAX_data.passenger_combined` ORDER BY Arrival_Departure;
SELECT DISTINCT Domestic_International FROM `LAX_data.passenger_combined` ORDER BY Domestic_International;
