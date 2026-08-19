Sistema de Controle de Acesso - Catraca

Este é um projeto acadêmico desenvolvido para realizar o controle e gerenciamento de usuários de um sistema de catraca. A aplicação integra uma **API REST** backend em Python/Flask, uma **Interface Gráfica (GUI)** desktop em Tkinter, e uma **simulação de hardware com ESP32 no Wokwi** para autenticação e liberação de acesso.

---

Funcionalidades

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

Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Backend / API:** [Flask](https://flask.palletsprojects.com/)
- **Frontend / Interface Desktop:** [Tkinter](https://docs.python.org/3/library/tkinter.html)
- **Requisições HTTP:** [Requests](https://requests.readthedocs.io/)
- **Simulação de Hardware:** [Wokwi](https://wokwi.com/) (ESP32)
- **Tunnelling / Exposição de API:** [Ngrok](https://ngrok.com/) (para expor o servidor local para o Wokwi)
- **Armazenamento:** JSON

---

Estrutura do Projeto

```text
.
├── catraca.py        # API REST (Servidor Flask)
├── cadastro_gui.py   # Interface Gráfica (Cliente Tkinter)
├── usuarios.json     # Base de dados local em formato JSON
└── README.md         # Documentação do projeto
```
🌐 Integração Backend & ESP32 (Wokwi + Ngrok)
Como o simulador Wokwi executa na nuvem, ele não consegue se conectar diretamente ao endereço local http://127.0.0.1:5000 da sua máquina. Para resolver isso, utilizamos o Ngrok para criar um túnel seguro de acesso público à API local.
