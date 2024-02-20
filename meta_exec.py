from classes.social_net import Social_Manager
from configparser import ConfigParser



def menu():
	read_acc = ConfigParser()
	read_acc.read("./config.ini")
	acc_list = list(filter(lambda x : x.startswith("section") , read_acc.sections()))
	acc_dict = {acc_list.index(i) : i for i in acc_list}
	select_account = input(f"""Qual conta gostaria de selecionar:
{acc_dict}: """)
	value = acc_dict.get(int(select_account))

	manager = Social_Manager(value)
	manager.face_description()
	manager.insta_description()

def video_metrics(manager: Social_Manager, video_obj):
	resp = manager.makeRequest(video_obj["post_id"]
						+ "/insights?metric=post_video_length,post_video_views,post_video_views_unique,"
						+ "post_video_avg_time_watched,post_video_complete_views_organic,post_video_complete_views_organic_unique,"
						+ "post_video_complete_views_paid, post_video_complete_views_paid_unique, post_video_view_time_by_age_bucket_and_gender,"
						+ "post_video_view_time_by_region_id,"
						+ "post_video_social_actions_count_unique,"
						+ "post_video_views_15s,"
						+ "post_video_views_60s_excludes_shorter,"
						+ "post_video_view_time",
						token=manager.cred["token_30days"])
# post_video_retention_graph,"
# + "post_video_retention_graph_autoplayed,"
# + "post_video_retention_graph_clicked_to_play,"
	metrics = resp[0]["data"]
	dataCols = {}
	dataCols["post_id"] = video_obj["post_id"]
	for type in metrics:
		metric_title = type["title"]
		lifetime = type["period"]
		values = type["values"][0]
		if lifetime == "lifetime":
			dataCols[metric_title] = values["value"]
	return dataCols

def merge_obj(unique_obj1, obj2, id_field):
	append_obj = list(filter(lambda x: x[id_field] == unique_obj1[id_field], obj2))
	print("APPEND OBJECT : ", append_obj)
	data = append_obj[0]
	for i in data.keys():
		print("i is: " ,i)
		unique_obj1[i] = data[i]



def united_metrics(manager: Social_Manager):
	file = manager.getJsonFile("rodrigonevesoficial-face_description", "temp_data")
	video_descs = list(filter(lambda x : x["type"] == "video", file))
	metrics_post_normal = list(map(lambda x : manager.face_post_metric(x), video_descs))
	metrics_video = list(map(lambda x : video_metrics(manager, x), video_descs))

	for i in video_descs:
		print(f"i before {i}\nMERGING OBJECTS")
		merge_obj(i, metrics_post_normal, "post_id")
		merge_obj(i, metrics_video, "post_id")

	print("video descs is" , video_descs)
	manager.writeJsonFile("video_metrics - rn",video_descs)

if __name__ == "__main__":
	manager = Social_Manager("section_r")
	# manager.test_req()
	# Social_Manager("section_m").face_metrics()
	# manager.face_description()
	# united_metrics(manager)
	manager.get_post_by_url("https://www.facebook.com/rodrigonevesoficial/posts/951703186316548")
