# Market Price Data Sources & Known Gaps

The prices in `market_prices.csv` are real, sourced figures — not
fabricated — pulled from PSA press releases and a few properly-cited
secondary reports. Coverage is **not** a clean uniform monthly series
across all 5 years for every commodity. Below is exactly what's real,
where it came from, and what's missing.

## Palay (dry) — farmgate price, national average (PhP/kg)

Best-covered commodity: 14 data points from 2021 to early 2026,
mostly sourced from PSA's monthly "Updates on Farmgate Prices of
Palay (Dry)" bulletins, plus one full-year 2024 average from a
Congressional Policy and Budget Research Department (CPBRD) fact
sheet, and two PSA "Seasonally Adjusted Palay/Rice Production and
Prices" quarterly releases for late 2025 / early 2026.

**Gaps:** 2021 (only 2 months), most of 2024, most of 2025.

## Regular milled rice & Well milled rice — retail price (PhP/kg)

Sourced from PSA's "Price Situationer of Selected Agricultural
Commodities" bi-monthly bulletins, a BusinessWorld article citing a
PSA release (June 2024), and full-year 2023/2024 averages from a
PCAARRD industry report that cites PSA data.

**Gaps:** almost nothing for 2021–2022; scattered coverage in
2023–2024; good coverage for 2026 (PSA's most recent bulletins were
easiest to find). 2025 has only one data point per rice type.

## Corn (dry) — farmgate price (PhP/kg)

Only 3 points (2020, 2022, late 2023), and these came from a
**secondary academic source** (a SADI Journal economics paper) that
itself cites PSA/DA data, rather than directly from a PSA bulletin.
Treat these as lower-confidence than the palay/rice figures above.

**Gaps:** 2021, 2024, 2025, 2026 — nothing found.

## Urea fertilizer — retail price (PhP/50kg bag)

Only **one** data point: December 2024 (~PhP 1,581/bag), from a
Statista chart that cites the Philippine Rice Research Institute
(PhilRice). A qualitative note from the same source says urea prices
"peaked in 2021 and 2022," but no exact figures for those years were
available without a paid Statista account.

**Gaps:** essentially the whole 5-year window except one month.
Fertilizer retail data isn't published as a clean historical time
series anywhere publicly accessible — PSA only publishes it in weekly
PDF bulletins (see the DA Fertilizer and Pesticide Authority's
"Weekly Prices" page), which would need to be opened and read
individually to fill this in.

## Why it's this patchy

I don't have programmatic access to PSA's OpenSTAT database (the
PXWeb interface requires interactive form selections, and my sandbox
can't reach `psa.gov.ph` at all). Everything above came from web
search snippets of already-published PSA bulletins, news articles,
and reports that happened to state a specific number for a specific
period. That's inherently spotty — it surfaces whatever got quoted
somewhere, not a complete series.

## To get a complete 5-year monthly series

Use the manual OpenSTAT export described earlier in this conversation
(the "Cereals: Farmgate Prices" and "Cereals: Retail Prices" tables)
— that's the only way to get the real, complete, uniform monthly
data PSA actually holds. Once you've downloaded and reshaped that
export into the `date,commodity,price,unit` format, it'll slot
straight into `market_prices.csv` (or a hosted CSV via
`MARKET_PRICES_CSV_URL`) and replace this partial dataset.

## Sugarcane, Coconut, Banana (added later)

These match the crop types farmers actually pick in "My Fields"
(Rice, Corn, Coconut, Banana, Sugarcane) rather than the original
dashboard commodity list. Only **one real data point each** was
findable through free sources:

- **Sugarcane** — national farmgate price for raw sugar production.
  2024: PhP 56.48/kg (Statista, citing PSA). 2023 figure (PhP 59.03)
  is *derived*, not directly stated — Statista's same page says the
  2024 figure is "a 2.55 peso decrease from the previous year," so
  2023 = 56.48 + 2.55, simple arithmetic on PSA's own stated figures.
- **Coconut** — national wholesale price of copra. 2023: PhP 19.39/kg
  (Statista, citing PSA). The source also says this was "significantly
  lower" than 2022, but didn't give an exact 2022 figure for free.
- **Banana** — national retail price of medium-sized Lakatan bananas.
  2023: PhP 74.84/kg (Statista, citing PSA).

Each of these is a **single point** — not enough to draw a trend
line yet (the dashboard will show "not enough historical data" for
them until more points are added). I found provincial-level data for
these three (Laguna, Camarines Sur, Aklan, Biliran) going back
further, but didn't include it here since it's not comparable to the
national-level figures used for the other commodities — mixing
national and provincial numbers in one series would be misleading.

