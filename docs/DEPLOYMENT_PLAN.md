# Plano de Implantação (Go-to-Market): Barifit+ App

Este documento descreve o processo passo a passo para compilar, assinar e publicar o aplicativo Barifit+ nas lojas de aplicativos (App Store e Google Play), além da configuração de infraestrutura.

## 1. Preparação da Infraestrutura

Antes da compilação final, as seguintes configurações devem estar estabelecidas:

1. **Variáveis de Ambiente**:
   - O arquivo `.env` de produção deve ser gerado contendo: `API_BASE_URL`, `OPENAI_API_KEY`, e `SENTRY_DSN` (para monitoramento de erros).
2. **Backend**:
   - Garantir que a API do Barifit+stack esteja escalonada e rodando em ambiente de produção (AWS/GCP).
3. **Analytics e Crashlytics**:
   - Integrar o Firebase (ou Sentry) para monitoramento de falhas e comportamento dos usuários.

## 2. CI/CD (Integração e Entrega Contínuas)

A automação do processo de build e testes será configurada via **GitHub Actions** ou **Codemagic**.

### Fluxo do Pipeline (main branch)
1. **Lint & Test**: Executa `flutter analyze` e `flutter test`.
2. **Build Android**: Gera o App Bundle (`.aab`) assinado.
3. **Build iOS**: Gera o arquivo `.ipa` assinado (requer runner macOS).
4. **Deploy Interno**: Envia builds automáticos para o Firebase App Distribution (Android) e TestFlight (iOS) para homologação interna.

## 3. Publicação no Google Play (Android)

### 3.1. Assinatura do App
1. Criar um Keystore de produção:
   ```bash
   keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
   ```
2. Configurar o arquivo `android/key.properties` com as credenciais do Keystore.
3. Atualizar o `build.gradle` (nível do app) para utilizar as chaves de assinatura em modo `release`.

### 3.2. Build e Upload
1. Gerar o App Bundle:
   ```bash
   flutter build appbundle --release --obfuscate --split-debug-info=./debug_info
   ```
2. Acessar o **Google Play Console**, criar uma nova release na faixa de Produção (ou Teste Fechado) e fazer upload do arquivo `.aab`.

## 4. Publicação na App Store (iOS)

### 4.1. Assinatura e Certificados
1. Acessar o **Apple Developer Portal**.
2. Criar um *App ID* explícito e gerar os certificados de Distribuição e Provisioning Profiles (App Store).
3. Abrir o projeto no Xcode (`ios/Runner.xcworkspace`) e configurar a aba *Signing & Capabilities* com a equipe e o bundle identifier corretos.

### 4.2. Build e Upload
1. Gerar o build do iOS:
   ```bash
   flutter build ipa --release --obfuscate --split-debug-info=./debug_info
   ```
2. O comando gerará o arquivo `.ipa` em `build/ios/ipa/`.
3. Fazer o upload para a App Store Connect utilizando o aplicativo **Transporter** (disponível no macOS) ou via Xcode.

## 5. Checklist Pré-Lançamento

- [ ] Testes de regressão completos (QA) em dispositivos físicos.
- [ ] Revisão de permissões de privacidade (Câmera, Notificações, Biometria) nos arquivos `Info.plist` e `AndroidManifest.xml`.
- [ ] Textos e capturas de tela (screenshots) de marketing preparados para as lojas.
- [ ] Política de Privacidade publicada em URL acessível.
- [ ] Contas de teste fornecidas para os revisores da Apple e Google.

## 6. Pós-Lançamento

1. **Monitoramento**: Acompanhar as métricas de estabilidade via Crashlytics nas primeiras 48 horas.
2. **Suporte Rápido**: Preparar a equipe para corrigir bugs críticos com atualizações rápidas (hotfixes).
3. **Feedback Loop**: Monitorar as avaliações nas lojas para priorizar o roadmap das próximas versões.
