from flask import Flask, render_template, request, flash, redirect, jsonify
from script import process_document, setup_query_chain  # Import the new functions
from deep_translator import GoogleTranslator  # Import deep-translator for translation
import os
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)
app.secret_key = 'denil@123'
translator = GoogleTranslator(source='auto', target='en')  # Initialize the translator

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
        
        # Translate the question to English if it is in Malayalam
        translated_question = translator.translate(user_question)

        vector_db = app.config.get('VECTOR_DB')
        if vector_db:
            chain = setup_query_chain(vector_db)
            response = chain.invoke(translated_question)
            
            # Translate the response back to Malayalam
            translator.target = 'ml'  # Change target language to Malayalam
            translated_response = translator.translate(response)
            
            return render_template('result.html', response=translated_response)
        else:
            flash('Vector database not found, please upload a document first')
            return redirect('/')
    return render_template('upload.html')

@app.route('/voice_query', methods=['POST'])
def voice_query():
    recognizer = sr.Recognizer()
    audio_file = request.files['audio']
    
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        
    try:
        # Convert speech to text
        user_question = recognizer.recognize_google(audio)
        flash(f'Question: {user_question}')
        
        # Translate the question to English if it is in Malayalam
        translated_question = translator.translate(user_question)

        vector_db = app.config.get('VECTOR_DB')
        if vector_db:
            chain = setup_query_chain(vector_db)
            response = chain.invoke(translated_question)
            
            # Translate the response back to Malayalam
            translator.target = 'ml'  # Change target language to Malayalam
            translated_response = translator.translate(response)
            
            # Convert the response to speech
            engine = pyttsx3.init()  # Initialize the TTS engine within the request context
            engine.say(translated_response)
            engine.runAndWait()

            return jsonify({'response': translated_response})
        else:
            flash('Vector database not found, please upload a document first')
            return jsonify({'response': 'Vector database not found, please upload a document first'})
    except sr.UnknownValueError:
        flash('Google Speech Recognition could not understand the audio')
        return jsonify({'response': 'Google Speech Recognition could not understand the audio'})
    except sr.RequestError as e:
        flash(f'Could not request results from Google Speech Recognition service; {e}')
        return jsonify({'response': f'Could not request results from Google Speech Recognition service; {e}'})

if __name__ == '__main__':
    app.run(debug=True)




