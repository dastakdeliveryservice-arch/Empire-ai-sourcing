import streamlit as st
import pandas as pd
import yagmail
import requests
import re
from googlesearch import search
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
st.set_page_config(page_title="Empire AI - Domain Hunter", layout="wide")

# --- INITIALIZATION ---
if 'master_data' not in st.session_state:
    st.session_state['master_data'] = pd.DataFrame(columns=["Domain", "Email", "Source"])

st.title("👑 Empire AI: Domain Hunter")
st.markdown("---")

tab1, tab2 = st.tabs(["🎯 Domain Scraper", "✉️ Auto Outreach"])

with tab1:
    st.header("Direct Company Targeting")
    # Yahan aap websites ki list dal sakte hain
    domains_input = st.text_area("Target Domains (Ek line mein ek, e.g., medline.com):", "medline.com\ncardinalhealth.com")
    
    if st.button("Extract Emails 🚀"):
        domain_list = domains_input.split('\n')
        new_leads = []
        
        for dom in domain_list:
            dom = dom.strip()
            if dom:
                with st.spinner(f"Hunting in {dom}..."):
                    # Technique: Searching for emails associated with this specific domain
                    query = f'site:{dom} "@gmail.com" OR "@"{dom}'
                    try:
                        for url in search(query, num_results=5):
                            try:
                                resp = requests.get(url, timeout=5)
                                # Improved Regex for deeper cleaning
                                found = re.findall(r"[a-zA-Z0-9._%+-]+@" + re.escape(dom) + r"|[a-zA-Z0-9._%+-]+@gmail\.com", resp.text)
                                for email in found:
                                    new_leads.append({"Domain": dom, "Email": email.lower(), "Source": url})
                            except:
                                continue
                    except Exception as e:
                        st.error(f"Error searching {dom}: {e}")
        
        if new_leads:
            new_df = pd.DataFrame(new_leads).drop_duplicates(subset=['Email'])
            st.session_state['master_data'] = pd.concat([st.session_state['master_data'], new_df], ignore_index=True).drop_duplicates(subset=['Email'])
            st.success(f"Zabardast! {len(new_df)} leads mil gayin.")
        else:
            st.warning("Koi emails nahi milin. Try a different domain.")

    st.dataframe(st.session_state['master_data'], use_container_width=True)

with tab2:
    st.header("Email Outreach")
    # Same outreach logic as before...
    my_email = st.text_input("Gmail:")
    app_pass = st.text_input("App Password:", type="password")
    if st.button("Send Emails"):
        try:
            yag = yagmail.SMTP(my_email, app_pass)
            for _, row in st.session_state['master_data'].iterrows():
                yag.send(to=row['Email'], subject="Business Inquiry", contents="Hi, we are exporters...")
            st.success("Sent!")
        except Exception as e:
            st.error(e)
