import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';
import '../../core/constants/app_constants.dart';
import '../../data/models/chat_model.dart';

class ChatProvider extends ChangeNotifier {
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;
  String? _error;
  final String _sessionId = const Uuid().v4();

  List<ChatMessage> get messages => _messages;
  bool get isTyping => _isTyping;
  String? get error => _error;
  bool get hasMessages => _messages.isNotEmpty;

  ChatProvider() {
    _addWelcomeMessage();
  }

  void _addWelcomeMessage() {
    _messages.add(ChatMessage(
      id: const Uuid().v4(),
      content:
          'Olá! 👋 Sou a **Babi**, sua assistente de saúde pós-bariátrica do Barifit+!\n\n'
          'Estou aqui para te ajudar com:\n'
          '• 🍽️ Dúvidas sobre nutrição e refeições\n'
          '• 💪 Orientações sobre treinos\n'
          '• 📊 Análise do seu progresso\n'
          '• 💊 Suplementação adequada\n'
          '• 🧠 Motivação e bem-estar\n\n'
          'Como posso te ajudar hoje?',
      role: MessageRole.assistant,
      timestamp: DateTime.now(),
    ));
  }

  Future<void> sendMessage(String content, {String? userName}) async {
    if (content.trim().isEmpty) return;

    _error = null;
    final uuid = const Uuid();

    // Add user message
    final userMessage = ChatMessage(
      id: uuid.v4(),
      content: content.trim(),
      role: MessageRole.user,
      status: MessageStatus.sent,
      timestamp: DateTime.now(),
    );
    _messages.add(userMessage);
    _isTyping = true;
    notifyListeners();

    try {
      final response = await _callOpenAI(content, userName: userName);

      final assistantMessage = ChatMessage(
        id: uuid.v4(),
        content: response,
        role: MessageRole.assistant,
        status: MessageStatus.sent,
        timestamp: DateTime.now(),
      );
      _messages.add(assistantMessage);
    } catch (e) {
      _error = 'Erro ao conectar com Babi. Verifique sua conexão.';
      // Fallback response
      _messages.add(ChatMessage(
        id: uuid.v4(),
        content: _getFallbackResponse(content),
        role: MessageRole.assistant,
        status: MessageStatus.sent,
        timestamp: DateTime.now(),
      ));
    } finally {
      _isTyping = false;
      notifyListeners();
    }
  }

  Future<String> _callOpenAI(String userMessage, {String? userName}) async {
    // Build conversation history (last 10 messages)
    final history = _messages
        .where((m) => m.role != MessageRole.system)
        .take(10)
        .map((m) => {'role': m.role.name, 'content': m.content})
        .toList();

    final messages = [
      {
        'role': 'system',
        'content': AppConstants.babiSystemPrompt +
            (userName != null
                ? '\nO usuário se chama $userName. Use o nome dele(a) ocasionalmente para personalizar a conversa.'
                : ''),
      },
      ...history,
      {'role': 'user', 'content': userMessage},
    ];

    // Try to use environment variable for API key
    const apiKey = String.fromEnvironment('OPENAI_API_KEY', defaultValue: '');

    if (apiKey.isEmpty) {
      return _getFallbackResponse(userMessage);
    }

    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/chat/completions'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $apiKey',
      },
      body: jsonEncode({
        'model': 'gpt-4o-mini',
        'messages': messages,
        'max_tokens': 500,
        'temperature': 0.7,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['choices'][0]['message']['content'] as String;
    } else {
      throw Exception('API error: ${response.statusCode}');
    }
  }

