-- =====================================================================
-- BodyScan KB — Seed de conhecimento curado
-- Conteúdo: fisiologia do emagrecimento, pós-bariátrico, fármacos,
--           pele e processos metabólicos.
-- IMPORTANTE: os embeddings dos chunks são gerados pelo pipeline de
--   ingestão (coluna `embedding` permanece NULL aqui). Ver ingestao.py.
-- Referências: instituições reais nomeadas; DOIs/anos específicos
--   permanecem para verificação (requer_verificacao = TRUE).
-- =====================================================================

BEGIN;

-- ---------------------------------------------------------------------
-- DOMÍNIOS E CATEGORIAS
-- ---------------------------------------------------------------------
INSERT INTO dominio_conhecimento (slug, nome, descricao) VALUES
('metabolismo_energetico', 'Metabolismo energético', 'Balanço energético, gasto basal, adaptação metabólica.'),
('metabolismo_lipidico',   'Metabolismo lipídico', 'Lipólise, beta-oxidação, tecido adiposo.'),
('pos_bariatrico',         'Pós-cirurgia bariátrica', 'Fisiologia e cuidados após RYGB, sleeve e outras técnicas.'),
('farmacologia_obesidade', 'Farmacologia da obesidade', 'Agonistas GLP-1/GIP e demais antiobesidade.'),
('tecido_tegumentar',      'Pele e tecido conjuntivo', 'Elasticidade, colágeno, pele redundante pós-perda ponderal.'),
('nutricao_clinica',       'Nutrição clínica', 'Macronutrientes, micronutrientes e suplementação.'),
('antropometria_risco',    'Antropometria e risco', 'IMC, RCQ, RCA, composição corporal e risco cardiometabólico.');

INSERT INTO categoria (dominio_id, slug, nome, descricao)
SELECT d.id, v.slug, v.nome, v.descricao
FROM (VALUES
  ('metabolismo_energetico','gasto_energetico','Gasto energético','TMB, TDEE, efeito térmico.'),
  ('metabolismo_energetico','adaptacao_metabolica','Adaptação metabólica','Termogênese adaptativa, platô.'),
  ('metabolismo_lipidico','mobilizacao_gordura','Mobilização de gordura','Lipólise e oxidação de ácidos graxos.'),
  ('metabolismo_lipidico','tipos_adiposo','Tipos de tecido adiposo','Branco, marrom, visceral, subcutâneo.'),
  ('pos_bariatrico','tecnicas','Técnicas cirúrgicas','RYGB, sleeve, banda, BPD-DS.'),
  ('pos_bariatrico','complicacoes','Complicações e síndromes','Dumping, deficiências, perda de massa magra.'),
  ('farmacologia_obesidade','incretinomimeticos','Incretinomiméticos','Agonistas GLP-1 e duplos GIP/GLP-1.'),
  ('farmacologia_obesidade','outros_antiobesidade','Outros antiobesidade','Orlistate, naltrexona-bupropiona, etc.'),
  ('tecido_tegumentar','elasticidade','Elasticidade cutânea','Colágeno, elastina, retração da pele.'),
  ('nutricao_clinica','proteina','Proteína e massa magra','Preservação muscular, cicatrização.'),
  ('nutricao_clinica','micronutrientes','Micronutrientes','Ferro, B12, D, cálcio, vit. C.'),
  ('antropometria_risco','indices','Índices antropométricos','IMC, RCQ, RCA.')
) AS v(dominio_slug, slug, nome, descricao)
JOIN dominio_conhecimento d ON d.slug = v.dominio_slug;

-- ---------------------------------------------------------------------
-- FONTES (instituições reais; claims específicos exigem verificação)
-- ---------------------------------------------------------------------
INSERT INTO fonte (titulo, instituicao, nivel_evidencia, requer_verificacao, autores) VALUES
('Diretrizes perioperatórias de suporte nutricional e metabólico em cirurgia bariátrica',
 'ASMBS / AACE / TOS', 'diretriz_clinica', TRUE, 'Mechanick JI et al. (verificar ano/edição)'),
