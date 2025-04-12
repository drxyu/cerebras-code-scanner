import streamlit as st
import asyncio
from pathlib import Path
import sys

# Add the parent directory to Python path so we can import our scanner
sys.path.append(str(Path(__file__).parent.parent))
from scanner.cerebras_scanner import CodeScanner

st.set_page_config(
    page_title="AI-Powered Python Security Scanner",
    page_icon="🔒",
    layout="wide"
)

# Initialize the scanner
@st.cache_resource
def get_scanner():
    return CodeScanner()

def main():
    st.title("AI-Powered Python Security Scanner")
    st.markdown("""
    This tool uses Cerebras + Llama 4 to analyze Python code for security vulnerabilities
    and performance issues. Simply paste your code below and select the type of analysis
    you want to perform.
    """)
    
    # Code input
    code = st.text_area("Enter your Python code here:", height=300)
    
    # Analysis options
    analysis_type = st.multiselect(
        "Select analysis categories:",
        ["SQL Injection", "Authentication", "Input Validation", "Cryptographic Issues"],
        default=["SQL Injection", "Authentication"]
    )
    
    if st.button("Analyze Code"):
        if not code:
            st.error("Please enter some code to analyze.")
            return
            
        scanner = get_scanner()
        
        # Show a spinner while analyzing
        with st.spinner("Analyzing code..."):
            # Create tasks for each selected category
            tasks = []
            for category in analysis_type:
                category_key = category.lower().replace(" ", "_")
                tasks.append(scanner.analyze_code(code, category_key))
            
            # Run all analysis tasks concurrently
            try:
                results = asyncio.run(asyncio.gather(*tasks))
                
                # Display results
                for category, result in zip(analysis_type, results):
                    st.subheader(f"{category} Analysis")
                    
                    if "error" in result:
                        st.error(f"Error during analysis: {result['error']}")
                        continue
                        
                    if not result.get("issues"):
                        st.success("No issues found in this category.")
                    else:
                        for issue in result["issues"]:
                            st.warning(
                                f"""
                                **Issue Found:**
                                {issue.get('description', 'No description available')}
                                
                                **Fix:**
                                {issue.get('fix', 'No fix suggestion available')}
                                """
                            )
                            
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main() 