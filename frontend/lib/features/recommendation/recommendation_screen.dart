/// Tela de recomendação de treino (RF-09).
/// Coleta intenção + restrições, dispara a recomendação e exibe o treino.
/// Estados: loading, erro e sucesso tratados.
import 'package:flutter/material.dart';
import 'recommendation_service.dart';
import 'widgets/training_block_widget.dart';
import 'widgets/feedback_widget.dart';

class RecommendationScreen extends StatefulWidget {
  const RecommendationScreen({super.key});

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _intencaoController = TextEditingController();
  final _service = RecommendationService();

  // Filtros
  String _nivel = 'iniciante';
  String _local = 'casa';
  int _duracao = 30;
  final List<String> _modalidadesSelecionadas = [];
  final List<String> _restricoesSelecionadas = [];
  final List<String> _equipamentos = ['Peso corporal'];

  // Estado
  bool _loading = false;
  String? _error;
  RecommendationResponse? _response;

  static const _modalidades = [
    'funcional',
    'calistenia',
    'musculacao',
    'aerobico',
    'esportes',
  ];

  static const _restricoesOpcoes = [
    'lombar',
    'joelho',
    'ombro',
    'cervical',
    'hipertensão',
    'gestante',
  ];

  static const _equipamentosOpcoes = [
    'Peso corporal',
    'Halteres',
    'Barra',
    'Kettlebell',
    'Elástico',
    'Corda',
    'Banco',
  ];

