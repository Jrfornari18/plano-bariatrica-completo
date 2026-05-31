# Barifit+ App

> App mobile completo para acompanhamento pós-bariátrico — iOS & Android

---

## Visão Geral

O **Barifit+** é um aplicativo Flutter multiplataforma desenvolvido para o produto **Barifit+stack**, integrando todos os serviços da plataforma em uma experiência mobile nativa e fluida. O app é voltado para pacientes em processo pós-bariátrico, oferecendo ferramentas de monitoramento corporal, treinos personalizados, controle nutricional e suporte via IA.

---

## Funcionalidades Principais

| Módulo | Descrição |
|---|---|
| **ScanBody** | Análise de composição corporal via câmera, histórico de medidas e evolução visual |
| **Treinos** | Planos de treino personalizados, biblioteca de exercícios, timer e histórico |
| **Refeições** | Plano alimentar diário, macros, hidratação, suplementação e receitas |
| **Babi IA** | Assistente de saúde inteligente com contexto personalizado do usuário |
| **Dashboard** | Resumo diário, progresso, streaks e métricas de saúde |
| **Perfil** | Dados pessoais, configurações, notificações e sincronização |

---

## Arquitetura

```
barifit_app/
├── lib/
│   ├── core/
│   │   ├── theme/           # Design system (cores, tipografia, espaçamentos)
│   │   ├── constants/       # Constantes do app
│   │   └── services/        # Serviços (notificações, sync, API)
│   ├── data/
│   │   └── models/          # Modelos de dados (User, Workout, Meal, ScanBody, Chat)
│   └── presentation/
│       ├── providers/       # State management (Provider)
│       ├── screens/         # Telas do app
│       │   ├── auth/        # Splash, Onboarding, Login
│       │   ├── home/        # Dashboard e navegação principal
│       │   ├── scanbody/    # ScanBody e câmera
│       │   ├── workouts/    # Treinos e exercícios
│       │   ├── meals/       # Refeições, macros e receitas
│       │   └── chat/        # Bot Babi (IA)
│       └── widgets/         # Widgets reutilizáveis
├── android/                 # Configurações Android
├── ios/                     # Configurações iOS
└── assets/                  # Imagens, ícones, fontes e animações
```

---

## Design System

### Paleta de Cores

| Token | Hex | Uso |
|---|---|---|
| `primary` | `#2563EB` | Ações principais, links |
| `primaryDark` | `#1D4ED8` | Hover/pressed |
| `secondary` | `#10B981` | Sucesso, confirmações, refeições |
| `warning` | `#F59E0B` | Alertas, calorias |
| `danger` | `#EF4444` | Erros, proteína |
| `background` | `#F8FAFC` | Fundo geral |
| `surface` | `#FFFFFF` | Cards e superfícies |

### Tipografia

A fonte principal é **Inter** (Google Fonts), com pesos de 400 a 800.

---

## Stack Técnica

| Camada | Tecnologia |
|---|---|
| Framework | Flutter 3.x (Dart 3.x) |
| State Management | Provider |
| HTTP Client | Dio |
| Cache Local | SharedPreferences + Hive |
| Câmera | camera + image_picker |
| Notificações | flutter_local_notifications |
| Gráficos | fl_chart + percent_indicator |
| Animações | flutter_animate + Lottie |
| IA / Chat | OpenAI API (GPT-4) |
| Auth | flutter_secure_storage + local_auth |
| Conectividade | connectivity_plus |

---

## Configuração do Ambiente

### Pré-requisitos

- Flutter SDK `>=3.0.0`
- Dart SDK `>=3.0.0`
- Android Studio / Xcode
- Dispositivo físico ou emulador

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Jrfornari18/plano-bariatrica-completo.git
cd barifit_app

# 2. Instale as dependências
flutter pub get

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API

# 4. Execute o app
flutter run
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-...
BARIFIT_API_BASE_URL=https://api.barifit.pro/v1
BARIFIT_API_KEY=...
```

---

## Módulos em Detalhe

### ScanBody

O módulo ScanBody permite ao usuário fotografar seu corpo em posições padronizadas (frontal, lateral, costas) para análise de composição corporal. Os dados são enviados para a API do Barifit+ para processamento e comparação evolutiva.

**Funcionalidades:**
- Câmera com guias de posicionamento
- Histórico de scans com timeline visual
- Gráficos de evolução de peso, IMC e medidas
- Comparação lado a lado entre datas

### Treinos

Planos de treino personalizados de acordo com a fase pós-bariátrica do usuário, com progressão gradual e adaptação ao nível de condicionamento.

**Tipos de treino:**
- Musculação (força)
- Natação
- Caminhada/Corrida
- Calistenia
- Alongamento
- HIIT
- Descanso ativo

### Refeições

Controle nutricional completo com foco nas necessidades específicas do pós-bariátrico: alta proteína, baixo volume, suplementação obrigatória.

**Funcionalidades:**
- 6 refeições diárias programadas
- Macros em tempo real (proteína, carbs, gordura, fibras)
- Controle de hidratação (copos de água)
- Lembretes de suplementação
- Biblioteca de receitas adaptadas

### Bot Babi (IA)

Assistente de saúde inteligente powered by GPT-4, com contexto personalizado do usuário (fase pós-op, peso atual, treinos, refeições).

**Capacidades:**
- Responder dúvidas sobre nutrição pós-bariátrica
- Sugerir receitas e adaptações alimentares
- Orientar sobre exercícios e recuperação
- Monitorar sintomas e sugerir ações
- Motivação e suporte emocional

---

## Notificações

O app configura automaticamente lembretes para:

| Notificação | Horário |
|---|---|
| Hidratação | A cada 2h (8h–20h) |
| Refeições | Horários configurados |
| Treinos | Conforme plano |
| ScanBody | Toda segunda-feira, 8h |
| Suplementos | Café, almoço e jantar |

---

## Sincronização

O app usa uma estratégia **offline-first**:

1. Dados são salvos localmente primeiro (Hive + SharedPreferences)
2. Quando online, sincroniza com a API do Barifit+
3. Operações offline são enfileiradas e enviadas quando a conexão retorna
4. Cache tem validade configurável por tipo de dado

---

## Licença

Propriedade de **Barifit.pro** — Todos os direitos reservados.
