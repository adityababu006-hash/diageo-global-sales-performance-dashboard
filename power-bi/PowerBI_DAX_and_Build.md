# Power BI build package

Use `diageo_sales_powerbi_ready.csv` as the source and import `diageo_powerbi_theme.json` from **View → Themes → Browse for themes**.

**Report title:** DIAGEO | Global Sales Performance Dashboard  
**Required footer:** Synthetic portfolio dataset — not official Diageo sales data.

## Data model

Rename the imported table `Sales`. Create a date table:

```DAX
Date =
ADDCOLUMNS(
    CALENDAR(MIN(Sales[Order_Date]), MAX(Sales[Order_Date])),
    "Year", YEAR([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "Month Number", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "Month Year", FORMAT([Date], "MMM yyyy"),
    "Month Start", DATE(YEAR([Date]), MONTH([Date]), 1)
)
```

Mark `Date` as the date table using `Date[Date]`. Create a one-to-many relationship from `Date[Date]` to `Sales[Order_Date]`. Sort `Date[Month]` by `Date[Month Number]` and `Date[Month Year]` by `Date[Month Start]`.

## Measures

```DAX
Total Net Revenue = SUM(Sales[Net_Revenue_GBP])

Gross Profit = SUM(Sales[Gross_Profit_GBP])

Profit Margin = DIVIDE([Gross Profit], [Total Net Revenue])

Units Sold = SUM(Sales[Units_Sold])

Sales Target = SUM(Sales[Sales_Target_GBP])

Target Achievement = DIVIDE([Total Net Revenue], [Sales Target])

Target Variance GBP = [Total Net Revenue] - [Sales Target]

Target Variance % = DIVIDE([Target Variance GBP], [Sales Target])

Transactions = DISTINCTCOUNT(Sales[Transaction_ID])

Average Selling Price = DIVIDE([Total Net Revenue], [Units Sold])

Revenue per Transaction = DIVIDE([Total Net Revenue], [Transactions])

Gross Profit per Transaction = DIVIDE([Gross Profit], [Transactions])

Average Units per Transaction = DIVIDE([Units Sold], [Transactions])

Average Discount = AVERAGE(Sales[Discount_Pct])

Discounted Revenue =
CALCULATE(
    [Total Net Revenue],
    Sales[Discount_Pct] > 0
)

Target Status =
IF([Total Net Revenue] >= [Sales Target], "Above Target", "Below Target")

Brand Revenue Share =
DIVIDE(
    [Total Net Revenue],
    CALCULATE([Total Net Revenue], ALLSELECTED(Sales[Brand]))
)
```

### Comparable YTD growth

The source ends on 31 August 2026. These measures preserve Brand, Region, Country, Channel and other business filters while deliberately ignoring an ordinary Date filter for the comparison period.

```DAX
Max Data Date =
CALCULATE(MAX(Sales[Order_Date]), REMOVEFILTERS('Date'))

Current YTD Revenue =
VAR Cutoff = [Max Data Date]
VAR StartDate = DATE(YEAR(Cutoff), 1, 1)
RETURN
    CALCULATE(
        [Total Net Revenue],
        REMOVEFILTERS('Date'),
        DATESBETWEEN('Date'[Date], StartDate, Cutoff)
    )

Prior YTD Revenue =
VAR Cutoff = [Max Data Date]
VAR PriorCutoff = EDATE(Cutoff, -12)
VAR PriorStart = DATE(YEAR(Cutoff) - 1, 1, 1)
RETURN
    CALCULATE(
        [Total Net Revenue],
        REMOVEFILTERS('Date'),
        DATESBETWEEN('Date'[Date], PriorStart, PriorCutoff)
    )

YoY Revenue Growth YTD =
DIVIDE([Current YTD Revenue] - [Prior YTD Revenue], [Prior YTD Revenue])
```

Expected result without business filters: **+1.5%**.

## Dynamic brand metric

Create a disconnected table:

```DAX
Metric Selector =
DATATABLE(
    "Metric", STRING,
    {
        {"Revenue"},
        {"Gross Profit"},
        {"Units Sold"},
        {"Profit Margin"}
    }
)
```