  Future<void> _solicitar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
      _response = null;
    });

    try {
      final request = RecommendationRequest(
        intencao: _intencaoController.text.trim(),
        nivel: _nivel,
        local: _local,
        duracaoMin: _duracao,
        modalidades: _modalidadesSelecionadas.isEmpty
            ? null
            : _modalidadesSelecionadas,
        restricoes:
            _restricoesSelecionadas.isEmpty ? null : _restricoesSelecionadas,
        equipamentosDisponiveis: _equipamentos,
      );

      final response = await _service.getRecommendation(request);
      setState(() {
        _response = response;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Não foi possível gerar o treino. Verifique sua conexão e tente novamente.\n\nDetalhe: $e';
        _loading = false;
      });
    }
  }

  void _resetar() {
    setState(() {
      _response = null;
      _error = null;
    });
  }

  @override
  void dispose() {
    _intencaoController.dispose();
    _service.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E86AB),
        foregroundColor: Colors.white,
        title: const Text('BodyScan — Recomendação de Treino'),
        actions: [
          if (_response != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Nova recomendação',
              onPressed: _resetar,
            ),
        ],
      ),
      body: _response != null
          ? _buildResult()
          : _buildForm(),
    );
  }

  // ─── Formulário ──────────────────────────────────────────────────────────

  Widget _buildForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _sectionHeader('O que você quer treinar?'),
            const SizedBox(height: 8),
            TextFormField(
              controller: _intencaoController,
              maxLines: 3,
              decoration: InputDecoration(
                hintText:
                    'Ex: quero perder gordura treinando em casa, 30 minutos, sem equipamentos...',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none),
                enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: Colors.grey[200]!)),
              ),
              validator: (v) {
                if (v == null || v.trim().length < 5) {
                  return 'Descreva sua intenção (mínimo 5 caracteres)';
                }
                return null;
              },
            ),
            const SizedBox(height: 20),
            _sectionHeader('Configurações'),
            const SizedBox(height: 8),
            _buildConfigCard(),
            const SizedBox(height: 16),
            _sectionHeader('Modalidades (opcional)'),
            const SizedBox(height: 8),
            _buildChipGroup(
              options: _modalidades,
              selected: _modalidadesSelecionadas,
              onToggle: (v) => setState(() {
                _modalidadesSelecionadas.contains(v)
                    ? _modalidadesSelecionadas.remove(v)
                    : _modalidadesSelecionadas.add(v);
              }),
            ),
            const SizedBox(height: 16),
            _sectionHeader('Equipamentos disponíveis'),
            const SizedBox(height: 8),
            _buildChipGroup(
              options: _equipamentosOpcoes,
              selected: _equipamentos,
              onToggle: (v) => setState(() {
                _equipamentos.contains(v)
                    ? _equipamentos.remove(v)
                    : _equipamentos.add(v);
              }),
            ),
            const SizedBox(height: 16),
            _sectionHeader('Restrições / Contraindicações'),
            const SizedBox(height: 8),
            _buildChipGroup(
              options: _restricoesOpcoes,
              selected: _restricoesSelecionadas,
              onToggle: (v) => setState(() {
                _restricoesSelecionadas.contains(v)
                    ? _restricoesSelecionadas.remove(v)
                    : _restricoesSelecionadas.add(v);
              }),
            ),
            const SizedBox(height: 24),
            // Disclaimer (Seção 13 do PRD)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber.withOpacity(0.4)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.amber, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Conteúdo informativo. Não substitui orientação de profissional de saúde ou educação física.',
                      style: TextStyle(fontSize: 12, color: Colors.black87),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            if (_error != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(_error!,
                    style: const TextStyle(color: Colors.red, fontSize: 13)),
              ),
              const SizedBox(height: 16),
            ],
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _loading ? null : _solicitar,
                icon: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.fitness_center),
                label: Text(
                  _loading ? 'Gerando treino...' : 'Gerar meu treino',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2E86AB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildConfigCard() {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Nível
            Row(
              children: [
                const Icon(Icons.bar_chart, size: 18, color: Color(0xFF2E86AB)),
                const SizedBox(width: 8),
                const Text('Nível:', style: TextStyle(fontWeight: FontWeight.w600)),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _nivel,
                    decoration: const InputDecoration(
                        isDense: true, border: InputBorder.none),
                    items: const [
                      DropdownMenuItem(
                          value: 'iniciante', child: Text('Iniciante')),
                      DropdownMenuItem(
                          value: 'intermediario', child: Text('Intermediário')),
                      DropdownMenuItem(
                          value: 'avancado', child: Text('Avançado')),
                    ],
                    onChanged: (v) => setState(() => _nivel = v!),
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
            // Local
            Row(
              children: [
                const Icon(Icons.location_on, size: 18, color: Color(0xFF2E86AB)),
                const SizedBox(width: 8),
                const Text('Local:', style: TextStyle(fontWeight: FontWeight.w600)),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _local,
                    decoration: const InputDecoration(
                        isDense: true, border: InputBorder.none),
                    items: const [
                      DropdownMenuItem(value: 'casa', child: Text('Casa')),
                      DropdownMenuItem(
                          value: 'academia', child: Text('Academia')),
                      DropdownMenuItem(
                          value: 'ar_livre', child: Text('Ar livre')),
                    ],
                    onChanged: (v) => setState(() => _local = v!),
                  ),
                ),
              ],
            ),
            const Divider(height: 20),
            // Duração
            Row(
              children: [
                const Icon(Icons.timer, size: 18, color: Color(0xFF2E86AB)),
                const SizedBox(width: 8),
                Text('Duração: ${_duracao}min',
                    style: const TextStyle(fontWeight: FontWeight.w600)),
                Expanded(
                  child: Slider(
                    value: _duracao.toDouble(),
                    min: 10,
                    max: 90,
                    divisions: 8,
                    activeColor: const Color(0xFF2E86AB),
                    onChanged: (v) => setState(() => _duracao = v.round()),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChipGroup({
    required List<String> options,
    required List<String> selected,
    required void Function(String) onToggle,
  }) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: options.map((opt) {
        final isSelected = selected.contains(opt);
        return FilterChip(
          label: Text(opt),
          selected: isSelected,
          onSelected: (_) => onToggle(opt),
          selectedColor: const Color(0xFF2E86AB).withOpacity(0.2),
          checkmarkColor: const Color(0xFF2E86AB),
          labelStyle: TextStyle(
            color: isSelected ? const Color(0xFF2E86AB) : Colors.black87,
            fontWeight:
                isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        );
      }).toList(),
    );
  }

  // ─── Resultado ───────────────────────────────────────────────────────────

  Widget _buildResult() {
    final r = _response!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header do treino
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          r.treino.nome,
                          style: const TextStyle(
                              fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                      ),
                      if (r.degraded)
                        Chip(
                          label: const Text('Modo básico',
                              style: TextStyle(fontSize: 11)),
                          backgroundColor: Colors.orange.withOpacity(0.2),
                          side: BorderSide(
                              color: Colors.orange.withOpacity(0.4)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 4,
                    children: [
                      _tag(Icons.fitness_center, r.treino.modalidade),
                      _tag(Icons.flag, r.treino.objetivo),
                      _tag(Icons.bar_chart, r.treino.nivel),
                      _tag(Icons.timer, '${r.treino.duracaoMin}min'),
                      _tag(Icons.loop, r.treino.estrutura),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Justificativa
          _sectionHeader('Justificativa'),
          const SizedBox(height: 8),
          Card(
            elevation: 1,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(r.justificativa,
                  style: const TextStyle(fontSize: 14, height: 1.5)),
            ),
          ),
          const SizedBox(height: 16),

          // Blocos do treino
          _sectionHeader('Treino'),
          ...r.treino.blocos
              .map((b) => TrainingBlockWidget(block: b))
              .toList(),
          const SizedBox(height: 16),

          // Feedback
          _sectionHeader('Avalie este treino'),
          const SizedBox(height: 8),
          FeedbackWidget(
            recomendacaoId: r.recomendacaoId,
            onSubmit: _service.submitFeedback,
          ),
          const SizedBox(height: 16),

          // Disclaimer
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber.withOpacity(0.4)),
            ),
            child: const Row(
              children: [
                Icon(Icons.info_outline, color: Colors.amber, size: 18),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Conteúdo informativo. Não substitui orientação de profissional de saúde ou educação física.',
                    style: TextStyle(fontSize: 12, color: Colors.black87),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Botão nova recomendação
          SizedBox(
            width: double.infinity,
            height: 48,
            child: OutlinedButton.icon(
              onPressed: _resetar,
              icon: const Icon(Icons.refresh),
              label: const Text('Gerar novo treino'),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF2E86AB),
                side: const BorderSide(color: Color(0xFF2E86AB)),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _sectionHeader(String title) {
    return Text(
      title,
      style: const TextStyle(
          fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1A1A2E)),
    );
  }

  Widget _tag(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF2E86AB).withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: const Color(0xFF2E86AB)),
          const SizedBox(width: 4),
          Text(label,
              style: const TextStyle(
                  fontSize: 12,
                  color: Color(0xFF2E86AB),
                  fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
