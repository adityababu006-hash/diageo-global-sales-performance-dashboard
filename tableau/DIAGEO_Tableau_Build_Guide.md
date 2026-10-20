# DIAGEO | Global Sales Performance Dashboard

**Build-ready Tableau Desktop / Tableau Public specification**  
**Dataset:** 10,000 synthetic transactions, 1 January 2023 to 31 August 2026  
**Required dashboard statement:** Synthetic portfolio dataset — not official Diageo sales data.

> Synthetic portfolio dataset created for analytical demonstration. This project is not affiliated with, endorsed by, or based on confidential data from Diageo plc.

## 1. Executive recommendation

Build one fixed-size desktop dashboard at **1400 × 850 px** with 14 supporting worksheets: six KPI sheets and eight analytical sheets. Use a deep-navy canvas, warm off-white KPI cards, a muted gold accent, teal for favourable results, and muted red for adverse results. Do not use a logo or other device that could imply endorsement.

The strongest story is:

> The synthetic portfolio generates **£17.25m net revenue** and **£9.45m gross profit** at a weighted **54.8% margin**, but achieves only **97.1% of target**, a **£507.1k shortfall**. Scale is concentrated in Johnnie Walker and Don Julio, while Don Julio also has the strongest brand margin. Comparable 2026 year-to-date revenue is **1.5% above** the same period in 2025 despite fewer transactions, suggesting higher transaction value. Promotional transactions have almost identical units per transaction but lower revenue and margin, an association that warrants commercial review rather than a causal conclusion.

### Dashboard headline values with no filters

| KPI | Validated value | Dashboard display |
|---|---:|---:|
| Total Net Revenue | £17,247,276.97 | **£17.2M** |
| Gross Profit | £9,451,587.11 | **£9.5M** |
| Weighted Profit Margin | 54.8005% | **54.8%** |
| Units Sold | 666,328 | **666K** |
| Target Achievement | 97.1439% | **97.1%** |
| Comparable YTD Revenue Growth, 2026 vs 2025 through 31 Aug | +1.5147% | **+1.5%** |

The 2026 KPI must use a like-for-like January–August comparison. Do not compare the first eight months of 2026 with all of 2025.

## 2. Dataset audit and validation

### 2.1 Structural audit

| Test | Result | Assessment |
|---|---:|---|
| Rows | 10,000 | Pass |
| Columns | 27 | Pass |
| Unique transaction IDs | 10,000 | Pass |
| Duplicate transaction IDs | 0 | Pass |
| Duplicate full rows | 0 | Pass |
| Missing values | 0 | Pass |
| Parsed dates | 10,000 of 10,000 | Pass |
| Date range | 2023-01-01 to 2026-08-31 | Pass; 2026 is partial |
| Year vs Order Date | 0 mismatches | Pass |
| Month number vs Order Date | 0 mismatches | Pass |
| Month name vs Order Date | 0 mismatches | Pass |
| Quarter vs Order Date | 0 mismatches | Pass |
| Country-to-region mapping | One region per country | Pass |
| Country-to-currency mapping | One currency per country | Pass |
| Brand-to-category mapping | One category per brand | Pass |

### 2.2 Commercial reconciliation

| Test | Result | Interpretation |
|---|---:|---|
| Net Revenue = Gross Revenue × (1 − Discount) | 10,000 of 10,000 within £0.01 | Pass |
| Gross Profit = Net Revenue − COGS | 10,000 of 10,000 within £0.01 | Pass |
| Profit_Margin_Pct = Gross Profit ÷ Net Revenue | 10,000 of 10,000 within 0.011 percentage points | Pass |
| Target_Achievement_Pct = Net Revenue ÷ Sales Target | 10,000 of 10,000 within 0.013 percentage points | Pass |
| Non-positive units | 0 | Pass |
| Non-positive revenue | 0 | Pass |
| Negative gross profit | 0 | Pass |
| Non-positive target | 0 | Pass |
| Discount outside 0%–100% | 0 | Pass |

The aggregate identity has a **£0.38 rounding difference**: £17,247,276.97 net revenue less £7,795,689.48 COGS equals £9,451,587.49, while the sum of row-level rounded Gross Profit is £9,451,587.11. This is immaterial and consistent with summing rounded transaction values. Use the supplied `Gross_Profit_GBP` field as the authoritative profit measure.

`Gross_Revenue_GBP` does not exactly equal `Units_Sold × Unit_Price_GBP` in 9,292 rows because Unit Price is displayed at two decimal places while Gross Revenue was evidently generated from greater price precision. Every difference is within the bound created by rounding the unit price to two decimals; the mean absolute gap is £0.17 and the maximum is £2.20. Do not rebuild Gross Revenue from the displayed unit price.

### 2.3 Field interpretation rules

- `Discount_Pct`, `Profit_Margin_Pct`, `Target_Achievement_Pct`, and `YoY_Growth_Simulation_Pct` are stored as decimal ratios. For example, `0.15` means 15%. Format them as percentages; do not multiply by 100.
- All revenue, price, target, cost, and profit fields are explicitly denominated in GBP. The `Currency` field describes the country’s local currency, not the unit of the monetary measures. Keep dashboard measures in GBP.
- Use `Order_Date` as the authoritative date. Treat Year, Quarter, Month, and Month Name as convenience dimensions.
- Do not use `YoY_Growth_Simulation_Pct` for the executive growth KPI. It is a simulated row-level field, not an aggregate time comparison.
- Use `COUNTD([Transaction_ID])` whenever transaction count is required.

### 2.4 Tableau data connection setup

