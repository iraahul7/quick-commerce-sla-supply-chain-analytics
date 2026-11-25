# Power BI DAX Measures & Executive Dashboard Specification

- **SLA Compliance %:** `DIVIDE(CALCULATE(COUNTROWS(Orders), Orders[is_sla_breach] = 0), COUNTROWS(Orders), 0)`
- **SLA Breach Rate %:** `DIVIDE(CALCULATE(COUNTROWS(Orders), Orders[is_sla_breach] = 1), COUNTROWS(Orders), 0)`
- **Peak Hour Breach Lift:** `CALCULATE([SLA Breach Rate %], Orders[is_peak_hour] = 1) - CALCULATE([SLA Breach Rate %], Orders[is_peak_hour] = 0)`
- **Picker Bottleneck Share %:** `DIVIDE(AVERAGE(Orders[dispatch_delay_mins]), AVERAGE(Orders[total_delivery_mins]), 0)`
