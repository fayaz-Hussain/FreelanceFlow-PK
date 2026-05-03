import streamlit as st
import os

# Create modules directory if not exists
os.makedirs(os.path.join(os.path.dirname(__file__), 'modules'), exist_ok=True)

import db
from modules import proposal, rate_advisor, contract, profile_optimizer

st.set_page_config(page_title="FreelanceFlow PK", layout="wide", page_icon="⚡")

# Ensure total_sessions is incremented per logical session (e.g. app load)
if 'session_logged' not in st.session_state:
    st.session_state['session_logged'] = False

def render_sidebar():
    st.sidebar.title("FreelanceFlow PK ⚡")
    
    if 'user_id' in st.session_state:
        user = db.get_user(st.session_state['user_id'])
        if user:
            st.sidebar.subheader("Your Profile")
            
            # Editable profile fields in sidebar
            with st.sidebar.form("profile_update_form"):
                name = st.text_input("Name", value=user.get('name', ''))
                domain = st.text_input("Domain", value=user.get('domain', ''))
                exp_index = ["beginner", "intermediate", "expert"].index(user.get('experience_level', 'beginner'))
                exp = st.selectbox("Experience", ["beginner", "intermediate", "expert"], index=exp_index)
                rate = st.number_input("Hourly Rate ($)", value=float(user.get('current_rate_usd', 0)), min_value=0.0)
                
                platforms_val = ", ".join(user.get('platforms', []))
                platforms_str = st.text_input("Platforms (comma separated)", value=platforms_val)
                
                skills_val = ", ".join(user.get('top_skills', []))
                skills_str = st.text_input("Top Skills (max 5)", value=skills_val)
                
                lang_index = ["english", "roman_urdu"].index(user.get('language_pref', 'english'))
                lang = st.selectbox("Language Preference", ["english", "roman_urdu"], index=lang_index)
                
                if st.form_submit_button("Update Profile"):
                    db.update_user(st.session_state['user_id'], {
                        'name': name,
                        'domain': domain,
                        'experience_level': exp,
                        'current_rate_usd': rate,
                        'platforms': [p.strip() for p in platforms_str.split(",") if p.strip()],
                        'top_skills': [s.strip() for s in skills_str.split(",") if s.strip()][:5],
                        'language_pref': lang
                    })
                    st.sidebar.success("Profile updated!")
                    st.rerun()
            
            if st.sidebar.button("Logout"):
                del st.session_state['user_id']
                st.rerun()
                
            # Auto-learning Nudge
            total_sessions = user.get('total_sessions', 0)
            if total_sessions >= 10:
                st.sidebar.info("💡 You've used FreelanceFlow 10+ times — consider raising your rate by $3!")

def render_onboarding():
    st.title("Welcome to FreelanceFlow PK 🚀")
    st.write("An AI-powered toolkit for Pakistani freelancers on Upwork and Fiverr.")
    
    users = db.get_all_users()
    
    if users:
        tab1, tab2 = st.tabs(["Log In", "Create Profile"])
        with tab1:
            st.subheader("Welcome Back!")
            user_options = {u['user_id']: f"{u['name']} ({u['domain']})" for u in users}
            selected_user_id = st.selectbox("Select your profile", options=list(user_options.keys()), format_func=lambda x: user_options[x])
            
            if st.button("Log In"):
                st.session_state['user_id'] = selected_user_id
                st.rerun()
                
        with tab2:
            _render_signup_form()
    else:
        _render_signup_form()

def _render_signup_form():
    with st.form("onboarding_form"):
        st.subheader("Create Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            domain = st.text_input("Domain (e.g. Web Development, Graphic Design)")
            exp = st.selectbox("Experience Level", ["beginner", "intermediate", "expert"])
            rate = st.number_input("Current Hourly Rate (USD)", min_value=0.0, value=10.0)
            
        with col2:
            platforms = st.multiselect("Platforms", ["Upwork", "Fiverr", "LinkedIn", "Other"])
            skills = st.text_input("Top Skills (comma separated, max 5)")
            lang = st.selectbox("Preferred Output Language", ["english", "roman_urdu"])
            
        submit = st.form_submit_button("Get Started")
        
        if submit:
            if not name or not domain:
                st.error("Please fill in Name and Domain.")
            else:
                user_data = {
                    'name': name,
                    'domain': domain,
                    'experience_level': exp,
                    'current_rate_usd': rate,
                    'platforms': platforms,
                    'top_skills': [s.strip() for s in skills.split(",") if s.strip()][:5],
                    'language_pref': lang
                }
                user_id = db.create_user(user_data)
                st.session_state['user_id'] = user_id
                st.rerun()

def main():
    if 'user_id' not in st.session_state:
        render_onboarding()
    else:
        user = db.get_user(st.session_state['user_id'])
        if not user:
            # Handle case where user is in session but not in DB
            del st.session_state['user_id']
            st.rerun()
            return
            
        if not st.session_state['session_logged']:
            db.increment_sessions(st.session_state['user_id'])
            st.session_state['session_logged'] = True
            
        render_sidebar()
        
        st.write(f"### Welcome back, {user['name']}. {user['domain']} • {user['experience_level'].title()} • ${user['current_rate_usd']}/hr")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Proposal Generator", 
            "💰 Rate Advisor", 
            "📄 Contract Drafter", 
            "✨ Profile Optimizer"
        ])
        
        with tab1:
            proposal.render(user)
        with tab2:
            rate_advisor.render(user)
        with tab3:
            contract.render(user)
        with tab4:
            profile_optimizer.render(user)

if __name__ == "__main__":
    main()
