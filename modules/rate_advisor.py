import streamlit as st
from tavily_search import search_web
from orchestrator import generate
import db

def render(user):
    st.header("Rate Advisor")
    st.write("Get recommendations on your pricing based on your profile and market data.")
    
    col1, col2 = st.columns(2)
    with col1:
        price_type = st.selectbox("Pricing Type", ["Hourly", "Fixed Price"])
    with col2:
        job_budget = st.number_input("Optional Job Budget ($)", min_value=0.0, value=0.0)
        
    if st.button("Analyze Rates", type="primary"):
        with st.spinner("Fetching market data and analyzing..."):
            
            skill_query = user.get('domain', 'freelancer')
            if user.get('top_skills'):
                skill_query = user['top_skills'][0]
                
            search_query1 = f"{skill_query} freelancer hourly rate Upwork 2026"
            search_query2 = f"{skill_query} Pakistan freelance rate"
            
            search_results = ""
            search_res1 = search_web(search_query1)
            search_res2 = search_web(search_query2)
            
            if search_res1 or search_res2:
                search_results = f"Search Results for '{search_query1}':\n{search_res1}\n\nSearch Results for '{search_query2}':\n{search_res2}"
            else:
                st.warning("Tavily search failed or returned no results. Proceeding with AI knowledge only.")
                
            context = search_results
            if job_budget > 0:
                context += f"\n\nNote: The client has an indicated budget of ${job_budget} ({price_type})."
                
            prompt = f"""
            You are a rate advisor for freelancers. Based on the market data provided and the user's profile, recommend an appropriate {price_type} rate.
            Calculate the PKR equivalent assuming roughly 1 USD = 280 PKR (or use your latest knowledge).
            
            Return a JSON object with EXACTLY these keys:
            - "min_rate_usd": number
            - "recommended_rate_usd": number
            - "max_rate_usd": number
            - "pkr_equivalent": string (e.g., "PKR 5,000/hr")
            - "justification": string explaining why this rate makes sense.
            - "negotiation_tip": string with advice on how to negotiate this rate.
            """
            
            result = generate(user, prompt, context)
            
            if "error" in result:
                st.error("Error analyzing rates:")
                st.write(result["error"])
                if "raw_response" in result:
                    st.text_area("Raw Response", result["raw_response"])
            else:
                st.subheader("Rate Recommendation")
                
                # Visual rate band
                min_r = result.get('min_rate_usd', 0)
                rec_r = result.get('recommended_rate_usd', 0)
                max_r = result.get('max_rate_usd', 0)
                
                cols = st.columns(3)
                cols[0].metric("Minimum Rate", f"${min_r}")
                cols[1].metric("Recommended", f"${rec_r}")
                cols[2].metric("Maximum", f"${max_r}")
                
                st.success(f"🇵🇰 Local Equivalent: **{result.get('pkr_equivalent', 'N/A')}**")
                
                st.markdown("### Justification")
                st.write(result.get("justification", ""))
                
                st.markdown("### Negotiation Tip")
                st.info(result.get("negotiation_tip", ""))
                
                # Save accepted rate functionality
                if st.button("Apply Recommended Rate to Profile"):
                    db.update_user(user['user_id'], {'last_used_rate': rec_r, 'current_rate_usd': rec_r})
                    st.success(f"Rate updated to ${rec_r}/hr! Refreshing...")
                    st.rerun()
