import os
import json
import pandas as pd
import re
import string
import pinecone
from langchain.document_loaders import DataFrameLoader
from langchain_pinecone import PineconeVectorStore
from langchain_together import TogetherEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate
from langchain_together import ChatTogether

class RagSetup:
    """A class to set up the RAG model for question-answering."""
    def __init__(self, data_filepath: str):
        self.data_filepath = data_filepath
        self.api_key_pinecone = os.getenv("PINECONE_API_KEY")
        self.api_key_together = os.getenv("TOGETHER_API_KEY")
        self.index_name = "stackragapp"
        self.doc_df = None
        self.docsearch = None
        self.llm = None
        self.qa_with_sources = None

    def wrangle_data(self) -> pd.DataFrame:
        """
        Reads, cleans, and returns a pandas DataFrame from the JSON file.
        """
        with open(self.data_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        doc = {
            'article_title': data['article_link_title'],
            'article_links': data['article_links'],
            'article_body': data['article_body'],
        }

        df = pd.DataFrame(doc)

        # Clean the data
        df['article_title_cleaned'] = df['article_title'].str.replace(r"\/", "", regex=True)
        df['article_title_cleaned'] = df['article_title_cleaned'].str.translate(str.maketrans('', '', string.punctuation))
        df['article_title_cleaned'] = df['article_title_cleaned'].str.replace(r"\d+", "", regex=True)
        df['article_title_cleaned'] = df['article_title_cleaned'].str.replace(r"\s{2,}", " ", regex=True)
        df['article_title_cleaned'] = df['article_title_cleaned'].str.lower()

        df['article_body_cleaned'] = df['article_body'].str.replace(r"\/", "", regex=True)
        df['article_body_cleaned'] = df['article_body_cleaned'].str.translate(str.maketrans('', '', string.punctuation))
        df['article_body_cleaned'] = df['article_body_cleaned'].str.replace(r"\d+", "", regex=True)
        df['article_body_cleaned'] = df['article_body_cleaned'].str.replace(r"\s{2,}", " ", regex=True)
        df['article_body_cleaned'] = df['article_body_cleaned'].str.lower()
        df['article_body_cleaned'] = df['article_body_cleaned'].str.replace('  ', ' ')
        df['article_body_cleaned'] = df['article_body_cleaned'].replace('', 'Empty')

        new_df = df[['article_title_cleaned', 'article_body_cleaned', 'article_links']]
        new_df.rename(columns={'article_title_cleaned': 'title', 
                               'article_body_cleaned': 'page_content', 
                               'article_links': 'urls'}, inplace=True)

        self.doc_df = new_df
        return new_df

    def set_up_store(self) -> PineconeVectorStore:
        """
        Sets up the Pinecone vector store and returns the document search object.
        """
        docs = DataFrameLoader(
            self.doc_df,
            page_content_column="page_content",
        ).load()


        pc = pinecone.Pinecone(self.api_key_pinecone)

        existing_index_names = [idx.name for idx in pc.list_indexes().indexes]

        if self.index_name not in existing_index_names:
            pc.create_index(
                name=self.index_name,
                metric='cosine',
                dimension=768,
                spec=pinecone.ServerlessSpec(cloud="aws", region="us-east-1")
            )

        embeddings = TogetherEmbeddings(api_key=self.api_key_together)
        index = pc.Index(self.index_name)
        n_vectors = index.describe_index_stats()['total_vector_count']

        if n_vectors > 0:
            docsearch = PineconeVectorStore.from_existing_index(self.index_name, embeddings)
        else:
            docsearch = PineconeVectorStore.from_documents(docs, embeddings, index_name=self.index_name)

        self.docsearch = docsearch
        return docsearch

    def setup_qa_chain(self):
        """
        Sets up the QA chain using the LLM and document search.
        """
        DOCUMENT_PROMPT = """
        Title: {title}
        page_content: {page_content}
        Help Center link: {urls}
        ========="""

        QUESTION_PROMPT = """Given the following extracted parts of a help center data and a question, create a final answer with the Help Center link as source ("SOURCE").
        If you don't know the answer, just say that you don't know. Don't try to make up an answer.
        ALWAYS return a "SOURCE" part in your answer. YOU CAN RETURN MULTIPLE 'SOURCES' relevant to the question asked

        QUESTION: Tell me about bounty?
        =========
        Title: What is bounty?
        Description: The StackUp bounty program offers an additional opportunity for Stackies to engage in more advanced learning activities with higher expectations for their output. This program presents a new level of challenge compared to quests, allowing Stackies to tackle more complex challenges in exchange for a larger reward amount.
        Help Center link: https://stackuphelpcentre.zendesk.com/hc/en-us/articles/18932072999065-What-is-Bounty
        =========
        NOTE: FOR ABOVE QUESTION, TAKE INFERENCES FROM ALL RELEVANT PAGE CONTENT PROVIDED AND OUTPUT A FINAL ANSWER


        NOTE: FOR FINAL ANSWER BELOW, GIVE A FINAL ANSWER BASED ON THE QUESTION ASKED AND THE DOCUMENTS PROVIDED ABOVE. ENSURE YOUR ANSWER IS INFORMATIVE AND CAN SOLVE THE QUESTION ASKED. YOU CAN PROVIDE MORE THAN ONE RELEVANT SOURCE IF AVAILABLE
        FINAL ANSWER: The StackUp bounty program provides Stackies with advanced learning opportunities and more challenging tasks than quests, offering higher rewards. Submissions are evaluated for quality and alignment with criteria, ensuring that only the best submissions receive rewards.
        SOURCE: https://stackuphelpcentre.zendesk.com/hc/en-us/categories/35260449941529-Earn-App

        QUESTION: {question}
        =========
        {summaries}
        FINAL ANSWER:"""

        document_prompt = PromptTemplate.from_template(DOCUMENT_PROMPT)
        question_prompt = PromptTemplate.from_template(QUESTION_PROMPT)

        self.llm = ChatTogether(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
            temperature=0,
            api_key=self.api_key_together
        )

        self.qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
            chain_type="stuff",
            llm=self.llm,
            chain_type_kwargs={
                "document_prompt": document_prompt,
                "prompt": question_prompt,
            },
            retriever=self.docsearch.as_retriever(),
        )

    def rag(self, question: str) -> dict:
        """
        Retrieves the answer to a question using the RAG setup.
        """
        if self.doc_df is None:
            self.wrangle_data()
        
        if self.docsearch is None:
            self.set_up_store()
        
        if self.qa_with_sources is None:
            self.setup_qa_chain()

        qa_response = self.qa_with_sources.invoke(question)
        return qa_response

