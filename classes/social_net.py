# File to provide some functions to deal with credentials and stuff
from configparser import ConfigParser
import requests
import threading

class Social_Manager:

	def	__init__(self, account):
		self.account_name = account
		self.cred = self.display_credentials()
		self.url_requests = self.display_credentials('request')

	def	display_credentials(self, section=''):
		parser = ConfigParser()
		parser.read('config.ini')
		tuple_items = parser.items(self.account_name) if section == '' else parser.items(section)
		obj_items = {i[0] : i[1] for i in tuple_items}
		return obj_items

	def	write_new_token(self, new_token):
		parser = ConfigParser(self.cred)
		parser.read("config.ini")
		parser.set(self.account_name,"token", new_token)
		with open('./config.ini', 'w') as file:
			parser.write(file)

	def fetch_data(self, url):
		response = requests.get(url)
		return response.json()

	def	test_req(self):
		url_test = "https://graph.facebook.com/v18.0/me?fields=id%2Cname&access_token="
		token = self.cred["token"]
		response = self.fetch_data(url_test + token)
		while response.get("error") != None:
			new_token = input("Give a new token to the: " + self.account_name + " account - ")
			self.write_new_token(new_token)
			token = new_token
			response = self.fetch_data(url_test + token)
		return True

	def makeRequest(self, *args, media = "", token = "" ):
		arrayRequest = []

		for i in range(len(args)):
			url = self.url_requests['domain'] + media + args[i] + self.url_requests['prefix_acesstoken'] + token
			thread = threading.Thread(target=lambda : arrayRequest.append(self.fetch_data(url)))

			thread.start()
			thread.join()
		return arrayRequest

