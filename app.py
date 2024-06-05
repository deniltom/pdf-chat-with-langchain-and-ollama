from flask import Flask, render_template, request, flash, redirect
from script import process_document, setup_query_chain  # Import the new functions
import os

app = Flask(__name__)
app.secret_key = 'denil@123'

# Ensure the 'uploads' directory exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def home():
    return render_template('upload.html')

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
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)
            vector_db = process_document(file_path)
            if vector_db:
                app.config['VECTOR_DB'] = vector_db
                flash('Document processed and vector database created')
                return render_template('query.html', file_path=file_path)
            else:
                flash('Failed to process the document')
                return render_template('upload.html')
    return render_template('upload.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        user_question = request.form['question']
        vector_db = app.config.get('VECTOR_DB')
        if vector_db:
            chain = setup_query_chain(vector_db)
            response = chain.invoke(user_question)
            return render_template('result.html', response=response)
        else:
            flash('Vector database not found, please upload a document first')
            return redirect('/')
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)




