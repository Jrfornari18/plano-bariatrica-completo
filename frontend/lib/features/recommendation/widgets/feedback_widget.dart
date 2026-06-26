/// Widget de feedback com estrelas 1–5 (RF-06).
import 'package:flutter/material.dart';

class FeedbackWidget extends StatefulWidget {
  final int recomendacaoId;
  final Future<void> Function(int recomendacaoId, int nota) onSubmit;

  const FeedbackWidget({
    super.key,
    required this.recomendacaoId,
    required this.onSubmit,
  });

  @override
  State<FeedbackWidget> createState() => _FeedbackWidgetState();
}

class _FeedbackWidgetState extends State<FeedbackWidget> {
  int _selectedRating = 0;
  bool _submitted = false;
  bool _loading = false;
  String? _error;

  Future<void> _submit() async {
    if (_selectedRating == 0) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await widget.onSubmit(widget.recomendacaoId, _selectedRating);
      setState(() {
        _submitted = true;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Erro ao enviar feedback. Tente novamente.';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_submitted) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.green.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.green.withOpacity(0.3)),
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle, color: Colors.green),
            SizedBox(width: 8),
            Text('Obrigado pelo seu feedback!',
                style: TextStyle(color: Colors.green, fontWeight: FontWeight.w600)),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Como foi este treino para você?',
            style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(5, (index) {
              final star = index + 1;
              return GestureDetector(
                onTap: () => setState(() => _selectedRating = star),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Icon(
                    star <= _selectedRating ? Icons.star : Icons.star_border,
                    color: star <= _selectedRating
                        ? const Color(0xFFFFB300)
                        : Colors.grey[400],
                    size: 36,
                  ),
                ),
              );
            }),
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: const TextStyle(color: Colors.red, fontSize: 12)),
          ],
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _selectedRating > 0 && !_loading ? _submit : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2E86AB),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
              ),
              child: _loading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Text('Enviar avaliação'),
            ),
          ),
        ],
      ),
    );
  }
}