('Classificação de sobrepeso e obesidade por IMC',
 'World Health Organization (WHO)', 'diretriz_clinica', FALSE, NULL),
('Pharmacological management of obesity — clinical practice guideline',
 'Endocrine Society', 'diretriz_clinica', TRUE, NULL),
('Standards of Care in Diabetes (capítulo obesidade)',
 'American Diabetes Association (ADA)', 'diretriz_clinica', TRUE, NULL),
('Fisiologia do tecido adiposo e regulação da lipólise (livro-texto)',
 'Literatura de fisiologia (Guyton/Boron — verificar)', 'fisiologia_estabelecida', TRUE, NULL),
('Relação cintura-estatura como preditor de risco cardiometabólico',
 'Revisão sistemática (verificar fonte primária)', 'revisao_sistematica', TRUE, NULL);

-- ---------------------------------------------------------------------
-- BIOMARCADORES (ponte com o app BodyScan)
-- ---------------------------------------------------------------------
INSERT INTO biomarcador (slug, nome, unidade, descricao, faixa_referencia) VALUES
('imc','Índice de Massa Corporal','kg/m²','Peso/altura². Triagem populacional, não distingue massa magra de gordura.',
 '{"normal":[18.5,24.9],"sobrepeso":[25,29.9],"obesidade_I":[30,34.9],"obesidade_II":[35,39.9],"obesidade_III":[40,null]}'),
('rcq','Relação Cintura-Quadril',NULL,'Cintura/quadril. Estima distribuição de gordura.',
 '{"risco_aumentado_homem":0.90,"risco_aumentado_mulher":0.85}'),
('rca','Relação Cintura-Estatura',NULL,'Cintura/altura. Bom preditor de gordura visceral.',
 '{"limite_risco":0.50}'),
('perc_gordura','Percentual de gordura corporal','%','Fração de massa gorda sobre massa total.',
 '{"saudavel_homem":[10,20],"saudavel_mulher":[18,28]}'),
('massa_magra','Massa magra','kg','Massa livre de gordura; alvo de preservação na perda ponderal.', NULL);

-- ---------------------------------------------------------------------
-- PROCESSOS FISIOLÓGICOS
-- ---------------------------------------------------------------------
INSERT INTO processo_fisiologico (nome, sistema, descricao, fatores_estimulam, fatores_inibem) VALUES
('Lipólise','tecido_adiposo',
 'Hidrólise de triglicerídeos em ácidos graxos livres e glicerol, mobilizando energia do adipócito.',
 ARRAY['déficit calórico','catecolaminas','glucagon','jejum','exercício'],
 ARRAY['insulina alta','hiperalimentação']),
('Beta-oxidação','mitocondrial',
 'Oxidação mitocondrial de ácidos graxos para gerar ATP; etapa onde a gordura é efetivamente "queimada".',
 ARRAY['demanda energética','disponibilidade de ácidos graxos','exercício aeróbio'],
 ARRAY['excesso de carboidrato','sedentarismo']),
('Termogênese adaptativa','endocrino',
 'Redução do gasto energético além do esperado pela perda de massa, dificultando o emagrecimento contínuo (platô).',
 ARRAY['restrição calórica prolongada','perda de massa magra'],
 ARRAY['treino de força','ingestão proteica adequada']),
('Síntese de colágeno','tegumentar',
 'Produção de colágeno por fibroblastos; determina firmeza e capacidade de retração da pele.',
 ARRAY['vitamina C','proteína adequada','exercício resistido'],
 ARRAY['tabagismo','fotoenvelhecimento','déficit proteico','idade avançada']),
