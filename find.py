import requests
import time
import sys

url = 'https://api.twitch.tv/helix/'
headers = {'Client-ID': '003xkrdr02vwtl6s14vjmef1992bt2'}

def get_response(url, headers, params):
	response = requests.get(url,  headers=headers, params=params)	
	if response.status_code == 400:
		print('bad request', flush=True)		
	if response.status_code == 404:
		print('invalid url', flush=True)
	while response.status_code in [429, 503]:
		print('waiting for more requests', flush=True)
		time.sleep(5)
		response = requests.get(url,  headers=headers, params=params)
	if response.status_code == 503:
		print('503', flush=True)
	return response
	
def get_id_of_user(username):
	try:
		response = get_response(url+'users?login='+username, headers,'')	
		data = response.json()['data']
		return data[0]['id']
	except:
		print('user does not exist')
		sys.exit()
		
def get_following_of_id(id):
	response = get_response(url+'users/follows?from_id='+id, headers, {'first': 100})
	data = response.json()['data']
	idList = []
	while len(data) > 0:	
		cursor = response.json()['pagination']['cursor']
		for follower in data:
			idList.append(follower['to_id'])
		response = get_response(url+'users/follows?from_id='+id, headers, {'after': cursor, 'first': 100})
		data = response.json()['data']
	return idList

def get_online_ids_from_id_list(list):
	if len(list) == 0:
		print('list is empty')
		sys.exit()
	count = 0
	idString = ''
	online = []
	for id in list:
		idString += id+'&user_id='
		count += 1
		if count == 100:
			response = get_response(url+'streams?user_id='+idString[:-9], headers,'')
			data = response.json()['data']
			for id in data:
				if id['type'] is not None:
					online.append(id['user_id'])
			idString = ''
			count = 0
	response = get_response(url+'streams?user_id='+idString[:-9], headers,'')
	data = response.json()['data']
	for id in data:
		if id['type'] is not None:
			online.append(id['user_id'])
	return online

def get_usernames_from_id_list(list):
	if len(list) == 0:
		print('list is empty')
		sys.exit()
	count = 0
	idString = ''
	usernames = []
	for id in list:
		idString += id+'&id='
		count += 1
		if count == 100:
			response = get_response(url+'users?id='+idString[:-4], headers,'')
			data = response.json()['data']
			for user in data:
				usernames.append(user['login'])
			idString = ''
			count = 0
	response = get_response(url+'users?id='+idString[:-4], headers,'')
	data = response.json()['data']
	for user in data:
		usernames.append(user['login'])
	return usernames

def search_following(user):
	usernames = get_usernames_from_id_list(get_online_ids_from_id_list(get_following_of_id(get_id_of_user(user))))
	for username in usernames:
		while True:
			try:
				response =  get_response('https://tmi.twitch.tv/group/user/'+username+'/chatters', '', '')
				total = response.json()['chatter_count']
				print('Checking: {:<25}{}'.format(username, total), flush=True)
				viewers = response.json()['chatters']['viewers']
				if user.lower() in viewers:
					print('found '+user+' in '+username,flush=True)
				mods = response.json()['chatters']['moderators']
				if user.lower() in mods:
					print('found '+user+'(mod)'+' in '+username,flush=True)
				staff = response.json()['chatters']['staff']
				if user.lower() in staff:
					print('found '+user+'(staff)'+' in '+username,flush=True)
				break
			except:
				pass
	print(len(usernames), flush=True)

def search_all(user):
	response = get_response(url+'streams?', headers, {'first': 99})
	data = response.json()['data']
	idList = []
	while len(data) > 0:
		cursor = response.json()['pagination']['cursor']
		for stream in data:
			idList.append(stream['user_id'])
		channels = get_usernames_from_id_list(idList)
		for username in channels:
			while True:
				try:
					response =  get_response('https://tmi.twitch.tv/group/user/'+username+'/chatters', '', '')
					total = response.json()['chatter_count']
					print('Checking: {:<25}{}'.format(username, total), flush=True)
					viewers = response.json()['chatters']['viewers']
					if user.lower() in viewers:
						print('found '+user+' in '+username,flush=True)
					mods = response.json()['chatters']['moderators']
					if user.lower() in mods:
						print('found '+user+'(mod)'+' in '+username,flush=True)
					staff = response.json()['chatters']['staff']
					if user.lower() in staff:
						print('found '+user+'(staff)'+' in '+username,flush=True)
					break
				except:
					pass
		response = get_response(url+'streams?', headers, {'after': cursor, 'first': 99})
		data = response.json()['data']
		idList = []

def main():
	while True:
		user = input('user: ')
		search_following(user)
		if input('search all: ') == 'y':
			search_all(user)
	
main()