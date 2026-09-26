from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave_dev_adote_plus")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB = os.path.join(BASE_DIR, "adote_plus.db")
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

# PostgreSQL is supported when DATABASE_URL starts with postgresql://.
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    psycopg2 = None
    POSTGRES_AVAILABLE = False


def using_postgres():
    return DATABASE_URL.lower().startswith(("postgresql://", "postgres://"))


def get_db():
    """Open the configured database. SQLite is the default for local development."""
    if using_postgres():
        if not POSTGRES_AVAILABLE:
            raise RuntimeError(
                "psycopg2 não está instalado. Execute: pip install psycopg2-binary"
            )
        return psycopg2.connect(DATABASE_URL)

    db = sqlite3.connect(SQLITE_DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_sqlite_db():
    """Create the local database and seed basic data on first run."""
    db = sqlite3.connect(SQLITE_DB)
    db.execute("PRAGMA foreign_keys = ON")

    db.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        telefone TEXT,
        cidade TEXT,
        estado TEXT,
        tipo TEXT NOT NULL DEFAULT 'Adotante',
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS ongs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        cidade TEXT NOT NULL,
        estado TEXT DEFAULT 'MG',
        endereco TEXT,
        descricao TEXT,
        especialidades TEXT,
        site TEXT,
        instagram TEXT,
        imagem_url TEXT,
        verificada INTEGER DEFAULT 0,
        criada_em TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ong_id INTEGER REFERENCES ongs(id) ON DELETE SET NULL,
        nome TEXT NOT NULL,
        especie TEXT NOT NULL,
        raca TEXT,
        idade_meses INTEGER,
        porte TEXT,
        sexo TEXT,
        cidade TEXT,
        status TEXT NOT NULL DEFAULT 'Disponível',
        temperamento TEXT,
        descricao TEXT,
        cuidados_especiais TEXT,
        vacinado INTEGER DEFAULT 0,
        castrado INTEGER DEFAULT 0,
        microchip TEXT,
        imagem_url TEXT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
        telefone TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        experiencia_com_animais TEXT,
        tipo_moradia TEXT,
        possui_outros_animais INTEGER,
        status TEXT NOT NULL DEFAULT 'Em análise',
        observacao_ong TEXT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS visitas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
        animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        data_visita TEXT NOT NULL,
        horario TEXT NOT NULL,
        status TEXT DEFAULT 'Agendada',
        observacao TEXT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS apoios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
        ong_id INTEGER NOT NULL REFERENCES ongs(id) ON DELETE CASCADE,
        valor REAL NOT NULL CHECK (valor > 0),
        forma TEXT NOT NULL,
        status TEXT DEFAULT 'Registrado',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Dados iniciais para o sistema já abrir com animais no banco.
    db.execute("""
        INSERT OR IGNORE INTO ongs
        (id, nome, email, telefone, cidade, estado, descricao, especialidades, verificada)
        VALUES (1, 'Vida Verde', 'contato@vidaverde.org', '(31) 99999-1003',
                'Betim', 'MG', 'Projeto demonstrativo focado em animais silvestres autorizados.',
                'Tartarugas', 1)
    """)
    db.execute("""
        INSERT OR IGNORE INTO ongs
        (id, nome, email, telefone, cidade, estado, descricao, especialidades, verificada)
        VALUES (2, 'Amigos de Quatro Patas', 'contato@amigos4patas.org', '(31) 99999-1001',
                'Betim', 'MG', 'Resgate e adoção responsável.', 'Cães,Gatos', 1)
    """)

    db.execute("""
        INSERT OR IGNORE INTO animais
        (id, ong_id, nome, especie, raca, idade_meses, porte, sexo, cidade, status,
         temperamento, cuidados_especiais, vacinado, castrado, descricao)
        VALUES (1, 1, 'Teca', 'Tartaruga', 'Tigre-d''água', 48, 'Pequeno', 'Fêmea',
                'Betim', 'Disponível', 'Calma',
                'Habitat adequado, água limpa e acompanhamento especializado.',
                1, 0, 'Tartaruga tranquila para adoção responsável.')
    """)
    db.execute("""
        INSERT OR IGNORE INTO animais
        (id, ong_id, nome, especie, raca, idade_meses, porte, sexo, cidade, status,
         temperamento, cuidados_especiais, vacinado, castrado, descricao)
        VALUES (2, 1, 'Ninja', 'Tartaruga', 'Jabuti-piranga', 36, 'Pequeno', 'Macho',
                'Betim', 'Disponível', 'Calmo',
                'Espaço seguro, alimentação adequada e acompanhamento especializado.',
                1, 0, 'Jabuti dócil que precisa de ambiente apropriado.')
    """)

    # Usuário de teste para permitir testar pedidos/visitas sem cadastro manual.
    db.execute("""
        INSERT OR IGNORE INTO usuarios
        (id, nome, email, senha, telefone, cidade, estado)
        VALUES (1, 'Usuário de Teste', 'teste@adoteplus.local', 'teste',
                '(31) 99999-0000', 'Betim', 'MG')
    """)

    db.commit()
    db.close()


def row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        return dict(row)
    return dict(row)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    try:
        db = get_db()
        db.execute("SELECT 1")
        db.close()
        return jsonify({
            "status": "ok",
            "sistema": "Adote+",
            "versao": "2.2",
            "banco": "PostgreSQL" if using_postgres() else "SQLite",
            "conexao": "conectado"
        })
    except Exception as e:
        app.logger.exception("Falha na conexão com o banco")
        return jsonify({
            "status": "erro",
            "banco": "PostgreSQL" if using_postgres() else "SQLite",
            "conexao": "falhou",
            "detalhes": str(e)
        }), 500


@app.get("/api/indicadores")
def indicadores():
    db = get_db()
    try:
        cur = db.execute("""
            SELECT
                (SELECT COUNT(*) FROM animais) AS total_animais,
                (SELECT COUNT(*) FROM animais WHERE status='Disponível') AS animais_disponiveis,
                (SELECT COUNT(*) FROM pedidos) AS total_pedidos,
                (SELECT COUNT(*) FROM pedidos WHERE status='Em análise') AS pedidos_em_analise,
                (SELECT COUNT(*) FROM visitas WHERE status='Agendada') AS visitas_agendadas,
                (SELECT COUNT(*) FROM ongs WHERE verificada=1) AS ongs_verificadas
        """)
        return jsonify(row_to_dict(cur.fetchone()))
    finally:
        db.close()


@app.get("/api/animais")
def listar_animais():
    db = get_db()
    try:
        filtros = []
        params = []

        especie = request.args.get("especie")
        status = request.args.get("status")
        cidade = request.args.get("cidade")

        query = """
            SELECT a.*, o.nome AS ong_nome
            FROM animais a
            LEFT JOIN ongs o ON o.id = a.ong_id
        """

        if especie:
            filtros.append("LOWER(a.especie) LIKE LOWER(?)")
            params.append(f"%{especie}%")
        if status:
            filtros.append("a.status = ?")
            params.append(status)
        if cidade:
            filtros.append("LOWER(a.cidade) LIKE LOWER(?)")
            params.append(f"%{cidade}%")

        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        query += " ORDER BY a.id DESC"

        cur = db.execute(query, params)
        animais = [row_to_dict(row) for row in cur.fetchall()]

        return jsonify({"total": len(animais), "animais": animais})
    except Exception as e:
        app.logger.exception("Erro ao buscar animais")
        return jsonify({"erro": "Não foi possível buscar os animais.", "detalhes": str(e)}), 500
    finally:
        db.close()


@app.get("/api/pedidos")
def listar_pedidos():
    usuario_id = request.args.get("usuario_id", type=int)
    db = get_db()
    try:
        query = """
            SELECT p.*, a.nome AS animal_nome, a.imagem_url, a.cidade, a.raca,
                   u.nome AS adotante, u.email
            FROM pedidos p
            JOIN animais a ON a.id = p.animal_id
            JOIN usuarios u ON u.id = p.usuario_id
        """
        params = []
        if usuario_id:
            query += " WHERE p.usuario_id = ?"
            params.append(usuario_id)
        query += " ORDER BY p.id DESC"

        cur = db.execute(query, params)
        return jsonify([row_to_dict(row) for row in cur.fetchall()])
    finally:
        db.close()


@app.post("/api/pedidos")
def criar_pedido():
    data = request.get_json(silent=True) or {}
    required = ["usuario_id", "animal_id", "telefone", "mensagem"]
    if any(k not in data for k in required):
        return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

    db = get_db()
    try:
        cur = db.execute("""
            INSERT INTO pedidos
            (usuario_id, animal_id, telefone, mensagem, experiencia_com_animais,
             tipo_moradia, possui_outros_animais)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["usuario_id"], data["animal_id"], data["telefone"], data["mensagem"],
            data.get("experiencia_com_animais"), data.get("tipo_moradia"),
            data.get("possui_outros_animais")
        ))
        db.commit()
        pedido_id = cur.lastrowid
        row = db.execute(
            "SELECT id, status, criado_em FROM pedidos WHERE id = ?", (pedido_id,)
        ).fetchone()
        return jsonify(row_to_dict(row)), 201
    except Exception as e:
        db.rollback()
        return jsonify({"erro": "Não foi possível criar o pedido.", "detalhes": str(e)}), 500
    finally:
        db.close()


@app.patch("/api/pedidos/<int:pedido_id>")
def atualizar_pedido(pedido_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    permitidos = {
        "Em análise", "Entrevista", "Visita agendada",
        "Aprovado", "Rejeitado", "Cancelado"
    }

    if status not in permitidos:
        return jsonify({"erro": "Status inválido."}), 400

    db = get_db()
    try:
        cur = db.execute("""
            UPDATE pedidos
            SET status = ?,
                observacao_ong = COALESCE(?, observacao_ong),
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, data.get("observacao_ong"), pedido_id))
        if cur.rowcount == 0:
            return jsonify({"erro": "Pedido não encontrado."}), 404
        db.commit()
        row = db.execute(
            "SELECT id, status, atualizado_em FROM pedidos WHERE id = ?",
            (pedido_id,)
        ).fetchone()
        return jsonify(row_to_dict(row))
    finally:
        db.close()


