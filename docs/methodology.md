# Methodology

This project implements an independent synthetic smart-city mobility risk digital twin. The workflow creates fictional city zones, road segments, transit stops, emergency facilities, and traffic traces; applies planning scenarios; and audits congestion, accident risk, emissions burden, emergency route delay, and transport equity.

## Synthetic city model

Zones include population, income index, car ownership, transit access, vulnerable-population share, and an equity-priority score. Road segments include length, lanes, speed limit, road class, bus-priority flags, bike-lane flags, emergency-corridor flags, and capacity.

## Scenario simulation

The system compares baseline traffic against congestion-pricing, emergency-lane priority, transit-priority, low-emission routing, and equity-aware mobility interventions. These scenarios are transparent proxies, not official policy prescriptions.

## Risk scoring

Congestion is based on volume-capacity ratio and speed drop. Accident risk is based on incident flags, rain, heavy-vehicle share, congestion, and road class. Emissions burden is a synthetic CO2e proxy based on vehicle count, road length, speed regime, and heavy-vehicle share. Emergency delay is estimated from low-percentile speed, congestion, incidents, emergency-corridor availability, and facility coverage.

## Equity review

The equity audit checks whether zones with lower transit access, lower income index, or higher vulnerable-population share carry disproportionate congestion, emissions, accident, and emergency-delay burden.

## Reproducibility

Each run writes structured CSV outputs, a JSON summary, figures, a Markdown report, and a hash-chained audit ledger.
