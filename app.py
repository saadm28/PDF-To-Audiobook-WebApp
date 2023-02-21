import os
from google.cloud import texttospeech
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from PyPDF2 import PdfReader


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
bootstrap = Bootstrap(app)


def text_to_speech(text):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ.get(
        'CREDENTIALS_PATH')
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("audio/audio_file.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "AudioBook.mp3"')


def handle_pdf(filename):
    pdf_reader = PdfReader(open(f"PDF/{filename}", 'rb'))
    print("Number of Pages:", len(pdf_reader.pages))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    # call google text to speech function
    text_to_speech(text)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form['text']
        file = request.files['file']
        # Pass in text to speech function here
        if text and file:
            return render_template('index.html', error=True)
        if file and not text:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            handle_pdf(filename)
            return send_file('audio/audio_file.mp3', as_attachment=True)
        if text and not file:
            print("Text passed")
            text_to_speech(text)
            return send_file('audio/audio_file.mp3', as_attachment=True)
    return render_template('index.html', error=False)


if __name__ == '__main__':
    app.run(debug=True)
