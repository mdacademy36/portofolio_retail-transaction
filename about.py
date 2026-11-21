
import streamlit as st
import base64
from pathlib import Path


def tampilkan_tentang():

    # Load foto profil
    image_path = Path("maulana.png")

    if image_path.exists():
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

        profile_img_html = f"""
        <div style="display:flex; justify-content:center; margin-top:10px;">
            <img src="data:image/png;base64,{img_base64}"
                 alt="Maulana Profile Picture"
                 style="width:260px; height:260px; object-fit:cover;
                        border-radius:50%; border:3px solid #ff9d2e;" />
        </div>
        """
    else:
        profile_img_html = ""

    # Judul About Me
    st.markdown(
        """
        <div style="margin-bottom:24px;">
            <p style="color:#ff9d2e; font-size:13px;
                      font-weight:700; letter-spacing:2px;">
                ABOUT ME
            </p>
            <h1 style="margin-bottom:8px;">
                Data Analytics &amp; Business Insights
            </h1>
            <p style="color:#a8b0bb; font-size:16px;">
                Business Thinking. Data-Driven Solutions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Layout dua kolom
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:

        # Professional Summary
        st.markdown(
            """
            I am a **business professional with 8 years of experience
            in sales and marketing**, with a growing focus on data
            analytics and business intelligence. My business background
            enables me to understand business challenges and transform
            raw data into meaningful insights that support informed
            decision-making and business growth.

            I use tools such as **Excel, SQL, Python, and Power BI**
            to analyze data, identify trends, and uncover business
            opportunities. I also leverage **n8n workflow automation**
            to streamline repetitive tasks and improve operational
            efficiency.

            My goal is to combine business knowledge, data analytics,
            and automation to deliver practical, data-driven solutions
            that create value for businesses.
            """
        )

        # Technical Skills
        st.markdown("### Technical Skills")

        st.markdown(
            """
            **Excel** · **SQL** · **Python** · **Power BI** ·
            **Looker Studio** · **n8n Automation**
            """
        )

        st.markdown("---")

        # Featured Project
        st.markdown("### Featured Project")

        st.markdown(
            """
            **Customer Segmentation Using RFM Analysis**

            This project analyzes retail transaction data using
            Recency, Frequency, and Monetary (RFM) analysis to
            understand customer purchasing behavior, identify
            valuable customer segments, and support data-driven
            business decisions.
            """
        )
        st.markdown(
            "[View Project Presentation](https://drive.google.com/file/d/1-x_uO6LhGUsmZdbOVBP5_v-aRNwtlrCO/view?usp=sharing)"
        )

    with col2:

        if profile_img_html:
            st.markdown(profile_img_html, unsafe_allow_html=True)

        st.markdown(
            """
            <div style="text-align:center; margin-top:18px;">
                <h3 style="margin-bottom:4px;">Maulana</h3>
                <p style="color:#a8b0bb; font-size:14px;">
                    Data Analyst
                </p>
                <p style="font-size:13px;">
                    📍 Banda Aceh, Indonesia
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("### Connect With Me")
        st.write(
            "Interested in data analytics, business insights, and automation?"
        )

        st.markdown("[LinkedIn](https://www.linkedin.com/)")
        st.markdown("[GitHub](https://github.com/)")
