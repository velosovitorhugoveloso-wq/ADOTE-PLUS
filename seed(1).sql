-- ============================================================
-- CARGA INICIAL DEMONSTRATIVA DO ADOTE+
-- Execute após schema.sql
-- ============================================================
INSERT INTO ongs (nome,email,telefone,cidade,estado,descricao,especialidades,verificada)
VALUES
('Amigos de Quatro Patas','contato@amigos4patas.org','(31) 99999-1001','Betim','MG','Resgate e adoção responsável de cães e gatos.','Cães,Gatos',TRUE),
('Lar de Patas','contato@lardepatas.org','(31) 99999-1002','Contagem','MG','Acolhimento temporário e preparação para adoção.','Cães,Gatos',TRUE),
('Vida Verde','contato@vidaverde.org','(31) 99999-1003','Betim','MG','Projeto demonstrativo focado em animais silvestres autorizados.','Tartarugas',TRUE),
('Cantinho dos Bichos','contato@cantinhodosbichos.org','(31) 99999-1004','Contagem','MG','Cuidados e adoção de pequenos animais.','Coelhos,Aves',TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO animais
(ong_id,nome,especie,raca,idade_meses,porte,sexo,cidade,status,temperamento,cuidados_especiais,vacinado,castrado,descricao)
SELECT o.id,'Teca','Tartaruga','Tigre-d''água',48,'Pequeno','Fêmea','Betim','Disponível','Calma',
'Habitat adequado, água limpa e acompanhamento especializado.',TRUE,FALSE,
'Tartaruga tranquila para adoção responsável, com necessidades específicas de habitat.'
FROM ongs o WHERE o.nome='Vida Verde'
AND NOT EXISTS (SELECT 1 FROM animais a WHERE a.nome='Teca');

INSERT INTO animais
(ong_id,nome,especie,raca,idade_meses,porte,sexo,cidade,status,temperamento,cuidados_especiais,vacinado,castrado,descricao)
SELECT o.id,'Ninja','Tartaruga','Jabuti-piranga',36,'Pequeno','Macho','Betim','Disponível','Calmo',
'Espaço seguro, alimentação adequada e acompanhamento especializado.',TRUE,FALSE,
'Jabuti dócil que precisa de ambiente apropriado para a espécie.'
FROM ongs o WHERE o.nome='Vida Verde'
AND NOT EXISTS (SELECT 1 FROM animais a WHERE a.nome='Ninja');

-- Estatísticas úteis para o painel
CREATE OR REPLACE VIEW vw_indicadores_adote AS
SELECT
 (SELECT COUNT(*) FROM animais) AS total_animais,
 (SELECT COUNT(*) FROM animais WHERE status='Disponível') AS animais_disponiveis,
 (SELECT COUNT(*) FROM pedidos) AS total_pedidos,
 (SELECT COUNT(*) FROM pedidos WHERE status='Em análise') AS pedidos_em_analise,
 (SELECT COUNT(*) FROM visitas WHERE status='Agendada') AS visitas_agendadas,
 (SELECT COUNT(*) FROM ongs WHERE verificada=TRUE) AS ongs_verificadas;
