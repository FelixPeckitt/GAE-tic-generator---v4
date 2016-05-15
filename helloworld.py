import sys
sys.path.insert(0, 'libs')
import webapp2
import json
import string
from jinja2 import Template
import cgi
import jinja2
import os
#this function returns a list of tics that rhyme using rhymebrain.com json data as input
def get_rhyming_tic(json_string):
    #parsing the json string so it can be read by python
    parsed_json = json.loads(json_string)
    
    #opening the tic file
    fo = open("files/tic text.txt", "r")        
    line = fo.readlines()
    fo.close()

    #tic file is now a list - clean for punctuation and whitespace
    out = [s.translate(None, string.punctuation) for s in line]
    strip_line = map(str.strip, out)

    #last word text from excel - how to do this without hard coding?
    fp = open("files/last word.txt", "r")
    last_word = fp.readlines()
    fp.close()

    #last word file now a list - clean for punctuation and whitespace
    out2 = [s.translate(None, string.punctuation) for s in last_word]
    strip_word = map(str.strip, out2)

    #make a dictionary from tics and last words of tics
    tic_dict = dict(zip(strip_word, strip_line))

    #list of just the rhyming words from json data
    rhyming_word_list = []
    for i in range(0,len(parsed_json)):
        if parsed_json[i]["score"] >= 300:
            rhyming_word_list.append(parsed_json[i]["word"])

    #gets rhyming words that are also last words of tics
    rhyming_tic_words = set(strip_word).intersection(rhyming_word_list)

    #gets rhyming tics from those words as a list
    word_list = []
    for i in rhyming_tic_words:
         word_list.append(tic_dict[i])
    return word_list

#last word text from excel - how to do this without hard coding?
fp = open("files/unique tic text.txt", "r")
last_word = fp.readlines()
fp.close()

#cleaning the last words
out2 = [s.translate(None, string.punctuation) for s in last_word]
strip_word = map(str.strip, out2)

rhyme_api = "http://rhymebrain.com/talk?function=getRhymes&word=%s"

import urllib
def get_rhyme(word):
    #gets word information and rhyme of a word from rhymebrain.com
    # fetch the data
    response = urllib.urlopen(rhyme_api % word)
    return response.read()
	
#generates a poem from tic data and a word of choice
def generate_tic_poem_from_word(word):
    if get_rhyming_tic((get_rhyme(word))) == []:
        return "Sorry, no rhyming tics found!"
    else:
        return "<br>".join(get_rhyming_tic((get_rhyme(word))))
             

#Start of Web App
JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

def unescape(s):
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	# this has to be last:
	s = s.replace("&amp;", "&")
	return s
	
#webform
class MainPage(webapp2.RequestHandler):
	def get(self):
		template_values = {}
		template = JINJA_ENVIRONMENT.get_template('templates/hello_form.html')
		self.response.write(template.render(template_values))

#response as poem
class Poem(webapp2.RequestHandler):
	def post(self):
		word_form = self.request.get('chosen_word')
		word = word_form.capitalize()
		poem = generate_tic_poem_from_word(word_form)
		template_values = {
		'poem' : poem ,
		'word' : word
		}
		
		template = JINJA_ENVIRONMENT.get_template('templates/index.html')
		self.response.write(unescape(template.render(template_values)))
        
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/poem', Poem),
], debug=True)

def main():
    app.run()

if __name__=='__main__':
    main()


