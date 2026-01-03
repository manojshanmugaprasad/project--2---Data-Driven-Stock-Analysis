import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Stock Market Analytics Dashboard", layout="wide")

st.title("📊 Stock Market Analytics Dashboard")

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
conn = sqlite3.connect("stock_analysis.db")

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
section = st.sidebar.radio(
    "📌 Select Analysis",
    [
        "Market Overview",
        "Volatility Analysis",
        "Sector-wise Performance",
        "Cumulative Returns",
        "Monthly Gainers & Losers",
        "Correlation Matrix"
    ]
)

# ==================================================
# 1️⃣ MARKET OVERVIEW
# ==================================================
if section == "Market Overview":
    st.header("📈 Market Overview")

    df = pd.read_sql("SELECT * FROM market_overview", conn)

    # Convert into dictionary
    metrics = dict(zip(df["metric"], df["value"]))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Stocks", int(metrics.get("Total Stocks", 0)))
    col2.metric("Average Price", round(metrics.get("Average Price", 0), 2))
    col3.metric("Green Stocks", int(metrics.get("Green Stocks", 0)))
    col4.metric("Red Stocks", int(metrics.get("Red Stocks", 0)))

    st.subheader("📊 Market Overview Table")
    st.dataframe(df, use_container_width=True)

# ==================================================
# 2️⃣ VOLATILITY ANALYSIS
# ==================================================
elif section == "Volatility Analysis":
    st.header("📉 Top 10 Most Volatile Stocks")

    df = pd.read_sql(
        "SELECT symbol, Volatility FROM top10_volatility ORDER BY Volatility DESC",
        conn
    )

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("symbol")["Volatility"])


# ==================================================
# 3️⃣ SECTOR-WISE PERFORMANCE
# ==================================================
elif section == "Sector-wise Performance":
    st.header("🏭 Sector-wise Average Return")

    df = pd.read_sql("""
        SELECT symbol, sector, "Average Yearly Return (%)" 
        FROM sector_returns
        ORDER BY "Average Yearly Return (%)" DESC
    """, conn)

    st.dataframe(df, use_container_width=True)

    st.subheader("Sector Performance Chart")
    fig, ax = plt.subplots(figsize=(20, 8))
    sns.barplot(
        data=df,
        x="symbol",
        y="Average Yearly Return (%)",
        hue="sector",
        dodge=False,
        ax=ax
    )
    plt.xticks(rotation=90)
    plt.title("Average Yearly Return by Sector")
    st.pyplot(fig)

# ==================================================
# 4️⃣ CUMULATIVE RETURNS
# ==================================================
elif section == "Cumulative Returns":
    st.header("📈 Cumulative Returns Over Time")

    df = pd.read_sql("SELECT * FROM cumulative_returns", conn)
    df["date"] = pd.to_datetime(df["date"])

    st.dataframe(df, use_container_width=True)

    top_symbols = (
        df.groupby("symbol")["cumulative_return"]
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index
    )

    fig, ax = plt.subplots(figsize=(14, 7))
    for sym in top_symbols:
        temp = df[df["symbol"] == sym]
        ax.plot(temp["date"], temp["cumulative_return"], label=sym)

    ax.set_title("Top 5 Symbols - Cumulative Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.legend()
    st.pyplot(fig)


# ==================================================
# 5️⃣ MONTHLY GAINERS & LOSERS
# ==================================================
elif section == "Monthly Gainers & Losers":
    st.header("📆 Monthly Top 5 Gainers & Losers")

    df = pd.read_sql("SELECT * FROM monthly_gainers_losers", conn)

    month = st.selectbox("Select Month", sorted(df["year_month"].unique()))
    filtered = df[df["year_month"] == month]

    st.dataframe(filtered, use_container_width=True)

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.barplot(
        data=filtered,
        x="symbol",
        y="monthly_return_pct",
        hue="type",
        palette={"gainer": "green", "loser": "red"},
        ax=ax
    )

    ax.axhline(0, color="black")
    ax.set_title(f"Top 5 Gainers & Losers - {month}")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ==================================================
# 6️⃣ CORRELATION MATRIX
# ==================================================
elif section == "Correlation Matrix":
    st.header("🔗 Stock Correlation Matrix")

    df = pd.read_sql("""
        SELECT symbol, correlated_symbol, correlation
        FROM correlation_matrix
    """, conn)

    pivot_df = df.pivot(index="symbol", columns="correlated_symbol", values="correlation")

    st.dataframe(pivot_df, use_container_width=True)

    fig, ax = plt.subplots(figsize=(18, 14))
    sns.heatmap(
        pivot_df,
        cmap="RdBu_r",
        center=0,
        linewidths=0.3,
        cbar_kws={"label": "Correlation"}
    )
    plt.title("Stock Correlation Heatmap")
    st.pyplot(fig)

conn.close()