1. Open Tableau Desktop or Tableau Public and choose **Connect → Text file**.
2. Select the CSV and rename the data source `Diageo Synthetic Sales`.
3. Set `Order_Date` to **Date**.
4. Set `Year` and `Month` to **Number (whole)**, then convert them to Dimensions if they are used directly.
5. Set `Units_Sold` to **Number (whole)**.
6. Set all GBP fields, percentage fields, and Unit Price to **Number (decimal)**.
7. Keep `Transaction_ID` and `Sales_Rep_ID` as string dimensions.
8. Assign `Country` the geographic role **Country/Region**.
9. Use **Data Source → Extract** for smoother interaction in Tableau Public.
10. Set default formats:
   - GBP measures: Currency (Custom), symbol `£`, 0 or 1 decimal depending on view.
   - Percent measures: Percentage, 1 decimal.
   - Units: Number (Custom), 0 decimals, display units Automatic.
   - Dates: `MMM yyyy` on the monthly trend.

## 3. Exact Tableau calculated fields

Create these fields with the names shown. The denominator guards prevent invalid output if future filtered data contains a zero denominator.

### 3.1 Profit Margin

```tableau
IF SUM([Net_Revenue_GBP]) = 0 THEN
    NULL
ELSE
    SUM([Gross_Profit_GBP]) / SUM([Net_Revenue_GBP])
END
```

Default format: Percentage, 1 decimal.

### 3.2 Target Achievement

```tableau
IF SUM([Sales_Target_GBP]) = 0 THEN
    NULL
ELSE
    SUM([Net_Revenue_GBP]) / SUM([Sales_Target_GBP])
END
```

Default format: Percentage, 1 decimal.

### 3.3 Target Variance GBP

```tableau
SUM([Net_Revenue_GBP]) - SUM([Sales_Target_GBP])
```

Default format: Currency, `£`, 0 decimals.

### 3.4 Target Variance %

```tableau
IF SUM([Sales_Target_GBP]) = 0 THEN
    NULL
ELSE
    (SUM([Net_Revenue_GBP]) - SUM([Sales_Target_GBP]))
    / SUM([Sales_Target_GBP])
END
```

Default format: Percentage, 1 decimal.

### 3.5 Average Selling Price

```tableau
IF SUM([Units_Sold]) = 0 THEN
    NULL
ELSE
    SUM([Net_Revenue_GBP]) / SUM([Units_Sold])
END
```

Default format: Currency, `£`, 2 decimals.

### 3.6 Revenue per Transaction

```tableau
IF COUNTD([Transaction_ID]) = 0 THEN
    NULL
ELSE
    SUM([Net_Revenue_GBP]) / COUNTD([Transaction_ID])
END
```

Default format: Currency, `£`, 0 decimals.

### 3.7 Gross Profit per Transaction

```tableau
IF COUNTD([Transaction_ID]) = 0 THEN
    NULL
ELSE
    SUM([Gross_Profit_GBP]) / COUNTD([Transaction_ID])
END
```

Default format: Currency, `£`, 0 decimals.

### 3.8 Discounted Revenue

```tableau
IF [Discount_Pct] > 0 THEN
    [Net_Revenue_GBP]
END
```

This is a row-level field. Use `SUM([Discounted Revenue])` in a view.

### 3.9 Target Status

```tableau
IF SUM([Net_Revenue_GBP]) >= SUM([Sales_Target_GBP]) THEN
    "Above Target"
ELSE
    "Below Target"
END
```

### 3.10 YoY Revenue Growth

```tableau
IF ABS(LOOKUP(SUM([Net_Revenue_GBP]), -1)) = 0 THEN
    NULL
ELSE
    (
        SUM([Net_Revenue_GBP])
        - LOOKUP(SUM([Net_Revenue_GBP]), -1)
    )
    / ABS(LOOKUP(SUM([Net_Revenue_GBP]), -1))
END
```

Configuration:

1. Put discrete `YEAR([Order_Date])` on Columns or Detail in ascending order.
2. Add `YoY Revenue Growth` to Text.
3. Choose **Edit Table Calculation → Specific Dimensions**.
4. Check only `YEAR(Order_Date)` and compute in ascending year order.
5. Use `LAST() = 0` as a table-calculation filter if only the latest mark should display.
6. Do not remove the prior year with an ordinary dimension filter before the table calculation. A single-year dimension filter removes the lookup value and returns Null.

This standard calculation produces +2.8% for 2024, +3.2% for 2025, and −31.9% for 2026 versus full-year 2025. The 2026 result is mathematically correct but commercially misleading because 2026 ends in August. Use the comparable-YTD calculation below for the executive KPI.

### 3.11 Revenue Share

```tableau
SUM([Net_Revenue_GBP])
/
TOTAL(SUM([Net_Revenue_GBP]))
```

Use this in Brand, Category, Country, or Channel views where the denominator should be the visible partition. Configure **Compute Using** to the displayed dimension, such as Brand. The share changes with filters, which is appropriate for “share of current selection.” Do not use it when a fixed all-company denominator is required.

### 3.12 Avg Units per Transaction

```tableau
IF COUNTD([Transaction_ID]) = 0 THEN
    NULL
ELSE
    SUM([Units_Sold]) / COUNTD([Transaction_ID])
END
```

Default format: Number, 1 decimal.

## 4. Robust comparable-YTD growth for the executive KPI

### 4.1 Max Data Date

```tableau
{ FIXED : MAX([Order_Date]) }
```

### 4.2 Current YTD Revenue

```tableau
SUM(
    IF YEAR([Order_Date]) = YEAR([Max Data Date])
       AND [Order_Date] <= [Max Data Date]
    THEN [Net_Revenue_GBP]
    END
)
```

### 4.3 Prior YTD Revenue

```tableau
SUM(
    IF [Order_Date] >= DATETRUNC('year', DATEADD('year', -1, [Max Data Date]))
       AND [Order_Date] <= DATEADD('year', -1, [Max Data Date])
    THEN [Net_Revenue_GBP]
    END
)
```

### 4.4 Comparable YTD Revenue Growth

```tableau
IF ABS([Prior YTD Revenue]) = 0 THEN
    NULL
ELSE
    ([Current YTD Revenue] - [Prior YTD Revenue])
    / ABS([Prior YTD Revenue])
END
```

