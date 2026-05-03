import streamlit as st
from tavily_search import search_web
from orchestrator import generate

def render(user):
    st.header("Profile Optimizer")
    st.write("Optimize your freelance profile for your target platform.")
    
    target_platform = st.selectbox("Target Platform", ["Upwork", "Fiverr"])
    current_bio = st.text_area("Paste your current Bio (Leave blank to generate from scratch)", height=150)
    
    if st.button("Optimize Profile", type="primary"):
        with st.spinner("Analyzing top profiles and optimizing..."):
            
            context = ""
            domain = user.get('domain', 'freelancer')
            skills = " ".join(user.get('top_skills', []))
            
            search_query = f"top {target_platform} profiles in {domain} {skills}"
            st.info(f"Researching top profiles on {target_platform}...")
            
            search_results = search_web(search_query)
            if search_results:
                context = f"Top {target_platform} profiles research:\n{search_results}"
            else:
                st.warning("Tavily search failed or returned no results. Proceeding with AI knowledge only.")
            
            prompt = f"""
            Optimize or create a freelance profile for {target_platform}.
            Current Bio: {current_bio if current_bio.strip() else '[None provided, create from scratch]'}
            
            Return a JSON object with exactly these keys:
            - "optimized_title": A catchy, SEO-friendly profile title.
            - "optimized_bio": The complete optimized bio/description.
            - "keyword_list": A JSON array of strings containing keywords to include as skills/tags.
            - "improvement_notes": A short string explaining what changes were made and why.
            """
            
            result = generate(user, prompt, context)
            
            if "error" in result:
                st.error("Error optimizing profile:")
                st.write(result["error"])
                if "raw_response" in result:
                    st.text_area("Raw Response", result["raw_response"])
            else:
                st.subheader("Optimized Profile")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Original")
                    if current_bio.strip():
                        st.write(current_bio)
                    else:
                        st.write("*(None provided)*")
                        
                with col2:
                    st.markdown("### Optimized")
                    st.markdown(f"**Title:** {result.get('optimized_title', '')}")
                    opt_bio = result.get('optimized_bio', '')
                    
                    st.text_area("Copy Optimized Bio:", opt_bio, height=150)
                    
                st.markdown("### Keywords / Tags to Use")
                keywords = result.get('keyword_list', [])
                if isinstance(keywords, list):
                    st.write(", ".join(keywords))
                else:
                    st.write(keywords)
                    
                st.markdown("### Improvement Notes")
                st.info(result.get('improvement_notes', ''))
