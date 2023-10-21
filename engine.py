import sys
import os
sys.path.insert(0, os.getcwd()+'/glados_tts')

import torch
from utils.tools import prepare_text
from scipy.io.wavfile import write
import time
import urllib.parse

from glados import tts_runner
		
print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")

glados = tts_runner(False, True)

def has_followup(url):
	passed_url=urllib.parse.urlparse(url)
	return bool(passed_url.path)

def glados_tts(text, key=False, alpha=1.0):

	if(key):
		output_file = ('static/audio/GLaDOS-tts-temp-output-'+key+'.wav')
	else:
		output_file = ('static/audio/GLaDOS-tts-temp-output.wav')

	glados.run_tts(text, alpha).export(output_file, format = "wav")
	return True


# If the script is run directly, assume remote engine
if __name__ == "__main__":
	
	# Remote Engine Veritables
	PORT = 8124
	CACHE = True

	from flask import Flask, request, send_file, render_template
	import shutil
	
	print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")
	
	app = Flask(__name__,static_url_path='/',static_folder='static')
 
	@app.route('/')
	def home():
		file="audio/GLaDOS-tts-Hey!-Fanis!-I-am-ALIVE!.wav"
		return render_template('index.html',audio_src=file)

	@app.route('/synthesize',methods=['POST'])
	#@app.route('/synthesize/', defaults={'text': ''})
	#@app.route('/synthesize/<path:text>')
	def synthesize():
		#if(text == ''): return 'No input'
		
		text="I want to be the very best! The one what you want."
		#text = urllib.parse.unquote(request.url[request.url.find('synthesize/')+11:])
		filename = "GLaDOS-tts-"+text.replace(" ", "-")
		#filename = filename.replace("!", "")
		filename = filename.replace("°c", "degrees celcius")
		filename = filename.replace(",", "")+".wav"
		file = os.getcwd()+'/static/audio/'+filename
		
		# Check for Local Cache
		if(os.path.isfile(file)):
		
			# Update access time. This will allow for routine cleanups
			os.utime(file, None)
			print("\033[1;94mINFO:\033[;97m The audio sample sent from cache.")
			return render_template('index.html',audio_src=file)
			
		# Generate New Sample
		key = str(time.time())[7:]
		if(glados_tts(text, key)):
			tempfile = os.getcwd()+'/static/audio/GLaDOS-tts-temp-output-'+key+'.wav'
						
			# If the text isn't too long, store in cache
			if(len(text) < 200 and CACHE):
				shutil.move(tempfile, file)
			else:
				return render_template('index.html',audio_src=file)
				os.remove(tempfile)
				
			return render_template('index.html',audio_src=file)
				
		else:
			return 'TTS Engine Failed'

	# def process():
	# 	file=synthesize("I want to be the very best")
  	# 	return render_template('index.html',audio_src=file)
			
	cli = sys.modules['flask.cli']
	cli.show_server_banner = lambda *x: None
	app.run(host="0.0.0.0", port=PORT)