Format with custom positive/negative signs: `+0.0%;-0.0%;0.0%`.

This KPI returns **+1.5%** for January–August 2026 versus January–August 2025. Exclude the ordinary Year quick filter from this KPI sheet so the prior-period records remain available. Region, Country, Brand, Category, Channel, Customer Type, and Market Segment filters can apply normally. Label the card `YOY REVENUE GROWTH (YTD)` and add `Through 31 Aug 2026 vs prior year` as its small caption.

## 5. Dynamic brand metric parameter

Create parameter `Metric Selector` with:

| Property | Definition |
|---|---|
| Data type | String |
| Current value | Revenue |
| Allowable values | List |
| Value 1 | Revenue |
| Value 2 | Gross Profit |
| Value 3 | Units Sold |
| Value 4 | Profit Margin |

Create `Selected Brand Metric`:

```tableau
CASE [Metric Selector]
WHEN "Revenue" THEN SUM([Net_Revenue_GBP])
WHEN "Gross Profit" THEN SUM([Gross_Profit_GBP])
WHEN "Units Sold" THEN SUM([Units_Sold])
WHEN "Profit Margin" THEN [Profit Margin]
END
```

Show the parameter as a compact single-value dropdown above the Brand Performance chart. Tableau uses one number format for the dynamic axis, so rely on the parameter-aware title and the correctly formatted individual measures in the tooltip. Avoid a string-formatted measure on the axis because it will not sort or scale correctly.

## 6. Worksheet inventory

Create and name the worksheets exactly as follows:

1. `KPI - Net Revenue`
2. `KPI - Gross Profit`
3. `KPI - Profit Margin`
4. `KPI - Units Sold`
5. `KPI - Target Achievement`
6. `KPI - YoY Revenue Growth`
7. `Revenue & Profit Trend`
8. `Brand Performance`
9. `Global Revenue by Market`
10. `Sales Target Performance`
11. `Revenue by Sales Channel`
12. `Revenue vs Profitability`
13. `Sales by Category`
14. `Promotion Impact`

Create one dashboard named `DIAGEO - Global Sales Performance`.

## 7. Build the six KPI worksheets

Use separate sheets so spacing, number formats, and conditional colours remain predictable. For every KPI sheet:

1. Set Marks to **Text**.
2. Put the relevant measure on Text.
3. Choose **Fit → Entire View**.
4. Hide the worksheet title.
5. Format with a small uppercase label, a large bold value, and an optional small caption.
6. Remove gridlines, zero lines, dividers, borders, and shading from the sheet itself. The dashboard container supplies the card background.
7. Set sheet padding to approximately 8 px inside the dashboard card.

### 7.1 KPI - Net Revenue

| Shelf | Field |
|---|---|
| Marks | Text |
| Text | `SUM([Net_Revenue_GBP])` |
| Filters | Year, Region, Country, Brand, Category, Channel, Customer Type, Market Segment |

Text arrangement:

```text
TOTAL NET REVENUE
<SUM(Net_Revenue_GBP)>
```

Format the value as Currency (Custom), `£`, 1 decimal, display units Millions.

### 7.2 KPI - Gross Profit

| Shelf | Field |
|---|---|
| Marks | Text |
| Text | `SUM([Gross_Profit_GBP])` |
| Filters | Same as Net Revenue |

Format as `£0.0M` using Tableau display units Millions.

### 7.3 KPI - Profit Margin

| Shelf | Field |
|---|---|
| Marks | Text |
| Text | `[Profit Margin]` |
| Filters | Same as Net Revenue |

Format as Percentage, 1 decimal. This must show **54.8%** with no filters, not the 53.3% simple average of the row-level margin field.

### 7.4 KPI - Units Sold

| Shelf | Field |
|---|---|
| Marks | Text |
| Text | `SUM([Units_Sold])` |
| Filters | Same as Net Revenue |

Format as Number, 0 decimals, display units Automatic. The unfiltered card should show approximately **666K**.

### 7.5 KPI - Target Achievement

| Shelf | Field |
|---|---|
| Marks | Text |
| Text | `[Target Achievement]` |
| Colour | `[Target Status]` |
| Filters | Same as Net Revenue |

Format as Percentage, 1 decimal. Use muted teal `#2A8C82` for Above Target and muted red `#C65D57` for Below Target. With no filters this card is below target at **97.1%**.

### 7.6 KPI - YoY Revenue Growth

| Shelf | Field |
|---|---|
| Marks | Text |
| Text | `[Comparable YTD Revenue Growth]` |
| Colour | `[Comparable YTD Revenue Growth]` |
| Filters | Region, Country, Brand, Category, Channel, Customer Type, Market Segment; do not apply Year |

Use a two-step diverging colour with teal for values at or above zero and muted red below zero. Add the caption `Through 31 Aug 2026 vs prior year`. Format as `+0.0%;-0.0%;0.0%`.

## 8. Build the analytical worksheets

### 8.1 Revenue & Profit Trend

Purpose: show the full monthly movement of revenue and gross profit, and expose recent volatility.

| Shelf / card | Configuration |
|---|---|
| Columns | `MONTH([Order_Date])` as continuous Exact Month (green pill) |
| Rows | `SUM([Net_Revenue_GBP])` |
| Secondary Rows | `SUM([Gross_Profit_GBP])`, then Dual Axis |
| Net Revenue Marks | Line, 2.5 px, `#D8B56A` |
| Gross Profit Marks | Line, 2 px, `#F4F6F8` or `#8FA9C2` |
| Detail | None |
| Filters | Year, Region, Country, Brand, Category, Channel, Customer Type, Market Segment |

Build steps:

