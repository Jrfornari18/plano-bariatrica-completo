/// Widget que exibe um bloco de treino (aquecimento, principal, finalização).
import 'package:flutter/material.dart';
import '../recommendation_service.dart';

class TrainingBlockWidget extends StatelessWidget {
  final TrainingBlock block;

  const TrainingBlockWidget({super.key, required this.block});

  String _blockLabel(String bloco) {
    switch (bloco.toLowerCase()) {
      case 'aquecimento':
        return '🔥 Aquecimento';
      case 'principal':
        return '💪 Principal';
      case 'finalizacao':
      case 'finalização':
        return '🧘 Finalização';
      default:
        return bloco;
    }
  }

  Color _blockColor(String bloco) {
    switch (bloco.toLowerCase()) {
      case 'aquecimento':
        return const Color(0xFFFF6B35);
      case 'principal':
        return const Color(0xFF2E86AB);
      case 'finalizacao':
      case 'finalização':
        return const Color(0xFF4CAF50);
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _blockColor(block.bloco);
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Cabeçalho do bloco
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
              border: Border(left: BorderSide(color: color, width: 4)),
            ),
            child: Text(
              _blockLabel(block.bloco),
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 15,
                color: color,
              ),
            ),
          ),
          // Itens do bloco
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: block.itens.length,
            separatorBuilder: (_, __) => const Divider(height: 1, indent: 16),
            itemBuilder: (context, index) {
              return ExerciseItemWidget(item: block.itens[index]);
            },
          ),
        ],
      ),
    );
  }
}

class ExerciseItemWidget extends StatelessWidget {
  final TrainingItem item;

  const ExerciseItemWidget({super.key, required this.item});

  @override
  Widget build(BuildContext context) {
    return ExpansionTile(
      tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      title: Text(
        item.nome,
        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
      ),
      subtitle: Text(
        '${item.series}x ${item.repeticoes} · descanso: ${item.descansoSeg}s',
        style: TextStyle(color: Colors.grey[600], fontSize: 12),
      ),
      children: [
        if (item.alternativa != null)
          _infoTile(Icons.swap_horiz, 'Alternativa', item.alternativa!,
              Colors.orange),
        if (item.regressao != null)
          _infoTile(Icons.arrow_downward, 'Regressão', item.regressao!,
              Colors.blue),
        if (item.progressao != null)
          _infoTile(Icons.arrow_upward, 'Progressão', item.progressao!,
              Colors.green),
        if (item.alternativa == null &&
            item.regressao == null &&
            item.progressao == null)
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text('Sem alternativas cadastradas',
                style: TextStyle(color: Colors.grey, fontSize: 12)),
          ),
      ],
    );
  }

  Widget _infoTile(
      IconData icon, String label, String value, Color color) {
    return ListTile(
      dense: true,
      contentPadding: const EdgeInsets.symmetric(horizontal: 32),
      leading: Icon(icon, color: color, size: 18),
      title: Text(label,
          style: TextStyle(
              color: color, fontSize: 12, fontWeight: FontWeight.w600)),
      subtitle: Text(value, style: const TextStyle(fontSize: 12)),
    );
  }
}
