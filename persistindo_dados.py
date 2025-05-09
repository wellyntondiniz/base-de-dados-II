#pip install sqlalchemy mysql-connector-python

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, insert, text

username = "root" 
password = "suasenha"  
host = "localhost"  
port = 3306  
database = "banco_de_sangue"  

connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

metadata = MetaData()


#Exemplo utilizando Table
doador = Table(
    "doador", metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(100)),
    Column("tipo_sanguineo", String(5))
)

with engine.connect() as conexao:
    novo_doador = {
        "nome": "Wellynton",
        "tipo_sanguineo": "O+"
    }

    comando = insert(doador).values(novo_doador)
    conexao.execute(comando)
    conexao.commit() 

#Exemplo inserindo via script
sql = text("""
    INSERT INTO doador (nome, tipo_sanguineo)
    VALUES (:nome, :tipo_sanguineo)
""")

dados = {
    "nome": "Júlio",
    "tipo_sanguineo": "B-"
}

with engine.begin() as conexao:
    conexao.execute(sql, dados)
