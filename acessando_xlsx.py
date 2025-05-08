import pandas as pd


#https://www.kaggle.com/datasets/amalsp220/bloodbankdetails

arquivo_excel = "BloodBankDetails.csv"

df = pd.read_csv(arquivo_excel)

#df = pd.read_csv("dados.csv", sep=';')
#df = pd.read_csv("dados.csv", encoding='ISO-8859-1')
#df = pd.read_csv("dados.csv", header=None)
#df = pd.read_csv("dados.csv", usecols=["NAME"])


print(df)