1. Drag `Order_Date` to Columns and choose continuous Month so Tableau creates one mark per calendar month, not twelve month-name buckets.
2. Drag Net Revenue to Rows.
3. Drag Gross Profit to the right side of the view and choose **Dual Axis**.
4. Because both measures are GBP, synchronize axes. Keep the primary left axis and hide the secondary header.
5. Add an average reference line for Net Revenue only: Scope Entire Table, Value Average `SUM(Net_Revenue_GBP)`, dashed light grey line, label `Avg monthly revenue`.
6. Fix the y-axis at zero but leave the maximum automatic.
7. Format the axis as `£0.0M` or `£0K` depending on available space.
8. Show no mark labels by default. Highlight the selected month on hover.
9. Keep the full 2023–August 2026 period visible when Year is All.

Validated reading: 2026 monthly YoY movement is mixed, from **+21.7% in April** to **−14.7% in June**, while total January–August growth is +1.5%.

### 8.2 Brand Performance

Purpose: rank brands by a user-selected commercial metric.

| Shelf / card | Configuration |
|---|---|
| Rows | `Brand` |
| Columns | `[Selected Brand Metric]` |
| Marks | Bar |
| Colour | Single muted gold `#C9A45C`; use a darker highlight on selection |
| Label | `[Selected Brand Metric]`, only if it remains unclipped |
| Detail | `Category` |
| Sort | Descending by `[Selected Brand Metric]` |
| Filters | Year, Region, Country, Category, Channel, Customer Type, Market Segment |
| Parameter | Show `Metric Selector` |

Build steps:

1. Put Brand on Rows and Selected Brand Metric on Columns.
2. Sort Brand descending on the selected field.
3. Use horizontal bars. Keep labels to the right only if the selected metric formats legibly; otherwise omit labels and use the tooltip.
4. Edit the title to `Brand Performance — <Parameters.Metric Selector>` using **Insert → Parameters → Metric Selector**.
5. Fit to height. Do not add scrollbars; all 12 brands should be visible.
6. Add a thin reference line at the average selected measure only when it helps interpretation.

Validated unfiltered ranking by revenue: Johnnie Walker £3.38m, Don Julio £2.61m, Tanqueray £1.77m.

### 8.3 Global Revenue by Market

Purpose: compare market scale without allowing the map to dominate the dashboard.

| Shelf / card | Configuration |
|---|---|
| Geographic field | `Country`, Geographic Role Country/Region |
| Marks | Map (filled map preferred); use Circle if Tableau Public cannot fill a geography cleanly |
| Colour | `SUM([Net_Revenue_GBP])` |
| Detail | `Country`, `Region` |
| Filters | Year, Region, Brand, Category, Channel, Customer Type, Market Segment |

Build steps:

1. Double-click Country after assigning its geographic role.
2. Change Marks to Map.
3. Put Net Revenue on Colour and use a sequential blue scale from `#D8E3EC` to `#234C72`.
4. Keep land and borders muted. Remove map search, zoom controls, and the view toolbar from the published dashboard unless needed.
5. Use **Map → Edit Locations** and confirm all 16 countries are recognized. Resolve any ambiguity rather than leaving “Unknown” locations.
6. Fit Entire View. Avoid adding text labels over small countries.

### 8.4 Sales Target Performance

Purpose: rank the market shortfall and show actual, target, and variance without redundant side-by-side bars.

| Shelf / card | Configuration |
|---|---|
| Rows | `Country` |
| Columns | `[Target Variance GBP]` |
| Marks | Bar |
| Colour | `[Target Status]` |
| Label | `[Target Variance %]` |
| Sort | Ascending by Target Variance GBP, largest shortfall at top |
| Filters | Year, Region, Country, Brand, Category, Channel, Customer Type, Market Segment |

Build steps:

1. Put Country on Rows and Target Variance GBP on Columns.
2. Sort ascending so the most negative variance is immediately visible.
3. Add a zero reference line with a thin neutral grey stroke.
4. Use muted red for Below Target and teal for Above Target.
5. Format the axis and tooltip as GBP. Format labels as Percentage, 1 decimal.
6. Show all 16 countries without scrolling by using 9–10 pt row labels.
7. Include Actual and Target in the tooltip so the variance is traceable.

Data limitation: every country, brand, category, channel, region, and month is below target in aggregate. The chart will therefore be entirely “Below Target” with the current unfiltered data. This is a real property of the supplied synthetic dataset; do not invent green marks. Use bar length and variance labels to distinguish severity. At transaction level, 3,840 of 10,000 records are above target, but aggregation produces a net shortfall in every major business group.

### 8.5 Revenue by Sales Channel

Purpose: show scale and margin together without implying that small margin differences are large.

| Shelf / card | Configuration |
|---|---|
| Rows | `Channel` |
| Primary Columns | `SUM([Net_Revenue_GBP])` |
| Secondary Columns | `[Profit Margin]`, then Dual Axis |
| Revenue Marks | Bar, `#6F8FAF` |
| Margin Marks | Circle, `#C9A45C`, medium size |
| Sort | Descending by Net Revenue |
| Filters | Year, Region, Country, Brand, Category, Customer Type, Market Segment |

Do not synchronize the two axes because they use different units. Keep the top axis for Profit Margin and the bottom axis for Net Revenue. Fix the margin axis to a narrow but honest range only if clearly labelled; otherwise use 0%–60% to avoid exaggeration. The channel margin range is only about 0.38 percentage points, so the main story is channel scale, not a dramatic profitability gap.

### 8.6 Revenue vs Profitability

Purpose: position brands by scale and weighted margin.

| Shelf / card | Configuration |
|---|---|
| Columns | `SUM([Net_Revenue_GBP])` |
| Rows | `[Profit Margin]` |
| Marks | Circle |
| Detail | `Brand` |
| Label | `Brand` |
| Size | `SUM([Units_Sold])` |
| Colour | Single blue `#6F8FAF`; selected brand in gold |
| Filters | Year, Region, Country, Category, Channel, Customer Type, Market Segment |

Build steps:

1. Put Brand on Detail and Label.
2. Put Units Sold on Size; use a restrained size range so Guinness does not obscure other marks.
3. Add an average reference line to Net Revenue, scope Entire Table. Unfiltered value is approximately **£1.437m per brand**.
4. Add an average reference line to Profit Margin, scope Entire Table. This is the unweighted average of the 12 displayed brand-level margins, approximately **53.83%**.
5. Use dashed neutral lines and no permanent quadrant text.
6. Prevent overlapping labels with manual mark-label alignment or allow labels only for highlighted marks if necessary.

Unfiltered quadrant examples:

- High revenue / high margin: Johnnie Walker, Don Julio, Tanqueray.
- Low revenue / high margin: Cîroc, Crown Royal, Ketel One, Buchanan’s.
- Low revenue / low margin: Smirnoff, Baileys, Captain Morgan, Guinness, J&B.

These assignments change with filters because the reference lines recalculate over the visible marks.

### 8.7 Sales by Category

Purpose: rank category scale and expose mix differences.

| Shelf / card | Configuration |
|---|---|
| Rows | `Category` |
| Columns | `SUM([Net_Revenue_GBP])` |
| Marks | Bar |
| Colour | Single muted blue `#6F8FAF` |
| Label | `SUM([Net_Revenue_GBP])` |
| Detail | None |
| Sort | Descending by Net Revenue |
| Filters | Year, Region, Country, Brand, Channel, Customer Type, Market Segment |

Put Gross Profit, Units Sold, Profit Margin, Target Achievement, and Average Selling Price in the tooltip. Keep the visible chart to one scale; do not place Units and GBP on the same axis.

### 8.8 Promotion Impact

Purpose: compare observable promotion associations across metrics with different units.

Use a highlight table rather than forcing incompatible units onto one axis.

| Shelf / card | Configuration |
|---|---|
| Rows | `Promotion_Flag` |
| Columns | `Measure Names` |
| Text | `Measure Values` |
| Measure Values | Avg Units per Transaction, Net Revenue, Profit Margin, Gross Profit |
| Colour | Profit Margin only if a separate Marks card is available; otherwise use neutral cells |
| Filters | Year, Region, Country, Brand, Category, Channel, Customer Type, Market Segment |

Build steps:

1. Put Promotion Flag on Rows and Measure Names on Columns.
2. Put Measure Values on Text.
3. Filter Measure Names to exactly four measures: `Avg Units per Transaction`, `SUM(Net_Revenue_GBP)`, `Profit Margin`, `SUM(Gross_Profit_GBP)`.
4. Use aliases: `Avg units / transaction`, `Revenue`, `Margin`, `Gross profit`.
5. Preserve each measure’s native number format.
6. Add Average Discount, Revenue per Transaction, Gross Profit per Transaction, and transaction count to the tooltip.
7. Do not use causal wording. Title the view `Promotion Impact` but phrase the tooltip as an observed comparison.

Validated unfiltered comparison:

| Promotion | Transactions | Avg discount | Avg units / transaction | Revenue / transaction | Profit margin | Gross profit / transaction |
|---|---:|---:|---:|---:|---:|---:|
| No | 7,631 | 1.0% | 66.6 | £1,762 | 55.1% | £971 |
| Yes | 2,369 | 10.1% | 66.8 | £1,606 | 53.6% | £861 |

## 9. Dashboard layout

Create `DIAGEO - Global Sales Performance` with **Fixed Size 1400 × 850**. Use tiled containers for the main structure and floating only for the collapsible filter panel.

### 9.1 Pixel plan

| Zone | Approximate bounds | Contents |
|---|---|---|
| Header | x 20–1380, y 12–66 | Title, subtitle, filter toggle |
| KPI row | x 20–1380, y 72–164 | Six equal cards with 8 px gutters |
| Row 2 | x 20–1380, y 172–405 | Trend, 850 px wide; Brand, 510 px wide |
| Row 3 | x 20–1380, y 413–620 | Map, 500 px; Target, 500 px; Channel, 340 px |
| Row 4 | x 20–1380, y 628–817 | Profitability, 700 px; Category, 350 px; Promotion, 290 px |
| Footer | x 20–1380, y 821–846 | Disclaimer |

Use 8 px horizontal and vertical gutters. If the dashboard becomes crowded, reduce chart title padding before reducing font size. Keep body text at 9 pt or larger.

### 9.2 Header

Title, 24 pt semibold:

```text
DIAGEO
GLOBAL SALES PERFORMANCE
```

Subtitle, 11 pt regular:

```text
Synthetic Commercial Analytics Portfolio | 2023–2026
```

Add a small right-aligned label: `Data through 31 Aug 2026`.

### 9.3 Footer

Use 9 pt muted text on the dashboard background:

```text
Synthetic portfolio dataset — not official Diageo sales data.
```

On the Tableau Public description and GitHub page, use the longer disclaimer:

```text
Synthetic portfolio dataset created for analytical demonstration. This project is not affiliated with, endorsed by, or based on confidential data from Diageo plc.
```

### 9.4 Filter panel

Create a floating vertical container, approximately 230 × 470 px, anchored to the upper-right. Add a Show/Hide button labelled `FILTERS`.

Visible first:

1. Year — multiple-values dropdown, default All.
2. Region — multiple-values dropdown, default All.
3. Brand — multiple-values dropdown, default All.
4. Channel — multiple-values dropdown, default All.

Secondary filters below a divider:

5. Country.
6. Category.
7. Customer Type.
8. Market Segment.

Use **Only Relevant Values** for Country after Region. Avoid individual checklists on the dashboard; use compact dropdowns.

## 10. Filter application matrix

Apply filters with **Apply to Worksheets → Selected Worksheets**.

| Filter | KPI 1–5 | YoY KPI | Trend | Brand | Map | Target | Channel | Scatter | Category | Promotion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Year | Yes | **No** | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Region | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Country | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Brand | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Category | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Channel | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Customer Type | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Market Segment | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