@app.post("/api/visitas")
def criar_visita():
    data = request.get_json(silent=True) or {}
    required = ["animal_id", "usuario_id", "data_visita", "horario"]
    if any(k not in data for k in required):
        return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

    db = get_db()
    try:
        cur = db.execute("""
            INSERT INTO visitas
            (animal_id, usuario_id, data_visita, horario, observacao)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["animal_id"], data["usuario_id"], data["data_visita"],
            data["horario"], data.get("observacao")
        ))
        db.commit()
        return jsonify({"id": cur.lastrowid, "status": "Agendada"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"erro": "Não foi possível criar a visita.", "detalhes": str(e)}), 500
    finally:
        db.close()


@app.post("/api/apoios")
def registrar_apoio():
    data = request.get_json(silent=True) or {}
    required = ["ong_id", "valor", "forma"]
    if any(k not in data for k in required):
        return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

    db = get_db()
    try:
        cur = db.execute("""
            INSERT INTO apoios(usuario_id, ong_id, valor, forma)
            VALUES (?, ?, ?, ?)
        """, (data.get("usuario_id"), data["ong_id"], data["valor"], data["forma"]))
        db.commit()
        row = db.execute(
            "SELECT id, status, criado_em FROM apoios WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return jsonify(row_to_dict(row)), 201
    except Exception as e:
        db.rollback()
        return jsonify({"erro": "Não foi possível registrar o apoio.", "detalhes": str(e)}), 500
    finally:
        db.close()


@app.get("/api/apoios/indicadores")
def indicadores_apoio():
    db = get_db()
    try:
        ongs = db.execute(
            "SELECT COUNT(*) FROM ongs WHERE verificada = 1"
        ).fetchone()[0]
        animais = db.execute("SELECT COUNT(*) FROM animais").fetchone()[0]
        adocoes = db.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = 'Aprovado'"
        ).fetchone()[0]
        return jsonify({
            "ongs_rede": ongs,
            "animais_acolhidos": animais,
            "adocoes_realizadas": adocoes
        })
    finally:
        db.close()


if __name__ == "__main__":
    # Cria automaticamente o banco local quando o projeto usa SQLite.
    if not using_postgres():
        init_sqlite_db()

    port = int(os.environ.get("PORT", 5000))
    print(f"Banco configurado: {'PostgreSQL' if using_postgres() else 'SQLite'}")
    app.run(host="0.0.0.0", port=port, debug=True)