Create the switching measure:

```DAX
Selected Brand Metric =
SWITCH(
    SELECTEDVALUE('Metric Selector'[Metric], "Revenue"),
    "Revenue", [Total Net Revenue],
    "Gross Profit", [Gross Profit],
    "Units Sold", [Units Sold],
    "Profit Margin", [Profit Margin]
)
```

## Report page

Use a fixed 16:9 page. Recommended canvas: 1400 × 850.

### Header and slicers

- Title: `DIAGEO` on the first line and `GLOBAL SALES PERFORMANCE` on the second.
- Subtitle: `Synthetic Commercial Analytics Portfolio | 2023–2026`.
- Visible dropdown slicers: Date[Year], Sales[Region], Sales[Brand], Sales[Channel].
- Secondary slicers in a bookmark-controlled panel: Country, Category, Customer Type, Market Segment.

### KPI cards

1. Total Net Revenue.
2. Gross Profit.
3. Profit Margin.
4. Units Sold.
5. Target Achievement.
6. YoY Revenue Growth YTD.

Use `£0.0M`, `0.0%`, and `0.0M` or `0K` display units. Add conditional colour only to Target Achievement and YoY Growth.

### Dimensional visual styling

- Use a deep navy canvas (`#0B1526`) with a slightly lighter navy panel behind the chart grid.
- Place each KPI and chart on a cream container (`#F7F4EE`) with 8–12 px rounded corners.
- Turn on a restrained outer shadow: black at roughly 65–75% transparency, 6–10 px blur and 3–5 px distance.
- Add a thin gold top/left border or highlight (`#C9A45C`) and a darker lower/right edge (`#70552B`) to suggest a bevel.
- For KPI cards, place a narrow semi-transparent gold gradient shape behind the value area and group it with the card.
- Keep chart axes flat and proportional. Apply depth to containers and marks rather than using perspective or tilted 3D axes.
- Use gold for revenue, steel blue for profit/market values, teal for favourable status and muted red for adverse status.

### Visuals

| Visual | Configuration |
|---|---|
| Revenue & Profit Trend | Line chart; X = Date[Month Start]; Y = Total Net Revenue and Gross Profit |
| Brand Performance | Clustered bar; Y = Sales[Brand]; X = Selected Brand Metric; sort descending |
| Global Revenue by Market | Filled map; Location = Country; Colour = Total Net Revenue |
| Sales Target Performance | Bar; Y = Country; X = Target Variance GBP; colour by Target Status |
| Revenue by Sales Channel | Combo chart; Axis = Channel; columns = Total Net Revenue; line = Profit Margin |
| Revenue vs Profitability | Scatter; X = Total Net Revenue; Y = Profit Margin; Size = Units Sold; Details = Brand |
| Sales by Category | Bar; Y = Category; X = Total Net Revenue; tooltip = Gross Profit, Units Sold, Profit Margin |
| Promotion Impact | Matrix; Rows = Promotion Flag; Values = Average Units per Transaction, Total Net Revenue, Profit Margin, Gross Profit |

## Interactions

- Selecting a Brand filters the trend, map, target, channel, category and promotion visuals.
- Selecting a Country filters brand, category and channel visuals.
- Keep the Year slicer from filtering the YoY YTD card through **Edit interactions**.
- Add a Reset Filters bookmark and button after setting the published default state.

## Validation benchmarks

| Measure | Expected unfiltered value |
|---|---:|
| Total Net Revenue | £17,247,276.97 |
| Gross Profit | £9,451,587.11 |
| Profit Margin | 54.8005% |
| Units Sold | 666,328 |
| Sales Target | £17,754,365.47 |
| Target Achievement | 97.1439% |
| Target Variance | −£507,088.50 |
| YoY Revenue Growth YTD | +1.5147% |

## Disclaimer

Synthetic portfolio dataset created for analytical demonstration. This project is not affiliated with, endorsed by, or based on confidential data from Diageo plc.
