# File to provide some functions to deal with credentials and stuff
from configparser import ConfigParser
import requests
import threading
from utils.date_formats import *
import json

def read_config(section):
	config = ConfigParser()
	config.read('config.ini')
	tuple_items = config.items(section)
	object = {i[0] : i[1] for i in tuple_items}
	return object

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

	def	write_new_temp_token(self, new_token):
		parser = ConfigParser(self.cred)
		parser.read("config.ini")
		parser.set(self.account_name,"token", new_token)
		with open('./config.ini', 'w') as file:
			parser.write(file)

	def write_new_long_token(self, token_temp):
		parser_app = self.display_credentials('myapp')
		response = self.fetch_data(self.url_requests["domain"]
				+"oauth/access_token?grant_type=fb_exchange_token&client_id="
				+parser_app["client_id"]
				+ "&client_secret="
				+parser_app["client_secret"]
				+"&fb_exchange_token="
				+token_temp)
		access_token = response["access_token"]
		parser = ConfigParser(self.cred)
		parser.read("config.ini")
		parser.set(self.account_name,"token_30days", access_token)
		with open('./config.ini', 'w') as file:
			parser.write(file)

		return access_token

	def fetch_data(self, url):
		response = requests.get(url)
		return response.json()

	def	test_req(self):
		url_test = "https://graph.facebook.com/v19.0/me?fields=id%2Cname&access_token="
		token = "" if self.cred.get("token_30days") == None else self.cred["token_30days"]
		response = self.fetch_data(url_test + token)
		while response.get("error") != None:
			new_token = input("Give a new token to the: " + self.account_name + " account - ")
			self.write_new_temp_token(new_token)
			token = self.write_new_long_token(new_token)
			response = self.fetch_data(url_test + token)
		return True

	def makeRequest(self, *args, media = "", token = "" ):
		arrayRequest = []

		for i in range(len(args)):
			url = self.url_requests['domain'] + media + args[i] + self.url_requests['prefix_acesstoken'] + token
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

	def	endpoints(self, type, date_array=None):
		js_obj = self.getJsonFile(file_name="endpoints", file_folder='classes')[type]

		date = list(filter(lambda x : x == '$(since_date)' or x == '$(until_date)', js_obj))
		period = return_period(date_array) if not(date == []) else None
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

	def get_face_post_info(self, link):
		page_id = self.cred["face_page_id"]
		print(f"link is : {link}")
		len_substr = link.rfind('/') + 1
		post_id = link[len_substr:len(link)]
		endpoint = self.endpoints('face_post_desc')
		data = self.makeRequest(page_id +"_"+ post_id + endpoint, token=self.cred["token_30days"])
		#PAREI AQUI. NECESSÁRIO PEGAR OS DADOS DE MÉTRICAS DOS POSTS
		return data

	def face_description(self, date_optional=None):
		request_validated = self.endpoints('face_desc', date_optional)
		if request_validated == False:
			return False
		face_request = self.makeRequest(request_validated,
										media=self.cred['face_id'],
										token=self.cred['token_30days'])

		description_data = list(face_request[0]["data"])

	#print("First Dict JSON New", description_data)
		try: next_page = face_request[0]["paging"]["next"]
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
							new_desc,
							"temp_data")
		print(f"File Writed with success")
		return new_desc

	def face_post_metric(self, data_obj, date_optional=None):
		request_validated1 = self.endpoints('face_metric1', date_optional)
		request_validated2 = self.endpoints('face_metric2', date_optional)
		if request_validated1 == False or request_validated2 == False:
			return False
		data = self.makeRequest(data_obj["post_id"] +
								request_validated1,
								data_obj["post_id"] +
								request_validated2,
								token=self.cred['token_30days'])

		dataCols = {}
		dataCols["post_id"] = data_obj["post_id"]
		try:		dataCols["shares"] = data[1]["shares"]["count"]
		except: 	dataCols["shares"] = 0
		dataCols["comments"] = data[1]["comments"]["summary"]["total_count"]
		for type in data[0]["data"]:
			metric_title = type["title"]
			values = type["values"][0]
			match metric_title:
					case "Lifetime Total post Reactions by Type.":
						reactions = type["values"][0]["value"]
						dataCols["like"] = 0 if reactions.get("like")== None else reactions.get("like")
						dataCols["haha"] = 0 if reactions.get("haha") == None else reactions.get("haha")
						dataCols["love"] = 0 if reactions.get("love") == None else reactions.get("love")
						dataCols["sorry"] = 0 if reactions.get("sorry") == None else reactions.get("sorry")
						dataCols["wow"] = 0 if reactions.get("wow") == None else reactions.get("wow")
						dataCols["anger"] = 0 if reactions.get("anger") == None else reactions.get("anger")

					case "Lifetime Matched Audience Targeting Consumers on Post":
						dataCols["unique_clicks_on_post"] = values.get("value")
						#print("cliques únicos no post: ",dataCols["unique_clicks_on_post"])
					case "Lifetime Engaged Users":
						dataCols["engaged_users"] = values.get("value")
					case "Lifetime People who have liked your Page and engaged with your post":
						dataCols["engaged_fans"] = values.get("value")
					case "Lifetime Post Total Reach":
						dataCols["reach"] = values.get("value")
						#print("Alcance: ", dataCols["reach"])
					case _:
						print("Não entrei em nenhum case")
		return dataCols

	def face_metrics(self, posts_archive='file'):

		if posts_archive == 'file':
			posts = self.getJsonFile(self.cred['face_id']
							+ "-face_description",
							"temp_data")
		else:
			posts = posts_archive

		def get_metrics(value):
			metrics = self.face_post_metric(value)
			return metrics
		obj = list(map(get_metrics, posts))
		self.writeJsonFile( self.cred['face_id']
					 		+ "-face_metrics",
							obj,
							"temp_data")
		return obj

	def face_all_data(self, date_optional=None):
		js_desc_obj = self.face_description(date_optional)
		def returning_dict(desc_obj):
			metric_obj = self.face_post_metric(desc_obj)
			del metric_obj["post_id"]
			dict_new = {i: desc_obj.get(i) for i in desc_obj.keys()}
			# print("dict_before: ", dict_new)
			dict_metrics = {i : metric_obj.get(i) for i in metric_obj.keys()}
			dict_new.update(dict_metrics)
			# print("dict_after: ", dict_new)
			return dict_new
		all_data_obj = list(map(returning_dict, js_desc_obj))
		return all_data_obj


	def insta_description(self, date_optional=None):
		request_validated = self.endpoints('insta_desc', date_optional)
		if request_validated == False:
			return False
		insta_request = self.makeRequest(request_validated,
						media=self.cred['insta_id'],
						token=self.cred['token_30days'])
		js_obj = insta_request[0]
		data = js_obj["data"]
		try: next_page = insta_request[0]["paging"]["next"]
		except: next_page = 0
		while next_page != 0:
			# print("Entering in loop While")
			new_request = requests.get(next_page)
			new_data_file = new_request.json()
			new_data = list(new_data_file["data"])
			data = data + new_data
			try:
				next_page = new_data_file["paging"]["next"]
			except:
				next_page = 0
		return data

	def insta_post_metric(self, posts, date_optional=None):
		if posts["media_product_type"] == "FEED":
			request_validated = self.endpoints('insta_metric_feed', date_optional)
			if request_validated == False:
				return False
			url = posts["id"] + request_validated
		elif posts["media_product_type"] == "REELS":
			request_validated = self.endpoints('insta_metric_reels', date_optional)
			if request_validated == False:
				return False
			url = posts["id"] + request_validated
		data = self.makeRequest(url, token=self.cred["token_30days"])
		info = data[0]["data"]
		metrics_dict = {i["name"]: i['values'][0]['value'] for i in info}
		metrics_dict["comments_count"] = posts["comments_count"]
		metrics_dict["like_count"] = posts["like_count"]
		metrics_dict["media_product_type"] = posts["media_product_type"]
		metrics_dict["id"] = posts["id"]

		return metrics_dict

	def insta_metrics(self, posts_archive="file"):
		if posts_archive == "file":
			posts = self.getJsonFile(self.cred['face_id']
				+ "-insta_description",
				"temp_data")
		else:
			posts = posts_archive

		def get_metrics(value):
			metrics = self.insta_post_metric(value)
			return metrics
		obj = list(map(get_metrics, posts))
		self.writeJsonFile(self.cred['face_id']
							+ "-insta_metrics",
							obj,
							"temp_data")
		return obj

	def creating_text_for_obj(self, json, date, separator):
		print(json)
		message = f"""Métricas Facebook - datas:{date[0]} a {date[1]}:
"""
		metric_sum = {"comments" : 0,
					"reach": 0,
					"shares": 0,
					"unique_clicks_on_post": 0}
		for obj in json:
			data = "data do post : " + obj["created_time"]
			desc = "mensagem: " + obj["message"]
			link = "link: " + obj["permalink_url"]
			metric_sum["comments"] += obj["comments"]
			metric_sum["reach"] += obj["reach"]
			metric_sum["shares"] += obj["shares"]
			metric_sum["unique_clicks_on_post"] += obj["unique_clicks_on_post"]
			# like:{obj["like"]}
			# haha: {obj["haha"]}
			# love: {obj["love"]}
			# sorry: {obj["sorry"]}
			# wow: {obj["wow"]}
			# anger: {obj["anger"]}
			metrics = f"""****************
MÉTRICAS

compartilhamentos: {obj["shares"]}
comentários: {obj["comments"]}
alcance: {obj["reach"]}
engajamento: {obj["unique_clicks_on_post"]}
"""
			message = '\n'.join([message, link, data, desc,	 metrics, separator])
		sum_metrics = F"""
SOMA MÉTRICAS NO GERAL
compartilhamentos: {metric_sum["shares"]}
comentários: {metric_sum["comments"]}
alcance: {metric_sum["reach"]}
engajamento: {metric_sum["unique_clicks_on_post"]}
"""
		message = '\n'.join([message, sum_metrics])
		return message


