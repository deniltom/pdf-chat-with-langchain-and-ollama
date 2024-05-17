from flask import Flask, render_template, request, flash, redirect
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

app = Flask(__name__)
app.secret_key = 'denil@123'

def load_document(local_path):
    if local_path:
        loader = UnstructuredPDFLoader(file_path=local_path)
        data = loader.load()
        return data
    else:
        print("Upload a PDF file")
        return None

def split_and_chunk(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    return chunks

def add_to_vector_database(chunks):
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="nomic-embed-text", show_progress=True),
        collection_name="local-rag"
    )
    return vector_db

def prepare_query_retriever(vector_db, llm):
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(),
        llm,
        prompt=QUERY_PROMPT
    )
    return retriever

def prepare_rag_chain(retriever, llm):
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

def main(local_path, llm_model="llama3"):
    data = load_document(local_path)
    if data:
        chunks = split_and_chunk(data)
        vector_db = add_to_vector_database(chunks)
        llm = ChatOllama(model=llm_model)
        retriever = prepare_query_retriever(vector_db, llm)
        chain = prepare_rag_chain(retriever, llm)
        return chain
    else:
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            file_path = "uploads" + file.filename
            file.save(file_path)
            chain = main(file_path)
            if chain:
                user_question = request.form['question']
                response = chain.invoke(user_question)
                return render_template('result.html', response=response)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
