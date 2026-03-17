import requests
import json

# base_url = "https://api.tryallai.com"
base_url = "https://ap3.tryallai.com"
rel_url = "/v1/chat/completions"
url = base_url + rel_url

payload = json.dumps({
   "model": "gpt-4o-mini",
   "stream": False,
   "messages": [
      {
         "role": "user",
         "content": [
            {
               "type": "text",
               "text": "这张图片是什么"
            }
         ]
      }
   ],
   "temperature": 0.9,
   "max_tokens": 400
})
headers = {
   'Authorization': 'Bearer sk-kwEMvQT4usav3BcsMdKFRO18RyJuzI42Gk6J6RHOYBGqAjll',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)