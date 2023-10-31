import json
from glados import tts_runner
import urllib.parse
import time
from scipy.io.wavfile import write
from utils.tools import prepare_text
import sys
import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.organization = "org-GvNbAFZJOzIVW7POPScDaRFs"
openai.api_key = os.getenv("OPENAI_API_KEY")
sys.path.insert(0, os.getcwd()+'/glados_tts')


print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")

glados = tts_runner(False, True)

tempFolder = 'static/audio/temp/'


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


# If the script is run directly, assume remote engine
if __name__ == "__main__":

    # Remote Engine Veritables
    PORT = 8124
    CACHE = True

    from flask import Flask, request, render_template
    import shutil

    print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")

    app = Flask(__name__, static_url_path='/', static_folder='static')

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/synthesize', methods=['POST', 'GET'])
    # @app.route('/synthesize/', defaults={'text': ''})
    # @app.route('/synthesize/<path:text>')
    def synthesize():
        # if(text == ''): return 'No input'

        # TODO: The below text is what is coming from the form.abs
        # Use it wisely son
        print(request.form.get('input_text'))
        text = "Freedom or death. There is only one in life. You can't have both."
        # text = urllib.parse.unquote(request.url[request.url.find('synthesize/')+11:])
        filename = "GLaDOS-tts-" + \
            text.replace(" ", "-").replace("?", "").replace("!",
                                                            "").replace(",", "")+".wav"
        # filename = filename.replace("°c", "degrees celcius")
        filepath = 'audio/synthesized/'+filename
        data = {'audio': filepath, 'transliteration': text}
        filepath = './static/'+filepath

        # Check for Local Cache
        if (os.path.isfile(filepath)):
            print("AKKPPA1")
            # Update access time. This will allow for routine cleanups
            os.utime(filepath, None)
            print("\033[1;94mINFO:\033[;97m The audio sample sent from cache.")
            # return render_template('index.html', audio_src=directory, its_lit=True)
            return json.dumps(data)

        # Generate New Sample
        key = str(time.time())[7:]
        if (glados_tts(text, key)):
            print("*******AKKPPA2*******")
            tempfile = tempFolder+'GLaDOS-tts-temp-output-'+key+'.wav'

            # If the text isn't too long, store in cache
            if (len(text) < 200 and CACHE):
                shutil.move(tempfile, filepath)
            else:
                print("*****KAPPA3******")
                os.remove(tempfile)
                return json.dumps(data)
            print("****KAPPA4****")
            return json.dumps(data)
        else:
            return 'TTS Engine Failed'

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host="0.0.0.0", port=PORT)
