"""
database.py
------------
Responsável por tudo relacionado ao armazenamento de dados, que agora
é feito em um arquivo JSON (banco.json) em vez de um banco SQLite.

- Carregar os dados do arquivo banco.json
- Criar o arquivo (se não existir)
- Salvar os dados de volta no arquivo
- Funções auxiliares de consulta/gravação usadas pelo app.py

Este arquivo NÃO contém lógica de rotas Flask. Ele só cuida dos dados.
"""

import json
import os
from datetime import datetime

# Nome do arquivo físico dos dados. Ele será criado na mesma pasta
# onde o app.py é executado, caso ainda não exista.
NOME_BANCO = "banco.json"


def _banco_padrao():
    """Estrutura inicial (vazia) do banco em JSON."""
    return {
        "usuarios": [],
        "registros_acesso": [],
    }


def carregar_banco():
    """
    Lê o arquivo banco.json e devolve o conteúdo como dicionário
    Python. Se o arquivo não existir ou estiver corrompido/vazio,
    devolve a estrutura padrão (vazia).
    """
    if not os.path.exists(NOME_BANCO):
        return _banco_padrao()

    with open(NOME_BANCO, "r", encoding="utf-8") as arquivo:
        try:
            dados = json.load(arquivo)
        except json.JSONDecodeError:
            dados = _banco_padrao()

    # Garante que as chaves sempre existam, mesmo que o arquivo
    # tenha sido editado manualmente e esteja incompleto.
    dados.setdefault("usuarios", [])
    dados.setdefault("registros_acesso", [])
    return dados


def salvar_banco(dados):
    """Grava o dicionário `dados` de volta no arquivo banco.json."""
    with open(NOME_BANCO, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def inicializar_banco():
    """
    Cria o arquivo banco.json (vazio) caso ele ainda não exista.

    Deve ser chamada uma vez quando a aplicação Flask é iniciada.
    Se o arquivo já existir, não faz nada (não apaga dados).
    """
    if not os.path.exists(NOME_BANCO):
        salvar_banco(_banco_padrao())


def _proximo_id(lista):
    """Calcula o próximo id disponível (maior id atual + 1)."""
    if not lista:
        return 1
    return max(item["id"] for item in lista) + 1


def linha_para_dicionario_usuario(usuario):
    """
    Converte um registro de usuário (dict vindo do JSON) para o
    formato usado nas respostas da API, garantindo que "ativo"
    seja sempre um booleano real (True/False).
    """
    if usuario is None:
        return None

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "cpf": usuario["cpf"],
        "ativo": bool(usuario["ativo"]),
    }


def buscar_usuario_por_cpf(dados, cpf):
    """
    Busca um único usuário pelo CPF dentro da lista `dados["usuarios"]`.
    Retorna o dicionário do usuário encontrado ou None.
    """
    for usuario in dados["usuarios"]:
        if usuario["cpf"] == cpf:
            return usuario
    return None


def criar_usuario(dados, nome, cpf):
    """
    Cria um novo usuário (sempre com ativo = True), adiciona na
    lista `dados["usuarios"]` e devolve o registro criado.

    Não salva no arquivo — quem chama esta função é responsável
    por chamar `salvar_banco(dados)` depois.
    """
    novo_usuario = {
        "id": _proximo_id(dados["usuarios"]),
        "nome": nome,
        "cpf": cpf,
        "ativo": True,
    }
    dados["usuarios"].append(novo_usuario)
    return novo_usuario


def atualizar_usuario(usuario, novo_nome, novo_ativo):
    """
    Atualiza nome e ativo de um usuário (dict) já encontrado dentro
    de `dados["usuarios"]`. Como o dict é uma referência dentro da
    lista, alterar aqui já reflete na estrutura `dados`.
    """
    usuario["nome"] = novo_nome
    usuario["ativo"] = bool(novo_ativo)
    return usuario


def registrar_tentativa_acesso(dados, usuario_id, cpf_informado, autorizado):
    """
    Cria um novo registro na lista `dados["registros_acesso"]`.

    - usuario_id pode ser None quando o CPF não pertence a nenhum
      usuário cadastrado.
    - autorizado deve ser True ou False.
    - data_hora é preenchida automaticamente com o momento atual.

    Não salva no arquivo — quem chama esta função é responsável
    por chamar `salvar_banco(dados)` depois.
    """
    novo_registro = {
        "id": _proximo_id(dados["registros_acesso"]),
        "usuario_id": usuario_id,
        "cpf_informado": cpf_informado,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "autorizado": bool(autorizado),
    }
    dados["registros_acesso"].append(novo_registro)
    return novo_registro
