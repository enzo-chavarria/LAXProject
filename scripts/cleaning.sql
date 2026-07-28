---PASSENGER TRAFFIC
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

--check for duplicate rows
SELECT ReportPeriod, Terminal, Arrival_Departure, Domestic_International, COUNT(*) AS occurrences
FROM `LAX_data.passenger_combined`
GROUP BY ReportPeriod, Terminal, Arrival_Departure, Domestic_International
HAVING COUNT(*) > 1;

---GROUND TRANSPORTATION
--check for null rows
SELECT COUNT(*) AS fully_null_rows
FROM `LAX_data.gt_traffic_combined`
WHERE ReportPeriod IS NULL
  AND OperatorType IS NULL
  AND Monthly_Trips IS NULL;

--check for null in columns
SELECT
  COUNTIF(ReportPeriod IS NULL) AS null_report_period,
  COUNTIF(OperatorType IS NULL) AS null_operator_type,
  COUNTIF(Monthly_Trips IS NULL) AS null_monthly_trips
FROM `LAX_data.gt_traffic_combined`;

--check for duplicate rows
SELECT ReportPeriod, OperatorType, COUNT(*) AS occurrences
FROM `LAX_data.gt_traffic_combined`
GROUP BY ReportPeriod, OperatorType
HAVING COUNT(*) > 1;
