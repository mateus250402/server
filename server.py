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
# Atualizar jogador
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
# Buscar jogador pelo nome
# =========================================
@app.route('/api/jogador/get', methods=['POST', 'OPTIONS'])
def get_jogador():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    jogadorNome = data.get('nome')
    jogadorSenha = data.get('senha')
    
    if jogadorNome is None:
        return jsonify({"erro": "nome é obrigatório"}), 400
    if jogadorSenha is None:
        return jsonify({"erro": "senha é obrigatória"}), 400
    
    conn = get_db_connection()
    jogador = conn.execute(
        'SELECT * FROM jogador WHERE nome = ? AND senha = ?',
        (jogadorNome, jogadorSenha)
    ).fetchone()
    conn.close()

    if jogador is None:
        return jsonify({"erro": "Jogador não encontrado"}), 404

    return jsonify(dict(jogador))


# =========================================
# Buscar carta aleatória por raridade
# =========================================
@app.route('/api/carta/get', methods=['POST', 'OPTIONS'])
def get_carta_random():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    raridade = data.get('raridade')

    if raridade is None:
        return jsonify({"erro": "raridade é obrigatória"}), 400

    conn = get_db_connection()
    carta = conn.execute(
        'SELECT * FROM carta WHERE raridade = ? ORDER BY RANDOM() LIMIT 1;',
        (raridade,)
    ).fetchone()
    conn.close()

    if carta is None:
        return jsonify({"erro": "Nenhuma carta encontrada para essa raridade"}), 404

    return jsonify(dict(carta))


