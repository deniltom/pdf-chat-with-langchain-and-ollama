from flask import Flask, render_template, request, flash, redirect
from script import main

app = Flask(__name__)

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
            file_path = "uploads/" + file.filename  # Changed directory separator
            file.save(file_path)
            chain = main(file_path)
            if chain:
                return render_template('query.html', file_path=file_path)
    return render_template('upload.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        user_question = request.form['question']
        file_path = request.form['file_path']
        chain = main(file_path)
        if chain:
            response = chain.invoke(user_question)
            return render_template('result.html', response=response)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

