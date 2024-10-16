from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime, timedelta
import os
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb+srv://admin:admin@progeficaz.weaoq.mongodb.net/aps3")  # Substitua pela sua URI do MongoDB
mongo = PyMongo(app)
# Rota para listar usuários
@app.route('/usuarios', methods=['GET'])
def lista_usuarios():
    usuarios = list(mongo.db.usuarios.find({}, {"_id": 0}))
    return jsonify(usuarios), 200
    
# Rota para cadastrar usuários
@app.route('/usuarios', methods=['POST'])
def cadastra_usuario():
    data = request.json
    if ("nome" or "cpf" or "data_nascimento") not in data:
        return jsonify({"erro": "Nome e CPF são obrigatórios"}), 400
    
    result = mongo.db.usuarios.insert_one(data)
    return jsonify({"id": str(result.inserted_id)}), 201
# Rota para buscar usuário
@app.route('/usuarios/<string:id_usuario>', methods=['GET'])
def busca_usuario(id_usuario):
    usuario = mongo.db.usuarios.find_one({"_id": ObjectId(id_usuario)}, {"_id": 0})
    if usuario:
        return jsonify(usuario), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    
# Rota para atualizar usuário
@app.route('/usuarios/<string:id_usuario>', methods=['PUT'])
def atualiza_usuario(id_usuario):
    data = request.json
    result = mongo.db.usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404
# Rota para deletar usuário
@app.route('/usuarios/<string:id_usuario>', methods=['DELETE'])
def deleta_usuario(id_usuario):
    result = mongo.db.usuarios.delete_one({"_id": ObjectId(id_usuario)})
    if result.deleted_count > 0:
        return jsonify({"mensagem": "Usuário deletado com sucesso"}), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404
# Rota para listar bicicletas
@app.route('/bikes', methods=['GET'])
def lista_bikes():
    bicicletas = list(mongo.db.bicicletas.find({}, {"_id": 0}))
    return jsonify(bicicletas), 200
# Rota para cadastrar bicicletas
@app.route('/bikes', methods=['POST'])
def cadastra_bike():
    data = request.json
    if "marca" not in data or "modelo" not in data or "cidade" not in data:
        return jsonify({"erro": "Marca, modelo e cidade são obrigatórios!"}), 400
    
    data["status"] = "disponível"
    result = mongo.db.bicicletas.insert_one(data)
    return jsonify({"id": str(result.inserted_id)}), 201
# Rota para buscar bicicleta
@app.route('/bikes/<string:id_bike>', methods=['GET'])
def busca_bike(id_bike):
    bicicleta = mongo.db.bicicletas.find_one({"_id": ObjectId(id_bike)}, {"_id": 0})
    if bicicleta:
        return jsonify(bicicleta), 200
    else:
        return jsonify({"erro": "Bicicleta não encontrada"}), 404
# Rota para atualizar bicicleta
@app.route('/bikes/<string:id_bike>', methods=['PUT'])
def atualiza_bike(id_bike):
    data = request.json
    result = mongo.db.bicicletas.update_one({"_id": ObjectId(id_bike)}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"mensagem": "Bicicleta atualizada com sucesso"}), 200
    else:
        return jsonify({"erro": "Bicicleta não encontrada"}), 404
# Rota para deletar bicicleta
@app.route('/bikes/<string:id_bike>', methods=['DELETE'])
def deleta_bike(id_bike):
    result = mongo.db.bicicletas.delete_one({"_id": ObjectId(id_bike)})
    if result.deleted_count > 0:
        return jsonify({"mensagem": "Bicicleta deletada com sucesso"}), 200
    else:
        return jsonify({"erro": "Bicicleta não encontrada"}), 404
# Rota para cadastrar empréstimos
@app.route('/emprestimos/usuarios/<id_usuario>/bikes/<id_bike>', methods=['POST'])
def cadastra_emprestimo(id_usuario, id_bike):
    bicicleta = mongo.db.bicicletas.find_one({"_id": ObjectId(id_bike)})
    if not bicicleta:
        return jsonify({"erro": "Bicicleta não encontrada"}), 404
    if bicicleta.get("status") != "disponível":
        return jsonify({"erro": "Bicicleta não está disponível"}), 400
    emprestimo_existente = mongo.db.emprestimos.find_one({
        "bicicleta_id": id_bike,
        "data_devolucao": None
    })
    if emprestimo_existente:
        return jsonify({"erro": "Bicicleta já está alugada"}), 400
    novo_emprestimo = {
        "usuario_id": id_usuario,
        "bicicleta_id": id_bike,
        "data_aluguel": datetime.now(),
        "data_devolucao": datetime.now() + timedelta(days=15)
    }
    result = mongo.db.emprestimos.insert_one(novo_emprestimo)
    mongo.db.bicicletas.update_one(
        {"_id": ObjectId(id_bike)},
        {"$set": {"status": "indisponível"}}
    )
    return jsonify({"id": str(result.inserted_id)}), 201
# Rota para listar empréstimos
@app.route('/emprestimos', methods=['GET'])
def listar_emprestimos():
    usuario_id = request.args.get('usuario_id')
    bicicleta_id = request.args.get('bicicleta_id')
    filtro = {}
    if usuario_id:
        filtro["usuario_id"] = usuario_id
    if bicicleta_id:
        filtro["bicicleta_id"] = bicicleta_id
    emprestimos = list(mongo.db.emprestimos.find(filtro))
    
    resposta = []
    for emprestimo in emprestimos:
        emprestimo["_id"] = str(emprestimo["_id"])
        resposta.append(emprestimo)
    return jsonify(emprestimos=resposta), 200
# Rota para deletar empréstimos
@app.route('/emprestimos/<string:id>', methods=['DELETE'])
def deleta_emprestimo(id):
    emprestimo = mongo.db.emprestimos.find_one({"_id": ObjectId(id)})
    if not emprestimo:
        return jsonify({"erro": "Empréstimo não encontrado"}), 404
    result = mongo.db.emprestimos.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        mongo.db.bicicletas.update_one(
            {"_id": ObjectId(emprestimo["bicicleta_id"])},
            {"$set": {"status": "disponível"}}
        )
        return jsonify({"mensagem": "Empréstimo deletado com sucesso e bicicleta está disponível"}), 200
    else:
        return jsonify({"erro": "Empréstimo não encontrado"}), 404
if __name__ == '__main__':
    app.run(debug=True)