Year is intentionally excluded from the comparable-YTD KPI because filtering to one year would remove the prior-year records. The small caption makes its fixed comparison period explicit. If a selected-year YoY workflow is later required, replace the Year quick filter with a Reporting Year parameter that deliberately retains the selected and prior comparison periods.

## 11. Dashboard actions and interactions

### 11.1 Brand filter action

Go to **Dashboard → Actions → Add Action → Filter**.

| Setting | Value |
|---|---|
| Name | Filter dashboard by Brand |
| Source sheet | Brand Performance |
| Run action on | Select |
| Target sheets | Revenue & Profit Trend; Global Revenue by Market; Sales Target Performance; Revenue by Sales Channel; Revenue vs Profitability; Sales by Category; Promotion Impact; KPI sheets |
| Target filters | Selected Fields: Brand → Brand |
| Clearing selection | Show all values |

### 11.2 Country filter action

| Setting | Value |
|---|---|
| Name | Filter dashboard by Country |
| Source sheet | Global Revenue by Market |
| Run action on | Select |
| Target sheets | Brand Performance; Revenue & Profit Trend; Sales Target Performance; Revenue by Sales Channel; Revenue vs Profitability; Sales by Category; Promotion Impact; KPI sheets |
| Target filters | Selected Fields: Country → Country |
| Clearing selection | Show all values |

### 11.3 Brand highlight action

| Setting | Value |
|---|---|
| Name | Highlight selected Brand |
| Source sheet | Revenue vs Profitability |
| Run action on | Hover |
| Target sheets | Brand Performance; Revenue & Profit Trend |
| Target highlighting | Selected Fields: Brand → Brand |

### 11.4 Target action restraint

Do not make every chart filter every other chart. The two filter actions above establish an intuitive hierarchy: Brand and Country are the principal selection dimensions. Too many bidirectional actions make clearing selections difficult.

### 11.5 Reset behaviour

Keep the Tableau toolbar visible in the published view so users can use **Revert** to restore the initial state. A Show/Hide button only opens and closes the filter panel; it does not reset filters. Use a native Reset/Revert control if available in the deployed Tableau version. Do not add an unverified extension to a public portfolio dashboard.

## 12. Exact tooltip copy

Use **Insert** in Tableau’s tooltip editor to add the fields; do not type field tokens manually. Bold the first line only. Keep tooltips under nine lines.

### 12.1 Revenue & Profit Trend

```text
<Month of Order Date>

Net Revenue: <SUM(Net_Revenue_GBP)>
Gross Profit: <SUM(Gross_Profit_GBP)>
Profit Margin: <AGG(Profit Margin)>
Units Sold: <SUM(Units_Sold)>
Target Achievement: <AGG(Target Achievement)>
```

### 12.2 Brand Performance

```text
<Brand>
Category: <Category>

Net Revenue: <SUM(Net_Revenue_GBP)>
Gross Profit: <SUM(Gross_Profit_GBP)>
Profit Margin: <AGG(Profit Margin)>
Units Sold: <SUM(Units_Sold)>
Target Achievement: <AGG(Target Achievement)>
Revenue Share: <AGG(Revenue Share)>
```

### 12.3 Global Revenue by Market

```text
<Country>
Region: <Region>

Net Revenue: <SUM(Net_Revenue_GBP)>
Gross Profit: <SUM(Gross_Profit_GBP)>
Profit Margin: <AGG(Profit Margin)>
Units Sold: <SUM(Units_Sold)>
Target Achievement: <AGG(Target Achievement)>
```

### 12.4 Sales Target Performance

```text
<Country>

Actual Revenue: <SUM(Net_Revenue_GBP)>
Sales Target: <SUM(Sales_Target_GBP)>
Variance: <AGG(Target Variance GBP)>
Variance %: <AGG(Target Variance %)>
Status: <AGG(Target Status)>
```

### 12.5 Revenue by Sales Channel

```text
<Channel>

Net Revenue: <SUM(Net_Revenue_GBP)>
Gross Profit: <SUM(Gross_Profit_GBP)>
Profit Margin: <AGG(Profit Margin)>
Revenue Share: <AGG(Revenue Share)>
Avg Selling Price: <AGG(Average Selling Price)>
Target Achievement: <AGG(Target Achievement)>
```

### 12.6 Revenue vs Profitability

```text
<Brand>
Category: <Category>

Net Revenue: <SUM(Net_Revenue_GBP)>
Gross Profit: <SUM(Gross_Profit_GBP)>
Profit Margin: <AGG(Profit Margin)>
Units Sold: <SUM(Units_Sold)>
Avg Selling Price: <AGG(Average Selling Price)>
Target Achievement: <AGG(Target Achievement)>
```

### 12.7 Sales by Category

```text
<Category>

Net Revenue: <SUM(Net_Revenue_GBP)>
Gross Profit: <SUM(Gross_Profit_GBP)>
Profit Margin: <AGG(Profit Margin)>
Units Sold: <SUM(Units_Sold)>
Avg Selling Price: <AGG(Average Selling Price)>
Target Achievement: <AGG(Target Achievement)>
```

### 12.8 Promotion Impact

```text
Promotion: <Promotion_Flag>

Transactions: <CNTD(Transaction_ID)>
Average Discount: <AVG(Discount_Pct)>
Avg Units / Transaction: <AGG(Avg Units per Transaction)>
Revenue / Transaction: <AGG(Revenue per Transaction)>
Gross Profit / Transaction: <AGG(Gross Profit per Transaction)>
Profit Margin: <AGG(Profit Margin)>

Observed association in synthetic data; not a causal estimate.
```

## 13. Formatting specification

### 13.1 Colour palette

| Role | Hex |
|---|---|
| Dashboard background | `#0B1526` |
| Card background | `#F7F4EE` |
| Primary dark text | `#152235` |
| Light text on dark background | `#F4F6F8` |
| Primary accent | `#C9A45C` |
| Secondary blue | `#6F8FAF` |
| Positive / above target | `#2A8C82` |
| Negative / below target | `#C65D57` |
| Neutral grid / divider | `#D6D9DE` |
| Muted annotation | `#7B8491` |

