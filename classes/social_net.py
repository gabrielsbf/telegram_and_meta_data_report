# File to provide some functions to deal with credentials and stuff
from configparser import ConfigParser
import requests
import threading
from utils.date_formats import *
import json

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
			url = self.url_requests['domain'] + media + '/' + args[i] + self.url_requests['prefix_acesstoken'] + token
			print("url request is ", url )
			thread = threading.Thread(target=lambda : arrayRequest.append(self.fetch_data(url)))

			thread.start()
			thread.join()
		return arrayRequest

	def getJsonFile(self, file_name, file_folder='.'):

		with open(file_folder + "/" + file_name + ".json") as json_file:
			data = json.load(json_file)
		return data

	def writeJsonFile(self, file_name, archive, file_folder='.'):
		archive = json.dumps(archive)

		with open( file_folder + "/" + file_name + ".json", "w") as json_file:
			json_file.write(archive)

	def	endpoints(self, type):
		js_obj = self.getJsonFile(file_name="endpoints", file_folder='classes')[type]

		date = list(filter(lambda x : x == 'since_date' or x == 'until_date', js_obj))
		period = return_period() if not(date == []) else None

		def cases(iter):
			match iter:
				case '$(since_date)':
					return period["start_date"]["unix_time"]
				case '$(until_date)':
					return period["final_date"]["unix_time"]
				case _:
					return iter
		url = ''
		for i in js_obj:
			url = ''.join([url, cases(i)])

		return url

	def face_description(self):

		first_request = self.makeRequest(self.endpoints('face_desc'),
										media=self.cred['face_id'],
										token=self.cred['token_30days'])

		description_data = list(first_request[0]["data"])

	#print("First Dict JSON New", description_data)
		try: next_page = first_request[0]["paging"]["next"]
		except: next_page = 0

		while next_page != 0:
			# print("Entering in loop While")
			new_request = requests.get(next_page)
			newJson_file = new_request.json()
			dataFile =list(newJson_file["data"])
			# print(f"Data File to Append: \n type: {type(dataFile)}, \n texto: {dataFile}")
			# print("File JSON Data new", dataFile)
			description_data =  description_data + dataFile
			# print(f"Description Data File: \n type: {type(description_data)}, \n texto: {description_data}")
			try:
				next_page = newJson_file["paging"]["next"]
			except:
				next_page = 0
				#print("Entering in except")

		def new_key(value):
			new_dict = {}
			new_dict.update({"post_id": value["id"],
							"permalink_url" : value["permalink_url"],
							"message" : value["message"],
							"created_time" : value["created_time"]})
			return new_dict

		new_desc = list(map(new_key, description_data))
		print(new_desc)

		self.writeJsonFile( self.cred['face_id']
					 		+ "-face_description",
							new_desc)
		print(f"File Writed with success")

	def face_post_metric(self, post_id):
		data = self.makeRequest(post_id +
								self.endpoints('face_metric1'),
								post_id +
								self.endpoints('face_metric2'),
								token=self.cred['token_30days'])
		return data
