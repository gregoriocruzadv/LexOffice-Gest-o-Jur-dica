from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# 1. Função para conectar e criar o banco de dados inicial (Apenas para Clientes por enquanto)
def init_db():
    conn = sqlite3.connect('lexoffice.db')
    cursor = conn.cursor()
    
    # Criando a tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT,
            doc TEXT,
            tel TEXT,
            email TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 2. Rota principal que carrega a sua interface (o seu index.html)
@app.route('/')
def index():
    return render_template('index.html')

# 3. Rota da API para gerenciar os Clientes
@app.route('/api/clientes', methods=['GET', 'POST'])
def gerenciar_clientes():
    conn = sqlite3.connect('lexoffice.db')
    cursor = conn.cursor()

    # Se o front-end (HTML) estiver SALVANDO um cliente novo
    if request.method == 'POST':
        dados = request.json
        cursor.execute('''
            INSERT INTO clientes (nome, tipo, doc, tel, email, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (dados.get('nome'), dados.get('tipo'), dados.get('doc'), 
              dados.get('tel'), dados.get('email'), dados.get('status')))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Cliente salvo com sucesso!"}), 201

    # Se o front-end estiver BUSCANDO a lista de clientes
    else:
        cursor.execute("SELECT id, nome, tipo, doc, tel, email, status FROM clientes")
        linhas = cursor.fetchall()
        
        lista_clientes = []
        for linha in linhas:
            lista_clientes.append({
                "id": linha[0], "nome": linha[1], "tipo": linha[2], 
                "doc": linha[3], "tel": linha[4], "email": linha[5], "status": linha[6]
            })
        conn.close()
        return jsonify(lista_clientes)

if __name__ == '__main__':
    init_db() # Garante que a tabela existe antes de rodar
    # Roda o servidor na porta 5000
    app.run(debug=True, port=5000)