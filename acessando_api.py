import requests

#https://api.chucknorris.io/

category = "dev"
url = f"https://api.chucknorris.io/jokes/random?category={category}"

response = requests.get(url)

if response.status_code == 200:
    dados = response.json() 
    print(dados)
else:
    print(f"Erro ao acessar a API: {response.status_code}")
