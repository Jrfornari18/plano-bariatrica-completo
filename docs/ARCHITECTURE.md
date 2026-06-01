# Documentação de Arquitetura: Barifit+ Flutter App

## 1. Visão Geral

O Barifit+ é um aplicativo móvel construído em Flutter, focado no acompanhamento pós-bariátrico. A aplicação foi desenhada com uma abordagem **Offline-First**, garantindo que os usuários tenham acesso contínuo aos seus dados de treinos, refeições e evolução corporal, mesmo sem conexão à internet.

## 2. Padrão Arquitetural

A aplicação segue a **Clean Architecture** combinada com **Feature-First Structure**, promovendo separação clara de responsabilidades e alta testabilidade.

### 2.1 Estrutura de Diretórios

```text
lib/
├── core/                  # Recursos compartilhados e infraestrutura
│   ├── constants/         # Constantes, chaves, enums globais
│   ├── services/          # Serviços nativos (Notificações, Sync)
│   └── theme/             # Design System (Cores, Tipografia, Espaçamentos)
├── data/                  # Camada de Dados
│   └── models/            # Modelos de domínio (User, Workout, Meal, ScanBody)
├── presentation/          # Camada de Apresentação (UI)
│   ├── providers/         # Gerenciamento de Estado (ChangeNotifier)
│   ├── screens/           # Telas divididas por feature (auth, home, meals...)
│   └── widgets/           # Componentes UI reutilizáveis (common)
└── main.dart              # Ponto de entrada e injeção de dependências
```

## 3. Gerenciamento de Estado

O projeto utiliza o pacote `provider` (versão `^6.1.2`) para injeção de dependência e reatividade.

- **Abordagem**: `ChangeNotifier` com `MultiProvider` no nível raiz da aplicação.
- **Providers Principais**:
  - `AuthProvider`: Gerencia a sessão do usuário, fase do programa e biometria.
  - `WorkoutProvider`: Controla o calendário de treinos, exercícios e status de conclusão.
  - `MealProvider`: Gerencia a dieta diária, macros, hidratação e catálogo de receitas.
  - `ScanbodyProvider`: Processa o histórico de medidas, fotos e gráficos de evolução.
  - `ChatProvider`: Mantém o contexto e histórico da Babi IA.

## 4. Persistência de Dados e Sincronização

A estratégia de dados é baseada no conceito **Offline-First**:

1. **Cache Local**: Utiliza `hive` e `hive_flutter` para armazenamento NoSQL rápido de todos os modelos principais.
2. **Preferências**: `shared_preferences` para configurações leves (tema, onboarding, tokens).
3. **Sincronização**: O `SyncService` monitora o estado da rede via `connectivity_plus` e realiza background sync com a API REST usando `dio` quando a conexão é restabelecida.

## 5. Serviços Nativos

- **Notificações Push**: `flutter_local_notifications` combinado com `timezone` para agendamento local (lembretes de água a cada 2h, refeições e treinos).
- **Câmera e Galeria**: Integração via `camera` e `image_picker` para o módulo ScanBody, com gerenciamento estrito via `permission_handler`.
- **Biometria**: Proteção de dados sensíveis de saúde usando `local_auth` (FaceID/TouchID).

## 6. Integração com Inteligência Artificial

O módulo "Babi IA" é o core inteligente do aplicativo:

- **Contexto Dinâmico**: A IA recebe silenciosamente o contexto do usuário (fase atual, IMC, restrições alimentares) a cada prompt.
- **Comunicação**: Implementada usando `dart_openai` para chamadas diretas ou via backend próprio, dependendo da configuração de ambiente.

## 7. Design System

Todo o design está centralizado em `lib/core/theme/app_theme.dart`.

- **Cores Semânticas**: Baseado em tons de azul (Primary: `0xFF2563EB`) e verde (Secondary: `0xFF10B981`).
- **Tipografia**: Família de fontes `Inter` para legibilidade máxima.
- **Componentização**: Uso de botões, inputs e cards padronizados (`BarifitButton`, `BarifitTextField`) para garantir consistência visual em todas as telas.
