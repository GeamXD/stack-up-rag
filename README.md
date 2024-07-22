
# StackUp RAG Demo

**LINK TO APP**: [my-ragdemo-drcrbd9xhqbjiwsq2tfz6l.streamlit.app](https://my-ragdemo-drcrbd9xhqbjiwsq2tfz6l.streamlit.app)

## Introduction

The StackUp RAG Demo is designed to enhance the StackUp community experience by providing a more efficient way to access information from the StackUp help site. The project leverages modern AI techniques to streamline the process of finding specific information, making it quicker and more user-friendly.

## Summary of the Solution

This project comprises three main components:

1. **Web Scraper**: A custom-built web scraper extracts data from the StackUp help site, cleans it, and outputs a well-structured JSON document. This step ensures that the data is in a format suitable for further processing and querying.

2. **Retrieval-Augmented Generation (RAG) System**: The RAG system, built using Langchain, Pinecone as a vector store, and TogetherAI for embeddings and language model queries, forms the core of the solution. It allows users to enter queries and receive accurate, context-aware responses from the processed help site data.

3. **Streamlit App**: The user interface, built with Streamlit, mimics a ChatGPT setup where users can input their questions and get responses from the LLM. This makes it intuitive for users to interact with the system and obtain the information they need.

### Deployed Site and Working Prototype

The deployed version of the app can be accessed [here](https://my-ragdemo-drcrbd9xhqbjiwsq2tfz6l.streamlit.app). The prototype demonstrates the core functionality and provides a proof of concept for future enhancements.

### Video Demo

[Link to Video Demo](#) (Insert link to your video demo)

### Illustrations and Mock-ups

![Illustration](#) (Insert link to any illustrations or mock-ups)

## Future Plans

- **Query Limits**: Implementing a feature to limit the number of queries per user to manage load and ensure fair usage.
- **Login Page**: Adding a user authentication system to personalize the experience and secure access.
- **Model Improvements**: Enhancing the accuracy and efficiency of the LLM by integrating better models as they become available.

## Judging Criteria

### 1. Innovation & Creativity (30%)

The StackUp RAG Demo showcases originality by applying state-of-the-art AI techniques to solve a common problem in community help sites. The integration of a web scraper, a RAG system, and a user-friendly Streamlit interface demonstrates a novel approach to improving information accessibility.

### 2. Impact (30%)

The solution significantly impacts the StackUp community by providing faster and more efficient access to information. It aims to streamline the onboarding process for new members and assist existing members in navigating the platform more effectively. By reducing the time spent searching for information, the app enhances overall user satisfaction and engagement.

### 3. Feasibility (40%)

The project is highly feasible, leveraging existing technologies and frameworks to create a functional prototype. The use of Langchain, Pinecone, and TogetherAI ensures robust performance and scalability. Future enhancements, such as query limits and user authentication, are practical and achievable, further increasing the solution's viability.

## Conclusion

The StackUp RAG Demo is a promising solution to improve the StackUp community experience. By utilizing advanced AI techniques, it addresses the challenges of finding specific information quickly and efficiently. With planned enhancements, the app has the potential to become an indispensable tool for both new and existing StackUp members.
