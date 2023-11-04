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
load_dotenv()
openai.organization = "org-GvNbAFZJOzIVW7POPScDaRFs"
openai.api_key = os.getenv("OPENAI_API_KEY")
sys.path.insert(0, os.getcwd()+'/glados_tts')


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")

glados = tts_runner(False, True)

tempFolder = './static/audio/temp/'

h = hashlib.new('sha256')


def has_followup(url):
    passed_url = urllib.parse.urlparse(url)
    return bool(passed_url.path)


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


# If the script is run directly, assume remote engine
if __name__ == "__main__":

    # Remote Engine Veritables
    PORT = 8124
    CACHE = True

    print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")

    app = Flask(__name__, static_url_path='/', static_folder='static')

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/synthesize', methods=['POST'])
    # @app.route('/synthesize/', defaults={'text': ''})
    # @app.route('/synthesize/<path:text>')
    def synthesize():
        # if(text == ''): return 'No input'

        # TODO: The below text is what is coming from the form.abs
        # Use it wisely son
        user_input = request.form.get('input_text')
        response = send_message(user_input).replace(
            "*Sarcastic chuckle*", "Haha").replace("*sigh*", "Hah").replace("*Chuckles*", "Hahaha")
        print(color.CYAN + "GLaDOS: "+response+color.END)
        # response = "Freedom or death. There is only one in life. You can't have both."
        # text = urllib.parse.unquote(request.url[request.url.find('synthesize/')+11:])
        h.update(response.encode())
        filename = h.hexdigest()
        print(color.BLUE+filename+color.END)
        # filename = filename.replace("°c", "degrees celcius")
        filepath = 'audio/synthesized/'+filename+'.wav'
        data = {'audio': filepath, 'transliteration': response}
        filepath = './static/'+filepath

        # Check for Local Cache
        if (os.path.isfile(filepath)):
            print("AKKPPA1")
            # Update access time. This will allow for routine cleanups
            os.utime(filepath, None)
            print(
                "\033[1;94mINFO:\033[;97m The audio sample sent from cache.")
            # return render_template('index.html', audio_src=directory, its_lit=True)
            return json.dumps(data)

        # Generate New Sample
        key = str(time.time())[7:]
        if (glados_tts(response, key)):
            print("*******AKKPPA2*******")
            tempfile = tempFolder+'GLaDOS-tts-temp-output-'+key+'.wav'

            # If the response isn't too long, store in cache
            if (len(response) < 200 and CACHE):
                shutil.move(tempfile, filepath)
            else:
                print("*****KAPPA3******")
                data['audio'] = tempfile.replace('./static/', '')
                # os.remove(tempfile)
                return json.dumps(data)
            print("****KAPPA4****")
            return json.dumps(data)
        else:
            return 'TTS Engine Failed'

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host="0.0.0.0", port=PORT)
