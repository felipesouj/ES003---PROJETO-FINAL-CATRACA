# Projeto Catraca Eletrônica

## 1. Objetivo

API REST desenvolvida em **Python + Flask** para um sistema de **catraca eletrônica** (projeto acadêmico). A API recebe o CPF de uma pessoa, consulta um arquivo **JSON** (`banco.json`), verifica se o usuário existe e está ativo, e responde se o acesso deve ser **autorizado** ou **negado**. Toda tentativa de acesso (autorizada ou negada) é registrada em um histórico.

## 2. Tecnologias utilizadas

- **Python 3** — linguagem da aplicação.
- **Flask** — micro-framework web usado para criar a API REST.
- **JSON** — os dados são armazenados em um único arquivo de texto (`banco.json`), lido e escrito através do módulo `json`, que já vem embutido no Python. Não é necessário instalar nem configurar nenhum banco de dados.

## 3. Estrutura de pastas

```
projeto-catraca/
│
├── app.py              # Aplicação Flask: rotas/endpoints da API
├── database.py         # Leitura/escrita do banco.json, funções auxiliares
├── banco.json            # Arquivo de dados em JSON (criado automaticamente ao rodar a API)
├── requirements.txt     # Dependências do projeto
├── README.md            # Este arquivo
└── testes.py             # Script de testes automatizados de toda a API
```

## 4. Como instalar o Python

Baixe e instale o Python 3 (versão 3.10 ou superior) em: https://www.python.org/downloads/

Para conferir se já está instalado, abra o terminal e digite:

```
python3 --version
```

## 5. Como criar um ambiente virtual (recomendado)

Um ambiente virtual evita que as dependências do projeto se misturem com outros projetos Python da sua máquina.

Dentro da pasta `projeto-catraca`:

```
python3 -m venv venv
```

Para ativar:

- **Linux/Mac:**
  ```
  source venv/bin/activate
  ```
- **Windows:**
  ```
  venv\Scripts\activate
  ```

## 6. Como instalar as dependências

Com o ambiente virtual ativado (ou não, se preferir instalar globalmente):

```
pip install -r requirements.txt
```

Isso instalará apenas o **Flask** — a leitura/escrita de JSON já faz parte do Python, então não é necessário instalar nenhuma biblioteca separada para isso.

## 7. Como executar a API

Dentro da pasta `projeto-catraca`, rode:

```
python3 app.py
```

Você verá uma saída parecida com:

```
 * Running on http://127.0.0.1:5000
```

A API estará disponível em `http://127.0.0.1:5000`.

Na **primeira execução**, o arquivo `banco.json` é criado automaticamente na mesma pasta, já com as listas `usuarios` e `registros_acesso` vazias. Nas execuções seguintes, o arquivo já existe e simplesmente é reaproveitado (nenhum dado é apagado).

## 8. Como o armazenamento em JSON funciona (resumo)

Em vez de um banco de dados, os dados ficam guardados em texto simples, no formato JSON, dentro do arquivo `banco.json`. Isso o torna ideal para projetos acadêmicos e protótipos: não é preciso instalar, configurar usuário/senha ou manter um serviço de banco rodando — basta ler e escrever no arquivo. Cada requisição que precisa consultar dados lê o arquivo inteiro (`database.carregar_banco()`), e cada requisição que precisa alterar dados salva o arquivo inteiro de volta (`database.salvar_banco()`).

## 9. Como o banco é criado

- O arquivo físico é `banco.json`, criado **na mesma pasta onde `app.py` é executado**.
- A função `database.inicializar_banco()` (em `database.py`) cria o arquivo `banco.json` com a estrutura vazia (`{"usuarios": [], "registros_acesso": []}`), caso ele ainda não exista.
- Essa função é chamada automaticamente assim que `app.py` é carregado (antes mesmo de qualquer requisição chegar), garantindo que o arquivo sempre exista quando a API for usada.

## 10. Estrutura dos dados

O arquivo `banco.json` guarda um único objeto com duas listas:

### Lista `usuarios`

| Campo  | Tipo               | Descrição                          |
|--------|--------------------|-------------------------------------|
| id     | número (inteiro)   | Identificador único do usuário      |
| nome   | texto              | Nome do usuário                     |
| cpf    | texto              | CPF do usuário (não pode repetir)   |
| ativo  | booleano           | Se o usuário pode acessar (true = sim) |

