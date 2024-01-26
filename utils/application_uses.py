##I made this functions for telegram server run with a limit of 4000 characters.
# And after, i addapt the code to the main.py, so i could work with that code functionality on the
# scope i wanted

def separating_characters(text):
	limit = 4000
	initial = 0
	storage = text
	while len(storage) / limit > 1:
		subtext = storage[initial:limit]
		len_sep = subtext.rfind("-----------------------") + 24
		text = subtext[initial:len_sep]
		print("RODANDO UMA OPERAÇÂO\n*******************\n",text)
		storage = storage[len_sep: -1]
	if len(storage) > 0:
		print("RODANDO UMA OPERAÇÂO\n*******************\n",storage)
