import streamlit as st
import pandas as pd
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Business Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 25px;
}

.insight-box {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 10px;
}

.small-text {
    color: #777;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="main-title">📊 AI Business Intelligence Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered business analytics dashboard for sales performance, trends and automated insights.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader(
    "📂 Upload your business CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("👉 Upload a CSV file to start the business analysis.")
    st.stop()

# =========================================================
# LOAD DATA
# =========================================================
try:
    df = pd.read_csv(uploaded_file)

    # Remove empty rows/columns
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")

    # Clean column names
    df.columns = [
        str(col).strip().replace("\n", " ")
        for col in df.columns
    ]

except Exception as e:
    st.error("❌ Could not read the CSV file.")
    st.code(str(e))
    st.stop()

# =========================================================
# DATA CLEANING
# =========================================================

for col in df.columns:

    if df[col].dtype == "object":

        original = df[col].copy()

        numeric_version = pd.to_numeric(
            original.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip(),
            errors="coerce"
        )

        non_empty = original.notna().sum()

        if non_empty > 0:
            numeric_ratio = numeric_version.notna().sum() / non_empty

            if numeric_ratio >= 0.70:
                df[col] = numeric_version

# =========================================================
# SUCCESS MESSAGE
# =========================================================
st.success("✅ Data loaded and cleaned successfully!")

# =========================================================
# DATA QUALITY
# =========================================================
missing_values = int(df.isna().sum().sum())
duplicate_rows = int(df.duplicated().sum())

if missing_values == 0:
    st.success("✅ Data quality looks good. No missing values detected.")
else:
    st.warning(
        f"⚠️ Data contains {missing_values} missing values."
    )

if duplicate_rows > 0:
    st.warning(
        f"⚠️ {duplicate_rows} duplicate rows detected."
    )

# =========================================================
# COLUMN DETECTION
# =========================================================
numeric_columns = df.select_dtypes(
    include=np.number
).columns.tolist()

if len(numeric_columns) == 0:
    st.error("❌ No numeric column found for sales analysis.")
    st.dataframe(df, use_container_width=True)
    st.stop()

# =========================================================
# DATE COLUMN DETECTION
# =========================================================
date_column = None

for col in df.columns:

    if df[col].dtype == "object":

        parsed = pd.to_datetime(
            df[col],
            errors="coerce",
            dayfirst=True
        )

        if len(df) > 0:
            ratio = parsed.notna().sum() / len(df)

            if ratio >= 0.60:
                date_column = col
                break

# =========================================================
# CATEGORY COLUMN DETECTION
# =========================================================
category_columns = []

for col in df.columns:

    if df[col].dtype == "object":

        unique_values = df[col].nunique()

        if 1 < unique_values <= 50:
            category_columns.append(col)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("🎛️ Dashboard Controls")

selected_sales_column = st.sidebar.selectbox(
    "💰 Sales / Value Column",
    numeric_columns
)

# Category filter
selected_category_column = None
selected_categories = None

if category_columns:

    selected_category_column = st.sidebar.selectbox(
        "🏷️ Category / Product",
        ["None"] + category_columns
    )

    if selected_category_column != "None":

        category_values = sorted(
            df[selected_category_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_categories = st.sidebar.multiselect(
            "Select values",
            category_values,
            default=category_values
        )

        df = df[
            df[selected_category_column]
            .astype(str)
            .isin(selected_categories)
        ]

# =========================================================
# DATE FILTER
# =========================================================
if date_column:

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
        dayfirst=True
    )

    valid_dates = df[date_column].dropna()

    if len(valid_dates) > 0:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        if min_date != max_date:

            date_range = st.sidebar.date_input(
                "📅 Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            if len(date_range) == 2:

                start_date = pd.Timestamp(date_range[0])
                end_date = pd.Timestamp(date_range[1])

                df = df[
                    (df[date_column] >= start_date)
                    & (df[date_column] <= end_date)
                ]

# =========================================================
# EMPTY DATA CHECK
# =========================================================
if df.empty:

    st.warning("⚠️ No data available for the selected filters.")
    st.stop()

# =========================================================
# BASIC METRICS
# =========================================================
sales = pd.to_numeric(
    df[selected_sales_column],
    errors="coerce"
).fillna(0)

total_sales = sales.sum()
total_orders = len(df)
average_sale = sales.mean()
highest_sale = sales.max()
lowest_sale = sales.min()

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================
st.subheader("🧠 Executive Business Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.metric(
        "💰 Revenue",
        f"₹{total_sales:,.2f}"
    )

with summary_col2:
    st.metric(
        "🧾 Transactions",
        f"{total_orders:,}"
    )

with summary_col3:
    st.metric(
        "📈 Avg Transaction",
        f"₹{average_sale:,.2f}"
    )

st.markdown(
    f"""
    <div class="insight-box">
    📌 The business recorded <b>₹{total_sales:,.2f}</b> in total revenue
    across <b>{total_orders}</b> transactions.
    The average transaction value is
    <b>₹{average_sale:,.2f}</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# KPI CARDS
# =========================================================
st.subheader("📌 Key Business Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Total Sales",
    f"₹{total_sales:,.2f}"
)

c2.metric(
    "🧾 Total Orders",
    f"{total_orders:,}"
)

c3.metric(
    "📊 Average Sale",
    f"₹{average_sale:,.2f}"
)

c4.metric(
    "🏆 Highest Sale",
    f"₹{highest_sale:,.2f}"
)

# =========================================================
# SALES CHART
# =========================================================
st.subheader("📊 Sales Performance")

chart1, chart2 = st.columns(2)

# =========================================================
# CATEGORY CHART
# =========================================================
with chart1:

    if category_columns:

        chart_category = st.selectbox(
            "📦 Sales by Category",
            category_columns,
            key="sales_category"
        )

        category_sales = (
            df.groupby(chart_category)[selected_sales_column]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_sales)

    else:

        st.info("No category/product column detected.")

# =========================================================
# TIME TREND
# =========================================================
with chart2:

    if date_column:

        trend_data = df.dropna(
            subset=[date_column]
        ).copy()

        if not trend_data.empty:

            trend_data["Analysis Date"] = (
                trend_data[date_column].dt.date
            )

            daily_sales = (
                trend_data
                .groupby("Analysis Date")[selected_sales_column]
                .sum()
            )

            st.line_chart(daily_sales)

        else:

            st.info("No valid dates available.")

    else:

        st.info("No date column detected.")

# =========================================================
# TOP PERFORMERS
# =========================================================
if category_columns:

    st.subheader("🏆 Top Performing Products / Categories")

    top_col = st.selectbox(
        "Select category for ranking",
        category_columns,
        key="top_category"
    )

    top_data = (
        df.groupby(top_col)[selected_sales_column]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    top_table = top_data.reset_index()

    top_table.columns = [
        "Category",
        "Total Sales"
    ]

    top_table["Total Sales"] = (
        top_table["Total Sales"].round(2)
    )

    st.dataframe(
        top_table,
        use_container_width=True,
        hide_index=True
    )

    if len(top_data) > 0:

        best_name = str(top_data.index[0])
        best_value = top_data.iloc[0]

        st.success(
            f"🚀 Best performer: **{best_name}** "
            f"with sales of **₹{best_value:,.2f}**."
        )

# =========================================================
# SALES DISTRIBUTION
# =========================================================
st.subheader("📈 Sales Distribution")

distribution_col1, distribution_col2 = st.columns(2)

with distribution_col1:

    st.write("Minimum Transaction")
    st.metric(
        "Lowest Sale",
        f"₹{lowest_sale:,.2f}"
    )

with distribution_col2:

    median_sale = sales.median()

    st.write("Median Transaction")
    st.metric(
        "Median Sale",
        f"₹{median_sale:,.2f}"
    )

# =========================================================
# AUTOMATED BUSINESS INTELLIGENCE
# =========================================================
st.subheader("🤖 Automated Business Intelligence")

insights = []

# Average transaction insight
if average_sale > 0:

    insights.append(
        f"💡 Average transaction value is "
        f"₹{average_sale:,.2f}. "
        f"Bundles and upselling can help increase order value."
    )

# Highest sale
if highest_sale > 0:

    insights.append(
        f"🏆 The highest single transaction is "
        f"₹{highest_sale:,.2f}."
    )

# Lowest sale
if lowest_sale > 0:

    insights.append(
        f"📉 The lowest transaction is "
        f"₹{lowest_sale:,.2f}."
    )

# Best category
if category_columns:

    insight_category = category_columns[0]

    grouped = (
        df.groupby(insight_category)[selected_sales_column]
        .sum()
        .sort_values(ascending=False)
    )

    if len(grouped) > 0:

        best_product = str(grouped.index[0])

        insights.append(
            f"🚀 **{best_product}** is the top-performing "
            f"category based on revenue."
        )

# Revenue concentration
if category_columns:

    concentration_category = category_columns[0]

    grouped_sales = (
        df.groupby(concentration_category)[selected_sales_column]
        .sum()
        .sort_values(ascending=False)
    )

    if total_sales > 0 and len(grouped_sales) > 0:

        top_share = (
            grouped_sales.iloc[0] / total_sales
        ) * 100

        if top_share >= 50:

            insights.append(
                f"⚠️ The leading category contributes "
                f"approximately {top_share:.1f}% of total revenue. "
                f"Consider reducing dependency by developing other categories."
            )

        else:

            insights.append(
                f"✅ Revenue is relatively diversified; "
                f"the top category contributes about {top_share:.1f}%."
            )

for insight in insights:

    st.info(insight)

# =========================================================
# TREND INSIGHT
# =========================================================
if date_column:

    trend_data = df.dropna(
        subset=[date_column]
    ).copy()

    if len(trend_data) >= 2:

        trend_data = trend_data.sort_values(
            date_column
        )

        first_period = trend_data.iloc[0][selected_sales_column]
        last_period = trend_data.iloc[-1][selected_sales_column]

        if first_period > 0:

            change_percent = (
                (last_period - first_period)
                / first_period
            ) * 100

            if change_percent > 0:

                st.success(
                    f"📈 **Trend Insight:** Sales increased by "
                    f"approximately {change_percent:.1f}% "
                    f"from the first to the latest recorded transaction."
                )

            elif change_percent < 0:

                st.warning(
                    f"📉 **Trend Insight:** Sales decreased by "
                    f"approximately {abs(change_percent):.1f}% "
                    f"from the first to the latest recorded transaction."
                )

            else:

                st.info(
                    "➡️ **Trend Insight:** Sales remained relatively stable."
                )

# =========================================================
# ANOMALY DETECTION
# =========================================================
st.subheader("🔎 Transaction Anomaly Detection")

if len(sales) >= 4:

    q1 = sales.quantile(0.25)
    q3 = sales.quantile(0.75)

    iqr = q3 - q1

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    anomalies = df[
        (df[selected_sales_column] < lower_limit)
        | (df[selected_sales_column] > upper_limit)
    ]

    if len(anomalies) > 0:

        st.warning(
            f"⚠️ {len(anomalies)} unusual transaction(s) "
            f"detected using the IQR method."
        )

        st.dataframe(
            anomalies,
            use_container_width=True
        )

    else:

        st.success(
            "✅ No significant transaction anomalies detected."
        )

else:

    st.info(
        "ℹ️ More transactions are required for reliable anomaly detection."
    )

# =========================================================
# DATA QUALITY SUMMARY
# =========================================================
st.subheader("🔍 Data Quality & Summary")

quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)

quality_col1.metric(
    "Rows",
    len(df)
)

quality_col2.metric(
    "Columns",
    len(df.columns)
)

quality_col3.metric(
    "Missing Values",
    missing_values
)

quality_col4.metric(
    "Duplicate Rows",
    duplicate_rows
)

with st.expander("📋 View Detailed Data Summary"):

    try:

        summary = df.describe(include="all").transpose()

        st.dataframe(
            summary,
            use_container_width=True
        )

    except Exception:

        st.write(df.describe())

# =========================================================
# RAW / FILTERED DATA
# =========================================================
with st.expander("📄 View Filtered Business Data"):

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# DOWNLOAD
# =========================================================
st.subheader("📥 Export Analysis Data")

download_data = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=download_data,
    file_name="business_analysis_filtered.csv",
    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown(
    """
    <div class="small-text">
    📊 AI Business Intelligence Agent<br>
    Built with Python • Pandas • NumPy • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)