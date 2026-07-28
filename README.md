# LAX Vehicle Trips per Passenger: Monitoring Congestion During the Airfield & Terminal Modernization Program

## Overview
This project analyzes vehicle traffic and passenger volume at Los Angeles International Airport (LAX) to build a monitoring framework for curbside and roadway congestion during LAX's ongoing Airfield & Terminal Modernization Program (ATMP).This is designed as a standing KPI, a metric LAWA could track on an ongoing basis to assess whether capital improvement projects are succeeding at reducing per-passenger vehicle congestion as construction progresses.

## Business Task
LAX is in the midst of a roughly $30 billion capital improvement program, including the SkyLink , the Terminal 5 rebuild, Tom Bradley International Terminal modernization, and major roadway reconfiguration (the ATMP Roadway Improvements Project). These projects are intended to reduce congestion and improve passenger access over the long term, but construction itself can temporarily disrupt traffic patterns, displace curbside activity, and shift how passengers and vehicles move through the airport in the near term.

This analysis addresses the following question:

> **How have passenger volume and ground vehicle traffic changed relative to one another during LAX's active construction period, and can a normalized metric (vehicle trips per passenger) meaningfully track congestion pressure over time?**


## Context: LAX's Capital Improvement Program
Key components of the ATMP relevant to this analysis:
- **SkyLink:** an elevated automated people mover connecting terminals, parking, and the Metro rail system; entered passenger-free testing in April 2026
- **Terminal 5 rebuild:** The terminal was shut down on Oct 28, 2025 for demolition and reconstruction, targeted for completion in late 2027
- **Tom Bradley International Terminal modernization:** construction began January 2026
- **ATMP Roadway Improvements Project:** Started mid 2023, the construction of 4.4 miles of replaced and reconfigured roadways to reduce congestion on Sepulveda Boulevard and creation of dedicated airport roadways for airport traffic queues headed to LAX’s Central Terminal Area (CTA).

## Data Sources
- **Passenger Traffic By Terminal:** monthly passenger counts by terminal, arrival/departure, and domestic/international status. Sourced from LA's Open Data Portal (2006–Oct 2023) and LAWA's monthly "Passenger Traffic Comparison by Terminal" PDF reports (Nov 2023–present).
- **Ground Transportation Monthly Report:** monthly vehicle trip counts by operator category, sourced from LAWA's Ground Transportation Statistics PDF archive.
- **Time period covered:** June 2022 – present

## Tools Used
- **Google BigQuery (SQL)** 
- **Python** 
- **Tableau Public**


# Process

## Data Collection

1. Exported Passenger Traffic by Terminal as a csv from [data.lacity.org](https://data.lacity.org/Transportation/Los-Angeles-International-Airport-Passenger-Traffi/g3qu-7q2u/about_data).
2. Removed rows 671 and below to narrow the scope to June 2022 - June 2026.
3. Exported individual pdf files for LAX Passenger Traffic Comparison by Terminal from [lawa.org](https://www.lawa.org/lawa-investor-relations/statistics-for-lax/volume-of-air-traffic) (December 2023 - June 2026). It is worth noting that the data for March 2026 was not publicly available, and therefore was not included in this analysis.
4.