# =========================================
# Inserir nova carta no album do jogador
# =========================================
@app.route('/api/carta/insert', methods=['POST', 'OPTIONS'])
def insert_carta():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    jogador_id = data.get('idJogador')
    carta_id = data.get('idCarta')
    quantidade = 1
    
    if jogador_id is None:
        return jsonify({"erro": "idJogador é obrigatório"}), 400
    if carta_id is None:
        return jsonify({"erro": "idCarta é obrigatório"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO album (idJogador, idCarta, quantidade) VALUES (?, ?, ?)',
        (jogador_id, carta_id, quantidade)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# =========================================
# Selecionar carta no album do jogador
# =========================================
@app.route('/api/carta/select', methods=['POST', 'OPTIONS'])
def select_carta():
    if request.method == 'OPTIONS':
        return '', 200  # preflight

    data = request.get_json()
    jogador_id = data.get('idJogador')
    carta_id = data.get('idCarta')

    if jogador_id is None:
        return jsonify({"erro": "idJogador é obrigatório"}), 400
    if carta_id is None:
        return jsonify({"erro": "idCarta é obrigatório"}), 400

    conn = get_db_connection()
    carta = conn.execute(
        'SELECT * FROM album WHERE idJogador = ? AND idCarta = ?',
        (jogador_id, carta_id)
    ).fetchone()
    conn.close()

    if carta is None:
        return jsonify({"erro": "Carta não encontrada no album do jogador"}), 404

    return jsonify(dict(carta))


# =========================================
# Atualizar carta no álbum do jogador
# =========================================
@app.route('/api/carta/update', methods=['POST', 'OPTIONS'])
def update_carta():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    jogador_id = data.get('idJogador')
    carta_id = data.get('idCarta')

    if jogador_id is None or carta_id is None:
        return jsonify({"erro": "idJogador e idCarta são obrigatórios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica se já existe
    row = cursor.execute(
        'SELECT quantidade FROM album WHERE idJogador=? AND idCarta=?',
        (jogador_id, carta_id)
    ).fetchone()

    if row:
        nova_quantidade = row['quantidade'] + 1
        cursor.execute(
            'UPDATE album SET quantidade=? WHERE idJogador=? AND idCarta=?',
            (nova_quantidade, jogador_id, carta_id)
        )
    else:
        cursor.execute(
            'INSERT INTO album (idJogador, idCarta, quantidade) VALUES (?, ?, ?)',
            (jogador_id, carta_id, 1)
        )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# Adicione estes endpoints no seu arquivo Flask

# =========================================
# Buscar TODAS as cartas do jogo
# =========================================
@app.route('/api/cartas/todas', methods=['GET', 'OPTIONS'])
def get_todas_cartas():
    if request.method == 'OPTIONS':
        return '', 200
    
    conn = get_db_connection()
    cartas = conn.execute('SELECT * FROM carta ORDER BY nome').fetchall()
    conn.close()
    
    return jsonify([dict(carta) for carta in cartas])


# =========================================
# Buscar cartas do álbum de um jogador 
# =========================================
@app.route('/api/album/jogador', methods=['POST', 'OPTIONS'])
def get_album_jogador():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    jogador_id = data.get('idJogador')
    
    if jogador_id is None:
        return jsonify({"erro": "idJogador é obrigatório"}), 400
    
    conn = get_db_connection()
    
    # Buscar todas as cartas do álbum do jogador
    cartas_album = conn.execute(
        '''SELECT a.idCarta, a.quantidade, c.nome, c.caminhoImagem, c.raridade, c.categoria
           FROM album a
           JOIN carta c ON a.idCarta = c.id
           WHERE a.idJogador = ?
           ORDER BY c.raridade''',
        (jogador_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify([dict(carta) for carta in cartas_album])


# =========================================
# Buscar estatísticas do álbum
# =========================================
@app.route('/api/album/stats', methods=['POST', 'OPTIONS'])
def get_album_stats():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    jogador_id = data.get('idJogador')
    
    if jogador_id is None:
        return jsonify({"erro": "idJogador é obrigatório"}), 400
    
    conn = get_db_connection()
    
    # Total de cartas no jogo
    total_cartas = conn.execute('SELECT COUNT(*) as total FROM carta').fetchone()['total']
    
    # Cartas únicas que o jogador possui
    cartas_obtidas = conn.execute(
        'SELECT COUNT(DISTINCT idCarta) as obtidas FROM album WHERE idJogador = ?',
        (jogador_id,)
    ).fetchone()['obtidas']
    
    # Cartas por raridade
    stats_raridade = conn.execute(
        '''SELECT c.raridade, COUNT(*) as quantidade
           FROM album a
           JOIN carta c ON a.idCarta = c.id
           WHERE a.idJogador = ?
           GROUP BY c.raridade''',
        (jogador_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify({
        "total": total_cartas,
        "obtidas": cartas_obtidas,
        "porcentagem": round((cartas_obtidas / total_cartas * 100), 2) if total_cartas > 0 else 0,
        "por_raridade": [dict(stat) for stat in stats_raridade]
    })

# =========================================
# Buscar pontos do jogador
# =========================================
@app.route('/api/jogador/pontos/get', methods=['POST', 'OPTIONS'])
def get_pontos_jogador():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    jogador_id = data.get('idJogador')
    
    if jogador_id is None:
        return jsonify({"erro": "idJogador é obrigatório"}), 400
    
    conn = get_db_connection()
    jogador = conn.execute(
        'SELECT pontos FROM jogador WHERE id = ?',
        (jogador_id,)
    ).fetchone()
    conn.close()
    
    if jogador is None:
        return jsonify({"erro": "Jogador não encontrado"}), 404
    
    return jsonify({"pontos": jogador['pontos']})


# =========================================
# Atualizar pontos do jogador
# =========================================
@app.route('/api/jogador/pontos/update', methods=['POST', 'OPTIONS'])
def update_pontos_jogador():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    jogador_id = data.get('idJogador')
    pontos = data.get('pontos')
    
    if jogador_id is None:
        return jsonify({"erro": "idJogador é obrigatório"}), 400
    if pontos is None:
        return jsonify({"erro": "pontos é obrigatório"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE jogador SET pontos = ? WHERE id = ?',
        (pontos, jogador_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "ok", "pontos": pontos})



# =========================================
# Rodar o servidor pyanywhere
# =========================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
