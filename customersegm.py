import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =====================================================
# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_parquet("Retail_Transactions_.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


# =====================================================
# RFM LOGIC
def build_rfm(df):
    rfm = (
        df.groupby("Customer_Name")
        .agg(
            LastPurchase=("Date", "max"),
            Frequency=("Transaction_ID", "count"),
            Monetary=("Total_Cost", "sum")
        )
        .reset_index()
    )

    last_date = df["Date"].max()
    rfm["Recency"] = (last_date - rfm["LastPurchase"]).dt.days

    # Quantiles
    r_q = rfm["Recency"].quantile([0.2, 0.4, 0.6, 0.8])
    f_q = rfm["Frequency"].quantile([0.2, 0.4, 0.6, 0.8])
    m_q = rfm["Monetary"].quantile([0.2, 0.4, 0.6, 0.8])

    rfm["R_Score"] = rfm["Recency"].apply(
        lambda x: 5 if x <= r_q[0.2] else
                  4 if x <= r_q[0.4] else
                  3 if x <= r_q[0.6] else
                  2 if x <= r_q[0.8] else 1
    )

    rfm["F_Score"] = rfm["Frequency"].apply(
        lambda x: 1 if x <= f_q[0.2] else
                  2 if x <= f_q[0.4] else
                  3 if x <= f_q[0.6] else
                  4 if x <= f_q[0.8] else 5
    )

    rfm["M_Score"] = rfm["Monetary"].apply(
        lambda x: 1 if x <= m_q[0.2] else
                  2 if x <= m_q[0.4] else
                  3 if x <= m_q[0.6] else
                  4 if x <= m_q[0.8] else 5
    )

    def segment(row):
        if row["R_Score"] == 5 and row["F_Score"] >= 4:
            return "Champions"
        elif row["R_Score"] >= 4 and row["F_Score"] >= 2:
            return "Loyal Customers"
        elif row["R_Score"] >= 4:
            return "Potential Loyalists"
        elif row["R_Score"] <= 2:
            return "At Risk"
        else:
            return "Lost"

    rfm["RFM_Segment"] = rfm.apply(segment, axis=1)

    return rfm


# =====================================================
# COHORT & RETENTION
def cohort_retention(df):
    data = df.copy()

    data["TransactionMonth"] = data["Date"].dt.to_period("M").dt.to_timestamp()

    join_month = (
        data.groupby("Customer_Name")["TransactionMonth"]
        .min()
        .reset_index()
        .rename(columns={"TransactionMonth": "JoinMonth"})
    )

    data = data.merge(join_month, on="Customer_Name", how="left")

    data["MonthOffset"] = (
        (data["TransactionMonth"].dt.year - data["JoinMonth"].dt.year) * 12 +
        (data["TransactionMonth"].dt.month - data["JoinMonth"].dt.month)
    )

    cohort_size = (
        data[data["MonthOffset"] == 0]
        .groupby("JoinMonth")["Customer_Name"]
        .nunique()
        .rename("CohortSize")
    )

    active = (
        data.groupby(["JoinMonth", "MonthOffset"])["Customer_Name"]
        .nunique()
        .rename("ActiveCustomers")
        .reset_index()
    )

    retention = active.merge(cohort_size, on="JoinMonth")
    retention["RetentionRate"] = retention["ActiveCustomers"] / retention["CohortSize"]

    pivot = retention.pivot(
        index="JoinMonth",
        columns="MonthOffset",
        values="RetentionRate"
    ).sort_index()

    return pivot


# =====================================================
# STREAMLIT PAGE
def tampilkan_segmentasi():
    st.title("Customer Segmentation & Retention Analysis")
    st.caption("Retail Transaction Dataset | RFM & Cohort Analysis")

    df = load_data()
    rfm = build_rfm(df)

    # ---------------- FILTER ----------------
    st.subheader("🎛️ Filter Segment")
    segments = sorted(rfm["RFM_Segment"].unique())

    selected = st.multiselect(
        "Select customer segment(s):",
        options=segments,
        default=segments
    )

    filtered_rfm = rfm[rfm["RFM_Segment"].isin(selected)]

    # ---------------- METRICS ----------------
    st.subheader("📊 Executive Summary")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Customers", f"{filtered_rfm.shape[0]:,}")
    c2.metric("Total Revenue", f"${filtered_rfm['Monetary'].sum():,.0f}")
    c3.metric("Avg Recency (Days)", f"{filtered_rfm['Recency'].mean():.1f}")
    c4.metric("Avg Frequency", f"{filtered_rfm['Frequency'].mean():.1f}")

    # ---------------- TABLE ----------------
    st.subheader("📄 RFM Table")
    st.dataframe(filtered_rfm.head(20))

    # ---------------- BAR ----------------
    st.subheader("📦 Customer Distribution")
    seg_count = filtered_rfm["RFM_Segment"].value_counts().reset_index()
    seg_count.columns = ["Segment", "Customers"]

    fig_bar = px.bar(
        seg_count,
        x="Segment",
        y="Customers",
        color="Segment",
        text="Customers"
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- PIE ----------------
    st.subheader("💰 Revenue Contribution")
    rev = filtered_rfm.groupby("RFM_Segment")["Monetary"].sum().reset_index()

    fig_pie = px.pie(
        rev,
        names="RFM_Segment",
        values="Monetary",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------- INSIGHT ----------------
    st.subheader("📌 Key Insights")
    st.markdown("""
    - High-value customers (**Champions & Loyal**) contribute the majority of revenue.
    - A large portion of customers fall into **At Risk** and **Lost** segments.
    - Retention drops significantly after early transactions.
    """)

    # ---------------- RECOMMENDATION ----------------
    st.subheader("🎯 Business Recommendations")
    with st.expander("View Recommendations"):
        st.markdown("""
        - Strengthen loyalty programs for high-value customers  
        - Launch reactivation campaigns for at-risk customers  
        - Improve early customer experience to reduce churn  
        """)

    # ---------------- COHORT ----------------
    st.subheader("🔁 Cohort Retention Analysis")
    cohort = cohort_retention(df)

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=cohort.values,
            x=cohort.columns,
            y=cohort.index.strftime("%Y-%m"),
            colorscale="Blues",
            hovertemplate="Retention: %{z:.0%}<extra></extra>"
        )
    )

    fig_heat.update_layout(
        xaxis_title="Months Since First Purchase",
        yaxis_title="Cohort Month"
    )

    st.plotly_chart(fig_heat, use_container_width=True)
