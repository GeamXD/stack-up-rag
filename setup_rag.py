import os
import json
import pandas as pd
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
    def __init__(self, data_filepath='data/stack-help_data.json'):
        self.data_filepath = data_filepath
        self.api_key_pinecone = os.getenv("PINECONE_API_KEY")
        self.api_key_together = os.getenv("TOGETHER_API_KEY")
        self.index_name = "stackragapp"
        self.doc_df = None
        self.docsearch = None
        self.llm = None
        self.qa_with_sources = None
        self.data_loaded = False
        self.store_setup = False
        self.qa_chain_setup = False

    def _clean_text(self, text: pd.Series) -> pd.Series:
        """Helper function to clean text data."""
        text = text.str.replace(r"\/", "", regex=True)
        text = text.str.translate(str.maketrans('', '', string.punctuation))
        text = text.str.replace(r"\d+", "", regex=True)
        text = text.str.replace(r"\s{2,}", " ", regex=True)
        text = text.str.lower()
        return text

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
        df['article_title_cleaned'] = self._clean_text(df['article_title'])
        df['article_body_cleaned'] = self._clean_text(df['article_body']).str.replace('  ', ' ')
        df['article_body_cleaned'] = df['article_body_cleaned'].replace('', 'Empty')

        new_df = df[['article_title_cleaned', 'article_body_cleaned', 'article_links']]
        new_df.rename(columns={'article_title_cleaned': 'title', 
                               'article_body_cleaned': 'page_content', 
                               'article_links': 'urls'}, inplace=True)

        self.doc_df = new_df
        self.data_loaded = True
        return new_df

    def set_up_store(self) -> PineconeVectorStore:
        """
        Sets up the Pinecone vector store and returns the document search object.
        """
        if not self.data_loaded:
            self.wrangle_data()

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
        self.store_setup = True
        return docsearch

    def setup_qa_chain(self):
        """
        Sets up the QA chain using the LLM and document search.
        """
        if not self.store_setup:
            self.set_up_store()

        DOCUMENT_PROMPT = """
        Title: {title}
        page_content: {page_content}
        Help Center link: {urls}
        ========="""

        QUESTION_PROMPT = """Given the following extracted parts of a help center data and a question, create a final answer with the Help Center link as source ("SOURCE").
        If you don't know the answer, just say that you don't know. Don't try to make up an answer. Ensure answer makes sense. You are allowed to give an answer based on context. Be careful when doing this
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

        self.qa_chain_setup = True

    def rag(self, question: str) -> dict:
        """
        Retrieves the answer to a question using the RAG setup.
        """
        if not self.data_loaded:
            self.wrangle_data()
        
        if not self.store_setup:
            self.set_up_store()
        
        if not self.qa_chain_setup:
            self.setup_qa_chain()
        try:
            qa_response = self.qa_with_sources.invoke(question)
            return qa_response
        except Exception as e:
            print(e)
