import requests

url = "http://localhost:5000/predict"
data = {
    "timestamp": "2024-11-28T22:43:50+05:30",
    "processed_data": {
        "vibration_1": 7.120928, 	  	
        "vibration_2": 2.000000,
        "vibration_3": 2.000000,
        "temperature": 36.251570,
        "rpm": 407.433520 	
    }
      	 	 	 	 		 	 	 	
}

response = requests.post(url, json=data)
print(response.json())
