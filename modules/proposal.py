import streamlit as st
from tavily_search import search_web
from orchestrator import generate
import db

def render(user):
    st.header("Proposal Generator")
    
    tab1, tab2 = st.tabs(["✨ Generate", "🕒 History"])
    
    with tab1:
        st.write("Generate a personalized proposal referencing specific job details.")
        
        job_source = st.radio("Job Details Source", ["Paste Job Description", "Job URL (Tavily fetches it)"])
        
        job_desc = ""
        job_url = ""
        
        if job_source == "Paste Job Description":
            job_desc = st.text_area("Paste Job Description Here", height=200)
        else:
            job_url = st.text_input("Job URL")
            
        custom_notes = st.text_area("Optional Custom Notes (e.g. highlight my React project)")
        
        if st.button("Generate Proposal", type="primary"):
            if job_source == "Paste Job Description" and not job_desc.strip():
                st.warning("Please paste a job description.")
                return
            elif job_source == "Job URL (Tavily fetches it)" and not job_url.strip():
                st.warning("Please provide a job URL.")
                return
                
            with st.spinner("Analyzing job and generating proposal..."):
                context = ""
                if job_source == "Job URL (Tavily fetches it)":
                    st.info("Fetching job details via Tavily...")
                    search_results = search_web(f"Extract job description from {job_url}")
                    if search_results:
                        context = f"Job URL Content:\n{search_results}"
                    else:
                        st.warning("Tavily failed to fetch URL or no content found. Falling back to Gemini with just the URL.")
                        context = f"Job URL: {job_url}"
                else:
                    context = f"Job Description:\n{job_desc}"
                    
                past_proposals = user.get('past_proposals', [])
                past_context = ""
                if past_proposals:
                    past_context = "Here are some of my past proposals to learn my style:\n"
                    for i, p in enumerate(past_proposals):
                        if isinstance(p, dict):
                            p_text = p.get('body', str(p))
                        else:
                            p_text = str(p)
                        past_context += f"Past Proposal {i+1}:\n{p_text}\n\n"
                
                prompt = f"""
                Generate a highly personalized freelance proposal for the provided job.
                Incorporate any custom notes: {custom_notes}
                
                {past_context}
                
                Return a JSON object with the following keys:
                - "opening": The hook or greeting.
                - "body": The main pitch, aligning my skills to their needs.
                - "closing": Wrapping up and mentioning my availability.
                - "cta": A call to action (e.g., Let's hop on a call).
                - "full_proposal": The complete merged proposal text.
                """
                
                result = generate(user, prompt, context)
                
                if "error" in result:
                    st.error("Error generating proposal:")
                    st.write(result["error"])
                    if "raw_response" in result:
                        st.text_area("Raw Response", result["raw_response"], height=200)
                else:
                    st.success("Proposal Generated!")
                    
                    full_text = result.get("full_proposal", "")
                    if not full_text:
                        # fallback to joining
                        full_text = f"{result.get('opening', '')}\n\n{result.get('body', '')}\n\n{result.get('closing', '')}\n\n{result.get('cta', '')}"
                    
                    # Copy to clipboard
                    st.text_area("Copy your proposal from here:", full_text, height=300)
                    
                    # Save to DB
                    db.add_proposal(user['user_id'], full_text)
    
    with tab2:
        st.subheader("Your Past Proposals")
        past_proposals = user.get('past_proposals', [])
        if not past_proposals:
            st.write("You haven't generated any proposals yet.")
        else:
            for i, p in enumerate(reversed(past_proposals)):
                with st.expander(f"Proposal {len(past_proposals) - i}"):
                    if isinstance(p, dict):
                        st.write(p.get('full_proposal') or p.get('body') or str(p))
                    else:
                        st.write(p)