  String _getFallbackResponse(String userMessage) {
    final lower = userMessage.toLowerCase();

    if (lower.contains('proteína') || lower.contains('proteina') || lower.contains('whey')) {
      return '💪 **Proteína pós-bariátrica**\n\nA meta proteica diária para você é de **150-175g/dia**. '
          'Priorize fontes magras como frango, peixe, ovos e whey protein. '
          'O whey deve ser consumido preferencialmente nos 30 minutos após o treino para maximizar a síntese muscular. '
          'Lembre-se: a proteína é fundamental para preservar a massa muscular durante o processo de emagrecimento! 🥩';
    } else if (lower.contains('treino') || lower.contains('exercício') || lower.contains('exercicio')) {
      return '🏋️ **Treinos Barifit+**\n\nSeu programa inclui:\n'
          '• **Musculação**: 3-6x/semana para ganho de massa\n'
          '• **Natação**: 2x/semana (terça e quinta)\n'
          '• **Corrida**: 2x/semana (quarta e sábado)\n'
          '• **Calistenia**: Diariamente (15-20 min)\n'
          '• **Alongamento**: Todo dia (10-15 min)\n\n'
          'Respeite os períodos de descanso e ouça seu corpo! 💪';
    } else if (lower.contains('peso') || lower.contains('emagrecer') || lower.contains('gordura')) {
      return '⚖️ **Controle de Peso**\n\nO progresso saudável pós-bariátrica é de **0,5-1kg/semana**. '
          'Foque em:\n• Manter o déficit calórico adequado\n• Atingir a meta proteica diária\n'
          '• Fazer os treinos programados\n• Dormir 7-8 horas por noite\n\n'
          'Use o ScanBody regularmente para acompanhar sua composição corporal! 📊';
    } else if (lower.contains('água') || lower.contains('hidratação') || lower.contains('hidratacao')) {
      return '💧 **Hidratação**\n\nA meta diária é de **2,5-3,5 litros de água**. '
          'Dicas importantes:\n• Beba água entre as refeições, não durante\n'
          '• Evite líquidos 30 min antes e após as refeições\n'
          '• Prefira água e chás sem açúcar\n'
          '• Monitore a cor da urina (deve ser clara) 🌊';
    } else if (lower.contains('suplemento') || lower.contains('vitamina') || lower.contains('cálcio') || lower.contains('calcio')) {
      return '💊 **Suplementação Pós-Bariátrica**\n\nSuplementos essenciais:\n'
          '• **Multivitamínico**: 1x ao dia\n'
          '• **Cálcio + Vitamina D**: 1.200-1.500mg/dia\n'
          '• **Vitamina B12**: 500mcg/dia\n'
          '• **Ferro**: Conforme orientação médica\n'
          '• **Whey Protein**: Pós-treino\n'
          '• **Creatina**: 5g/dia\n\n'
          '⚠️ Sempre consulte seu médico ou nutricionista antes de iniciar qualquer suplementação!';
    } else if (lower.contains('receita') || lower.contains('comer') || lower.contains('alimento')) {
      return '🍽️ **Alimentação Saudável**\n\nAlimentos prioritários na sua dieta:\n'
          '• **Proteínas**: Frango, peixe, ovos, cottage, whey\n'
          '• **Carboidratos complexos**: Batata doce, arroz integral, aveia\n'
          '• **Gorduras boas**: Azeite, abacate, castanhas\n'
          '• **Vegetais**: Brócolis, espinafre, abobrinha\n\n'
          'Acesse a aba **Refeições** para ver seu cardápio personalizado e receitas! 📖';
    } else if (lower.contains('dor') || lower.contains('cansaço') || lower.contains('cansaco') || lower.contains('fadiga')) {
      return '🩺 **Atenção à Recuperação**\n\nAlgumas dores musculares são normais (DOMS). '
          'Mas se sentir:\n• Dor intensa ou aguda\n• Tontura ou fraqueza excessiva\n'
          '• Dor no peito\n\n**Pare o treino imediatamente e consulte seu médico!** '
          'Para recuperação normal: hidratação, sono adequado e alimentação proteica são fundamentais. 💙';
    } else {
      return '😊 Entendi sua pergunta! Como sua assistente de saúde pós-bariátrica, '
          'estou aqui para ajudar com nutrição, treinos, progresso e bem-estar.\n\n'
          'Posso te ajudar com:\n'
          '• 🍽️ **Nutrição e cardápios**\n'
          '• 💪 **Treinos e exercícios**\n'
          '• 📊 **Análise de progresso**\n'
          '• 💊 **Suplementação**\n'
          '• 🧠 **Motivação e dicas**\n\n'
          'O que você gostaria de saber? 🌟';
    }
  }

  void clearMessages() {
    _messages.clear();
    _addWelcomeMessage();
    notifyListeners();
  }

  List<String> get quickSuggestions => [
        '💪 Qual é minha meta proteica hoje?',
        '🍽️ O que devo comer pós-treino?',
        '⚖️ Como está meu progresso?',
        '💊 Quais suplementos devo tomar?',
        '🏊 Dicas para a natação de hoje',
        '😴 Como melhorar minha recuperação?',
      ];
}
