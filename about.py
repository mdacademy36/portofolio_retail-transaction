import streamlit as st
import base64

def tampilkan_tentang():
    # Baca gambar sebagai base64
    with open("maulana.png", "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # HTML + CSS untuk tampilkan gambar bulat
    profile_img_html = f"""
        <div style="display: flex; justify-content: flex-end; margin-top: -40px;">
            <img src="data:image/jpeg;base64,{img_base64}" 
                 alt="Profile Picture"
                 style="width: 300px; height: 300px; object-fit: cover; border-radius: 50%;" />
        </div>
    """

    # Layout dua kolom
    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown(profile_img_html, unsafe_allow_html=True)

    with col1:
        st.markdown("## 👋 Hello, I’maulana..")
        st.markdown("🌍 Based in **Banda Aceh, Indonesia**")
        st.markdown("🎓 Currently joining a **6-month Full Stack Data Science Bootcamp** with [dibimbing.id](https://dibimbing.id)")
        st.markdown("---")
        st.markdown("### 🧠 Final Project Summary")
        st.markdown(
            """
            I have completed my final project as a **Data Analyst**, focusing on Retail Transaction.  
            Using **Customer Segmentation Analysis**, I analyzed **43,000+ retail transactions** using RFM-based customer segmentation to uncover customer behavior, 
            revenue contribution, and retention issues. The analysis shows that high-value customers drive most revenue, 
            while low retention and recurring early-year sales declines highlight the need for targeted retention and reactivation strategies. 
            This project demonstrates how data-driven insights can support more effective business decisions.
.
            """
        )
        st.markdown("📊 Dataset Source: [Kaggle - Retail Transaction](https://drive.google.com/file/d/10cNDAdEzH8be6ZY_upS3YVmU7TUCuS-y/view?usp=sharing)")
        st.markdown("📎 Project Slide Deck: [Google Slides](https://drive.google.com/file/d/11BuJWpz3vulD8bHkXxuqm_1lQWfaygvF/view?usp=sharing)")
        st.markdown("---")
        st.markdown("### 📬 Contact Me")
        st.markdown("Please feel free to reach out with any Questions, compliments, or concerns. Let’s collaborate and connect!")