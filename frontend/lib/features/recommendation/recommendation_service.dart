/// Cliente HTTP para o endpoint de recomendação (RF-09).
/// Consome POST /api/v1/recommendations e POST /api/v1/recommendations/{id}/feedback.
import 'dart:convert';
import 'package:http/http.dart' as http;

// URL base da API — configurar via variável de ambiente ou build config
const String _baseUrl =
    String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000');

class RecommendationRequest {
  final int? perfilId;
  final String intencao;
  final List<String>? modalidades;
  final String? nivel;
  final int? duracaoMin;
  final String? local;
  final List<String>? equipamentosDisponiveis;
  final List<String>? restricoes;
  final int topK;

  const RecommendationRequest({
    this.perfilId,
    required this.intencao,
    this.modalidades,
    this.nivel,
    this.duracaoMin,
    this.local,
    this.equipamentosDisponiveis,
    this.restricoes,
    this.topK = 8,
  });

  Map<String, dynamic> toJson() => {
        if (perfilId != null) 'perfil_id': perfilId,
        'intencao': intencao,
        if (modalidades != null) 'modalidades': modalidades,
        if (nivel != null) 'nivel': nivel,
        if (duracaoMin != null) 'duracao_min': duracaoMin,
        if (local != null) 'local': local,
        if (equipamentosDisponiveis != null)
          'equipamentos_disponiveis': equipamentosDisponiveis,
        if (restricoes != null) 'restricoes': restricoes,
        'top_k': topK,
      };
}

class TrainingItem {
  final int exercicioId;
  final String nome;
  final int series;
  final String repeticoes;
  final int descansoSeg;
  final String? alternativa;
  final String? regressao;
  final String? progressao;

  const TrainingItem({
    required this.exercicioId,
    required this.nome,
    required this.series,
    required this.repeticoes,
    required this.descansoSeg,
    this.alternativa,
    this.regressao,
    this.progressao,
  });

  factory TrainingItem.fromJson(Map<String, dynamic> json) => TrainingItem(
        exercicioId: json['exercicio_id'] as int,
        nome: json['nome'] as String,
        series: json['series'] as int,
        repeticoes: json['repeticoes'].toString(),
        descansoSeg: json['descanso_seg'] as int,
        alternativa: json['alternativa'] as String?,
        regressao: json['regressao'] as String?,
        progressao: json['progressao'] as String?,
      );
}

class TrainingBlock {
  final String bloco;
  final List<TrainingItem> itens;

  const TrainingBlock({required this.bloco, required this.itens});

  factory TrainingBlock.fromJson(Map<String, dynamic> json) => TrainingBlock(
        bloco: json['bloco'] as String,
        itens: (json['itens'] as List)
            .map((e) => TrainingItem.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class TrainingPlan {
  final String nome;
  final String modalidade;
  final String objetivo;
  final String nivel;
  final int duracaoMin;
  final String estrutura;
  final List<TrainingBlock> blocos;

  const TrainingPlan({
    required this.nome,
    required this.modalidade,
    required this.objetivo,
    required this.nivel,
    required this.duracaoMin,
    required this.estrutura,
    required this.blocos,
  });

  factory TrainingPlan.fromJson(Map<String, dynamic> json) => TrainingPlan(
        nome: json['nome'] as String,
        modalidade: json['modalidade'] as String,
        objetivo: json['objetivo'] as String,
        nivel: json['nivel'] as String,
        duracaoMin: json['duracao_min'] as int,
        estrutura: json['estrutura'] as String,
        blocos: (json['blocos'] as List)
            .map((e) => TrainingBlock.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class RecommendationResponse {
  final int recomendacaoId;
  final bool degraded;
  final TrainingPlan treino;
  final String justificativa;
  final List<int> contextoRecuperado;

  const RecommendationResponse({
    required this.recomendacaoId,
    required this.degraded,
    required this.treino,
    required this.justificativa,
    required this.contextoRecuperado,
  });

  factory RecommendationResponse.fromJson(Map<String, dynamic> json) =>
      RecommendationResponse(
        recomendacaoId: json['recomendacao_id'] as int,
        degraded: json['degraded'] as bool? ?? false,
        treino: TrainingPlan.fromJson(json['treino'] as Map<String, dynamic>),
        justificativa: json['justificativa'] as String,
        contextoRecuperado:
            (json['contexto_recuperado'] as List).cast<int>(),
      );
}

class RecommendationService {
  final http.Client _client;

  RecommendationService({http.Client? client})
      : _client = client ?? http.Client();

  /// Solicita uma recomendação de treino (RF-09).
  Future<RecommendationResponse> getRecommendation(
      RecommendationRequest request) async {
    final uri = Uri.parse('$_baseUrl/api/v1/recommendations');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      return RecommendationResponse.fromJson(json);
    } else if (response.statusCode == 422) {
      final json = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception('Dados inválidos: ${json['detail']}');
    } else {
      throw Exception('Erro na API: ${response.statusCode}');
    }
  }

  /// Registra feedback 1–5 para uma recomendação (RF-06).
  Future<void> submitFeedback(int recomendacaoId, int nota) async {
    final uri =
        Uri.parse('$_baseUrl/api/v1/recommendations/$recomendacaoId/feedback');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'nota': nota}),
    );

    if (response.statusCode != 200) {
      throw Exception('Erro ao enviar feedback: ${response.statusCode}');
    }
  }

  void dispose() => _client.close();
}