Use red and teal only for status and directional performance. Use gold and blue for ordinary series. Avoid rainbow palettes.

### 13.2 Typography

Use Tableau Book / Tableau Semibold, or Arial if a cross-platform font is required.

| Element | Size / style |
|---|---|
| Main title | 24 pt semibold, uppercase |
| Subtitle | 11 pt regular |
| KPI value | 24–28 pt semibold |
| KPI label | 9 pt semibold, uppercase |
| Chart title | 12 pt semibold |
| Axis / headers | 9 pt regular |
| Tooltip | 10 pt regular |
| Footer | 9 pt regular |

### 13.3 Chart styling

- Remove worksheet gridlines, row dividers, and column dividers unless a divider aids reading.
- Use zero lines only where they carry meaning, especially Target Variance.
- Use no outer chart borders; rely on spacing and card backgrounds.
- Keep chart title alignment left.
- Hide redundant legends. Retain only the target-status legend if colour meaning is not obvious.
- Use 6–10 px inner padding within cards.
- Keep number formats consistent: `£0.0M`, `£0K`, `0.0%`, and `#,##0`.
- Use sentence case for chart titles. Keep the main dashboard title uppercase as specified.

## 14. Business insights from the synthetic dataset

Label this section in any presentation as **Insights from a synthetic portfolio dataset**.

1. **The portfolio is profitable but behind target.** Net revenue totals £17.25m and gross profit £9.45m at a weighted 54.8% margin. Target achievement is 97.1%, a £507.1k shortfall. Every major aggregate group is below target, so the commercial issue is broad rather than isolated to a single brand or market.

2. **Johnnie Walker is the scale leader; Don Julio is the strongest combination of scale and margin.** Johnnie Walker contributes £3.38m, or 19.6% of total revenue, at a 55.4% margin. Don Julio contributes £2.61m, or 15.1%, at the highest brand margin of 59.6%. Together they produce 34.7% of portfolio revenue; the top three brands including Tanqueray produce 45.0%.

3. **The United States and United Kingdom dominate geographic scale.** The United States contributes £5.01m, 29.0% of revenue, and the United Kingdom contributes £3.10m, 18.0%. Together they account for 47.0% of revenue. They also have the two largest absolute country shortfalls: approximately £153.4k and £84.9k respectively.

4. **Comparable 2026 YTD revenue is growing, but monthly performance is volatile.** January–August 2026 revenue is £3.269m versus £3.220m in the same period of 2025, up 1.5%. Transactions fell 5.5%, while revenue per transaction rose 7.4%, from about £1,700 to £1,826. Monthly YoY results range from +21.7% in April to −14.7% in June, so the YTD improvement is not uniform.

5. **Tequila is the premium profitability engine.** Tequila, represented by Don Julio in this dataset, contributes £2.61m and has a 59.6% margin and £48.79 average selling price, the strongest category economics. Scotch Whisky is larger at £5.23m, 30.3% of revenue, but has a lower 54.6% margin.

6. **Beer / Stout is high-volume but low-value and low-margin.** The category sells 100,436 units but produces only £0.76m revenue, a 4.4% share, at a £7.61 average selling price and 47.5% margin. It needs a different commercial interpretation from premium spirits; units alone overstate its economic contribution.

7. **Duty Free / Travel Retail is small but commercially attractive.** It contributes 9.2% of revenue, has the highest channel margin at 55.1%, and the highest channel revenue per transaction at about £2,063. Channel margins are tightly grouped, however, so this is an incremental opportunity signal rather than a dramatic structural gap.

8. **Promotions are associated with lower value and margin, not meaningfully higher basket volume.** Promotional transactions average 66.8 units versus 66.6 without promotion, only 0.3% higher. Their revenue per transaction is 8.8% lower, gross profit per transaction is 11.4% lower, and margin is 1.54 percentage points lower. Average discount is 10.1% versus 1.0%. This is descriptive association in synthetic data and does not prove that promotion causes the difference; brand, country, channel, and customer mix may confound it.

## 15. Validation before publishing

### 15.1 Data and calculation checks

- [ ] Row count is 10,000 and distinct Transaction ID count is 10,000.
- [ ] Date range is 1 Jan 2023 to 31 Aug 2026.
- [ ] No null or unknown map locations remain.
- [ ] Total Net Revenue equals **£17,247,276.97** with no filters.
- [ ] Total Gross Profit equals **£9,451,587.11** with no filters.
- [ ] Total Units Sold equals **666,328**.
- [ ] Total Sales Target equals **£17,754,365.47**.
- [ ] Weighted Profit Margin equals **54.8005%**.
- [ ] Target Achievement equals **97.1439%**.
- [ ] Target Variance equals **−£507,088.50**.
- [ ] Comparable 2026 YTD growth equals **+1.5147%**.
- [ ] The Profit Margin card uses `SUM(Gross Profit) / SUM(Net Revenue)`, not `AVG(Profit_Margin_Pct)`.
- [ ] The Target Achievement card uses aggregate revenue divided by aggregate target.
- [ ] Percent fields are formatted as percentages without multiplying by 100.
- [ ] All monetary measures display GBP even when local Currency is present.
- [ ] Gross Revenue is not rebuilt from the two-decimal Unit Price field.

### 15.2 YoY checks

- [ ] Standard annual YoY computes across Year in ascending order.
- [ ] A display filter such as `LAST() = 0` is applied after the table calculation, not before it.
- [ ] The ordinary Year quick filter is not applied to the comparable-YTD KPI.
- [ ] The KPI caption states `Through 31 Aug 2026 vs prior year`.
- [ ] 2026 is not compared with the full 2025 year in executive commentary.

### 15.3 Filter and action checks

