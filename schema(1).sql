-- ============================================================
-- ADOTE+ 2.0 — BANCO DE DADOS COMPLETO (PostgreSQL)
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(25),
    cidade VARCHAR(80),
    estado CHAR(2),
    tipo VARCHAR(20) NOT NULL DEFAULT 'Adotante'
        CHECK (tipo IN ('Adotante','Administrador','ONG')),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ongs (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(150),
    telefone VARCHAR(25),
    cidade VARCHAR(80) NOT NULL,
    estado CHAR(2) DEFAULT 'MG',
    endereco VARCHAR(180),
    descricao TEXT,
    especialidades VARCHAR(255),
    site VARCHAR(255),
    instagram VARCHAR(120),
    imagem_url TEXT,
    verificada BOOLEAN DEFAULT FALSE,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS animais (
    id SERIAL PRIMARY KEY,
    ong_id INT REFERENCES ongs(id) ON DELETE SET NULL,
    nome VARCHAR(60) NOT NULL,
    especie VARCHAR(40) NOT NULL,
    raca VARCHAR(80),
    idade_meses INT CHECK (idade_meses IS NULL OR idade_meses >= 0),
    porte VARCHAR(20),
    sexo VARCHAR(15),
    cidade VARCHAR(80),
    status VARCHAR(25) NOT NULL DEFAULT 'Disponível'
        CHECK (status IN ('Disponível','Em avaliação','Adotado','Indisponível')),
    temperamento VARCHAR(100),
    descricao TEXT,
    cuidados_especiais TEXT,
    vacinado BOOLEAN DEFAULT FALSE,
    castrado BOOLEAN DEFAULT FALSE,
    microchip VARCHAR(80),
    imagem_url TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fotos_animais (
    id SERIAL PRIMARY KEY,
    animal_id INT NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    legenda VARCHAR(150),
    principal BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS saude_animais (
    id SERIAL PRIMARY KEY,
    animal_id INT NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    tipo_registro VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    data_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    veterinario VARCHAR(120),
    proxima_data DATE
);

CREATE TABLE IF NOT EXISTS favoritos (
    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    animal_id INT REFERENCES animais(id) ON DELETE CASCADE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, animal_id)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    animal_id INT NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    telefone VARCHAR(25) NOT NULL,
    mensagem TEXT NOT NULL,
    experiencia_com_animais TEXT,
    tipo_moradia VARCHAR(60),
    possui_outros_animais BOOLEAN,
    status VARCHAR(30) NOT NULL DEFAULT 'Em análise'
        CHECK (status IN ('Em análise','Entrevista','Visita agendada','Aprovado','Rejeitado','Cancelado')),
    observacao_ong TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documentos_adocao (
    id SERIAL PRIMARY KEY,
    pedido_id INT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    tipo VARCHAR(60) NOT NULL,
    nome_arquivo VARCHAR(180),
    status VARCHAR(25) DEFAULT 'Pendente',
    enviado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS visitas (
    id SERIAL PRIMARY KEY,
    pedido_id INT REFERENCES pedidos(id) ON DELETE CASCADE,
    animal_id INT NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    data_visita DATE NOT NULL,
    horario TIME NOT NULL,
    status VARCHAR(25) DEFAULT 'Agendada'
        CHECK (status IN ('Agendada','Realizada','Cancelada')),
    observacao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notificacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo VARCHAR(120) NOT NULL,
    mensagem TEXT NOT NULL,
    tipo VARCHAR(40) DEFAULT 'Sistema',
    lida BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS apoios (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
    ong_id INT NOT NULL REFERENCES ongs(id) ON DELETE CASCADE,
    valor NUMERIC(10,2) NOT NULL CHECK (valor > 0),
    forma VARCHAR(40) NOT NULL,
    status VARCHAR(25) DEFAULT 'Registrado',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
    ong_id INT REFERENCES ongs(id) ON DELETE CASCADE,
    nota INT NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS preferencias_adotante (
    usuario_id INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    especies VARCHAR(255),
    portes VARCHAR(255),
    cidade VARCHAR(80),
    tem_tempo BOOLEAN,
    possui_espaco BOOLEAN,
    aceita_animal_especial BOOLEAN,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS historico_status (
    id SERIAL PRIMARY KEY,
    pedido_id INT NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    status_anterior VARCHAR(30),
    status_novo VARCHAR(30) NOT NULL,
    observacao TEXT,
    alterado_por INT REFERENCES usuarios(id) ON DELETE SET NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_animais_especie ON animais(especie);
CREATE INDEX IF NOT EXISTS idx_animais_status ON animais(status);
CREATE INDEX IF NOT EXISTS idx_animais_cidade ON animais(cidade);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos(status);
CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario ON notificacoes(usuario_id, lida);
CREATE INDEX IF NOT EXISTS idx_visitas_data ON visitas(data_visita);
