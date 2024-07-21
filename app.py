import streamlit as st
from data_checker import check_data_folder
from setup_rag import RagSetup

def my_app():
    
    st.set_page_config(
        page_title="RAG-based Document Search",
        page_icon="🔍",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # st.sidebar.title("RAG-based Document Search")
    # st.sidebar.write("This app uses the RAG model to search for documents.")


    # st.chat_input("Ask a question")
    st.chat_input("Hello! How can I help you today?")

        # Example usage
    rag_setup = RagSetup('data/stack-help_data.json')
    response = rag_setup.rag("Tell me about bounty?")
    print(response)



def main():
    # Call the function to ensure the data folder and JSON file are present
    check_data_folder()
    # Continue with the rest of your script
    print("Proceeding with the rest of the script...")



if __name__ == '__main__':
    main()
