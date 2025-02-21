import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from utilz.log_parser import LogParser
from utilz.graph_generator import GraphGenerator
from utilz.context_builder import ContextBuilder
from core.database_handlers import MongoDBHandler, VectorDatabaseHandler
from core.rag import RAG_Engine
import tempfile
from models.context_data_models import Context

def main():
    st.title("Log Analysis & Incident Resolution System")
    
    # Initialize session state
    if 'current_context' not in st.session_state:
        st.session_state.current_context = None
    # Add new session state variables
    if 'processed_log' not in st.session_state:
        st.session_state.processed_log = {
            'file_hash': None,
            'dag': None,
            'context': None,
            'summary': None,
            'severity': None,
            'root_cause': None
        }
    if 'stored_docs' not in st.session_state:
        st.session_state.stored_docs = {
            'file_hash': None,
            'docs': None
        }
    
    # Initialize components
    mongo = MongoDBHandler()
    rag = RAG_Engine()
    
    # Modified file upload section
    with st.expander("Upload Log File"):
        log_file = st.file_uploader("Upload log file", type=["log", "txt"])
        if log_file:
            current_file_hash = hash(log_file.getvalue())
            
            # Only process if file is new
            if st.session_state.processed_log['file_hash'] != current_file_hash:
                # Get original file extension
                file_extension = os.path.splitext(log_file.name)[1]
                
                # Create temp file with original extension
                with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
                    tmp.write(log_file.getvalue())
                    tmp_path = tmp.name
                
                parser = LogParser()
                log_chain = parser.parse_log_from_file(tmp_path)
                graph_gen = GraphGenerator(log_chain)
                dag = graph_gen.generate_dag()
                
                # Build context
                context_builder = ContextBuilder()
                context = context_builder.build_context(dag)
                
                if log_chain:
                    summary = rag.generate_summary(context.causal_chain)
                    st.subheader("Log Analysis Summary")
                    for summary_point in summary.summary:
                        if summary_point:
                            st.write(f"• {summary_point}")
                    st.subheader("Root Cause")
                    st.write(summary.root_cause_expln)
                    st.subheader("Severity")
                    st.write(summary.severity)
                
                # Store results in session state
                st.session_state.processed_log = {
                    'file_hash': current_file_hash,
                    'dag': dag,
                    'context': context,
                    'summary': summary,
                    'severity': summary.severity,
                    'root_cause': summary.root_cause_expln
                }
                
                # Store in MongoDB (keep this outside session state)
                mongo.save_dag(dag.model_dump())
                mongo.save_context(context.model_dump())
                st.success("Log processed and stored successfully!")
            else:
                st.info("Using cached log analysis results")
                
                # Display the log analysis results
                st.subheader("Log Analysis Results")
                st.write(f"Severity: {st.session_state.processed_log['severity']}")
                st.write(f"Root Cause: {st.session_state.processed_log['root_cause']}") 
                for summary_point in st.session_state.processed_log['summary'].summary:
                    if summary_point:
                        st.write(f"• {summary_point}")

            # Update current context from session state
            st.session_state.current_context = {
                "causal_chain": st.session_state.processed_log['context'].causal_chain,
                "root_cause": st.session_state.processed_log['summary'].root_cause_expln
            }

    # Modified documentation section
    with st.expander("Add Documentation"):
        doc_files = st.file_uploader("Upload documentation", 
                                   type=["txt", "md"], 
                                   accept_multiple_files=True)
        if doc_files:
            current_docs_hash = hash(tuple(f.getvalue() for f in doc_files))
            
            if st.session_state.stored_docs['file_hash'] != current_docs_hash:
                docs = [f.read().decode() for f in doc_files]
                
                if not docs or len(docs) == 0:
                    st.error("No valid text extracted from uploaded file!")
                    return
                
                # Store in session state
                st.session_state.stored_docs = {
                    'file_hash': current_docs_hash,
                    'docs': docs
                }
                
                rag.store_documentation(docs)
                st.success(f"Stored {len(docs)} documentation chunks")
            else:
                st.info("Using cached documentation")
            
            # Display preview from session state
            st.write("First 500 characters of extracted text:")
            st.code(st.session_state.stored_docs['docs'][0][:500])

    # Modified query section
    with st.expander("Automatic Incident Resolution"):
        if st.session_state.processed_log.get('summary') and st.session_state.processed_log.get('context'):
            try:
                with st.spinner("Generating solution..."):
                    # Ensure context is properly formatted before passing
                    context_data = st.session_state.processed_log['context'].causal_chain
                    if isinstance(context_data, (list, tuple)):
                        context_str = "\n".join(context_data)
                    else:
                        context_str = str(context_data)
                    
                    solution = rag.generate_solution(
                        context=context_str,
                        root_cause=st.session_state.processed_log['summary'].root_cause_expln
                    )
                
                # Display the solution in a clean format
                st.subheader("🔍 Root Cause Analysis")
                st.info(st.session_state.processed_log['summary'].root_cause_expln)
                
                st.subheader("💡 Recommended Solution")
                if solution and solution.response:
                    if "Error:" in solution.response:
                        st.error(solution.response)
                    else:
                        # Split the response into sections if they exist
                        sections = solution.response.split('\n\n')
                        for section in sections:
                          
                            st.markdown(section.strip())
                
                    if solution.sources and any(source != "unknown" for source in solution.sources):
                        st.subheader("📚 Reference Documents")
                        sources_shown = set()
                        for source in solution.sources:
                            if source != "unknown" and source not in sources_shown:
                                st.markdown(f"- {source}")
                                sources_shown.add(source)
                else:
                    st.warning("No solution could be generated. Please check the documentation and try again.")

            except Exception as e:
                st.error("⚠️ Error generating solution")
                st.error(str(e))
        else:
            st.warning("Please process a log file first to generate solutions")

if __name__ == "__main__":
    main()
