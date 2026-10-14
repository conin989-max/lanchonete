import customtkinter as ctk
import sqlite3
import os
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
#----usuario e senha para entrar no sistema----
def verificar_login():
    usuario = usuario_entry.get()
    senha = senha_entry.get()
    if usuario == "" and senha == '':
        janela_principal()
        janela_login.destroy()
    else:
        messagebox.showerror("Erro de login", "Usuário ou senha incorretos.")


#-----------------funcoes da janela de estoque-----------------

def consultar_produtos():
    conexao, cursor = conectar()
    cursor.execute('SELECT * FROM produtos')
    itens = cursor.fetchall()
    conexao.close()

    for widget in caixa_resultado.winfo_children():
        widget.destroy()

    for linha in itens:

        nome = linha[0]
        preco = linha[1]
        quantidade = linha[2]

        texto = (f"Produto: {nome}   |   "f"Preço: R$ {preco:.2f}   |   "f"Estoque: {quantidade}")
        ctk.CTkLabel(caixa_resultado,text=texto,font=("Helvetica", 15),anchor="w").grid(row=itens.index(linha),column=0,sticky="w",padx=10,pady=5)
        ctk.CTkButton(caixa_resultado,fg_color="red",text="excluir",command=lambda nome=nome: excluir_produto(nome),width=10).grid(row=itens.index(linha),column=1,padx=10,pady=5)
        ctk.CTkButton(caixa_resultado,fg_color="green",text="editar",command=lambda nome=nome: editar(nome),width=10).grid(row=itens.index(linha),column=2,padx=10,pady=5)
        ctk.CTkButton(caixa_resultado,text="Salvar alteração",font=("Helvetica", 16),command=salvar_edicao).grid(row=itens.index(linha),column=3,pady=10,padx=5)

#funcoes do sistema db
#funcoes do sistema db
def salvar_edicao():

    global produto_editando

    if produto_editando is None:
        messagebox.showwarning("Aviso","Selecione um produto para editar.")
        return

    novo_nome = nome_produto_entry.get().strip()
    novo_preco = preco_entry.get().strip()
    nova_quantidade = quantidade_entry.get().strip()

    if not novo_nome:
        messagebox.showwarning("Aviso","O nome não pode ficar vazio.")
        return
    try:
        novo_preco = float(novo_preco)
        nova_quantidade = int(nova_quantidade)

    except ValueError:
        messagebox.showerror("Erro","Preço e quantidade devem ser números.")
        return

    if novo_preco < 0 or nova_quantidade < 1:
        messagebox.showerror("Erro","Preço não pode ser negativo e quantidade deve ser maior que zero.")
        return
    conexao, cursor = conectar()
    cursor.execute(
        """
        UPDATE produtos
        SET nome = ?, preco = ?, quantidade = ?
        WHERE nome = ?
        """,
        (novo_nome,novo_preco,nova_quantidade,produto_editando))
    conexao.commit()
    conexao.close()
    produto_editando = None
    nome_produto_entry.delete(0, "end")
    preco_entry.delete(0, "end")
    quantidade_entry.delete(0, "end")
    consultar_produtos()
    messagebox.showinfo("Sucesso","Produto editado com sucesso!")

def editar(nome):
    conexao, cursor = conectar()
    cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE nome = ?",(nome,))
    produto = cursor.fetchone()
    conexao.close()
    if produto:
        nome_produto_entry.delete(0, "end")
        preco_entry.delete(0, "end")
        quantidade_entry.delete(0, "end")
        nome_produto_entry.insert(0, produto[0])
        preco_entry.insert(0, produto[1])
        quantidade_entry.insert(0, produto[2])
        global produto_editando
        produto_editando = nome
        messagebox.showinfo(
            "Editar produto",
            "Altere os dados nos campos acima e clique em 'Salvar alteração'.")

def excluir_produto(nome):
    conexao, cursor = conectar()
    cursor.execute("DELETE FROM produtos WHERE nome = ?", (nome,))
    conexao.commit()
    conexao.close()
    messagebox.showinfo("Produto excluído", f"O produto '{nome}' foi excluído do estoque.")
    consultar_produtos()

def conectar():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_banco = os.path.join(diretorio_atual,"sistema2.db")

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        nome TEXT,
        preco REAL,
        quantidade INTEGER
    )