- [ ] Each visible filter affects every intended major worksheet.
- [ ] Brand selection filters the trend, map, target, channel, category, promotion, scatter, and KPIs.
- [ ] Country selection filters brand, category, channel, target, trend, promotion, and KPIs.
- [ ] Clearing a mark selection restores all values.
- [ ] Selecting multiple quick-filter values does not create empty or misleading sheets.
- [ ] The Revert control returns the dashboard to its published default.

### 15.4 Visual checks at 1400 × 850

- [ ] No chart has a scrollbar.
- [ ] No KPI value is clipped at 100% browser zoom.
- [ ] All 12 brands, 16 countries in the target view, 8 categories, and 5 channels are readable.
- [ ] The map does not exceed roughly one-third of the analytical canvas.
- [ ] Tooltip currency, percentages, commas, and signs are correct.
- [ ] Red and teal are used only for adverse/favourable meaning.
- [ ] The footer disclaimer is visible without scrolling.
- [ ] The published Tableau Public thumbnail remains legible.

## 16. Recommended presentation sequence

When presenting the dashboard in an interview or portfolio walkthrough:

1. Start with overall scale, profitability, and the target gap.
2. Establish the time context: 2026 is partial, and comparable YTD growth is +1.5%.
3. Move to brand mix: Johnnie Walker leads scale, Don Julio leads margin.
4. Show geographic concentration in the United States and United Kingdom.
5. Use the profitability matrix to distinguish scale from margin opportunity.
6. Close on promotion association and the need for controlled follow-up analysis.

This sequence moves from executive status to drivers and then to action, rather than giving a tour of chart types.

## 17. LinkedIn project description

```text
DIAGEO | Global Sales Performance Dashboard — Tableau Portfolio Project

I built an executive commercial analytics dashboard in Tableau using a synthetic dataset of 10,000 beverage sales transactions covering January 2023 to August 2026.

The dashboard brings together revenue, gross profit, weighted margin, target achievement, comparable year-over-year growth, brand and category performance, geographic mix, channel economics, and promotion analysis. I also added interactive filters and dashboard actions so users can move from a global view to individual brands and markets.

Key analytical choices included calculating margin and target achievement from aggregated components, using a like-for-like YTD comparison for the partial 2026 period, and separating observable promotion associations from causal claims.

Tools and skills demonstrated: Tableau, calculated fields, table calculations, LOD expressions, parameters, dashboard actions, commercial KPI design, target-versus-actual analysis, profitability analysis, geographic visualisation, data validation, and executive storytelling.

Synthetic portfolio dataset created for analytical demonstration. This project is not affiliated with, endorsed by, or based on confidential data from Diageo plc.
```

Suggested LinkedIn carousel order: dashboard overview, KPI and trend close-up, brand profitability matrix, geographic and target analysis, promotion finding, methodology/disclaimer.

## 18. CV project summary

Long version:

```text
Built an executive Tableau sales-performance dashboard from 10,000 synthetic FMCG transactions, combining revenue, gross profit, weighted margin, target variance, comparable YTD growth, brand/category mix, geographic performance, channel economics and promotion analysis. Developed aggregate calculations, table calculations, LOD logic, a dynamic metric parameter, dashboard actions and a validated executive layout; identified a £507k synthetic target gap, portfolio concentration and margin opportunities.
```

Short version:

```text
Created an interactive Tableau commercial dashboard for 10,000 synthetic FMCG sales records, using validated KPIs, YoY/YTD logic, target variance, profitability segmentation, maps, parameters and dashboard actions.
```

## 19. Interview explanation using STAR

### Situation

```text
I wanted to demonstrate how I would turn transaction-level sales data into an executive commercial reporting product. I used a synthetic 10,000-row beverage dataset covering brands, markets, channels, targets, discounts, revenue, costs and profit from 2023 to August 2026.
```

### Task

```text
My objective was to build one concise Tableau dashboard that senior sales leaders could use to assess overall performance, identify target gaps, compare brand and market economics, and locate growth or margin opportunities. I also needed to make the analysis portfolio-safe and avoid presenting the synthetic figures as official company data.
```

### Action

```text
I first audited uniqueness, completeness, dates, field mappings and financial relationships. I found that percentage fields were stored as decimal ratios and that the displayed unit price was rounded, so I preserved Gross Revenue as the authoritative field. I then created weighted margin and target calculations from aggregate components, built a comparable YTD growth measure for the partial 2026 period, and added a parameter to switch the brand ranking between revenue, gross profit, units and margin. I designed 14 supporting worksheets, combined them in a 1400 by 850 executive layout, and added Brand and Country filter actions. I used restrained colours, concise tooltips and a clear synthetic-data disclaimer. Finally, I reconciled the headline KPIs to the source and tested filters, actions and YoY behaviour.
```

### Result

```text
The finished design surfaces a clear commercial story: £17.25m synthetic net revenue and £9.45m gross profit at a 54.8% weighted margin, but a £507k target shortfall. It shows concentration in Johnnie Walker, Don Julio, the United States and the United Kingdom; a premium profitability opportunity in Tequila; and a non-causal association between promotions and lower transaction value and margin. The project demonstrates both Tableau execution and the judgement required to make executive metrics comparable, traceable and honest.
```

## 20. Final portfolio positioning

The project demonstrates:

- Tableau Desktop / Tableau Public dashboard development.
- Commercial sales and FMCG analysis.
- KPI definition and reconciliation.
- Aggregate calculations, table calculations, LOD expressions, and parameters.
- Revenue, margin, target, geographic, channel, category, and promotion analysis.
- Interactive filters, dashboard actions, and executive tooltips.
- Evidence-based storytelling and explicit handling of partial-period comparisons.
- Responsible presentation of synthetic brand-related data.

**Final project title:** `DIAGEO | Global Sales Performance Dashboard`  
**Final disclaimer:** `Synthetic portfolio dataset created for analytical demonstration. This project is not affiliated with, endorsed by, or based on confidential data from Diageo plc.`