### Lista `registros_acesso`

| Campo         | Tipo                        | Descrição                                                        |
|----------------|-----------------------------|--------------------------------------------------------------------|
| id             | número (inteiro)            | Identificador único do registro                                    |
| usuario_id     | número ou null              | Usuário relacionado à tentativa (null se o CPF não existir)        |
| cpf_informado  | texto                       | CPF exatamente como foi enviado na tentativa de acesso             |
| data_hora      | texto (preenchido sozinho)  | Data/hora da tentativa                                             |
| autorizado     | booleano                    | true = acesso liberado, false = acesso negado                      |

O campo `cpf_informado` existe para que tentativas com CPFs **que não pertencem a nenhum usuário cadastrado** também fiquem registradas no histórico (nesse caso `usuario_id` fica `null`, mas o CPF usado na tentativa não se perde).

Exemplo de como o `banco.json` fica no disco:

```json
{
  "usuarios": [
    {"id": 1, "nome": "João da Silva", "cpf": "12345678900", "ativo": true}
  ],
  "registros_acesso": [
    {"id": 1, "usuario_id": 1, "cpf_informado": "12345678900", "data_hora": "2026-08-12 12:30:00", "autorizado": true}
  ]
}
```

## 11. Endpoints

| Método | Rota                | Descrição                                   |
|--------|----------------------|-----------------------------------------------|
| GET    | `/`                  | Testa se a API está no ar                     |
| POST   | `/usuarios`          | Cadastra um novo usuário                       |
| GET    | `/usuarios`          | Lista todos os usuários                        |
| GET    | `/usuarios/<cpf>`    | Busca um usuário pelo CPF                      |
| PUT    | `/usuarios/<cpf>`    | Atualiza nome e/ou status ativo de um usuário  |
| GET    | `/catraca/<cpf>`     | Verifica se o CPF pode ter acesso liberado     |
| GET    | `/acessos`           | Lista o histórico de tentativas de acesso      |

### Sobre o endpoint da catraca

Optamos por **`GET /catraca/<cpf>`** em vez de `POST /catraca`. A verificação de acesso é, na prática, uma **consulta**: a catraca só precisa informar um CPF e receber uma decisão, sem a necessidade de enviar um corpo JSON. Isso simplifica bastante a implementação do lado do hardware/software da catraca física, que muitas vezes só precisa montar uma URL simples (ex: `GET /catraca/12345678900`), sem lidar com cabeçalhos ou corpo de requisição.

Códigos HTTP usados nesse endpoint:

- **200** — usuário encontrado e ativo → acesso autorizado.
- **403 (Forbidden)** — usuário encontrado, porém inativo → acesso negado (a pessoa existe no sistema, mas não tem permissão no momento).
- **404 (Not Found)** — CPF não encontrado na base → acesso negado (o "recurso" usuário não existe).

## 12. Exemplos de requisições e respostas

### Cadastrar usuário

```
POST /usuarios
Content-Type: application/json

{
    "nome": "João da Silva",
    "cpf": "12345678900"
}
```

Resposta (201):
```json
{
    "mensagem": "Usuário cadastrado com sucesso!",
    "usuario": {
        "id": 1,
        "nome": "João da Silva",
        "cpf": "12345678900",
        "ativo": true
    }
}
```

### Verificar acesso (autorizado)

```
GET /catraca/12345678900
```

Resposta (200):
```json
{
    "acesso": true,
    "mensagem": "Acesso autorizado",
    "usuario": {
        "id": 1,
        "nome": "João da Silva",
        "cpf": "12345678900"
    }
}
```

### Verificar acesso (negado — usuário inativo)

Resposta (403):
```json
{
    "acesso": false,
    "mensagem": "Acesso negado"
}
```

### Verificar acesso (negado — CPF inexistente)

Resposta (404):
```json
{
    "acesso": false,
    "mensagem": "Usuário não encontrado"
}
```

### Histórico de acessos

```
GET /acessos
```

Resposta (200):
```json
{
    "acessos": [
        {
            "id": 1,
            "nome": "João da Silva",
            "cpf": "12345678900",
            "data_hora": "2026-08-12 12:30:00",
            "autorizado": true
        }
    ]
}
```