""")
    conexao.commit()
    return conexao, cursor



def cadastrar_produto():
    nome = nome_produto_entry.get().strip()
    preco = preco_entry.get().strip()
    quantidade = quantidade_entry.get().strip()
    if not nome:
        messagebox.showwarning('Aviso, o nome do produto nao pode ficar vazio!')
        return
    try:
        preco = float(preco)
        quantidade = int(quantidade)
        if preco < 0 or quantidade < 1:
            messagebox.showerror("O preço ou a quantidade não podem ser negativo!")
            preco_entry.delete(0,'end')
            quantidade_entry.delete(0,'end')
            return
        if preco >1000000000 or quantidade > 10000000:
            messagebox.showerror('O preço ou o estoque estão muito grandes!')
            preco_entry.delete(0,'end')
            quantidade_entry.delete(0,'end')
            return
        conexao, cursor = conectar()

        cursor.execute("SELECT * FROM produtos WHERE nome = ?",(nome,))
        if cursor.fetchone():
            messagebox.showerror("AVISO!! Esse produto ja esta cadastrado!")
            conexao.close

            nome_produto_entry.delete(0,'end')
            preco_entry.delete(0,'end')
            quantidade_entry.delete(0,'end')
            return
        

        cursor.execute("INSERT INTO produtos VALUES (?, ?, ?)",(nome, preco, quantidade))
        nome_produto_entry.delete(0,'end')
        preco_entry.delete(0,'end')
        quantidade_entry.delete(0,'end')
        conexao.commit()
        conexao.close()

        messagebox.showinfo('Sucesso',f"Produto {nome} cadastrado!")
    except ValueError:
        messagebox.showerror("Erro de digitacão, digite valores numéricos!")
    consultar_produtos()

#---------------JANELAS -------------------------------
# ---- janela principal ----
def janela_principal():
    janela_login.withdraw()
    janela_principal = ctk.CTk()
    janela_principal.title("sistema da lanchonete")
    janela_principal.geometry("400x300")

    ctk.CTkLabel(janela_principal, text="Bem-vindo ao sistema da lanchonete!", font=("Helvetica", 20)).grid(row=0,column=0, pady =20, padx=40)
    botao_estoque = ctk.CTkButton(janela_principal, text="Estoque da lanchonete", font=("Helvetica", 16), command=janela_estoque)
    botao_estoque.grid(row=1,column=0, pady=30, padx=40)
    botao_vendas = ctk.CTkButton(janela_principal, text="Vendas da lanchonete", font=("Helvetica", 16))
    botao_vendas.grid(row=2,column=0, pady=30, padx=40)

    janela_principal.mainloop()
    janela_login.destroy()

def janela_estoque():
    global nome_produto_entry, preco_entry, quantidade_entry, caixa_resultado
    janela_estoque = ctk.CTk()

    
    janela_estoque.title("Estoque da lanchonete")
    janela_estoque.geometry("800x500")

    ctk.CTkLabel(janela_estoque,text="-------------- Cadastro de produtos --------------", font=("Comic Sans MS", 20)).place(x=75,y=10)
    ctk.CTkLabel(janela_estoque,text="", font=("Comic Sans MS", 20)).grid(row=0,column=0, pady = (20,0), padx=70)
    ctk.CTkLabel(janela_estoque, text="Nome do produto:", font=("Helvetica", 16)).grid(row=1,column=0, pady =0, padx=0,sticky='E')
    ctk.CTkLabel(janela_estoque, text="Quantidade:", font=("Helvetica", 16)).grid(row=2,column=0, pady =0, padx=0,sticky='E')
    ctk.CTkLabel(janela_estoque, text="Preço:", font=("Helvetica", 16)).grid(row=3,column=0, pady =0, padx=0,sticky='E')
    ctk.CTkLabel(janela_estoque, text="-------------- Estoque --------------", font=("Comic Sans MS", 20)).place(x=130,y=140)
    caixa_resultado = ctk.CTkScrollableFrame(janela_estoque, width=1000, height=5, orientation="vertical")
    caixa_resultado.place(x=40, y=220)

    nome_produto_entry = ctk.CTkEntry(janela_estoque, placeholder_text="Digite o nome do produto", width=250)
    nome_produto_entry.grid(row=1,column=1, pady =0, padx=10,sticky='W')
    quantidade_entry = ctk.CTkEntry(janela_estoque, placeholder_text="Digite a quantidade", width=250)
    quantidade_entry.grid(row=2,column=1, pady =0, padx=10,sticky='W')
    preco_entry = ctk.CTkEntry(janela_estoque, placeholder_text="Digite o preço", width=250)
    preco_entry.grid(row=3,column=1, pady =0, padx=10,sticky='W') 

    botao_salvar = ctk.CTkButton(janela_estoque, text="Salvar produto", font=("Helvetica", 16),command=cadastrar_produto)
    botao_salvar.grid(row=2,column=2)
    botao_atualizar = ctk.CTkButton(janela_estoque, text="Atualizar Estoque", font=("Helvetica", 16),command=consultar_produtos)
    botao_atualizar.grid(row=4,column=1, pady=45, padx=30)

    consultar_produtos()

    janela_estoque.mainloop()

#---janela de login---
janela_login = ctk.CTk()
janela_login.title("Login Lanchonete")
janela_login.geometry("400x300")


usuario_label = ctk.CTkLabel(janela_login, font=("Helvetica", 16), text="Usuário:").grid(row=0, column=0, padx=30, pady=(30,20), sticky='S')
usuario_entry = ctk.CTkEntry(janela_login, placeholder_text="Digite seu usuário", width=250)
usuario_entry.grid(row=0, column=1, padx=10,pady=(30,20))
senha_label = ctk.CTkLabel(janela_login, font=("Helvetica", 16), text="Senha:").grid(row=1, column=0, padx=30, pady=1, sticky='W')
senha_entry = ctk.CTkEntry(janela_login, placeholder_text="Digite sua senha", width=250, show="*")
senha_entry.grid(row=1, column=1, padx=10, pady=1, sticky='W')

entrar_botao = ctk.CTkButton(janela_login, text="entrar", font=("Helvetica", 16), fg_color="#3FB2FF", command=verificar_login).grid(row=2, column=0, columnspan=2, pady=(40,30))


janela_login.mainloop()