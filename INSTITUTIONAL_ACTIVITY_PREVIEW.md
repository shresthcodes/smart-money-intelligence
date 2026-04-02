# Institutional Activity Page - Visual Preview

## 📱 Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🏢 Institutional Activity Analysis                              │
│  Track FII and DII investment flows and their impact on markets  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📊 Institutional Flow Statistics                                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Total FII    │ Total DII    │ Avg Daily    │ Avg Daily    │ │
│  │ Net Flow     │ Net Flow     │ FII Flow     │ DII Flow     │ │
│  │ ₹-22,016 Cr  │ ₹-38,306 Cr  │ ₹-21 Cr      │ ₹-37 Cr      │ │
│  │ 📉 45.2%     │ 📉 42.8%     │              │              │ │
│  │ positive     │ positive     │              │              │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Max FII      │ Max FII      │ Max DII      │ Max DII      │ │
│  │ Buying Day   │ Selling Day  │ Buying Day   │ Selling Day  │ │
│  │ ₹2,318 Cr    │ ₹-1,853 Cr   │ ₹1,457 Cr    │ ₹-1,330 Cr   │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  📈 FII vs DII Net Flows Comparison                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │  2000 ┤                    ╭─╮                           │   │
│  │       │        ╭─╮        ╱   ╲        ╭─╮              │   │
│  │  1000 ┤       ╱   ╲      ╱     ╲      ╱   ╲             │   │
│  │       │      ╱     ╲    ╱       ╲    ╱     ╲            │   │
│  │     0 ┼─────────────────────────────────────────────    │   │
│  │       │    ╱         ╲  ╱         ╲  ╱         ╲        │   │
│  │ -1000 ┤   ╱           ╲╱           ╲╱           ╲       │   │
│  │       │  ╱                                       ╲      │   │
│  │ -2000 ┤ ╱                                         ╲     │   │
│  │       └─────────────────────────────────────────────    │   │
│  │         2020    2021    2022    2023    2024            │   │
│  │                                                           │   │
│  │  ─── FII Net Flow    ─── DII Net Flow                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ▼ 📊 Flow Analysis Insights                                    │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  📊 Cumulative Institutional Flows                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │ 20000 ┤                                                  │   │
│  │       │                                                  │   │
│  │ 10000 ┤        ╱╲                                        │   │
│  │       │       ╱  ╲                                       │   │
│  │     0 ┼──────────────────────────────────────           │   │
│  │       │                      ╲                           │   │
│  │-10000 ┤                       ╲                          │   │
│  │       │                        ╲                         │   │
│  │-20000 ┤                         ╲                        │   │
│  │       │                          ╲                       │   │
│  │-30000 ┤                           ╲                      │   │
│  │       │                            ╲                     │   │
│  │-40000 ┤                             ╲___                 │   │
│  │       └─────────────────────────────────────────────    │   │
│  │         2020    2021    2022    2023    2024            │   │
│  │                                                           │   │
│  │  ─── FII Cumulative    ─── DII Cumulative               │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ▼ 📈 Cumulative Flow Insights                                  │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  🎯 Accumulation & Distribution Periods                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🟢 FII Accumulation (16) │ 🔴 FII Distribution (16)     │   │
│  │ 🟢 DII Accumulation (17) │ 🔴 DII Distribution (16)     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  Start Date  │  End Date   │ Duration │ Avg Flow        │   │
│  ├──────────────┼─────────────┼──────────┼─────────────────┤   │
│  │  2020-01-08  │ 2020-01-14  │  5 days  │ ₹1,136 Cr       │   │
│  │  2020-07-10  │ 2020-07-17  │  6 days  │ ₹1,459 Cr       │   │
│  │  2020-09-17  │ 2020-09-24  │  6 days  │ ₹1,812 Cr       │   │
│  │  2020-09-30  │ 2020-10-08  │  7 days  │ ₹1,294 Cr       │   │
│  │  ...         │ ...         │  ...     │ ...             │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ℹ️ Adjust detection settings in sidebar                        │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  🔗 Correlation Analysis                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │              FII_Net  DII_Net  Daily_Return  Volatility  │   │
│  │  FII_Net      1.00    -0.02      0.02         0.01      │   │
│  │  DII_Net     -0.02     1.00      0.04        -0.01      │   │
│  │  Daily_Ret    0.02     0.04      1.00         0.15      │   │
│  │  Volatility   0.01    -0.01      0.15         1.00      │   │
│  │                                                           │   │
│  │  🟢 Positive    ⬜ Neutral    🔴 Negative                │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ▼ 📊 Correlation Insights                                      │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  📋 Summary & Key Insights                                       │
│  ┌──────────────────────────┬──────────────────────────────┐   │
│  │ 🎯 Institutional Behavior │ 💡 Key Takeaways             │   │
│  │                           │                               │   │
│  │ FII:                      │ • 🔄 FII and DII both net    │   │
│  │ • Total: ₹-22,016 Cr      │   sellers - bearish signal   │   │
│  │ • Avg: ₹-21 Cr/day        │                               │   │
│  │ • Positive: 45.2%         │ • ⚠️ FII showed consistent   │   │
│  │ • Accumulation: 16        │   selling behavior           │   │
│  │ • Distribution: 16        │                               │   │
│  │                           │ • ⚠️ DII showed consistent   │   │
│  │ DII:                      │   selling behavior           │   │
│  │ • Total: ₹-38,306 Cr      │                               │   │
│  │ • Avg: ₹-37 Cr/day        │ • 📊 Equal accumulation and  │   │
│  │ • Positive: 42.8%         │   distribution periods       │   │
│  │ • Accumulation: 17        │                               │   │
│  │ • Distribution: 16        │ • 🔗 Weak correlation with   │   │
│  │                           │   market returns             │   │
│  └──────────────────────────┴──────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 Sidebar Controls

