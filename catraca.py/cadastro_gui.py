import tkinter as tk
from tkinter import ttk, messagebox
import requests

# URL base da API - ajuste se rodar em outra porta/host
API_URL = "http://127.0.0.1:5000"


class TelaCadastro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cadastro de Usuários - Catraca")
        self.geometry("520x480")
        self.resizable(False, False)

        self._montar_formulario()
        self._montar_botoes()
        self._montar_lista()

    # ---------- INTERFACE ----------

    def _montar_formulario(self):
        frame = ttk.LabelFrame(self, text="Dados do Usuário")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nome = ttk.Entry(frame, width=40)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="CPF:").grid(row=1, column=0, sticky="w", padx=5, pady=5)#Aqui Basicamente eu so estou definindo altura e escala das funçoes predefinidas no tkinter
        self.entry_cpf = ttk.Entry(frame, width=40)
        self.entry_cpf.grid(row=1, column=1, padx=5, pady=5)

        self.var_ativo = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Ativo", variable=self.var_ativo).grid(
            row=2, column=1, sticky="w", padx=5, pady=5
        )

    def _montar_botoes(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Cadastrar", command=self.cadastrar).pack(side="left", padx=5)
        ttk.Button(frame, text="Buscar por CPF", command=self.buscar).pack(side="left", padx=5)
        ttk.Button(frame, text="Atualizar", command=self.atualizar).pack(side="left", padx=5)
        ttk.Button(frame, text="Excluir", command=self.excluir).pack(side="left", padx=5)
        ttk.Button(frame, text="Limpar Campos", command=self.limpar_campos).pack(side="left", padx=5)
        ttk.Button(frame, text="Listar Todos", command=self.listar).pack(side="left", padx=5)

    def _montar_lista(self):
        frame = ttk.LabelFrame(self, text="Usuários Cadastrados")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = ("id", "nome", "cpf", "ativo")
        self.tabela = ttk.Treeview(frame, columns=colunas, show="headings")
        for col, titulo, largura in [
            ("id", "ID", 40),
            ("nome", "Nome", 200),
            ("cpf", "CPF", 120),
            ("ativo", "Ativo", 60),
        ]:
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=largura)
        self.tabela.pack(fill="both", expand=True, padx=5, pady=5)

        # Ao clicar em uma linha, preenche o formulário automaticamente
        self.tabela.bind("<<TreeviewSelect>>", self.selecionar_linha)

        self.listar()  # já carrega a lista ao abrir a tela

    # ---------- AÇÕES (chamadas à API) ----------

    def cadastrar(self):
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()

        if not nome or not cpf:
            messagebox.showwarning("Atenção", "Nome e CPF são obrigatórios.")
            return

        try:
            resposta = requests.post(
                f"{API_URL}/usuarios",
                json={"nome": nome, "cpf": cpf},
            )
            dados = resposta.json()

            if resposta.status_code == 201:
                messagebox.showinfo("Sucesso", dados.get("mensagem"))
                self.limpar_campos()
                self.listar()
            else:
                messagebox.showerror("Erro", dados.get("erro", "Erro desconhecido"))
        except requests.exceptions.ConnectionError:
            self._erro_conexao()

    def buscar(self):
        cpf = self.entry_cpf.get().strip()
        if not cpf:
            messagebox.showwarning("Atenção", "Informe o CPF para buscar.")
            return

        try:
            resposta = requests.get(f"{API_URL}/usuarios/{cpf}")
            dados = resposta.json()

            if resposta.status_code == 200:
                self.entry_nome.delete(0, tk.END)
                self.entry_nome.insert(0, dados["nome"])
                self.var_ativo.set(dados["ativo"])
                messagebox.showinfo("Encontrado", f"Usuário: {dados['nome']}")
            else:
                messagebox.showerror("Erro", dados.get("erro", "Usuário não encontrado"))
        except requests.exceptions.ConnectionError:
            self._erro_conexao()

    def atualizar(self):
        cpf = self.entry_cpf.get().strip()
        nome = self.entry_nome.get().strip()

        if not cpf:
            messagebox.showwarning("Atenção", "Informe o CPF do usuário a atualizar.")
            return

        try:
            resposta = requests.put(
                f"{API_URL}/usuarios/{cpf}",
                json={"nome": nome, "ativo": self.var_ativo.get()},
            )
            dados = resposta.json()

            if resposta.status_code == 200:
                messagebox.showinfo("Sucesso", dados.get("mensagem"))
                self.listar()
            else:
                messagebox.showerror("Erro", dados.get("erro", "Erro desconhecido"))
        except requests.exceptions.ConnectionError:
            self._erro_conexao()

    def excluir(self):
        cpf = self.entry_cpf.get().strip()

        if not cpf:
            messagebox.showwarning("Atenção", "Informe o CPF do usuário a excluir.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir o usuário de CPF {cpf}?"
        )
        if not confirmar:
            return

        try:
            resposta = requests.delete(f"{API_URL}/usuarios/{cpf}")
            dados = resposta.json()

            if resposta.status_code == 200:
                messagebox.showinfo("Sucesso", dados.get("mensagem"))
                self.limpar_campos()
                self.listar()
            else:
                messagebox.showerror("Erro", dados.get("erro", "Erro desconhecido"))
        except requests.exceptions.ConnectionError:
            self._erro_conexao()

    def listar(self):
        try:
            resposta = requests.get(f"{API_URL}/usuarios")
            usuarios = resposta.json()

            for linha in self.tabela.get_children():
                self.tabela.delete(linha)

            for u in usuarios:
                self.tabela.insert(
                    "", "end",
                    values=(u["id"], u["nome"], u["cpf"], "Sim" if u["ativo"] else "Não")
                )
        except requests.exceptions.ConnectionError:
            self._erro_conexao()

    def selecionar_linha(self, event):
        selecionado = self.tabela.selection()
        if not selecionado:
            return
        valores = self.tabela.item(selecionado[0], "values")
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, valores[1])
        self.entry_cpf.delete(0, tk.END)
        self.entry_cpf.insert(0, valores[2])
        self.var_ativo.set(valores[3] == "Sim")

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.var_ativo.set(True)

    def _erro_conexao(self):
        messagebox.showerror(
            "Erro de conexão",
            f"Não foi possível conectar à API em {API_URL}.\n"
            "Verifique se o arquivo catraca.py está rodando."
        )


if __name__ == "__main__":
    app = TelaCadastro()
    app.mainloop()