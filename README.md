PDF QUERY USING LANGCHAIN AND OLLAMA

This is a RAG app which receives pdf from user and can generate response based on user queries

 Steps for running this app

 1.  Download ollama for running open source models
 
 2.  Clone the github repository
 
 3.  Install requirements.txt
 
         pip install -r requirements.txt
 
 4.  Run the following commands on commmand prompt
 
         ollama pull llama3
         ollama run  llama3

5.   Run the following command for getting embeddings
   
         ollama pull nomic-embed-text

 6.Run app.py file
         
         python app.py

 7.upload the pdf file to query
 
 8.Enter the question
