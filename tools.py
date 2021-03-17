import re

def ExtractURL(tag):
	''' Iz niza, ki vsebuje HTML znacko z URL naslovom izlusci ta URL '''
	return re.search(r"http.+?\"",tag).group()[:-1] # odstranimo zadnji znak, da se znebimo "