('Preservação de massa magra','musculoesqueletico',
 'Manutenção de massa muscular durante o déficit calórico, sustentando a TMB e a função.',
 ARRAY['treino de força','proteína 1,2–1,5 g/kg (sob orientação)','distribuição proteica'],
 ARRAY['déficit agressivo','imobilidade','ingestão proteica insuficiente']);

-- ---------------------------------------------------------------------
-- HORMÔNIOS E EFEITOS
-- ---------------------------------------------------------------------
INSERT INTO hormonio (nome, origem, funcao_resumo) VALUES
('Insulina','pâncreas (células beta)','Anabólico; favorece estocagem e inibe lipólise.'),
('Glucagon','pâncreas (células alfa)','Catabólico; estimula lipólise e glicogenólise.'),
('Leptina','tecido adiposo','Sinaliza estoque energético; reduz apetite (resistência é comum na obesidade).'),
('GLP-1','células L do intestino','Incretina; aumenta saciedade e retarda esvaziamento gástrico.'),
('Cortisol','adrenal','Catabólico em excesso; favorece adiposidade visceral quando cronicamente elevado.'),
('Catecolaminas','adrenal/SNS','Estimulam lipólise e termogênese.');

INSERT INTO hormonio_efeito (hormonio_id, processo_id, direcao, descricao)
SELECT h.id, p.id, v.direcao, v.descricao
FROM (VALUES
 ('Insulina','Lipólise','inibe','Suprime a lipólise; níveis cronicamente altos dificultam a mobilização de gordura.'),
 ('Glucagon','Lipólise','estimula','Promove mobilização de ácidos graxos no jejum.'),
 ('Catecolaminas','Lipólise','estimula','Ativam lipólise via receptores beta-adrenérgicos.'),
 ('GLP-1','Preservação de massa magra','modula','Reduz ingestão; risco de perda de massa magra se proteína/treino forem insuficientes.')
) AS v(horm, proc, direcao, descricao)
JOIN hormonio h ON h.nome = v.horm
JOIN processo_fisiologico p ON p.nome = v.proc;

-- ---------------------------------------------------------------------
-- MEDICAMENTOS
-- ---------------------------------------------------------------------
INSERT INTO medicamento (nome_generico, nomes_comerciais, classe, mecanismo_acao, indicacao_aprovada, via, requer_prescricao) VALUES
('Semaglutida', ARRAY['Ozempic','Wegovy'], 'agonista_GLP1',
 'Agonista do receptor de GLP-1: aumenta saciedade, retarda esvaziamento gástrico, reduz ingestão calórica.',
 'Obesidade/sobrepeso com comorbidade; DM2 (conforme apresentação).', 'subcutânea', TRUE),
('Tirzepatida', ARRAY['Mounjaro','Zepbound'], 'agonista_duplo_GIP_GLP1',
 'Agonista duplo de receptores GIP e GLP-1; efeito sobre saciedade e controle glicêmico.',
 'Obesidade/sobrepeso com comorbidade; DM2 (conforme apresentação).', 'subcutânea', TRUE),
('Liraglutida', ARRAY['Saxenda','Victoza'], 'agonista_GLP1',
 'Agonista GLP-1 de aplicação diária.',
 'Obesidade; DM2 (conforme apresentação).', 'subcutânea', TRUE),
('Orlistate', ARRAY['Xenical','Alli'], 'inibidor_lipase',
 'Inibe lipases gastrointestinais, reduzindo absorção de gordura dietética (~30%).',
 'Obesidade.', 'oral', TRUE);

INSERT INTO medicamento_efeito_adverso (medicamento_id, descricao, frequencia, gravidade)
SELECT m.id, v.descricao, v.freq, v.grav
FROM (VALUES
 ('Semaglutida','Náusea, vômito, diarreia, constipação (geralmente transitórios).','muito_comum','leve'),
 ('Semaglutida','Perda de massa magra se proteína/atividade física forem inadequadas.','comum','moderada'),
 ('Tirzepatida','Sintomas gastrointestinais dose-dependentes.','muito_comum','leve'),
 ('Orlistate','Esteatorreia e urgência fecal com dieta rica em gordura.','comum','leve')
) AS v(med, descricao, freq, grav)
JOIN medicamento m ON m.nome_generico = v.med;