```
┌─────────────────────────┐
│ 📅 Date Range Filter    │
├─────────────────────────┤
│ Start Date:             │
│ [2023-03-08]            │
│                         │
│ End Date:               │
│ [2024-03-08]            │
│                         │
│ ✅ Showing data from    │
│    2023-03-08 to        │
│    2024-03-08           │
│                         │
│ 📊 Total trading days:  │
│    252                  │
├─────────────────────────┤
│ ⚙️ Period Detection     │
│    Settings             │
├─────────────────────────┤
│ Minimum Consecutive     │
│ Days:                   │
│ [━━━━━●━━━━] 5          │
│ (3-10 days)             │
│                         │
│ Minimum Average Flow:   │
│ [0] ₹ Cr                │
│ (0-1000)                │
│                         │
│ ℹ️ Adjust to find       │
│    different patterns   │
└─────────────────────────┘
```

## 🖱️ Interactive Features

### Hover Tooltips
```
┌─────────────────────────┐
│ Date: 2023-04-06        │
│ FII Net: ₹2,318 Cr      │
│ DII Net: ₹-456 Cr       │
└─────────────────────────┘
```

### Expandable Insights
```
▼ 📊 Flow Analysis Insights
  ┌─────────────────────────────────────┐
  │ FII Behavior: 📉 Mild Net Sellers   │
  │ DII Behavior: 📉 Mild Net Sellers   │
  │ Relationship: 🤝 Balanced           │
  └─────────────────────────────────────┘
```

### Tab Navigation
```
┌────────────────────────────────────────────────────────┐
│ [🟢 FII Accumulation (16)] [🔴 FII Distribution (16)] │
│ [ 🟢 DII Accumulation (17)] [ 🔴 DII Distribution (16)]│
├────────────────────────────────────────────────────────┤
│ Currently showing: FII Accumulation Periods            │
│ ✅ Found 16 FII accumulation periods                   │
└────────────────────────────────────────────────────────┘
```

## 📊 Chart Features

### FII vs DII Flows Chart
- **Type:** Dual-axis line chart
- **Colors:** Green (FII), Orange (DII)
- **Features:**
  - Interactive hover tooltips
  - Zoom and pan
  - Zero reference line
  - Date range filtering

### Cumulative Flows Chart
- **Type:** Line chart with running totals
- **Colors:** Green (FII), Orange (DII)
- **Features:**
  - Shows long-term trends
  - Identifies accumulation/distribution phases
  - Interactive tooltips

### Correlation Heatmap
- **Type:** Color-coded matrix
- **Colors:** Green (positive), Red (negative), White (neutral)
- **Features:**
  - Hover for exact values
  - Multiple variables
  - Easy interpretation

## 🎯 Key Metrics Display

```
┌──────────────────────┐
│ Total FII Net Flow   │
│ ₹-22,016 Cr          │
│ 📉 45.2% positive    │
└──────────────────────┘
```

Each metric card shows:
- Label (what it measures)
- Value (with currency formatting)
- Delta (change or percentage)

## 💡 Insight Generation

The page automatically generates insights like:

```
✅ Both FII and DII were strong net buyers - bullish signal
🔄 FII buying while DII selling - mixed signals
⚠️ FII showed consistent selling behavior
📈 More FII accumulation than distribution periods
🔗 FII flows positively correlated with returns
```

## 🎨 Color Scheme

- **Green (#2ca02c):** Positive, buying, accumulation
- **Red (#d62728):** Negative, selling, distribution
- **Orange (#ff7f0e):** DII flows, neutral
- **Blue (#1f77b4):** General data, NIFTY
- **Gray:** Reference lines, neutral zones

## 📱 Responsive Design

The page adapts to different screen sizes:
- **Desktop:** Full width with 4-column metrics
- **Tablet:** 2-column metrics, full-width charts
- **Mobile:** Single column layout, scrollable charts

## ⚡ Performance

- **Data Loading:** Cached for 1 hour
- **Chart Rendering:** < 1 second
- **Period Detection:** < 2 seconds
- **Page Load:** < 3 seconds

## 🔍 Search & Filter

Users can:
- Filter by date range (sidebar)
- Adjust period detection parameters
- Toggle between different period types (tabs)
- Expand/collapse insight sections

---

**This preview shows the structure and layout of the Institutional Activity page.**  
**All charts are interactive and data updates in real-time based on user selections.**

*Smart Money Intelligence Platform*  
*Dashboard Preview - Institutional Activity Page*
