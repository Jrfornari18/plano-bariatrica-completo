-- =====================================================================
-- BodyScan KB — Esquema de base de conhecimento (fisiologia / emagrecimento)
-- Alvo: PostgreSQL >= 14 + extensão pgvector >= 0.5
-- Objetivo: base de conhecimento estruturada + vetorial para RAG e
--           camada de recomendação de IA Generativa com governança clínica.
-- Codificação de embeddings: vector(384) (configurável — ver NOTA 1).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. EXTENSÕES
-- ---------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;      -- busca vetorial (RAG)
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- busca lexical/fuzzy (híbrida)
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- gen_random_uuid()

-- NOTA 1: a dimensão do embedding deve corresponder ao modelo usado.
--   1536 = text-embedding-3-small (OpenAI). Para modelos locais
--   (ex.: e5-large = 1024, BGE-m3 = 1024, MiniLM = 384) ajuste vector(N)
--   em TODA coluna `embedding` antes de criar índices.

-- ---------------------------------------------------------------------
-- 1. TIPOS / DOMÍNIOS CONTROLADOS
-- ---------------------------------------------------------------------

-- Hierarquia de evidência (adaptada de GRADE / Oxford CEBM)
CREATE TYPE nivel_evidencia AS ENUM (
    'diretriz_clinica',      -- guideline de sociedade médica
    'revisao_sistematica',   -- meta-análise / RS
    'ensaio_clinico',        -- RCT
    'coorte_observacional',
    'consenso_especialista',
    'fisiologia_estabelecida',-- conhecimento de base, livro-texto
    'nao_verificado'         -- pendente de validação (bloqueia uso clínico)
);

-- Força/segurança de uma recomendação ao ser emitida
CREATE TYPE forca_recomendacao AS ENUM (
    'forte_a_favor',
    'condicional_a_favor',
    'neutra_informativa',
    'condicional_contra',
    'forte_contra'
);

-- Categoria de gatilho de escalonamento (human-in-the-loop)
CREATE TYPE tipo_alerta AS ENUM (
    'sinal_transtorno_alimentar',
    'risco_hidroeletrolitico',
    'deficiencia_nutricional_grave',
    'uso_medicamento_off_label',
    'interacao_medicamentosa',
    'sintoma_clinico_urgente',
    'meta_perda_peso_insegura',
    'gestacao_lactacao'
);

CREATE TYPE tipo_relacao_conceito AS ENUM (
    'regula', 'inibe', 'estimula', 'precede',
    'e_causa_de', 'e_consequencia_de', 'depende_de', 'antagoniza'
);

-- ---------------------------------------------------------------------
-- 2. TAXONOMIA E FONTES (camada de governança)
-- ---------------------------------------------------------------------

