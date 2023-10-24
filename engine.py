from glados import tts_runner
import urllib.parse
import time
from scipy.io.wavfile import write
from utils.tools import prepare_text
import torch
import sys
import os
import requests
sys.path.insert(0, os.getcwd()+'/glados_tts')


print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")

glados = tts_runner(False, True)


def has_followup(url):
    passed_url = urllib.parse.urlparse(url)
    return bool(passed_url.path)


def glados_tts(text, key=False, alpha=1.0):

    if (key):
        output_file = ('static/audio/GLaDOS-tts-temp-output-'+key+'.wav')
    else:
        output_file = ('static/audio/GLaDOS-tts-temp-output.wav')

    glados.run_tts(text, alpha).export(output_file, format="wav")
    return True


# If the script is run directly, assume remote engine
if __name__ == "__main__":

    # Remote Engine Veritables
    PORT = 8124
    CACHE = True

    from flask import Flask, request, send_file, render_template
    import shutil

    print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")

    app = Flask(__name__, static_url_path='/', static_folder='static')

    @app.route('/')
    def home():
        file = "audio/GLaDOS-tts-Hey!-Fanis!-I-am-ALIVE!.wav"
        return render_template('index.html', audio_src=file, its_lit=False)

    @app.route('/synthesize', methods=['POST', 'GET'])
    # @app.route('/synthesize/', defaults={'text': ''})
    # @app.route('/synthesize/<path:text>')
    def synthesize():
        # if(text == ''): return 'No input'

        print(request.url)
        print(request.data)
        print(request.form.get('input_text'))
        return render_template('index.html', audio_src="KAPPA", its_lit=True)
        text = "I solemnly swear that I am up to no good."
        # text = urllib.parse.unquote(request.url[request.url.find('synthesize/')+11:])
        filename = "GLaDOS-tts-"+text.replace(" ", "-")
        # filename = filename.replace("!", "")
        filename = filename.replace("°c", "degrees celcius")
        filename = filename.replace(",", "")+".wav"
        directory = 'audio/'+filename
        filepath = './static/'+directory

        # Check for Local Cache
        if (os.path.isfile(filepath)):
            print("AKKPPA1")
            # Update access time. This will allow for routine cleanups
            os.utime(filepath, None)
            print("\033[1;94mINFO:\033[;97m The audio sample sent from cache.")
            return render_template('index.html', audio_src=directory, its_lit=True)

        # Generate New Sample
        key = str(time.time())[7:]
        if (glados_tts(text, key)):
            print("*******AKKPPA2*******")
            tempfile = './static/audio/GLaDOS-tts-temp-output-'+key+'.wav'

            # If the text isn't too long, store in cache
            if (len(text) < 200 and CACHE):
                shutil.move(tempfile, filepath)
            else:
                print("*****KAPPA3******")
                return render_template('index.html', audio_src=directory, its_lit=True)
                os.remove(tempfile)

            print("****KAPPA4****")
            return render_template('index.html', audio_src=directory, its_lit=True)

        else:
            return 'TTS Engine Failed'

    # def process():
    # 	file=synthesize("I want to be the very best")
    # 	return render_template('index.html',audio_src=file)

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host="0.0.0.0", port=PORT)
