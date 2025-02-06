from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os
from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    def __init__(self):
        self.llm = ChatOpenAI()
        self.memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )
        self.pdf_conversation_chain = None
        self.vectorstore = None

    def get_general_response(self, question):
        # For general questions without PDF context
        response = self.llm.predict(question)
        return response

    def process_pdf(self, pdf_file):
        # Process PDF when uploaded
        text = ""
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_texts(texts=chunks, embedding=embeddings)
        
        self.pdf_conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory
        )
        return "PDF processed successfully!"

    def get_response(self, question, context_type="general"):
        if context_type == "pdf" and self.pdf_conversation_chain:
            response = self.pdf_conversation_chain({'question': question})
            return response['answer']
        else:
            return self.get_general_response(question)