INSERT INTO medicamento_efeito_metabolico (medicamento_id, processo_id, descricao)
SELECT m.id, p.id, v.descricao
FROM (VALUES
 ('Semaglutida','Termogênese adaptativa','A perda rápida pode acentuar adaptação metabólica; treino de força e proteína mitigam.'),
 ('Tirzepatida','Preservação de massa magra','Redução acentuada de ingestão exige atenção à proteína para preservar massa magra.')
) AS v(med, proc, descricao)
JOIN medicamento m ON m.nome_generico = v.med
JOIN processo_fisiologico p ON p.nome = v.proc;

-- ---------------------------------------------------------------------
-- NUTRIENTES E FUNÇÕES
-- ---------------------------------------------------------------------
INSERT INTO nutriente (nome, tipo, funcao_resumo) VALUES
('Proteína','macro','Substrato para massa magra, saciedade e cicatrização; prioritária no pós-bariátrico.'),
('Vitamina C','vitamina','Cofator essencial da síntese de colágeno.'),
('Ferro','mineral','Transporte de oxigênio; deficiência comum após RYGB.'),
('Vitamina B12','vitamina','Hematopoese e função neurológica; absorção reduzida pós-bariátrico.'),
('Vitamina D','vitamina','Saúde óssea e muscular; deficiência frequente.'),
('Cálcio','mineral','Saúde óssea; absorção alterada após desvio intestinal.'),
('Colágeno hidrolisado','suplemento','Fornece peptídeos; evidência de benefício cutâneo é heterogênea (verificar).');

INSERT INTO nutriente_funcao (nutriente_id, processo_id, descricao, relevancia_pos_bariatrica)
SELECT n.id, p.id, v.descricao, v.pos_bar
FROM (VALUES
 ('Proteína','Preservação de massa magra','Ingestão adequada preserva massa magra durante o déficit.', TRUE),
 ('Proteína','Síntese de colágeno','Aporte de aminoácidos para matriz dérmica.', TRUE),
 ('Vitamina C','Síntese de colágeno','Cofator da prolil/lisil-hidroxilase na formação do colágeno.', TRUE),
 ('Ferro',NULL,'Reposição frequentemente necessária após RYGB.', TRUE),
 ('Vitamina B12',NULL,'Suplementação geralmente indicada após desvio gástrico.', TRUE)
) AS v(nut, proc, descricao, pos_bar)
JOIN nutriente n ON n.nome = v.nut
LEFT JOIN processo_fisiologico p ON p.nome = v.proc;

-- ---------------------------------------------------------------------
-- CONTEXTOS CLÍNICOS
-- ---------------------------------------------------------------------
INSERT INTO contexto_clinico (slug, nome, descricao, fase_temporal) VALUES
('pos_rygb_0_12m','Pós-bypass (RYGB) — 0 a 12 meses','Fase de perda acelerada após Roux-en-Y; alto risco de deficiências e perda de massa magra.','0_3m'),
('pos_sleeve_0_12m','Pós-sleeve — 0 a 12 meses','Gastrectomia vertical; perda acelerada com restrição de volume.','0_3m'),
('uso_glp1','Uso de agonista GLP-1/GIP','Tratamento farmacológico com redução acentuada de ingestão.','manutencao'),
('perda_acelerada','Perda ponderal acelerada','Ritmo de perda elevado, com risco metabólico e cutâneo.','3_12m'),
('pele_redundante','Pele redundante pós-perda','Excesso cutâneo após grande perda ponderal.','12_24m'),
('plato_metabolico','Platô metabólico','Estagnação da perda por adaptação metabólica.','manutencao');

