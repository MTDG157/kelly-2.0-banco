import os
import streamlit as st
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

#São as configurações iniciais, troca o icone da página e carrega a chave que está no env
st.set_page_config(page_title="Cadastro de Alunos", page_icon="🤓")
load_dotenv()
CAMINHO_CREDENCIAL = os.getenv("FIREBASE_CREDENTIALS_PATH")

@st.cache_resource #recurso que mantém as informações de conexao banco enquanto o programa roda
def conectar_firebase(caminho_credencial: str):#conecta no banco usando a chave carregada
    """Inicializa o Firebase uma única vez e retorna o cliente Firestore,
    o que fizemos no python, a função if not mata o problema de tentar conectar algo já conectado"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(caminho_credencial)
        firebase_admin.initialize_app(cred)
    return firestore.client()
#caso ele não ache a chave
if not CAMINHO_CREDENCIAL:
    st.error("Erro: Variável FIREBASE_CREDENTIALS_PATH não configurada no arquivo .env.")
    st.stop()
#trata o erro caso ele não consiga conectar
try:
    db = conectar_firebase(CAMINHO_CREDENCIAL)
except Exception as e:
    st.error(f"Erro ao conectar com o Firebase: {e}\nConfira o caminho no arquivo .env.")
    st.stop()

#a parte do frontend

st.title("🎓 Cadastro de Alunos")
st.caption("Conectado ao Firestore do Firebase")

aba_cadastro, aba_lista = st.tabs(["➕ Cadastrar", "📋 Alunos cadastrados"])

# ABA CADASTRO
with aba_cadastro:
    with st.form("form_aluno", clear_on_submit=True):
        nome = st.text_input("Nome do aluno")
        idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
        
        if st.form_submit_button("Cadastrar"):
            if nome.strip():
                db.collection("alunos").add({"nome": nome.strip(), "idade": int(idade)})
                st.success(f"Aluno '{nome}' cadastrado com sucesso!")
            else:
                st.warning("Informe o nome do aluno.")

# ABA LISTA
with aba_lista:
    if st.button("🔄 Atualizar lista"):
        st.rerun()

    # Busca os alunos direto em uma lista dentro do firebase e formata certinho em um dicionario python;
    alunos = [{"id": doc.id, **doc.to_dict()} for doc in db.collection("alunos").stream()]

    if not alunos:
        st.info("Nenhum aluno cadastrado ainda.")
    
    for aluno in alunos:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{aluno.get('nome', '—')}**")
        col2.write(f"{aluno.get('idade', '—')} anos")
        # Usa o ID do banco como chave única para o botão
        if col3.button("🗑️", key=aluno["id"]):
            db.collection("alunos").document(aluno["id"]).delete()
            st.rerun()