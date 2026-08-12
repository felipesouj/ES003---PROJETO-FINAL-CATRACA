"""
testes.py
---------
Script simples de testes automatizados da API da catraca.

Como usar:
1. Em um terminal, rode a API:      python3 app.py
2. Em outro terminal, rode:         python3 testes.py

Cada teste imprime o resultado esperado e o resultado obtido.
Não usa nenhuma biblioteca externa além de `urllib` (já vem com o Python),
para não depender de instalar bibliotecas extras só para testar.
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"

total_testes = 0
total_ok = 0


def chamar(metodo, caminho, corpo=None):
    """Faz uma requisição HTTP simples e devolve (status_code, json_resposta)."""
    url = BASE_URL + caminho
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None

    requisicao = urllib.request.Request(url, data=dados, method=metodo)
    requisicao.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(requisicao) as resposta:
            status = resposta.status
            corpo_resposta = json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        status = erro.code
        try:
            corpo_resposta = json.loads(erro.read().decode("utf-8"))
        except Exception:
            corpo_resposta = None

    return status, corpo_resposta


def chamar_json_invalido(caminho):
    """Envia um corpo que não é JSON válido, para testar tratamento de erro."""
    url = BASE_URL + caminho
    requisicao = urllib.request.Request(
        url, data=b"isso nao e um json", method="POST"
    )
    requisicao.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(requisicao) as resposta:
            return resposta.status, json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        try:
            return erro.code, json.loads(erro.read().decode("utf-8"))
        except Exception:
            return erro.code, None


def testar(nome, status_obtido, status_esperado, corpo_obtido=None):
    global total_testes, total_ok
    total_testes += 1
    ok = status_obtido == status_esperado
    if ok:
        total_ok += 1
    resultado = "OK" if ok else "FALHOU"
    print(f"[{resultado}] {nome} -> esperado HTTP {status_esperado}, obtido HTTP {status_obtido}")
    if corpo_obtido is not None:
        print(f"        resposta: {corpo_obtido}")


print("Iniciando testes da API da catraca...\n")
print("IMPORTANTE: rode este script com o banco.db recém-criado (apague-o antes,")
print("se quiser reproduzir exatamente os mesmos resultados a cada execução).\n")

# TESTE 1: GET /
status, corpo = chamar("GET", "/")
testar("TESTE 1 - GET /", status, 200, corpo)

# TESTE 2: POST /usuarios
status, corpo = chamar("POST", "/usuarios", {"nome": "João da Silva", "cpf": "12345678900"})
testar("TESTE 2 - Cadastrar usuário", status, 201, corpo)

# TESTE 3: GET /usuarios
status, corpo = chamar("GET", "/usuarios")
testar("TESTE 3 - Listar usuários", status, 200, corpo)

# TESTE 4: GET /usuarios/<cpf>
status, corpo = chamar("GET", "/usuarios/12345678900")
testar("TESTE 4 - Buscar usuário por CPF", status, 200, corpo)

# TESTE 5: GET /catraca/<cpf> (deve autorizar)
status, corpo = chamar("GET", "/catraca/12345678900")
testar("TESTE 5 - Acesso autorizado", status, 200, corpo)

# TESTE 6: PUT /usuarios/<cpf> (desativar)
status, corpo = chamar("PUT", "/usuarios/12345678900", {"ativo": False})
testar("TESTE 6 - Desativar usuário", status, 200, corpo)

# TESTE 7: GET /catraca/<cpf> (deve negar - inativo)
status, corpo = chamar("GET", "/catraca/12345678900")
testar("TESTE 7 - Acesso negado (usuário inativo)", status, 403, corpo)

# TESTE 8: GET /acessos
status, corpo = chamar("GET", "/acessos")
testar("TESTE 8 - Histórico de acessos", status, 200, corpo)

# TESTE 9: GET /catraca/<cpf inexistente>
status, corpo = chamar("GET", "/catraca/99999999999")
testar("TESTE 9 - Usuário inexistente na catraca", status, 404, corpo)

# Testes extras de validação
status, corpo = chamar("POST", "/usuarios", {"nome": "Outro", "cpf": "12345678900"})
testar("EXTRA - CPF duplicado", status, 400, corpo)

status, corpo = chamar_json_invalido("/usuarios")
testar("EXTRA - JSON inválido", status, 400, corpo)

status, corpo = chamar("POST", "/usuarios", {"cpf": "11122233344"})
testar("EXTRA - Nome ausente", status, 400, corpo)

status, corpo = chamar("POST", "/usuarios", {"nome": "Sem CPF"})
testar("EXTRA - CPF ausente", status, 400, corpo)

status, corpo = chamar("GET", "/usuarios/00000000000")
testar("EXTRA - Usuário inexistente (busca)", status, 404, corpo)

status, corpo = chamar("PUT", "/usuarios/00000000000", {"nome": "Não existe"})
testar("EXTRA - Atualizar usuário inexistente", status, 404, corpo)

print(f"\nResultado final: {total_ok}/{total_testes} testes passaram.")
