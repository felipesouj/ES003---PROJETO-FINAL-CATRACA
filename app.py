"""
app.py
------
API Flask do projeto CATRACA ELETRÔNICA.

Responsável apenas pelas rotas (endpoints) da aplicação. Toda a
parte de leitura/escrita do arquivo banco.json fica em database.py,
para manter o código organizado.

Fluxo geral do sistema:

CATRACA/CLIENTE -> API Flask -> Arquivo banco.json
    -> Consulta CPF -> Verifica usuário -> Verifica campo "ativo"
    -> ACESSO AUTORIZADO ou ACESSO NEGADO -> Registra a tentativa
"""

from flask import Flask, request, jsonify

import database

catraca = Flask(__name__)

# Cria o arquivo banco.json (se ainda não existir) assim que a
# aplicação é carregada. Assim, na primeira execução, o arquivo
# já é gerado automaticamente.
database.inicializar_banco()


@catraca.route("/")
def inicio():
    """Endpoint simples para verificar se a API está no ar."""
    return jsonify({
        "mensagem": "Minha API da catraca está funcionando"
    })


@catraca.route("/usuarios", methods=["POST"])
def cadastrar_usuario():
    """
    Cadastra um novo usuário no banco.json.

    Espera um JSON com "nome" e "cpf". O usuário é sempre criado
    com ativo = True. O CPF precisa ser único, então verificamos
    antes de criar para devolver uma mensagem de erro amigável.
    """
    dados_recebidos = request.get_json(silent=True)

    if not dados_recebidos:
        return jsonify({
            "erro": "JSON inválido ou incompleto"
        }), 400

    nome = dados_recebidos.get("nome")
    cpf = dados_recebidos.get("cpf")

    if not nome or not cpf:
        return jsonify({
            "erro": "Nesse sistema Nome e CPF são obrigatórios."
        }), 400

    dados = database.carregar_banco()

    usuario_existente = database.buscar_usuario_por_cpf(dados, cpf)

    if usuario_existente:
        return jsonify({
            "erro": "CPF já está cadastrado"
        }), 400

    novo_usuario = database.criar_usuario(dados, nome, cpf)
    database.salvar_banco(dados)

    resultado = database.linha_para_dicionario_usuario(novo_usuario)

    return jsonify({
        "mensagem": "Usuário cadastrado com sucesso!",
        "usuario": resultado
    }), 201


@catraca.route("/usuarios", methods=["GET"])
def listar():
    """Lista todos os usuários cadastrados, lendo o banco.json."""
    dados = database.carregar_banco()

    usuarios_ordenados = sorted(dados["usuarios"], key=lambda usuario: usuario["id"])
    usuarios = [database.linha_para_dicionario_usuario(usuario) for usuario in usuarios_ordenados]

    return jsonify(usuarios)


@catraca.route("/usuarios/<cpf>", methods=["GET"])
def buscar(cpf):
    """Busca um usuário específico pelo CPF."""
    dados = database.carregar_banco()

    usuario = database.buscar_usuario_por_cpf(dados, cpf)

    if usuario:
        return jsonify(database.linha_para_dicionario_usuario(usuario))

    return jsonify({
        "erro": "Usuário não encontrado"
    }), 404


@catraca.route("/usuarios/<cpf>", methods=["PUT"])
def atualizar(cpf):
    """
    Atualiza nome e/ou status ativo de um usuário, identificado
    pelo CPF. O CPF em si não pode ser alterado por este endpoint.
    """
    dados_recebidos = request.get_json(silent=True)

    if not dados_recebidos:
        return jsonify({
            "erro": "JSON inválido"
        }), 400

    dados = database.carregar_banco()

    usuario = database.buscar_usuario_por_cpf(dados, cpf)

    if not usuario:
        return jsonify({
            "erro": "Usuário não identificado/encontrado"
        }), 404

    novo_nome = dados_recebidos.get("nome", usuario["nome"])
    novo_ativo = dados_recebidos.get("ativo", bool(usuario["ativo"]))

    database.atualizar_usuario(usuario, novo_nome, novo_ativo)
    database.salvar_banco(dados)

    resultado = database.linha_para_dicionario_usuario(usuario)

    return jsonify({
        "mensagem": "Seu usuário foi atualizado com sucesso!",
        "usuario": resultado
    })


@catraca.route("/catraca/<cpf>", methods=["GET"])
def verificar_acesso(cpf):
    """
    Endpoint principal da catraca: decide se o acesso é autorizado
    ou negado para o CPF informado, e registra a tentativa no
    histórico (lista registros_acesso).

    Usamos GET /catraca/<cpf> (em vez de POST /catraca) porque essa
    operação é, do ponto de vista HTTP, uma CONSULTA (não estamos
    criando nem alterando um recurso do lado do cliente) e o CPF é
    o único dado necessário. Isso deixa a chamada simples de ser
    feita por qualquer dispositivo de catraca (só precisa montar a
    URL), sem precisar enviar corpo JSON.

    Regras:
    - CPF não encontrado  -> acesso negado, HTTP 404, registra a
      tentativa com usuario_id = None.
    - Usuário encontrado e ativo = True  -> acesso autorizado,
      HTTP 200, registra a tentativa com autorizado = True.
    - Usuário encontrado e ativo = False -> acesso negado,
      HTTP 403 (Forbidden: usuário existe mas não tem permissão),
      registra a tentativa com autorizado = False.
    """
    dados = database.carregar_banco()

    usuario = database.buscar_usuario_por_cpf(dados, cpf)

    if not usuario:
        database.registrar_tentativa_acesso(
            dados, usuario_id=None, cpf_informado=cpf, autorizado=False
        )
        database.salvar_banco(dados)

        return jsonify({
            "acesso": False,
            "mensagem": "Usuário não encontrado"
        }), 404

    ativo = bool(usuario["ativo"])

    database.registrar_tentativa_acesso(
        dados, usuario_id=usuario["id"], cpf_informado=cpf, autorizado=ativo
    )
    database.salvar_banco(dados)

    if ativo:
        return jsonify({
            "acesso": True,
            "mensagem": "Acesso autorizado",
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "cpf": usuario["cpf"],
            }
        }), 200

    return jsonify({
        "acesso": False,
        "mensagem": "Acesso negado"
    }), 403


@catraca.route("/acessos", methods=["GET"])
def historico_acessos():
    """
    Retorna o histórico de tentativas de acesso, cruzando a lista
    registros_acesso com usuarios (equivalente a um LEFT JOIN) para
    trazer nome sempre que possível.

    Tentativas com CPF desconhecido não têm um usuário
    correspondente (usuario_id = None), mas ainda assim aparecem no
    histórico.
    """
    dados = database.carregar_banco()

    # Mapa id -> usuario para achar o nome rapidamente (equivalente
    # ao JOIN que era feito em SQL).
    usuarios_por_id = {usuario["id"]: usuario for usuario in dados["usuarios"]}

    registros_ordenados = sorted(
        dados["registros_acesso"], key=lambda registro: registro["id"], reverse=True
    )

    acessos = []
    for registro in registros_ordenados:
        usuario = usuarios_por_id.get(registro["usuario_id"])
        acessos.append({
            "id": registro["id"],
            "nome": usuario["nome"] if usuario else None,
            "cpf": registro["cpf_informado"],
            "data_hora": registro["data_hora"],
            "autorizado": bool(registro["autorizado"]),
        })

    return jsonify({"acessos": acessos})


if __name__ == "__main__":
    catraca.run(debug=True, use_reloader=False)
