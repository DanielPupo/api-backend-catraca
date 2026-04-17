from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
from auth import token_obrigatorio, gerar_token
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from flasgger import Swagger
import re

load_dotenv()

app = Flask(__name__)

# Configuração do Swagger/OpenAPI
app.config['SWAGGER'] = {'openapi': '3.0.0'}
swagger = Swagger(app, template_file='openapi.yaml')

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app, origins="*")

ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

# Inicialização do Firebase (Local ou Vercel)
if os.getenv("VERCEL"):
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
else:
    caminho_firebase = os.path.join(os.path.dirname(__file__), "firebase.json")
    cred = credentials.Certificate(caminho_firebase)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Rota de boas-vindas
@app.route("/", methods=['GET'])
def root(): 
    return jsonify({
        "api": "sistema_academia",
        "version": "1.0",
        "Authors": "Daniel Pupo e João Guilherme"
    }), 200

# Rota de login para obter o Token
@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Envie os dados para login"}), 400
    
    usuario = dados.get("usuario")
    senha = dados.get("senha")
    
    if usuario == ADM_USUARIO and senha == ADM_SENHA:
        token = gerar_token(usuario)
        return jsonify({"message": "Login realizado!", "token": token}), 200
    
    # Adicione este retorno caso o IF acima falhe:
    return jsonify({"error": "Usuário ou senha inválidos"}), 401

# ========================================================================================================
# ROTA PÚBLICA (USADA PELA CATRACA)
# ========================================================================================================

@app.route("/catraca", methods=['POST'])
def verificar_catraca():
    dados = request.get_json()
    if not dados or "cpf" not in dados:
        return jsonify({"error": "CPF não enviado"}), 400

    cpf = str(dados.get("cpf"))
    try:
        docs = db.collection("cadastros").where("cpf", "==", cpf).limit(1).get()
        if not docs:
            return jsonify({"mensagem": "Aluno não encontrado"}), 404

        aluno = docs[0].to_dict()
        
        # Lógica de bloqueio conforme a imagem
        if aluno.get("status") == False:
            return jsonify({
                "status": "BLOQUEADO"
            }), 200 # Retornamos 200 pois a consulta em si deu certo

        return jsonify({
            "status": "LIBERADO",
            "nome": aluno.get("nome")
        }), 200
    except Exception as e:
        return jsonify({"error": "Erro ao consultar catraca"}), 500

# ========================================================================================================
# ROTAS PRIVADAS (ADMINISTRAÇÃO DE ALUNOS)
# ========================================================================================================

@app.route("/alunos", methods=['GET'])
@token_obrigatorio
def listar_alunos():
    alunos = []
    lista = db.collection('cadastros').stream()
    for item in lista:
        aluno = item.to_dict()
        aluno['doc_id'] = item.id
        alunos.append(aluno)
    return jsonify(alunos), 200

@app.route("/alunos", methods=['POST'])
@token_obrigatorio
def criar_aluno():
    dados = request.get_json()
    if not dados or "cpf" not in dados or "nome" not in dados:
        return jsonify({"error": "Dados incompletos!"}), 400
    
    # Remover caracteres do cadastro dos alunos
    cpf_limpo = re.sub(r'\D', '', str(dados["cpf"]))

    # 2. Validar o cpf com 11 dígitos
    if len(cpf_limpo) != 11:
        return jsonify({"error": "O CPF deve conter exatamente 11 dígitos numéricos!"}), 400

    try:
        # 3. Verificar se já há um CPF igual
        existente = db.collection("cadastros").where("cpf", "==", cpf_limpo).limit(1).get()
        
        if existente:
            return jsonify({"error": "Este CPF já está cadastrado!"}), 409

        # Lógica do Contador de ID
        contador_ref = db.collection("contador").document("controle_id")
        contador_doc = contador_ref.get()
        ultimo_id = contador_doc.to_dict().get("ultimo_id")
        novo_id = ultimo_id + 1
        contador_ref.update({"ultimo_id": novo_id})

        db.collection("cadastros").add({
            "id": novo_id,
            "cpf": cpf_limpo, # Salva apenas os números
            "nome": dados["nome"],
            "status": dados.get("status", True)
        })
        return jsonify({"message": "Aluno cadastrado!", "id": novo_id}), 201
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar aluno!"}), 500

@app.route("/alunos/<int:id>", methods=['PUT'])
@token_obrigatorio
def editar_aluno(id):
    dados = request.get_json()
    try:
        docs = db.collection("cadastros").where("id", "==", id).limit(1).get()
        if not docs:
            return jsonify({"error": "Aluno não encontrado!"}), 404
        
        doc_ref = db.collection("cadastros").document(docs[0].id)
        doc_ref.update(dados)
        return jsonify({"message": "Aluno atualizado!"}), 200
    except:
        return jsonify({"error": "Falha na atualização!"}), 500

@app.route("/alunos/<int:id>", methods=['DELETE'])
@token_obrigatorio
def excluir_aluno(id):
    try:
        docs = db.collection("cadastros").where("id", "==", id).limit(1).get()
        if not docs:
            return jsonify({"error": "Aluno não encontrado!"}), 404
        
        db.collection("cadastros").document(docs[0].id).delete()
        return jsonify({"message": "Aluno removido!"}), 200
    except:
        return jsonify({"error": "Falha ao excluir!"}), 500

# ========================================================================================================
# TRATAMENTO DE ERROS
# ========================================================================================================

@app.errorhandler(404)
def erro404(error):
    return jsonify({"error": "URL não encontrada"}), 404

@app.errorhandler(500)
def erro500(error):
    return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)