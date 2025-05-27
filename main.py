import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import altair as alt
import os
import sys
caminho_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(caminho_raiz)
os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'


# Dados de conexão
username = "root"
password = "********"
host = "localhost"
port = 3306
database = "panorama"
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)
conn = engine.connect()



def consultar_conhecimento(localidade, limit, id_tipo_conhecimento, cargo, grande_area, tipo):
    query = """
    SELECT com.descricao, COUNT(*) as quantidade
    FROM vaga
    INNER JOIN vaga_conhecimento hard ON vaga.id = hard.id_vaga
    INNER JOIN conhecimento com ON hard.id_conhecimento = com.id
    LEFT JOIN tipo_conhecimento tc ON com.id_tipo_conhecimento = tc.id
    LEFT JOIN cargo ON vaga.id_cargo = cargo.id
    LEFT JOIN cargo_area ON cargo.id_cargo_area = cargo_area.id
    LEFT JOIN cargo_grande_area ON cargo_area.id_cargo_grande_area  = cargo_grande_area.id
    WHERE  1=1  
    """
    
    if localidade != "Todas":
        query += f"and vaga.localidade = '{localidade}' "
    if id_tipo_conhecimento:
        query += f"and tc.id = '{id_tipo_conhecimento}' "
    if cargo != "Todos":
        query += f"and vaga.cargo = '{cargo}' "
    if grande_area != "Todas":
        query += f"and cargo_grande_area.descricao = '{grande_area}' "
    if tipo:
        query += f"and hard.tipo = '{tipo}' "

    query += f"""
    GROUP BY com.descricao
    ORDER BY quantidade DESC
    LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    return df

def consultar_quantidade_skills(localidade, cargo, grande_area, tipo=None):
    query = """
    SELECT COUNT(*) as quantidade
    FROM conhecimento c
    WHERE c.id IN (
    SELECT vc.id_conhecimento FROM vaga_conhecimento vc
    INNER JOIN vaga ON vaga.id = vc.id_vaga
    LEFT JOIN cargo ON vaga.id_cargo = cargo.id
    LEFT JOIN cargo_area ON cargo.id_cargo_area = cargo_area.id
    LEFT JOIN cargo_grande_area ON cargo_area.id_cargo_grande_area  = cargo_grande_area.id
    WHERE 1=1
    """
    
    if localidade != "Todas":
        query += f"and vaga.localidade = '{localidade}' "
    if tipo:
        query += f"and vc.tipo = '{tipo}' "
    if cargo != "Todos":
        query += f"and vaga.cargo = '{cargo}' "
    if grande_area != "Todas":
        query += f"and cargo_grande_area.descricao = '{grande_area}' "
     
    query += ")"
    
    df = pd.read_sql_query(query, conn)
    return df

def consultar_quantidade_vagas(localidade, cargo, grande_area):
    query = """
    SELECT COUNT(*) as quantidade
    FROM vaga
    LEFT JOIN cargo ON vaga.id_cargo = cargo.id
    LEFT JOIN cargo_area ON cargo.id_cargo_area = cargo_area.id
    LEFT JOIN cargo_grande_area ON cargo_area.id_cargo_grande_area  = cargo_grande_area.id
    WHERE  1=1 
    """

    if localidade != "Todas":
        query += f"and vaga.localidade = '{localidade}' "
    
    if cargo != "Todos":
        query += f"and vaga.cargo = '{cargo}' "
        
    if grande_area != "Todas":
        query += f"and cargo_grande_area.descricao = '{grande_area}' "
    
    df = pd.read_sql_query(query, conn)
    return df
   

def consultar_cidades():
    query = """
    SELECT DISTINCT localidade FROM vaga
    ORDER BY localidade DESC
    """
    df = pd.read_sql_query(query, conn)
    return df['localidade'].tolist()


def consultar_cargos():

    query = """
    SELECT DISTINCT vaga.cargo AS descricao FROM vaga
    WHERE vaga.cargo IS NOT NULL
    """
    query += " ORDER BY vaga.cargo"
    
    df = pd.read_sql_query(query, conn)
    return df['descricao'].tolist()


st.set_page_config(page_title="Dashboard Panorama de Vagas", page_icon="📊", layout="wide")


adjust_top_pad = """
    <style>
        div.block-container {padding-top:1rem;}
        .st-emotion-cache-10oheav {padding:1rem;}
        div[data-baseweb="select"] {
            margin-top: -10px !important;
        }
    </style>
    """
st.markdown(adjust_top_pad, unsafe_allow_html=True)


st.sidebar.image('logo2.png', use_column_width=True)

cidades = consultar_cidades()
cidades.insert(0, "Todas")
st.sidebar.markdown("## Filtros")
st.sidebar.markdown("Selecione a localidade (cidade):")
localidade = st.sidebar.selectbox("", cidades)
grande_area = 'Todas'


cargos = consultar_cargos()
cargos.insert(0, "Todos")
st.sidebar.markdown("Selecione o cargo:")
cargo = st.sidebar.selectbox("", cargos)


st.sidebar.markdown("---")


if localidade:
    tab1, tab2, tab3, tab4 = st.tabs(["Visão geral", "Hard Skills", "Soft Skills", "Formações"])
    
    with tab1:   
        # Total de vagas
        total_vagas = consultar_quantidade_vagas(localidade, cargo, grande_area);
        total_hard_skills = consultar_quantidade_skills(localidade, cargo, grande_area, "HARD_SKILL");
        total_soft_skills = consultar_quantidade_skills(localidade, cargo, grande_area, "SOFT_SKILL");
        total_formacao = consultar_quantidade_skills(localidade, cargo, grande_area, "FORMAÇÃO");
    
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("Vagas")
            st.success(total_vagas['quantidade'].to_string(index=False))
        
        with col2:
            st.subheader("Hard Skills")
            st.info(total_hard_skills['quantidade'].to_string(index=False))
        
        with col3:
            st.subheader("Soft Skills")
            st.error(total_soft_skills['quantidade'].to_string(index=False))
        
        with col4:
            st.subheader("Formações")
            st.warning(total_formacao['quantidade'].to_string(index=False))
        

        st.subheader("Skills")
        
        col1, col2, col3 = st.columns(3)
    
        with col1:
            
            data_hard = consultar_conhecimento(localidade, 10, None, cargo, grande_area, "HARD_SKILL")
            data_hard = data_hard.sort_values(by='quantidade', ascending=False)
            
            max_desc_length = data_hard['descricao'].apply(len).max()
            
            text = alt.Chart(data_hard).mark_text(
                align='left',
                baseline='middle',
                dx=3  
            ).encode(
                x=alt.X('quantidade:Q'),
                y=alt.Y('descricao:N', sort='-x'),
                text='quantidade:Q'
            )
            
            chart = alt.Chart(data_hard).mark_bar().encode(
                x=alt.X('quantidade:Q', axis=alt.Axis(title='Quantidade')),
                y=alt.Y('descricao:N', sort='-x', axis=alt.Axis(title='Hard Skills')),
                color=alt.value('#66a3ff'),
                tooltip=['quantidade:Q', 'descricao:N']  
            ).properties(
                width=500
            )
            
            combined_chart = (chart + text).properties(title='As 10+ Hard Skills')
            
            st.altair_chart(combined_chart, use_container_width=True)
    
    
    
        with col2:
            data_soft = consultar_conhecimento(localidade, 10, None, cargo, grande_area, "SOFT_SKILL")
            data_soft = data_soft.sort_values(by='quantidade', ascending=False)
           
            
            max_desc_length = data_soft['descricao'].apply(len).max()
            
            text = alt.Chart(data_soft).mark_text(
                align='left',
                baseline='middle',
                dx=3  
            ).encode(
                x=alt.X('quantidade:Q'),
                y=alt.Y('descricao:N', sort='-x'),
                text='quantidade:Q'
            )
            
            chart = alt.Chart(data_soft).mark_bar().encode(
                x=alt.X('quantidade:Q', axis=alt.Axis(title='Quantidade')),
                y=alt.Y('descricao:N', sort='-x', axis=alt.Axis(title='Soft Skills')),
                color=alt.value('#ff4d4d'),
                tooltip=['quantidade:Q', 'descricao:N']  
            ).properties(
                width=500
            )
            
            combined_chart = (chart + text).properties(title='As 10+ Soft Skills')
            
            st.altair_chart(combined_chart, use_container_width=True)
        
        with col3:
            data_form =  consultar_conhecimento(localidade, 10, None, cargo, grande_area, "FORMAÇÃO")
            data_form = data_form.sort_values(by='quantidade', ascending=False)
             
            max_desc_length = data_form['descricao'].apply(len).max()
            
            text = alt.Chart(data_form).mark_text(
                align='left',
                baseline='middle',
                dx=3  
            ).encode(
                x=alt.X('quantidade:Q'),
                y=alt.Y('descricao:N', sort='-x'),
                text='quantidade:Q'
            )
            
            chart = alt.Chart(data_form).mark_bar().encode(
                x=alt.X('quantidade:Q', axis=alt.Axis(title='Quantidade')),
                y=alt.Y('descricao:N', sort='-x', axis=alt.Axis(title='Formações')),
                color=alt.value('#ff751a'),
                tooltip=['quantidade:Q', 'descricao:N']  
            ).properties(
                width=500
            )
            
            combined_chart = (chart + text).properties(title='As 10+ Formações')
            
            st.altair_chart(combined_chart, use_container_width=True)

    
    with tab2:
        total_vagas = consultar_quantidade_vagas(localidade, cargo, grande_area);
        total_hard_skills = consultar_quantidade_skills(localidade, cargo, grande_area, "HARD_SKILL");

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total de Vagas")
            st.success(total_vagas['quantidade'].to_string(index=False))
        
        with col2:
            st.subheader("Total de Hard Skills")
            st.info(total_hard_skills['quantidade'].to_string(index=False))
        
        st.subheader('Visão geral')
        #st.text('Hello world!')
        
        data_hard = consultar_conhecimento(localidade, 100, None, cargo, grande_area, "HARD_SKILL")
        data_hard = data_hard.sort_values(by='quantidade', ascending=False)
        
        chart = alt.Chart(data_hard).mark_bar().encode(
            x=alt.X('descricao:N', sort='-y'),
            y=alt.Y('quantidade:Q')
        ).properties(
            width=1000
        )
            
    
        st.write('As 100 Hard Skills Mais Utilizadas')
        # Incorporar o gráfico no aplicativo Streamlit
        st.altair_chart(chart, use_container_width=True)

        
    with tab3:
        # Total de vagas
        total_vagas = consultar_quantidade_vagas(localidade, cargo, grande_area);
        total_soft_skills = consultar_quantidade_skills(localidade, cargo, grande_area, "SOFT_SKILL");
    
        # Layout em três colunas
        col1, col2 = st.columns(2)
        
        # Card para o total de vagas
        with col1:
            st.subheader("Total de Vagas")
            st.success(total_vagas['quantidade'].to_string(index=False))
        
        # Card para o total de soft skills
        with col2:
            st.subheader("Total de Soft Skills")
            st.error(total_soft_skills['quantidade'].to_string(index=False))

        st.subheader('Visão geral')
        #st.text('Hello world!')
        
        data_hard = consultar_conhecimento(localidade, 50, None, cargo, grande_area, "SOFT_SKILL")
        
        data_hard = data_hard.sort_values(by='quantidade', ascending=False)
        # Criar um gráfico Altair
        chart = alt.Chart(data_hard).mark_bar().encode(
            x=alt.X('descricao:N', sort='-y'),
            y=alt.Y('quantidade:Q'),
            color=alt.value('red')
        ).properties(
            width=1000
        )
            
    
        st.write('As 100 Soft Skills Mais Utilizadas')
        # Incorporar o gráfico no aplicativo Streamlit
        st.altair_chart(chart, use_container_width=True)

        
    with tab4:
        # Total de vagas
        total_vagas = consultar_quantidade_vagas(localidade, cargo, grande_area);
        total_soft_skills = consultar_quantidade_skills(localidade, cargo, grande_area, "FORMAÇÃO");
    
        # Layout em três colunas
        col1, col2 = st.columns(2)
        
        # Card para o total de vagas
        with col1:
            st.subheader("Total de Vagas")
            st.success(total_vagas['quantidade'].to_string(index=False))
        
        # Card para o total de soft skills
        with col2:
            st.subheader("Total de Formações")
            st.warning(total_soft_skills['quantidade'].to_string(index=False))

        st.subheader('Visão geral')
        #st.text('Hello world!')
        
        data_hard = consultar_conhecimento(localidade, 100, None, cargo, grande_area, "FORMAÇÃO")
        
        data_hard = data_hard.sort_values(by='quantidade', ascending=False)
        # Criar um gráfico Altair
        chart = alt.Chart(data_hard).mark_bar().encode(
            x=alt.X('descricao:N', sort='-y'),
            y=alt.Y('quantidade:Q'),
            color=alt.value('#ff751a')
        ).properties(
            width=1000
        )
            
    
        st.write('As 100 Formações Mais Requisitadas')
        # Incorporar o gráfico no aplicativo Streamlit
        st.altair_chart(chart, use_container_width=True)
            
                           
   
conn.close()