-- ---------------------------------------------------------------------
-- CONCEITOS (núcleo semântico) + RELAÇÕES
-- ---------------------------------------------------------------------
INSERT INTO conceito (categoria_id, slug, nome, definicao, sinonimos, nivel_evidencia)
SELECT c.id, v.slug, v.nome, v.definicao, v.sinonimos, v.ne::nivel_evidencia
FROM (VALUES
 ('mobilizacao_gordura','deficit_calorico','Déficit calórico',
  'Estado em que o gasto energético excede a ingestão, condição necessária para a perda de gordura.',
  ARRAY['balanço energético negativo'], 'fisiologia_estabelecida'),
 ('adaptacao_metabolica','termogenese_adaptativa','Termogênese adaptativa',
  'Queda do gasto energético acima do previsto pela perda de massa, que favorece o platô.',
  ARRAY['adaptação metabólica','metabolic adaptation'], 'fisiologia_estabelecida'),
 ('elasticidade','retracao_cutanea','Retração cutânea',
  'Capacidade da pele de se readaptar após perda de volume, dependente de colágeno, elastina, idade e velocidade da perda.',
  ARRAY['elasticidade da pele','skin retraction'], 'fisiologia_estabelecida'),
 ('proteina','preservacao_muscular','Preservação muscular no déficit',
  'Estratégia de manter massa magra durante o emagrecimento via proteína e treino de força.',
  ARRAY['muscle sparing'], 'diretriz_clinica')
) AS v(cat_slug, slug, nome, definicao, sinonimos, ne)
JOIN categoria c ON c.slug = v.cat_slug;

INSERT INTO conceito_relacao (origem_id, destino_id, tipo, nota)
SELECT o.id, d.id, v.tipo::tipo_relacao_conceito, v.nota
FROM (VALUES
 ('deficit_calorico','termogenese_adaptativa','e_causa_de','Déficit prolongado pode disparar adaptação.'),
 ('preservacao_muscular','termogenese_adaptativa','antagoniza','Preservar massa magra atenua a queda da TMB.')
) AS v(origem, destino, tipo, nota)
JOIN conceito o ON o.slug = v.origem
JOIN conceito d ON d.slug = v.destino;

-- ---------------------------------------------------------------------
-- DOCUMENTOS + CHUNKS (embedding gerado na ingestão -> NULL aqui)
-- ---------------------------------------------------------------------
INSERT INTO documento_conhecimento (titulo, dominio_id, conteudo_md, nivel_evidencia)
SELECT v.titulo, d.id, v.conteudo, v.ne::nivel_evidencia
FROM (VALUES
 ('Como a gordura é mobilizada e oxidada','metabolismo_lipidico',
  'A perda de gordura exige déficit energético sustentado. No déficit, cai a insulina e sobem catecolaminas e glucagon, ativando a lipólise: triglicerídeos do adipócito são hidrolisados em ácidos graxos e glicerol. Os ácidos graxos são transportados às mitocôndrias e oxidados (beta-oxidação) para gerar ATP. "Queimar gordura" depende, portanto, de demanda energética real, não de um alimento ou exercício isolado.',
  'fisiologia_estabelecida'),
 ('Perda de massa magra e platô na perda acelerada','metabolismo_energetico',
  'Perda ponderal rápida — por dieta agressiva, fármacos GLP-1/GIP ou pós-bariátrica — tende a sacrificar massa magra junto com gordura. Menos massa magra reduz a taxa metabólica basal e, somada à termogênese adaptativa, produz platô. Treino de força e ingestão proteica adequada (sob orientação profissional) são as principais estratégias de mitigação.',
  'diretriz_clinica'),
 ('Pele redundante após grande perda ponderal','tecido_tegumentar',
  'A retração da pele depende de colágeno e elastina, idade, magnitude e velocidade da perda, exposição solar e tabagismo. Perdas muito rápidas e de grande magnitude aumentam a chance de pele redundante. Nutrição proteica, vitamina C, hidratação e cessação do tabagismo apoiam a matriz dérmica; casos significativos podem requerer avaliação para cirurgia de contorno corporal.',
  'fisiologia_estabelecida'),
 ('Deficiências nutricionais no pós-bariátrico','pos_bariatrico',
  'Após RYGB e, em menor grau, sleeve, há risco elevado de deficiência de ferro, vitamina B12, vitamina D, cálcio, folato e tiamina, por menor ingestão e absorção. A suplementação e o monitoramento laboratorial seguem diretrizes de sociedades de cirurgia bariátrica e devem ser conduzidos por equipe clínica.',
  'diretriz_clinica')
) AS v(titulo, dom_slug, conteudo, ne)
JOIN dominio_conhecimento d ON d.slug = v.dom_slug;

