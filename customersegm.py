import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================
# LOAD DATA
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
    current_dir,
    "Retail_Transactions_Cleaned.parquet"
)

    print("LOKASI DATASET:", file_path)

    if not os.path.exists(file_path):
        st.error(f"File dataset tidak ditemukan: {file_path}")
        st.write("File yang tersedia:", os.listdir(current_dir))
        return None

    try:
        df = pd.read_parquet(file_path)

        print("JUMLAH BARIS DATASET:", len(df))

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        return df

    except Exception as exc:
        st.error(f"Gagal membaca dataset: {exc}")
        return None


# =====================================================
# RFM LOGIC

def build_rfm(df):
    rfm = (
        df.groupby("Customer_Name")
        .agg(
            LastPurchase=("Date", "max"),
            Frequency=("Date", "count"),
            Monetary=("Total_Cost", "sum")
        )
        .reset_index()
    )

    # Recency
    snapshot_date = df["Date"].max() + pd.Timedelta(days=1)
    rfm["Recency"] = (
        snapshot_date - rfm["LastPurchase"]
    ).dt.days

    # RFM Scoring
    rfm["R_Score"] = pd.qcut(
        rfm["Recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    rfm["F_Score"] = pd.cut(
        rfm["Frequency"],
        bins=[0, 1, 2, 3, 5, float("inf")],
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Customer Segmentation
    def segment_customer(row):
        R = row["R_Score"]
        F = row["F_Score"]
        M = row["M_Score"]

        if R >= 4 and F >= 4 and M >= 4:
            return "Champions"
        elif R >= 3 and F >= 3 and M >= 3:
            return "Loyal Customers"
        elif R >= 4 and F >= 2:
            return "Potential Loyalists"
        elif R >= 4 and F == 1:
            return "New Customers"
        elif R <= 2 and (F >= 3 or M >= 4):
            return "At Risk"
        else:
            return "Lost"

    rfm["RFM_Segment"] = rfm.apply(
        segment_customer, axis=1
    )

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

    if df is None or df.empty:
        st.error("Dataset kosong atau gagal dimuat.")
        return

    rfm = build_rfm(df)

    if rfm is None or rfm.empty:
        st.warning("Hasil analisis RFM tidak tersedia.")
        return

    # ---------------- FILTER ----------------
    st.subheader("🎛️ Filter Segment")
    segments = sorted(rfm["RFM_Segment"].unique())

    selected = st.multiselect(
        "Select customer segment(s):",
        options=segments,
        default=segments
    )

    filtered_rfm = rfm[rfm["RFM_Segment"].isin(selected)]

   
    # ---------------- EXECUTIVE SUMMARY ----------------
    st.subheader("📊 Executive Summary")

    c1, c2, c3, c4 = st.columns(4)

    kpi_data = [
        ("TOTAL CUSTOMERS", f"{filtered_rfm.shape[0]:,}"),
        ("TOTAL REVENUE", f"${filtered_rfm['Monetary'].sum():,.2f}"),
        ("AVG. RECENCY", f"{filtered_rfm['Recency'].mean():,.1f} Days"),
        ("AVG. FREQUENCY", f"{filtered_rfm['Frequency'].mean():,.1f}")
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], kpi_data):
        with col:
            st.markdown(
                f"""
                <div style="
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                    padding: 20px 16px;
                    min-height: 105px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.04);
                ">
                    <p style="
                        color: #64748B;
                        font-size: 12px;
                        font-weight: 600;
                        margin-bottom: 12px;
                    ">{label}</p>
                    <h3 style="
                        color: #164E4A;
                        font-size: 25px;
                        font-weight: 700;
                        margin: 0;
                    ">{value}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
   
# ---------------- RFM TABLE ----------------
    st.subheader("RFM Customer Details")

    rfm_display = filtered_rfm.head(20).copy()

    st.dataframe(
        rfm_display,
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "Customer_Name": st.column_config.TextColumn(
                "Customer Name",
                width="medium"
            ),
            "LastPurchase": st.column_config.DatetimeColumn(
                "Last Purchase",
                format="DD MMM YYYY",
                width="medium"
            ),
            "Frequency": st.column_config.NumberColumn(
                "Frequency",
                format="%d"
            ),
            "Monetary": st.column_config.NumberColumn(
                "Monetary",
                format="%.2f"
            ),
            "Recency": st.column_config.NumberColumn(
                "Recency (Days)",
                format="%d"
            ),
            "R_Score": st.column_config.NumberColumn(
                "R Score",
                format="%d"
            ),
            "F_Score": st.column_config.NumberColumn(
                "F Score",
                format="%d"
            ),
            "M_Score": st.column_config.NumberColumn(
                "M Score",
                format="%d"
            ),
            "RFM_Segment": st.column_config.TextColumn(
                "Customer Segment",
                width="medium"
            )
        }
    )


    # ---------------- CUSTOMER DISTRIBUTION ----------------
    st.subheader("Customer Distribution")

    seg_count = (
        filtered_rfm["RFM_Segment"]
        .value_counts()
        .reset_index()
    )

    seg_count.columns = ["Segment", "Customers"]

    # Consistent RFM colors
    segment_colors = {
        "Champions": "#164E4A",
        "Loyal Customers": "#2589F5",
        "Potential Loyalists": "#64B5F6",
        "New Customers": "#8CCFB5",
        "At Risk": "#F4A261",
        "Lost": "#D96C6C"
    }

    fig_bar = px.bar(
        seg_count,
        x="Segment",
        y="Customers",
        color="Segment",
        text="Customers",
        color_discrete_map=segment_colors
    )

    fig_bar.update_traces(
        textposition="outside",
        texttemplate="%{text:,.0f}"
    )

    fig_bar.update_layout(
        height=400,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=15, r=15, t=30, b=15),
        font=dict(color="#475569"),
        xaxis=dict(
            title="Customer Segment",
            color="#475569",
            showgrid=False,
            tickangle=-25
        ),
        yaxis=dict(
            title="Number of Customers",
            color="#475569",
            showgrid=True,
            gridcolor="#DDE5E7",
            rangemode="tozero"
        ),
        showlegend=False
    )

    st.plotly_chart(fig_bar, use_container_width=True)


    # ---------------- REVENUE CONTRIBUTION ----------------
    st.subheader("Revenue Contribution")

    rev = (
        filtered_rfm.groupby("RFM_Segment")["Monetary"]
        .sum()
        .reset_index()
    )

    fig_pie = px.pie(
        rev,
        names="RFM_Segment",
        values="Monetary",
        hole=0.55,
        color="RFM_Segment",
        color_discrete_map=segment_colors
    )

    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Revenue: %{value:,.2f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    fig_pie.update_layout(
        height=400,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=15, r=15, t=30, b=15),
        font=dict(color="#475569"),
        legend_title_text="Customer Segment"
    )

    st.plotly_chart(fig_pie, use_container_width=True)


    
    # ---------------- BUSINESS INSIGHTS ----------------
    st.subheader("Business Insights")

    st.markdown("""
    <div style="
        background-color: #FFFFFF;
        border-left: 5px solid #164E4A;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
    ">
        <h4 style="color: #164E4A; margin-top: 0;">
            1. Largest Customer Segment
        </h4>
        <p style="color: #475569; margin-bottom: 0;">
            Lost customers represent <b>47.2%</b> of the customer base,
            indicating a significant opportunity for customer reactivation.
        </p>
    </div>

    <div style="
        background-color: #FFFFFF;
        border-left: 5px solid #2589F5;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
    ">
        <h4 style="color: #164E4A; margin-top: 0;">
            2. Revenue Concentration
        </h4>
        <p style="color: #475569; margin-bottom: 0;">
            Champions contribute <b>48.5%</b> of total revenue,
            highlighting their importance to business performance.
        </p>
    </div>

    <div style="
        background-color: #FFFFFF;
        border-left: 5px solid #F4A261;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 12px;
    ">
        <h4 style="color: #164E4A; margin-top: 0;">
            3. Customer Retention Opportunity
        </h4>
        <p style="color: #475569; margin-bottom: 0;">
            Retention analysis indicates declining customer activity
            across later purchase periods. This creates an opportunity
            to strengthen customer engagement.
        </p>
    </div>
    """, unsafe_allow_html=True)


    # ---------------- BUSINESS RECOMMENDATIONS ----------------
    st.subheader("Business Recommendations")

    with st.expander("View Business Recommendations", expanded=True):

        st.markdown("""
        **1. Customer Reactivation**
        - Develop targeted campaigns for Lost and At Risk customers.
        - Use personalized offers to encourage repeat purchases.

        **2. Customer Loyalty**
        - Strengthen loyalty programs for Champions and Loyal Customers.
        - Provide exclusive rewards to retain high-value customers.

        **3. Customer Retention**
        - Improve the first-purchase experience for New Customers.
        - Develop follow-up campaigns to encourage second purchases.
        """)


    
    # ---------------- COHORT RETENTION ----------------
    st.subheader("Cohort Retention Analysis")

    cohort = cohort_retention(df)

    
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=cohort.values,
            x=cohort.columns,
            y=cohort.index.strftime("%Y-%m"),
            colorscale=[
                [0.0, "#F1F5F9"],
                [0.25, "#BFDBFE"],
                [0.50, "#60A5FA"],
                [0.75, "#2589F5"],
                [1.0, "#164E4A"]
            ],
            zmin=0,
            zmax=1,
            hovertemplate=(
                "<b>Cohort:</b> %{y}<br>"
                "<b>Month Offset:</b> %{x}<br>"
                "<b>Retention:</b> %{z:.1%}"
                "<extra></extra>"
            ),
            colorbar=dict(
                title="Retention",
                tickformat=".0%"
            )
        )
    )

    fig_heat.update_layout(
        height=550,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=30, b=30),
        font=dict(color="#475569"),
        xaxis=dict(
            title="Months Since First Purchase",
            showgrid=False,
            color="#475569",
            dtick=1
        ),
        yaxis=dict(
            title="Cohort Month",
            showgrid=False,
            color="#475569",
            autorange="reversed"
        )
    )

    st.plotly_chart(fig_heat, use_container_width=True)
