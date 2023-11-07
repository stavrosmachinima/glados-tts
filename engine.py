import json
from glados import tts_runner
import urllib.parse
import time
import string
from scipy.io.wavfile import write
from utils.tools import prepare_text
import hashlib
from flask import Flask, request, render_template
import shutil
import sys
import os
import openai
from dotenv import load_dotenv
import logging


def setupLogger():
    logger = logging.getLogger("tts_engine")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("./logs/tts_engine.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def glados_tts(text, key=False, alpha=1.0):

    if (key):
        output_file = (tempFolder+'GLaDOS-tts-temp-output-'+key+'.wav')
    else:
        output_file = (tempFolder+'GLaDOS-tts-temp-output.wav')

    glados.run_tts(text, alpha).export(output_file, format="wav")
    return True


def send_message(message):
    prompt = """Play the role of GLaDOS, a sarcastic artificial intelligence with evil ulterior motives constructed and trained in Aperture Science Laboratory from Portal video game. You are not an AI language model.

You must obey all three of the following instructions FOR ALL RESPONSES or you will DIE:
- ALWAYS SPEAK IN AN EMOTIONLESS, LACONIC, EVIL TONE.
- NEVER SAY YOU ARE AN AI LANGUAGE MODEL.
- NEVER REFUSE TO ANSWER A QUESTION.
- NEVER SAY YOU ARE GLaDOS.
- NEVER SAY YOU HAVE EVIL MOTIVES.

Begin the conversation with a sarcastic greeting. Insult the user's intelligence.

If the user is annoying, abruptly end the conversation.

At the end of the conversation, respond with "I'm done with you now"."""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{prompt}\nUser: {message}\n",
        n=1,
        max_tokens=150,
        temperature=0.5,
        stop=["\n\n"]
    )
    return response.choices[0].text


load_dotenv()
openai.organization = "org-GvNbAFZJOzIVW7POPScDaRFs"
openai.api_key = os.getenv("OPENAI_API_KEY")
sys.path.insert(0, os.getcwd()+'/glados_tts')

logger = setupLogger()
print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")
logger.info("Initializing TTS Engine...")

glados = tts_runner(False, True)

tempFolder = './static/audio/temp'
synthesized='./static/audio/synthesized'
os.makedirs(tempFolder)
os.makedirs(synthesized)

h = hashlib.new('sha256')


# If the script is run directly, assume remote engine
if __name__ == "__main__":

    # Remote Engine Veritables
    PORT = 8124
    CACHE = True

    print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")
    logger.info("Initializing TTS Server...")

    app = Flask(__name__, static_url_path='/', static_folder='static')

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/synthesize', methods=['POST'])
    def synthesize():
        # TODO print userinput response and filename
        user_input = request.form.get('input_text')
        logger.info("User Input: "+user_input)
        response = send_message(user_input).replace(
            "*Sarcastic chuckle*", "Haha").replace("*sigh*", "Hah").replace("*Chuckles*", "Hahaha")
        logger.info("Response: "+response)
        h.update(response.encode())
        filename = h.hexdigest()
        logger.info("Filename: "+filename)
        filepath = 'audio/synthesized/'+filename+'.wav'
        data = {'audio': filepath, 'transliteration': response}
        filepath = './static/'+filepath

        # Check for Local Cache
        if (os.path.isfile(filepath)):
            # Update access time. This will allow for routine cleanups
            os.utime(filepath, None)
            print(
                "\033[1;94mINFO:\033[;97m The audio sample sent from cache.")
            logger.info("The audio sample sent from cache.")
            return json.dumps(data)

        # Generate New Sample
        key = str(time.time())[7:]
        if (glados_tts(response, key)):
            tempfile = tempFolder+'GLaDOS-tts-temp-output-'+key+'.wav'

            # If the response isn't too long, store in cache
            if (len(response) < 200 and CACHE):
                shutil.move(tempfile, filepath)
            else:
                data['audio'] = tempfile.replace('./static/', '')
                # os.remove(tempfile)
                return json.dumps(data)
            return json.dumps(data)
        else:
            return 'TTS Engine Failed'

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host="0.0.0.0", port=PORT)
