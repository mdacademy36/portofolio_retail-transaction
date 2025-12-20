import streamlit as st

def tampilkan_kontak():
    st.markdown("## 🤝 Let's Connect!")
    st.markdown(
        """
        I'm always open to collaboration, questions, or just a friendly chat.  
        Feel free to reach out through any of the platforms below:
        """
    )

    # LinkedIn badge
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Maulana%20-blue?logo=linkedin)](https://www.linkedin.com/in/maulana-maulana-00b6308a/)"
    )

    # GitHub badge 
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-Maulana-blue?logo=github)](https://github.com/mdacademy36)"
    )

    # Email
    st.markdown("📧 **Email:** [molana.secret12@gmail.com](mailto:Jihan.molana.secret12@gmail.com)")

    # WhatsApp
    st.markdown("📱 **WhatsApp:** [Click to chat](https://wa.me/628116893312)")

    st.markdown("---")
    st.info("Let’s build something with data. Looking forward to hearing from you.. 😊")