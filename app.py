import streamlit as st
from data_checker import check_data_folder
from setup_rag import RagSetup

def my_app():
    
    st.set_page_config(
        page_title="HelpHub Insights Demo",
        page_icon="🔍",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    
    # Set the title and description of the app
    # Use HTML and CSS to center the title
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            color: cream;
            font-size: 2em;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # Display the title
    st.markdown('<h1 class="title">HelpHub Insights Demo</h1>', unsafe_allow_html=True)
    

    # Set up chatbot
    # Initialize the RagSetup with your data file path
    rag_setup = RagSetup(data_filepath="data/stack-help_data.json")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Welcome! How can I assist you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Use the rag method to get a response
        response = rag_setup.rag(prompt)
        
        # Extract and display the answer
        answer = response.get("answer", "I don't know.")
        sources = response.get("sources", [])
        
        with st.chat_message("assistant"):
            st.write(answer)
            if sources:
                st.write("Sources:")
                st.write(sources)

        st.session_state.messages.append({"role": "assistant", "content": answer})



def main():
    # Call the function to ensure the data folder and JSON file are present
    check_data_folder()

    # Run the Streamlit app
    my_app()

if __name__ == '__main__':
    main()