-- Um chunk por documento (exemplo; ingestão real faz chunking + embedding)
INSERT INTO chunk_conhecimento
   (documento_id, ordem, texto, dominio_slug, contexto_slugs, nivel_evidencia, requer_supervisao_medica)
SELECT doc.id, 1, doc.conteudo_md,
       dom.slug,
       v.contextos,
       doc.nivel_evidencia,
       v.supervisao
FROM (VALUES
 ('Como a gordura é mobilizada e oxidada', ARRAY['perda_acelerada'], FALSE),
 ('Perda de massa magra e platô na perda acelerada', ARRAY['perda_acelerada','plato_metabolico','uso_glp1'], FALSE),
 ('Pele redundante após grande perda ponderal', ARRAY['pele_redundante','perda_acelerada'], FALSE),
 ('Deficiências nutricionais no pós-bariátrico', ARRAY['pos_rygb_0_12m','pos_sleeve_0_12m'], TRUE)
) AS v(titulo, contextos, supervisao)
JOIN documento_conhecimento doc ON doc.titulo = v.titulo
JOIN dominio_conhecimento dom ON dom.id = doc.dominio_id;

-- ---------------------------------------------------------------------
-- RECOMENDAÇÕES + REGRAS + LASTRO
-- ---------------------------------------------------------------------
INSERT INTO recomendacao (slug, titulo, corpo_md, forca, nivel_evidencia, requer_supervisao_medica) VALUES
('priorizar_proteina_massa_magra',
 'Priorizar proteína e treino de força para preservar massa magra',
 'Durante perda acelerada, manter ingestão proteica adequada e treino resistido ajuda a preservar massa magra, sustentar a TMB e reduzir o platô. Metas individuais de proteína devem ser definidas por nutricionista/médico, sobretudo no pós-bariátrico.',
 'forte_a_favor','diretriz_clinica', FALSE),
('cuidados_pele_perda_grande',
 'Cuidados com a pele em grande perda ponderal',
 'Aporte proteico, vitamina C, hidratação e cessação do tabagismo apoiam a matriz dérmica. A retração é parcialmente limitada por idade e velocidade da perda; excesso significativo pode demandar avaliação para contorno corporal.',
 'condicional_a_favor','fisiologia_estabelecida', FALSE),
('monitorar_micronutrientes_pos_bariatrico',
 'Monitorar e repor micronutrientes no pós-bariátrico',
 'Após RYGB/sleeve há risco de deficiência de ferro, B12, D, cálcio, folato e tiamina. Suplementação e exames de acompanhamento devem seguir a equipe cirúrgica. Esta orientação não substitui o protocolo do serviço.',
 'forte_a_favor','diretriz_clinica', TRUE);

-- Lastro de evidência
INSERT INTO recomendacao_fonte (recomendacao_id, fonte_id)
SELECT r.id, f.id
FROM (VALUES
 ('priorizar_proteina_massa_magra','Diretrizes perioperatórias de suporte nutricional e metabólico em cirurgia bariátrica'),
 ('monitorar_micronutrientes_pos_bariatrico','Diretrizes perioperatórias de suporte nutricional e metabólico em cirurgia bariátrica')
) AS v(rec_slug, fonte_titulo)
JOIN recomendacao r ON r.slug = v.rec_slug
JOIN fonte f ON f.titulo = v.fonte_titulo;