## 13. Como testar no Postman

1. Abra o Postman e crie uma nova requisição.
2. Escolha o método (GET, POST ou PUT) e digite a URL, por exemplo: `http://127.0.0.1:5000/usuarios`.
3. Para POST/PUT: vá na aba **Body**, escolha **raw** e o tipo **JSON**, e cole o JSON de exemplo.
4. Clique em **Send** e veja a resposta na parte inferior.

## 14. Como testar no navegador

O navegador só faz requisições **GET** diretamente pela barra de endereço, então funciona para:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/usuarios`
- `http://127.0.0.1:5000/usuarios/12345678900`
- `http://127.0.0.1:5000/catraca/12345678900`
- `http://127.0.0.1:5000/acessos`

Para POST e PUT (cadastrar/atualizar usuário), use o Postman, o `curl` ou o script `testes.py` deste projeto.

## 15. Como cadastrar um usuário

```
POST /usuarios
{
    "nome": "Maria Souza",
    "cpf": "98765432100"
}
```

O usuário já é criado com `ativo = true` automaticamente.

## 16. Como desativar um usuário

```
PUT /usuarios/98765432100
{
    "ativo": false
}
```

A partir daí, tentativas de acesso desse CPF na catraca retornarão "Acesso negado" (HTTP 403).

## 17. Como testar acesso autorizado

1. Cadastre um usuário (ele já nasce ativo).
2. Chame `GET /catraca/<cpf>` desse usuário.
3. Deve retornar `"acesso": true` com HTTP 200.

## 18. Como testar acesso negado

Existem duas formas de gerar acesso negado:

- **Usuário inativo:** desative um usuário existente (`PUT /usuarios/<cpf>` com `"ativo": false`) e chame `GET /catraca/<cpf>` → retorna HTTP 403.
- **CPF inexistente:** chame `GET /catraca/<cpf>` com um CPF que nunca foi cadastrado → retorna HTTP 404.

Em ambos os casos, a tentativa fica registrada em `/acessos`.

## 19. Como consultar o histórico de acessos

```
GET /acessos
```

Retorna todas as tentativas (autorizadas e negadas) já feitas na catraca, da mais recente para a mais antiga, com nome (quando disponível), CPF, data/hora e se foi autorizado.

## 20. Como visualizar o arquivo `banco.json`

Por ser um arquivo de texto simples, você pode abrir e inspecionar o `banco.json` de várias formas:

- **Qualquer editor de texto** (Bloco de Notas, VS Code, Sublime, etc.): basta abrir o arquivo `banco.json` normalmente.
- **VS Code**: já formata e destaca a sintaxe do JSON automaticamente, facilitando a leitura.
- **Terminal** (Linux/Mac):
  ```
  cat banco.json
  ```

## 21. Executando os testes automatizados

Este projeto inclui um script `testes.py` que percorre toda a API na sequência sugerida (cadastro, listagem, busca, acesso autorizado, desativação, acesso negado, histórico, CPF inexistente, validações, etc).

1. Rode a API em um terminal: `python3 app.py`
2. Em **outro** terminal, com o ambiente virtual ativado, rode:
   ```
   python3 testes.py
   ```
3. O script imprime no console o resultado (esperado x obtido) de cada teste.

## Decisões técnicas (resumo)

- **SQLite** escolhido por ser simples, não exigir servidor externo, e já vir embutido no Python — ideal para um projeto acadêmico de catraca.
- **`GET /catraca/<cpf>`** em vez de `POST /catraca`, por se tratar de uma consulta simples, sem necessidade de corpo JSON, facilitando a integração com hardware de catraca.
- **HTTP 403** para usuário inativo e **HTTP 404** para usuário inexistente, distinguindo claramente "existe mas não pode entrar" de "não existe no sistema".
- **`cpf_informado`** na tabela `registros_acesso`, além de `usuario_id`, para conseguir auditar tentativas com CPFs desconhecidos sem quebrar a integridade referencial (usuario_id fica `NULL` nesses casos).
- Todas as consultas usam **parâmetros (`?`)** no lugar de concatenação de strings, evitando SQL Injection.
