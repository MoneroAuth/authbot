import json

def generate_json(d,challenge_msg):
	if 'dataset' not in d.keys():
		for x in d['params']:
			print(x)
			challenge_msg = challenge_msg + ',"' + x + '":"' + str(d['params'][x]) + '"'
		challenge_msg = challenge_msg + '}}'
	else:
		for x in d['params']:
			print(x)
			if x == 'dataset':
				print("Entering x== 'dataset' conditional test.")
				challenge_msg = challenge_msg + ',"' + x + '":'
				ds = str(d['params']['dataset'])
				dsm = ds.replace("'", '"')
				challenge_msg = challenge_msg + dsm + "}}"
				break
			else:
				print(x)
				print(d['params'][x])
				challenge_msg = challenge_msg + ',"' + x + '":"' + str(d['params'][x]) + '"'
				print(challenge_msg)
					
	return challenge_msg



line = '{"json":"2.0","method":"challenge_request","params":{"resource_mgr_id":"498EM2vdJRSV6LcRUadS7TE4BdpusMz4wWMAm8YoBAw3M8D3ZkdvYSQN42FBm1aG7X8pRkEFpgvZBPAh78xbYLnj1NZbgJD","resource_id":"45BiaAEJgGJGgq3sdjyEgZgZcwETYCMeG1q2VWCU6CKZDS3grBQdDsZD2DgEYi3KRxKZfSCuFntdNWrN72vXcYm6CMNyJRW","id":"43mq8WjgSp9cdEztUZrsyNMjTNXy1QPJdWD8czEzzF8iPBVxFtMbS4EFVB1PpW2AapjY7nVsdp2nZGG2qcEzzp8A3AyKuts","action":"update_personal_data","dataset":{"id":"43mq8WjgSp9cdEztUZrsyNMjTNXy1QPJdWD8czEzzF8iPBVxFtMbS4EFVB1PpW2AapjY7nVsdp2nZGG2qcEzzp8A3AyKuts","first_name":"Douglas","last_name":"Bebber","email":"dougbebber@protonmail.com"}}}'
#line = '{"json":"2.0","method":"challenge_request","params":{"resource_mgr_id":"498EM2vdJRSV6LcRUadS7TE4BdpusMz4wWMAm8YoBAw3M8D3ZkdvYSQN42FBm1aG7X8pRkEFpgvZBPAh78xbYLnj1NZbgJD","resource_id":"45BiaAEJgGJGgq3sdjyEgZgZcwETYCMeG1q2VWCU6CKZDS3grBQdDsZD2DgEYi3KRxKZfSCuFntdNWrN72vXcYm6CMNyJRW","id":"43mq8WjgSp9cdEztUZrsyNMjTNXy1QPJdWD8czEzzF8iPBVxFtMbS4EFVB1PpW2AapjY7nVsdp2nZGG2qcEzzp8A3AyKuts","action":"get_personal_data"}}'
buffer = json.loads(line)

#print(buffer.keys())
print(buffer)

#for x in buffer['params']:
#	print(x)
#	if x == 'dataset':
#		for y in buffer['params']['dataset']:
#			print(y)

#if buffer['params']['dataset'] is None:
#	print("No dataset!")
#else:
#	print("dataset exists!")

#d = str(buffer['params']['dataset'])
#print(d)

dataset = buffer['params']['dataset']
ds = str(dataset).replace("'",'"')
print(dataset)
print(ds)
#challenge = "12345789"
#challenge_msg = '{"json":"2.0","method":"challenge","params":{"challenge_string":"' + challenge + '"'
#challenge_msg = generate_json(buffer,challenge_msg)
#print(challenge_msg)
