# Sistema de Controle de Acesso - Catraca

Projeto acadêmico para controle e gerenciamento de usuários de um sistema de catraca. A aplicação integra uma **API REST** backend em Python/Flask, uma **Interface Gráfica (GUI)** desktop em Tkinter, e uma **simulação de hardware com ESP32 no Wokwi** para autenticação e liberação de acesso.

---

## Funcionalidades

- **Gerenciamento de Usuários (GUI Desktop):**
  - Cadastrar novos usuários com Nome e CPF (com verificação de duplicidade de CPF).
  - Listar todos os usuários cadastrados.
  - Buscar usuário específico por CPF.
  - Atualizar dados de um usuário (Nome e Status Ativo/Inativo).
  - Excluir cadastros.
- **Simulação de Catraca (Wokwi / ESP32):**
  - Simulação de leitura de identificação e validação de acesso com microcontrolador ESP32.
  - Comunicação remota entre o ESP32 e a API Flask.
- **Persistência de Dados:**
  - Armazenamento local em arquivo JSON (`usuarios.json`).

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Backend / API:** [Flask](https://flask.palletsprojects.com/)
- **Frontend / Interface Desktop:** [Tkinter](https://docs.python.org/3/library/tkinter.html)
- **Requisições HTTP:** [Requests](https://requests.readthedocs.io/)
- **Simulação de Hardware:** [Wokwi](https://wokwi.com/) (ESP32)
- **Tunnelling / Exposição de API:** [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (`cloudflared`) — expõe o servidor local para o Wokwi
- **Armazenamento:** JSON

---

## Estrutura do Projeto

```text
.
├── catraca.py        # API REST (Servidor Flask)
├── cadastro_gui.py   # Interface Gráfica (Cliente Tkinter)
├── usuarios.json     # Base de dados local em formato JSON
└── README.md         # Documentação do projeto
```

---

## Como rodar o projeto (passo a passo)

### 1. Instalar as dependências Python

```bash
pip install flask requests
```

### 2. Rodar a API Flask

```bash
python catraca.py
```

A API vai subir em `http://127.0.0.1:5000` (porta 5000).

Teste no navegador: acesse `http://127.0.0.1:5000/` — deve aparecer a mensagem `"Minha API da catraca está funcionando"`.

### 3. Rodar a interface gráfica (opcional, para cadastro local)

Em outro terminal, com a API já rodando:

```bash
python cadastro_gui.py
```

Isso abre a tela de cadastro de usuários (Tkinter), que consome a API em `http://127.0.0.1:5000`.

---

## 🌐 Integração Backend & ESP32 (Wokwi + Cloudflare Tunnel)

Como o simulador Wokwi roda **na nuvem**, ele não consegue acessar diretamente o endereço local `http://127.0.0.1:5000` da sua máquina. Para resolver isso, usamos o **Cloudflare Tunnel** (`cloudflared`) para criar um túnel público e seguro até a API local, sem precisar mexer no roteador ou abrir portas.

### Passo 1 — Instalar o `cloudflared`

No Windows, com o [winget](https://learn.microsoft.com/pt-br/windows/package-manager/winget/) instalado, abra o **PowerShell** ou **Prompt de Comando** e rode:

```powershell
winget install --id Cloudflare.cloudflared
```

> Se o comando `winget` não for reconhecido, verifique se você está no Windows 10/11 atualizado (o App Installer da Microsoft Store traz o winget).

Para conferir se a instalação funcionou, feche e abra o terminal novamente e rode:

```powershell
cloudflared --version
```

Se aparecer a versão instalada, está tudo certo.

> **Linux/macOS:** siga o guia oficial de instalação em [developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).

### Passo 2 — Deixar a API rodando

Antes de criar o túnel, a API precisa estar de pé. Em um terminal:

```bash
python catraca.py
```

Deixe esse terminal aberto e rodando.

### Passo 3 — Criar o túnel apontando para a API local

Em **outro terminal** (sem fechar o anterior), rode:

```powershell
cloudflared tunnel --url http://localhost:5000
```

O `cloudflared` vai imprimir um log no terminal. Procure por uma linha parecida com esta:

```text
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://exemplo-qualquer-palavras-aleatorias.trycloudflare.com                             |
+--------------------------------------------------------------------------------------------+
```

Esse endereço `https://....trycloudflare.com` é o **link público** que aponta para a sua API local rodando na porta 5000. Ele é gerado aleatoriamente toda vez que você inicia o túnel — **não é fixo**, então sempre que reiniciar o `cloudflared`, você vai pegar um link novo.

> ⚠️ Mantenha esse terminal aberto enquanto estiver testando no Wokwi. Se fechar, o túnel cai e o link para de funcionar.

### Passo 4 — Colocar o link no código do ESP32 (Wokwi)

1. Abra o seu projeto no [Wokwi](https://wokwi.com/).
2. No arquivo de código do ESP32 (`.ino` / `sketch.cpp`), localize a variável/constante onde a URL da API é definida — normalmente algo como:

   ```cpp
   const char* serverUrl = "https://SEU-LINK-AQUI.trycloudflare.com";
   ```

3. Substitua pelo link que o `cloudflared` gerou no Passo 3, **mantendo o `https://`** e sem barra `/` extra no final, a menos que sua rota exija.
4. Se o código monta a URL completa concatenando o caminho da rota (ex.: `serverUrl + "/"`), confira que a rota bate com a que a API espera — nesse projeto, a rota usada pelo ESP32 é a raiz `/` com método **POST**, enviando um JSON assim:

   ```json
   { "matricula": "12345678900" }
   ```

5. Salve e clique em **Play/Start Simulation** no Wokwi.

### Passo 5 — Testar

- Digite/simule uma matrícula (CPF ou ID) no ESP32 simulado.
- A requisição deve chegar na sua API local (você verá o log no terminal do `catraca.py`).
- A resposta esperada é:

  ```json
  { "autorizado": true, "nome": "Seu Zé" }
  ```

  ou, se não cadastrado / inativo:

  ```json
  { "autorizado": false, "nome": "NAO CADASTRADO" }
  ```

### Dicas e problemas comuns

| Problema | Causa provável | Solução |
|---|---|---|
| Wokwi não conecta | Túnel fechado ou link expirado | Gere um novo link com `cloudflared tunnel --url http://localhost:5000` e atualize o código do ESP32 |
| Erro 502/503 no link do Cloudflare | API Flask não está rodando | Rode `python catraca.py` antes de criar o túnel |
| Link muda toda vez | Comportamento normal do "Quick Tunnel" | Para um link fixo, seria necessário configurar um túnel nomeado com conta Cloudflare (fora do escopo deste projeto acadêmico) |
| GUI dá "Erro de conexão" | API não está rodando na porta 5000 | Confirme que `catraca.py` está ativo antes de abrir `cadastro_gui.py` |

---

