
from flask import Flask, request, jsonify
import json
import os

catraca = Flask(__name__)

ARQUIVO = "usuarios.json"


def carregar_usuarios():
    if not os.path.exists(ARQUIVO):
        return []

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_usuarios(usuarios):
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, indent=4, ensure_ascii=False)


@catraca.route("/")
def inicio():
    return jsonify({
        "mensagem": "Minha API da catraca está funcionando"
    })


@catraca.route("/usuarios", methods=["POST"])
def cadastrar_usuario():
    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "JSON inválido ou incompleto"
        }), 400

    nome = dados.get("nome")
    cpf = dados.get("cpf")

    if not nome or not cpf:
        return jsonify({
            "erro": "Nesse sistema Nome e CPF são obrigatórios."
        }), 400

    usuarios = carregar_usuarios()

    for usuario in usuarios:
        if usuario["cpf"] == cpf:
            return jsonify({
                "erro": "CPF já está cadastrado"
            }), 400

    novo_usuario = {
        "id": len(usuarios) + 1,
        "nome": nome,
        "cpf": cpf,
        "ativo": True
    }

    usuarios.append(novo_usuario)
    salvar_usuarios(usuarios)

    return jsonify({
        "mensagem": "Usuário cadastrado com sucesso!",
        "usuario": novo_usuario
    }), 201


@catraca.route("/usuarios", methods=["GET"])
def listar():

    usuarios = carregar_usuarios()

    return jsonify(usuarios)


@catraca.route("/usuarios/<cpf>", methods=["GET"])
def buscar(cpf):

    usuarios = carregar_usuarios()

    for usuario in usuarios:
        if usuario["cpf"] == cpf:
            return jsonify(usuario)

    return jsonify({
        "erro": "Usuário não encontrado"
    }), 404


@catraca.route("/usuarios/<cpf>", methods=["PUT"])
def atualizar(cpf):

    usuarios = carregar_usuarios()

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "JSON inválido"
        }), 400

    for usuario in usuarios:

        if usuario["cpf"] == cpf:

            usuario["nome"] = dados.get(
                "nome",
                usuario["nome"]
            )

            usuario["ativo"] = dados.get(
                "ativo",
                usuario["ativo"]
            )

            salvar_usuarios(usuarios)

            return jsonify({
                "mensagem": "Seu usuário foi atualizado com sucesso!",
                "usuario": usuario
            })

    return jsonify({
        "erro": "Usuário não identificado/encontrado"
    }), 404


if __name__ == "__main__":
    catraca.run(debug=True)