CREATE TABLE dominio_conhecimento (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug         TEXT UNIQUE NOT NULL,          -- 'metabolismo_lipidico'
    nome         TEXT NOT NULL,
    descricao    TEXT,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE categoria (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dominio_id   UUID NOT NULL REFERENCES dominio_conhecimento(id) ON DELETE CASCADE,
    slug         TEXT NOT NULL,
    nome         TEXT NOT NULL,
    descricao    TEXT,
    UNIQUE (dominio_id, slug)
);

-- Fonte = referência rastreável (diretriz, paper, livro, órgão oficial).
-- requer_verificacao = TRUE impede que conteúdo dependente seja servido
-- como recomendação clínica até validação humana.
CREATE TABLE fonte (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo           TEXT NOT NULL,
    autores          TEXT,                 -- formato Vancouver quando aplicável
    instituicao      TEXT,                 -- ASMBS, WHO, Endocrine Society...
    ano              INT,
    doi              TEXT,
    url              TEXT,
    nivel_evidencia  nivel_evidencia NOT NULL DEFAULT 'nao_verificado',
    requer_verificacao BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 3. NÚCLEO SEMÂNTICO: CONCEITOS E PROCESSOS FISIOLÓGICOS
-- ---------------------------------------------------------------------

CREATE TABLE conceito (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    categoria_id  UUID NOT NULL REFERENCES categoria(id),
    slug          TEXT UNIQUE NOT NULL,
    nome          TEXT NOT NULL,
    definicao     TEXT NOT NULL,
    sinonimos     TEXT[],                  -- termos alternativos p/ busca
    nivel_evidencia nivel_evidencia NOT NULL DEFAULT 'fisiologia_estabelecida',
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Grafo de conhecimento leve: relações tipadas entre conceitos
CREATE TABLE conceito_relacao (
    origem_id    UUID NOT NULL REFERENCES conceito(id) ON DELETE CASCADE,
    destino_id   UUID NOT NULL REFERENCES conceito(id) ON DELETE CASCADE,
    tipo         tipo_relacao_conceito NOT NULL,
    nota         TEXT,
    PRIMARY KEY (origem_id, destino_id, tipo)
);

-- Processo fisiológico (lipólise, beta-oxidação, termogênese, síntese de colágeno)
CREATE TABLE processo_fisiologico (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conceito_id   UUID REFERENCES conceito(id),
    nome          TEXT NOT NULL,
    sistema       TEXT,                    -- 'tecido_adiposo', 'tegumentar', 'endocrino'
    descricao     TEXT NOT NULL,
    fatores_estimulam TEXT[],
    fatores_inibem    TEXT[]
);

-- ---------------------------------------------------------------------
-- 4. ENTIDADES DE DOMÍNIO ESPECÍFICAS
-- ---------------------------------------------------------------------

-- 4.1 Hormônios e sinalizadores metabólicos
CREATE TABLE hormonio (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome          TEXT UNIQUE NOT NULL,
    origem        TEXT,                    -- pâncreas, tec. adiposo, intestino...
    funcao_resumo TEXT NOT NULL
);

CREATE TABLE hormonio_efeito (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hormonio_id   UUID NOT NULL REFERENCES hormonio(id) ON DELETE CASCADE,
    processo_id   UUID REFERENCES processo_fisiologico(id),
    direcao       TEXT NOT NULL CHECK (direcao IN ('estimula','inibe','modula')),
    descricao     TEXT
);

-- 4.2 Medicamentos (anti-obesidade / pós-bariátrico)
CREATE TABLE medicamento (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_generico   TEXT UNIQUE NOT NULL,  -- semaglutida, tirzepatida...
    nomes_comerciais TEXT[],
    classe          TEXT NOT NULL,         -- 'agonista_GLP1', 'GIP_GLP1', ...
    mecanismo_acao  TEXT NOT NULL,
    indicacao_aprovada TEXT,
    via             TEXT,                  -- subcutânea, oral
    requer_prescricao BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE medicamento_efeito_metabolico (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medicamento_id UUID NOT NULL REFERENCES medicamento(id) ON DELETE CASCADE,
    processo_id   UUID REFERENCES processo_fisiologico(id),
    descricao     TEXT NOT NULL
);

CREATE TABLE medicamento_efeito_adverso (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medicamento_id UUID NOT NULL REFERENCES medicamento(id) ON DELETE CASCADE,
    descricao     TEXT NOT NULL,
    frequencia    TEXT,                    -- 'muito_comum','comum','raro'
    gravidade     TEXT                     -- 'leve','moderada','grave'
);

-- 4.3 Nutrientes / suplementos (proteína, colágeno, ferro, B12, vit. C, D)
CREATE TABLE nutriente (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome          TEXT UNIQUE NOT NULL,
    tipo          TEXT,                    -- 'macro','vitamina','mineral','suplemento'
    funcao_resumo TEXT NOT NULL
);

CREATE TABLE nutriente_funcao (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nutriente_id  UUID NOT NULL REFERENCES nutriente(id) ON DELETE CASCADE,
    processo_id   UUID REFERENCES processo_fisiologico(id),
    descricao     TEXT NOT NULL,
    relevancia_pos_bariatrica BOOLEAN NOT NULL DEFAULT FALSE
);

-- 4.4 Contextos clínicos (chave para a recomendação)
-- Ex.: pós-bypass RYGB, pós-sleeve, uso de GLP-1, perda ponderal acelerada,
--      pele redundante, platô metabólico.
CREATE TABLE contexto_clinico (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug          TEXT UNIQUE NOT NULL,
    nome          TEXT NOT NULL,
    descricao     TEXT NOT NULL,
    fase_temporal TEXT                     -- 'pre_op','0_3m','3_12m','12_24m','manutencao'
);

-- 4.5 Biomarcadores / métricas (ponte com o app BodyScan)
CREATE TABLE biomarcador (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug          TEXT UNIQUE NOT NULL,    -- 'imc','rcq','rca','perc_gordura','massa_magra'
    nome          TEXT NOT NULL,
    unidade       TEXT,
    descricao     TEXT,
    faixa_referencia JSONB                 -- {"baixo": ..., "alto": ...} por sexo/idade
);

-- ---------------------------------------------------------------------
-- 5. CAMADA DOCUMENTAL E VETORIAL (RAG)
-- ---------------------------------------------------------------------

-- Documento curado de conhecimento (pode referenciar conceito/contexto)
CREATE TABLE documento_conhecimento (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo        TEXT NOT NULL,
    dominio_id    UUID REFERENCES dominio_conhecimento(id),
    conteudo_md   TEXT NOT NULL,           -- markdown-fonte (auditável)
    nivel_evidencia nivel_evidencia NOT NULL DEFAULT 'fisiologia_estabelecida',
    idioma        TEXT NOT NULL DEFAULT 'pt-BR',
    versao        INT NOT NULL DEFAULT 1,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Chunk = unidade de recuperação. Embedding + metadados para filtragem.
CREATE TABLE chunk_conhecimento (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id    UUID NOT NULL REFERENCES documento_conhecimento(id) ON DELETE CASCADE,
    ordem           INT NOT NULL,
    texto           TEXT NOT NULL,
    embedding       vector(384),          -- ver NOTA 1
    tokens          INT,
    -- metadados desnormalizados p/ filtragem barata no momento da busca
    dominio_slug    TEXT,
    contexto_slugs  TEXT[],                -- contextos clínicos cobertos
    nivel_evidencia nivel_evidencia NOT NULL DEFAULT 'fisiologia_estabelecida',
    requer_supervisao_medica BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Procedência: vincula chunk -> fonte (rastreabilidade obrigatória)
CREATE TABLE chunk_fonte (
    chunk_id   UUID NOT NULL REFERENCES chunk_conhecimento(id) ON DELETE CASCADE,
    fonte_id   UUID NOT NULL REFERENCES fonte(id) ON DELETE CASCADE,
    PRIMARY KEY (chunk_id, fonte_id)
);

-- ---------------------------------------------------------------------
-- 6. CAMADA DE RECOMENDAÇÃO
-- ---------------------------------------------------------------------

-- Item de recomendação reutilizável (ação, orientação, alerta educativo)
CREATE TABLE recomendacao (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            TEXT UNIQUE NOT NULL,
    titulo          TEXT NOT NULL,
    corpo_md        TEXT NOT NULL,
    forca           forca_recomendacao NOT NULL DEFAULT 'neutra_informativa',
    nivel_evidencia nivel_evidencia NOT NULL DEFAULT 'fisiologia_estabelecida',
    requer_supervisao_medica BOOLEAN NOT NULL DEFAULT FALSE,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE
);

-- Lastro de evidência da recomendação (N:N com fonte)
CREATE TABLE recomendacao_fonte (
    recomendacao_id UUID NOT NULL REFERENCES recomendacao(id) ON DELETE CASCADE,
    fonte_id        UUID NOT NULL REFERENCES fonte(id) ON DELETE CASCADE,
    PRIMARY KEY (recomendacao_id, fonte_id)
);

-- Vínculo recomendação <-> processo fisiológico-alvo
CREATE TABLE recomendacao_processo (
    recomendacao_id UUID NOT NULL REFERENCES recomendacao(id) ON DELETE CASCADE,
    processo_id     UUID NOT NULL REFERENCES processo_fisiologico(id) ON DELETE CASCADE,
    PRIMARY KEY (recomendacao_id, processo_id)
);

-- Regra de elegibilidade: mapeia contexto + condições de métrica -> recomendação.
-- `condicao_metrica` em JSONB permite regras declarativas avaliadas pelo backend.
-- Ex.: {"all": [{"biomarcador":"rca","op":">","valor":0.5}]}
CREATE TABLE regra_recomendacao (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recomendacao_id UUID NOT NULL REFERENCES recomendacao(id) ON DELETE CASCADE,
    contexto_id     UUID REFERENCES contexto_clinico(id),
    condicao_metrica JSONB,                -- regra declarativa (opcional)
    prioridade      INT NOT NULL DEFAULT 100,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- 7. GOVERNANÇA CLÍNICA E HUMAN-IN-THE-LOOP
-- ---------------------------------------------------------------------

-- Regras de contraindicação e interação (bloqueiam/qualificam recomendações)
CREATE TABLE contraindicacao (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descricao       TEXT NOT NULL,
    medicamento_id  UUID REFERENCES medicamento(id),
    contexto_id     UUID REFERENCES contexto_clinico(id),
    recomendacao_id UUID REFERENCES recomendacao(id),
    gravidade       TEXT NOT NULL DEFAULT 'moderada'  -- 'leve','moderada','grave'
);

-- Gatilhos de escalonamento: padrões que devem desviar para profissional humano.
-- A camada de IA deve detectar e NÃO emitir recomendação autônoma.
CREATE TABLE gatilho_escalonamento (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo          tipo_alerta NOT NULL,
    descricao     TEXT NOT NULL,
    palavras_chave TEXT[],                 -- termos/sinais detectáveis no input
    acao          TEXT NOT NULL            -- 'bloquear','encaminhar_profissional','exibir_recurso'
);

-- ---------------------------------------------------------------------
-- 8. PERFIL DO USUÁRIO E AUDITORIA (dados pessoais — minimizar/pseudonimizar)
-- ---------------------------------------------------------------------

CREATE TABLE perfil_usuario (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pseudonimo      TEXT UNIQUE NOT NULL,  -- nunca PII direta nesta tabela
    sexo_biologico  TEXT,
    faixa_etaria    TEXT,
    contexto_id     UUID REFERENCES contexto_clinico(id),
    consentimento_lgpd BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE perfil_metrica (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perfil_id     UUID NOT NULL REFERENCES perfil_usuario(id) ON DELETE CASCADE,
    biomarcador_id UUID NOT NULL REFERENCES biomarcador(id),
    valor         NUMERIC NOT NULL,
    medido_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Auditoria de cada recomendação emitida (rastreabilidade fim-a-fim)
CREATE TABLE log_recomendacao (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perfil_id       UUID REFERENCES perfil_usuario(id),
    recomendacao_id UUID REFERENCES recomendacao(id),
    chunks_recuperados UUID[],             -- IDs dos chunks usados no RAG
    modelo_gerador  TEXT,                  -- ex.: 'claude-opus-4-x'
    prompt_hash     TEXT,
    houve_escalonamento BOOLEAN NOT NULL DEFAULT FALSE,
    tipo_alerta_disparado tipo_alerta,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feedback_recomendacao (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_id        UUID NOT NULL REFERENCES log_recomendacao(id) ON DELETE CASCADE,
    util          BOOLEAN,
    comentario    TEXT,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 9. ÍNDICES
-- ---------------------------------------------------------------------

-- Busca vetorial (cosseno). HNSW: melhor recall/latência; exige pgvector>=0.5.
CREATE INDEX idx_chunk_embedding_hnsw
    ON chunk_conhecimento USING hnsw (embedding vector_cosine_ops);

-- Filtragem barata por metadados antes/depois do ANN
CREATE INDEX idx_chunk_dominio   ON chunk_conhecimento (dominio_slug);
CREATE INDEX idx_chunk_contexto  ON chunk_conhecimento USING gin (contexto_slugs);
CREATE INDEX idx_chunk_supervisao ON chunk_conhecimento (requer_supervisao_medica);

-- Busca lexical/híbrida (trigram) sobre o texto do chunk
CREATE INDEX idx_chunk_texto_trgm ON chunk_conhecimento USING gin (texto gin_trgm_ops);

CREATE INDEX idx_conceito_sinonimos ON conceito USING gin (sinonimos);
CREATE INDEX idx_regra_contexto ON regra_recomendacao (contexto_id) WHERE ativo;
CREATE INDEX idx_perfil_metrica_perfil ON perfil_metrica (perfil_id, biomarcador_id);

-- ---------------------------------------------------------------------
-- 10. VIEWS DE APOIO
-- ---------------------------------------------------------------------

-- Conteúdo "seguro para servir" sem supervisão (gate de governança)
CREATE VIEW vw_chunk_servivel AS
SELECT c.*
FROM chunk_conhecimento c
WHERE c.nivel_evidencia <> 'nao_verificado'
  AND c.requer_supervisao_medica = FALSE;

-- Recomendações com lastro de evidência consolidado
CREATE VIEW vw_recomendacao_com_evidencia AS
SELECT r.id, r.slug, r.titulo, r.forca, r.nivel_evidencia,
       r.requer_supervisao_medica,
       array_agg(DISTINCT f.titulo) FILTER (WHERE f.id IS NOT NULL) AS fontes
FROM recomendacao r
LEFT JOIN recomendacao_fonte rf ON rf.recomendacao_id = r.id
LEFT JOIN fonte f ON f.id = rf.fonte_id
WHERE r.ativo
GROUP BY r.id;

-- =====================================================================
-- FIM DO ESQUEMA
-- =====================================================================