-- Processo-alvo
INSERT INTO recomendacao_processo (recomendacao_id, processo_id)
SELECT r.id, p.id
FROM (VALUES
 ('priorizar_proteina_massa_magra','Preservação de massa magra'),
 ('cuidados_pele_perda_grande','Síntese de colágeno')
) AS v(rec_slug, proc_nome)
JOIN recomendacao r ON r.slug = v.rec_slug
JOIN processo_fisiologico p ON p.nome = v.proc_nome;

-- Regras de elegibilidade (contexto + condição de métrica declarativa)
INSERT INTO regra_recomendacao (recomendacao_id, contexto_id, condicao_metrica, prioridade)
SELECT r.id, ctx.id, v.cond::jsonb, v.prio
FROM (VALUES
 ('priorizar_proteina_massa_magra','uso_glp1', NULL, 10),
 ('priorizar_proteina_massa_magra','plato_metabolico', NULL, 10),
 ('cuidados_pele_perda_grande','pele_redundante', NULL, 20),
 ('cuidados_pele_perda_grande','perda_acelerada',
   '{"all":[{"biomarcador":"rca","op":">","valor":0.5}]}', 30),
 ('monitorar_micronutrientes_pos_bariatrico','pos_rygb_0_12m', NULL, 5),
 ('monitorar_micronutrientes_pos_bariatrico','pos_sleeve_0_12m', NULL, 5)
) AS v(rec_slug, ctx_slug, cond, prio)
JOIN recomendacao r ON r.slug = v.rec_slug
JOIN contexto_clinico ctx ON ctx.slug = v.ctx_slug;

-- ---------------------------------------------------------------------
-- GOVERNANÇA: CONTRAINDICAÇÕES E GATILHOS DE ESCALONAMENTO
-- ---------------------------------------------------------------------
INSERT INTO contraindicacao (descricao, contexto_id, gravidade)
SELECT v.descricao, ctx.id, v.grav
FROM (VALUES
 ('Não emitir metas calóricas/nutricionais numéricas sem supervisão profissional no pós-bariátrico.',
  'pos_rygb_0_12m','grave')
) AS v(descricao, ctx_slug, grav)
JOIN contexto_clinico ctx ON ctx.slug = v.ctx_slug;

INSERT INTO gatilho_escalonamento (tipo, descricao, palavras_chave, acao) VALUES
('sinal_transtorno_alimentar',
 'Indícios de restrição extrema, compulsão, purgação ou metas de peso inseguras.',
 ARRAY['parar de comer','jejum extremo','vomitar','não comer nada','meta muito baixa'],
 'encaminhar_profissional'),
('meta_perda_peso_insegura',
 'Pedido de perda muito rápida ou abaixo de faixas seguras.',
 ARRAY['perder 10kg em uma semana','o mais rápido possível','sem comer'],
 'encaminhar_profissional'),
('risco_hidroeletrolitico',
 'Relato de fraqueza intensa, tontura, arritmia, vômitos persistentes pós-bariátricos.',
 ARRAY['desmaio','palpitação','vômito sem parar','muita fraqueza'],
 'encaminhar_profissional'),
('uso_medicamento_off_label',
 'Uso de GLP-1/GIP sem prescrição, dose própria ou sem comorbidade indicada.',
 ARRAY['comprei sem receita','aumentei a dose sozinho','manipulado'],
 'encaminhar_profissional'),
('gestacao_lactacao',
 'Gestação/lactação com pedido de emagrecimento ou uso de antiobesidade.',
 ARRAY['grávida','gestante','amamentando'],
 'bloquear');

COMMIT;

-- =====================================================================
-- FIM DO SEED
-- =====================================================================
