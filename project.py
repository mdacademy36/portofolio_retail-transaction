
import streamlit as st
import pandas as pd
import plotly.express as px

from customersegm import load_data, build_rfm


def tampilkan_dashboard():
    # =====================================================
    # 1. LOAD DATA
    # =====================================================
    df = load_data()

    if df is None or df.empty:
        st.error("Dataset could not be loaded. Please check the dataset file.")
        return

    required_columns = {"Date", "Customer_Name", "Total_Cost"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        st.error(
            "The dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )
        return

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    if df.empty:
        st.warning("No valid transaction dates are available.")
        return

    # =====================================================
    # 2. PROJECT HEADER
    # =====================================================
    st.title("Retail Transaction Analysis")
    st.caption(
        "Customer Segmentation | RFM Analysis | Business Insights"
    )

    st.markdown(
        """
        This project analyzes retail transaction data to understand
        customer purchasing behavior, identify valuable customer
        segments, and support data-driven business decisions.
        """
    )

    st.divider()

    # =====================================================
    # 3. DATASET OVERVIEW
    # =====================================================
    
    st.subheader("Dataset Overview")

    # Calculate KPI values
    total_records = len(df)
    total_columns = len(df.columns)
    total_customers = df["Customer_Name"].nunique()

    total_sales = df["Total_Cost"].sum()
    total_transactions = df["Transaction_ID"].nunique()

    avg_transaction_value = (
        total_sales / total_transactions
        if total_transactions > 0 else 0
    )

    
    # Display KPI Cards
    st.markdown("""
    <style>
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #DDE5E7;
            border-radius: 10px;
            padding: 18px 16px;
            min-height: 115px;
            box-shadow: 0 2px 5px rgba(22, 78, 74, 0.05);
        }

        .kpi-label {
            color: #64748B;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .kpi-value {
            color: #164E4A;
            font-size: 27px;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    kpi_data = [
        ("TOTAL RECORDS", f"{total_records:,}"),
        ("TOTAL COLUMNS", f"{total_columns:,}"),
        ("UNIQUE CUSTOMERS", f"{total_customers:,}"),
        ("AVG. TRANSACTION VALUE", f"{avg_transaction_value:,.2f}")
    ]

    for col, (label, value) in zip(
        [col1, col2, col3, col4], kpi_data
    ):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    # =====================================================
    # 4. MONTHLY TRANSACTION TREND
    # =====================================================
    st.subheader("Monthly Transaction Trend")
    st.write(
        "Track transaction activity over time to identify patterns "
        "and changes in purchasing activity."
    )

    if "Transaction_ID" in df.columns:
        monthly = (
            df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
            .groupby("Month")["Transaction_ID"]
            .nunique()
            .reset_index(name="Transactions")
        )
    else:
        monthly = (
            df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
            .groupby("Month")
            .size()
            .reset_index(name="Transactions")
        )

    if not monthly.empty:
        fig_trend = px.line(
            monthly,
            x="Month",
            y="Transactions",
            markers=True,
            labels={
                "Month": "Month",
                "Transactions": "Number of Transactions",
            },
        )

        
        fig_trend.update_traces(
            line=dict(color="#2589F5", width=2.5),
            marker=dict(size=5, color="#2589F5")
        )

        fig_trend.update_layout(
            height=350,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            margin=dict(l=15, r=15, t=25, b=15),
            xaxis=dict(
                showgrid=False,
                color="#475569",
                title_font=dict(color="#164E4A")
            ),
            yaxis=dict(
                rangemode="tozero",
                showgrid=True,
                gridcolor="#DDE5E7",
                color="#475569",
                title_font=dict(color="#164E4A")
            ),
            showlegend=False,
            font=dict(color="#475569")
        )


        st.plotly_chart(fig_trend, use_container_width=True)

        latest_month = monthly["Month"].max()
        if latest_month == df["Date"].max().to_period("M").to_timestamp():
            st.caption(
                "Note: The latest month may be incomplete. "
                "Interpret its transaction count with caution."
            )
            

    else:
        st.info("Monthly transaction data is not available.")

    st.divider()

    # January vs February Transaction Analysis
    st.subheader("January vs February Transaction Analysis")

    df["Year"] = df["Date"].dt.year
    df["Month_Number"] = df["Date"].dt.month

    monthly_comparison = (
        df[df["Month_Number"].isin([1, 2])]
        .groupby(["Year", "Month_Number"])
        .size()
        .unstack(fill_value=0)
        .rename(columns={1: "January", 2: "February"})
    )

    monthly_comparison["Change (%)"] = (
        (monthly_comparison["February"] - monthly_comparison["January"])
        / monthly_comparison["January"].replace(0, pd.NA)
    ) * 100

    st.dataframe(
        monthly_comparison.style.format({
            "January": "{:,.0f}",
            "February": "{:,.0f}",
            "Change (%)": "{:.2f}%"
        }),
        use_container_width=True
    )
    # Monthly Transaction Insight
    st.markdown("""
            <div style="
                background-color: white;
                border-left: 5px solid #175B52;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            ">
                <h3 style="color: #175B52; margin-top: 0; font-size: 20px;">
                    Monthly Transaction Pattern
                </h3>
                <p style="color: #475569; margin-bottom: 0; line-height: 1.6;">
                    Across 2020–2024, transaction volume consistently declined
                    in February compared with January, with an average decrease
                    of approximately 8.25%. This recurring pattern suggests
                    potential seasonal fluctuations in customer purchasing activity.
                </p>
            </div>
            """, unsafe_allow_html=True)
    # =====================================================
    # 5. CUSTOMER SEGMENTATION
    # =====================================================
    st.subheader("Customer Segmentation Overview")
    st.write(
        "RFM analysis groups customers by Recency, Frequency, "
        "and Monetary value."
    )

    try:
        rfm = build_rfm(df)
    except Exception as exc:
        st.error(f"Unable to calculate RFM analysis: {exc}")
        return

    if rfm is None or rfm.empty or "RFM_Segment" not in rfm.columns:
        st.warning("Customer segmentation results are not available.")
        return

    segment_summary = (
        rfm.groupby("RFM_Segment", as_index=False)
        .agg(
            Customers=("Customer_Name", "nunique"),
            Total_Revenue=("Monetary", "sum"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
        )
    )

    total_segment_customers = segment_summary["Customers"].sum()
    total_revenue = segment_summary["Total_Revenue"].sum()

    if total_segment_customers > 0:
        segment_summary["Customer Share (%)"] = (
            segment_summary["Customers"] / total_segment_customers * 100
        )
    else:
        segment_summary["Customer Share (%)"] = 0

    if total_revenue != 0:
        segment_summary["Revenue Share (%)"] = (
            segment_summary["Total_Revenue"] / total_revenue * 100
        )
    else:
        segment_summary["Revenue Share (%)"] = 0

    segment_summary = segment_summary.sort_values(
        "Customers", ascending=False
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Customer Distribution by Segment**")

        
        fig_customers = px.bar(
            segment_summary,
            x="RFM_Segment",
            y="Customers",
            text="Customers",
            color="RFM_Segment",
            color_discrete_map={
                "Champions": "#164E4A",
                "Loyal Customers": "#2589F5",
                "Potential Loyalists": "#64B5F6",
                "New Customers": "#8CCFB5",
                "At Risk": "#F4A261",
                "Lost": "#D96C6C"
            },
            labels={
                "RFM_Segment": "Customer Segment",
                "Customers": "Number of Customers",
            },
        )


        fig_customers.update_traces(textposition="outside")
        fig_customers.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=25, b=10),
            xaxis_tickangle=-25,
            showlegend=False,
        )

        st.plotly_chart(fig_customers, use_container_width=True)

    with chart_col2:
        st.markdown("**Revenue Contribution by Segment**")

        
        fig_revenue = px.pie(
            segment_summary,
            names="RFM_Segment",
            values="Total_Revenue",
            hole=0.55,
            color="RFM_Segment",
            color_discrete_map={
                "Champions": "#164E4A",
                "Loyal Customers": "#2589F5",
                "Potential Loyalists": "#64B5F6",
                "New Customers": "#8CCFB5",
                "At Risk": "#F4A261",
                "Lost": "#D96C6C"
            }
        )


        fig_revenue.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate=(
                "Segment: %{label}<br>"
                "Revenue: %{value:,.2f}<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

        fig_revenue.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=25, b=10),
            legend_title_text="Customer Segment",
        )

        st.plotly_chart(fig_revenue, use_container_width=True)

    st.divider()

    # =====================================================
    
# =====================================================
    # 6. SEGMENT SUMMARY
    # =====================================================
    st.subheader("Segment Summary")

    display_summary = segment_summary.rename(
        columns={"RFM_Segment": "Segment"}
    ).copy()

    # Format numerical values
    display_summary["Total_Revenue"] = display_summary[
        "Total_Revenue"
    ].map(lambda x: f"{x:,.2f}")

    for column in ["Avg_Recency", "Avg_Frequency"]:
        display_summary[column] = display_summary[column].map(
            lambda x: f"{x:,.1f}"
        )

    for column in ["Customer Share (%)", "Revenue Share (%)"]:
        display_summary[column] = display_summary[column].map(
            lambda x: f"{x:.1f}%"
        )

    display_summary["Customers"] = display_summary["Customers"].map(
        lambda x: f"{x:,}"
    )

    # Table styling
    styled_summary = (
        display_summary.style
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#164E4A"),
                    ("color", "#FFFFFF"),
                    ("font-weight", "bold"),
                    ("text-align", "left"),
                    ("padding", "12px")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("padding", "10px"),
                    ("color", "#475569"),
                    ("border-bottom", "1px solid #DDE5E7")
                ]
            }
        ])
    )

    st.dataframe(
        styled_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =====================================================
    # 7. BUSINESS INSIGHTS
    # =====================================================
    st.subheader("Business Insights")

    # Revenue berdasarkan City
    city_revenue = (
        df.groupby("City")["Total_Cost"]
        .sum()
        .sort_values(ascending=False)
    )
    # Revenue berdasarkan Store Type
    store_revenue = (
        df.groupby("Store_Type")["Total_Cost"]
        .sum()
        .sort_values(ascending=False)
    )

    # Metode pembayaran paling banyak digunakan
    payment_count = df["Payment_Method"].value_counts()

    # Transaksi berdasarkan Season
    season_count = df["Season"].value_counts()

    insights = []

    if not city_revenue.empty:
        insights.append({
            "title": "1. Top Performing City",
            "description": (
                f"{city_revenue.index[0]} generates the highest revenue "
                f"with {city_revenue.iloc[0]:,.2f} in total sales."
            ),
            "color": "#175B52"
        })
    if not store_revenue.empty:
        insights.append({
            "title": "2. Store Performance",
            "description": (
                f"{store_revenue.index[0]} contributes the highest revenue "
                f"among all store types, generating "
                f"{store_revenue.iloc[0]:,.2f}."
            ),
            "color": "#3182CE"
        })
    if not payment_count.empty:
        insights.append({
            "title": "3. Payment Preferences",
            "description": (
                f"{payment_count.index[0]} is the most frequently used "
                f"payment method, accounting for "
                f"{payment_count.iloc[0]:,} transactions."
            ),
            "color": "#F4A261"
        })
    if not season_count.empty:
        insights.append({
            "title": "4. Seasonal Transaction Pattern",
            "description": (
                f"{season_count.index[0]} records the highest transaction "
                f"volume with {season_count.iloc[0]:,} transactions."
             ),
             "color": "#8B7DBE"
        })

    
    for insight in insights:
        html_card = f"""
    <div style="background-color:white;
    border-left:5px solid {insight['color']};
    border-radius:10px;
    padding:20px;
    margin-bottom:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);">
    <h3 style="color:#175B52;
    margin-top:0;
    font-size:20px;">
    {insight['title']}
    </h3>
    <p style="color:#475569;
    margin-bottom:0;
    line-height:1.6;">
    {insight['description']}
    </p>
    </div>
    """
        st.markdown(html_card, unsafe_allow_html=True)

    
    st.caption(
    "Insights are calculated from the currently loaded retail transaction dataset."
)
    # =====================================================
    # 8. BUSINESS RECOMMENDATIONS
# =====================================================
    st.subheader("Business Recommendations")

    with st.expander("View Recommended Actions"):

        st.markdown("""
        **1. Revenue Growth**

        - Prioritize marketing activities in cities with strong sales performance.
        - Identify opportunities to improve revenue in lower-performing cities.

        **2. Store Performance Optimization**

        - Evaluate the strategies used by top-performing store types.
        - Improve operational efficiency in underperforming store types.

        **3. Payment Experience**

        - Ensure popular payment methods remain convenient and reliable.
        - Evaluate alternative payment options to improve customer convenience.

        **4. Seasonal Marketing Strategy**

        - Align promotional campaigns with periods of high transaction activity.
        - Develop targeted promotions during lower-activity seasons.

        **5. February Sales Strategy**

        - Evaluate promotional activities during February to maintain transaction volume.
        - Develop targeted campaigns to improve customer engagement during this period.
        """)

    st.divider()
    # =====================================================
    # 9. METHODOLOGY
    # =====================================================
    st.subheader("Project Methodology")

    method_col1, method_col2 = st.columns(2)

    with method_col1:
        st.markdown("**RFM Analysis**")
        st.write(
            "Segments customers using Recency (how recently they "
            "purchased), Frequency (how often they purchased), and "
            "Monetary value (their total spending)."
        )

    with method_col2:
        st.markdown("**Business Analysis**")
        st.write(
            "Compares customer distribution and revenue contribution "
            "to identify opportunities for retention and reactivation."
        )

    # =====================================================
    # 10. DATASET PREVIEW
    # =====================================================
    with st.expander("Explore Dataset Preview"):
        st.write("Preview the first 10 rows of the retail transaction dataset.")
        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Download Dataset Preview (CSV)",
            data=df.head(100).to_csv(index=False).encode("utf-8"),
            file_name="retail_transaction_preview.csv",
            mime="text/csv",
        )
