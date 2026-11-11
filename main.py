import streamlit as st

st.set_page_config(
    page_title="Customer Segmentation | Maulana",
    layout="wide",
    page_icon="📊"
)


# Styling aplikasi
st.markdown("""
<style>
    /* Main title */
    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #64748B;
        font-size: 16px;
        margin-bottom: 22px;
    }

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #164E4A;
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    /* Sidebar radio selection */
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* Sidebar logo card */
    .sidebar-brand {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px 10px;
        text-align: center;
        margin-bottom: 22px;
    }

    .sidebar-brand h3 {
        color: #164E4A !important;
        margin: 0;
        font-size: 22px;
    }

    .sidebar-brand p {
        color: #64748B !important;
        font-size: 11px;
        margin: 5px 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<div class="sidebar-brand">
    <h3>MDacademy36</h3>
    <p>DATA ANALYTICS PORTFOLIO</p>
</div>
""", unsafe_allow_html=True)


page = st.sidebar.radio(
    "Choose what you want to know",
    [
        "About Me",
        "Projects",
        "Customer Segmentation",
        "Contacts"
    ]
)

# Navigasi halaman
if page == "About Me":
    import about
    about.tampilkan_tentang()

elif page == "Projects":
    import project
    project.tampilkan_dashboard()

elif page == "Customer Segmentation":
    import customersegm
    customersegm.tampilkan_segmentasi()

elif page == "Contacts":
    import contact
    contact.tampilkan_kontak()
