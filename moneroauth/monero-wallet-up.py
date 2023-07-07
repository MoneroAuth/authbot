import subprocess

monero_path = '/home/user/monero-v0.18.2.2/'

def wallet_up ():

	l = subprocess.check_output('ps aux | grep "monero-wallet-rpc"' , shell =True)
	res = l.split()
#	print('res:')
#	print(res)
#	print()
#	print(res[1])
	if b'/home/user/monero-v0.18.2.2/authbot' in res:
#		print('monero-wallet-rpc is running')
		return True
	else:
#		print('monero-wallet-rpc is NOT running')
		com = monero_path + "monero-wallet-rpc --rpc-bind-port 18089 --disable-rpc-login --wallet-file " + monero_path + "authbot --password-file " + monero_path + "pwd.txt &"
#		print(com)
		try:
#			ret = subprocess.check_output(com, shell=True)
			ret = subprocess.run(com,shell=True)
		except subprocess.CalledProcessError as e:
			print(e.output)
			sleep(2)
		return True

x = wallet_up()
