import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# Permite todas as origens e métodos, com suporte a credenciais
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DATABASE = 'game.db'

# Conexão com o banco
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "Servidor Flask funcionando corretamente!"

# =========================================
# Inserir jogador
# =========================================
@app.route('/api/jogador/insert', methods=['POST', 'OPTIONS'])
def insert_jogador():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    nome = data.get('nome')
    senha = data.get('senha')

    if not nome or not senha:
        return jsonify({"erro": "nome e senha são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO jogador (nome, senha) VALUES (?, ?)',
        (nome, senha)
    )
    conn.commit()
    jogador_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "ok", "id": jogador_id})

# =========================================
# Atualizar pontos e quizzes respondidos
# =========================================
@app.route('/api/jogador/update', methods=['POST', 'OPTIONS'])
def update_jogador():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    jogador_id = data.get('id')
    pontos = data.get('pontos')
    booster_abertos = data.get('quantidadeBoosterAbertos')
    quizes = data.get('quizesRespondidos')

    if jogador_id is None or pontos is None or quizes is None:
        return jsonify({"erro": "id, pontos e quizesRespondidos são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE jogador SET pontos=?, quizesRespondidos=?, quantidadeBoosterAbertos=? WHERE id=?',
        (pontos, quizes, booster_abertos, jogador_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# =========================================
# Buscar jogador pelo ID
# =========================================
@app.route('/api/jogador/get', methods=['POST', 'OPTIONS'])
def get_jogador():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    jogador_id = data.get('id')

    if jogador_id is None:
        return jsonify({"erro": "id é obrigatório"}), 400

    conn = get_db_connection()
    jogador = conn.execute('SELECT * FROM jogador WHERE id=?', (jogador_id,)).fetchone()
    conn.close()

    if jogador is None:
        return jsonify({"erro": "Jogador não encontrado"}), 404

    return jsonify(dict(jogador))


# =========================================
# Buscar carta aleatória por raridade
# =========================================
@app.route('/api/carta/random', methods=['POST', 'OPTIONS'])
def get_carta_random():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    raridade = data.get('raridade')

    if raridade is None:
        return jsonify({"erro": "raridade é obrigatória"}), 400

    conn = get_db_connection()
    carta = conn.execute(
        'SELECT * FROM cartas WHERE raridade = ? ORDER BY RANDOM() LIMIT 1;',
        (raridade,)
    ).fetchone()
    conn.close()

    if carta is None:
        return jsonify({"erro": "Nenhuma carta encontrada para essa raridade"}), 404

    return jsonify(dict(carta))


# =========================================
# Rodar o servidor
# =========================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
