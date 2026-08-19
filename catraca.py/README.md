# Sistema Catraca - API + Tela de Cadastro

Este projeto tem duas partes que trabalham juntas:

1. **`catraca.py`** — a API Flask (o código que você já tinha) que armazena os
   usuários no arquivo `usuarios.json`.
2. **`cadastro_gui.py`** — uma tela gráfica (janela) feita em Python/Tkinter
   que se conecta a essa API para facilitar o cadastro, sem precisar usar
   Postman, curl ou navegador.

Também incluído: **`usuarios.json`**, um arquivo de exemplo com 3 usuários
pré-cadastrados, no formato exato que a API espera.

---

## 📁 Estrutura de arquivos

Coloque os três arquivos na **mesma pasta**:

```
minha-catraca/
├── catraca.py        <- sua API (o código que você me enviou)
├── cadastro_gui.py    <- a tela de cadastro
└── usuarios.json      <- banco de dados em JSON (criado automaticamente se não existir)
```

> Se você não colocar o `usuarios.json`, não tem problema: a própria API cria
> o arquivo automaticamente na primeira vez que alguém for cadastrado
> (função `carregar_usuarios()` já trata isso).

---

## ⚙️ Instalação

Você precisa do Python 3 instalado. Depois, instale as duas bibliotecas usadas:

```bash
pip install flask requests
```

- `flask` → usada pela API (`catraca.py`)
- `requests` → usada pela tela (`cadastro_gui.py`) para "conversar" com a API

`tkinter` já vem instalado por padrão com o Python na maioria dos sistemas
(no Linux, se faltar, instale com `sudo apt install python3-tk`).

---

## ▶️ Como rodar

**Passo 1 — Ligue a API primeiro** (ela precisa estar rodando o tempo todo):

```bash
python catraca.py
```

Você verá algo como:
```
 * Running on http://127.0.0.1:5000
```
Deixe esse terminal aberto.

**Passo 2 — Em outro terminal, abra a tela de cadastro:**

```bash
python cadastro_gui.py
```

Uma janela vai abrir com o formulário e a lista de usuários.

---

## 🖥️ O que a tela faz

| Botão | O que acontece |
|---|---|
| **Cadastrar** | Envia Nome + CPF para a API (`POST /usuarios`) e cria um novo usuário |
| **Buscar por CPF** | Preenche o formulário com os dados do usuário daquele CPF (`GET /usuarios/<cpf>`) |
| **Atualizar** | Atualiza nome/status "ativo" de um usuário já existente (`PUT /usuarios/<cpf>`) |
| **Listar Todos** | Atualiza a tabela com todos os usuários cadastrados (`GET /usuarios`) |
| **Limpar Campos** | Limpa o formulário |

Você também pode **clicar em qualquer linha da tabela** para carregar aquele
usuário automaticamente no formulário (útil antes de editar ou atualizar).

---

## 🔗 Como a tela conversa com a API

A tela não mexe no arquivo `usuarios.json` diretamente — ela só faz
requisições HTTP para a API, exatamente como um aplicativo de celular faria.
Isso é importante porque:

- Mantém toda a lógica de validação (CPF duplicado, campos obrigatórios,
  etc.) centralizada na API.
- Se no futuro você quiser trocar a tela por um app mobile ou site, a API
  continua funcionando do mesmo jeito.

O endereço usado está fixo no topo do arquivo `cadastro_gui.py`:

```python
API_URL = "http://127.0.0.1:5000"
```

Se você rodar a API em outra porta ou outro computador, é só mudar essa
linha.

---

## 🗂️ Formato do `usuarios.json`

```json
[
    {
        "id": 1,
        "nome": "João da Silva",
        "cpf": "12345678900",
        "ativo": true
    }
]
```

- `id`: gerado automaticamente pela API (não precisa preencher na mão)
- `nome`: texto
- `cpf`: texto (a API não formata nem valida o CPF, então cuidado ao digitar)
- `ativo`: `true` ou `false`

---

## ⚠️ Erros comuns

| Mensagem | Causa provável |
|---|---|
| "Não foi possível conectar à API" | Você esqueceu de rodar `python catraca.py` antes de abrir a tela |
| "CPF já está cadastrado" | Já existe um usuário com esse CPF no `usuarios.json` |
| "Nesse sistema Nome e CPF são obrigatórios" | Algum dos dois campos ficou em branco ao cadastrar |
| A tela abre mas a lista fica vazia | O `usuarios.json` está vazio (`[]`) ou não existe ainda — cadastre o primeiro usuário |

---

## 💡 Possíveis melhorias futuras

- Validar formato de CPF (dígitos verificadores)
- Adicionar botão "Excluir usuário" (a API ainda não tem rota `DELETE`)
- Trocar Tkinter por uma interface web (ex: HTML + JavaScript consumindo a
  mesma API)
- Adicionar autenticação para proteger o cadastro
