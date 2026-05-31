import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/scanbody_provider.dart';
import '../../providers/auth_provider.dart';
import '../../../data/models/scanbody_model.dart';

class ScanbodyCameraScreen extends StatefulWidget {
  const ScanbodyCameraScreen({super.key});

  @override
  State<ScanbodyCameraScreen> createState() => _ScanbodyCameraScreenState();
}

class _ScanbodyCameraScreenState extends State<ScanbodyCameraScreen> {
  final _weightController = TextEditingController();
  final _waistController = TextEditingController();
  final _hipController = TextEditingController();
  final _chestController = TextEditingController();
  final _armController = TextEditingController();
  final _thighController = TextEditingController();

  @override
  void dispose() {
    _weightController.dispose();
    _waistController.dispose();
    _hipController.dispose();
    _chestController.dispose();
    _armController.dispose();
    _thighController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ScanbodyProvider>(
      builder: (context, provider, _) {
        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(
            title: const Text('Novo ScanBody'),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () {
                provider.resetScan();
                Navigator.pop(context);
              },
            ),
          ),
          body: _buildBody(context, provider),
        );
      },
    );
  }

  Widget _buildBody(BuildContext context, ScanbodyProvider provider) {
    switch (provider.currentStep) {
      case ScanStep.front:
        return _buildPhotoStep(
          context, provider,
          step: ScanStep.front,
          title: 'Foto Frontal',
          description: 'Fique em pé, de frente para a câmera, com os braços levemente afastados do corpo.',
          icon: '🧍',
          photoPath: provider.frontPhotoPath,
        );
      case ScanStep.side:
        return _buildPhotoStep(
          context, provider,
          step: ScanStep.side,
          title: 'Foto Lateral',
          description: 'Fique de lado para a câmera, com postura ereta e olhando para frente.',
          icon: '🧍',
          photoPath: provider.sidePhotoPath,
        );
      case ScanStep.back:
        return _buildPhotoStep(
          context, provider,
          step: ScanStep.back,
          title: 'Foto Posterior',
          description: 'Fique de costas para a câmera, com os braços levemente afastados.',
          icon: '🧍',
          photoPath: provider.backPhotoPath,
        );
      case ScanStep.measurements:
        return _buildMeasurementsStep(context, provider);
      case ScanStep.complete:
        return _buildCompleteStep(context, provider);
    }
  }

  Widget _buildPhotoStep(
    BuildContext context,
    ScanbodyProvider provider, {
    required ScanStep step,
    required String title,
    required String description,
    required String icon,
    String? photoPath,
  }) {
    final stepNumber = step.index + 1;
    return Column(
      children: [
        // Progress
        _buildStepProgress(stepNumber, 3),

        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              children: [
                // Photo preview or placeholder
                Container(
                  width: double.infinity,
                  height: 300,
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant,
                    borderRadius: AppRadius.xlRadius,
                    border: Border.all(
                      color: photoPath != null
                          ? AppColors.secondary
                          : AppColors.border,
                      width: photoPath != null ? 2 : 1,
                    ),
                  ),
                  child: photoPath != null
                      ? ClipRRect(
                          borderRadius: AppRadius.xlRadius,
                          child: Image.file(
                            File(photoPath),
                            fit: BoxFit.cover,
                          ),
                        )
                      : Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(icon, style: const TextStyle(fontSize: 80)),
                            const SizedBox(height: AppSpacing.md),
                            Text(
                              title,
                              style: AppTextStyles.headlineSmall,
                            ),
                            const SizedBox(height: AppSpacing.sm),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: AppSpacing.xl),
                              child: Text(
                                description,
                                style: AppTextStyles.bodyMedium.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ],
                        ),
                ),

                const SizedBox(height: AppSpacing.xl),

                // Tips
                Container(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.05),
                    borderRadius: AppRadius.lgRadius,
                    border: Border.all(
                        color: AppColors.primary.withOpacity(0.2)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.lightbulb_outline,
                          color: AppColors.primary, size: 20),
                      const SizedBox(width: AppSpacing.sm),
                      Expanded(
                        child: Text(
                          'Use roupas justas ou de treino para melhor análise. Iluminação uniforme é importante.',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        // Action buttons
        Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            children: [
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: () => provider.capturePhoto(step),
                  icon: const Icon(Icons.camera_alt),
                  label: Text(
                      photoPath != null ? 'Tirar Novamente' : 'Tirar Foto'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.warning,
                    shape: const RoundedRectangleBorder(
                      borderRadius: AppRadius.lgRadius,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () => provider.pickFromGallery(step),
                  icon: const Icon(Icons.photo_library_outlined),
                  label: const Text('Escolher da Galeria'),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AppColors.warning),
                    foregroundColor: AppColors.warning,
                    shape: const RoundedRectangleBorder(
                      borderRadius: AppRadius.lgRadius,
                    ),
                  ),
                ),
              ),
              if (photoPath != null) ...[
                const SizedBox(height: AppSpacing.sm),
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: () {
                      final nextStep = ScanStep.values[step.index + 1];
                      provider.goToStep(nextStep);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.secondary,
                      shape: const RoundedRectangleBorder(
                        borderRadius: AppRadius.lgRadius,
                      ),
                    ),
                    child: const Text('Continuar'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMeasurementsStep(
      BuildContext context, ScanbodyProvider provider) {
    return Column(
      children: [
        _buildStepProgress(4, 4),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Peso e Medidas', style: AppTextStyles.headlineMedium),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  'Informe seu peso atual e medidas (opcional)',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: AppSpacing.xl),

                // Weight (required)
                _buildMeasurementField(
                  controller: _weightController,
                  label: 'Peso Atual (kg) *',
                  hint: 'Ex: 85.5',
                  icon: Icons.monitor_weight,
                  color: AppColors.warning,
                ),
                const SizedBox(height: AppSpacing.lg),

                const Text('Medidas Corporais (cm)',
                    style: AppTextStyles.titleLarge),
                const SizedBox(height: AppSpacing.md),

                Row(
                  children: [
                    Expanded(
                      child: _buildMeasurementField(
                        controller: _waistController,
                        label: 'Cintura',
                        hint: '80',
                        icon: Icons.straighten,
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    Expanded(
                      child: _buildMeasurementField(
                        controller: _hipController,
                        label: 'Quadril',
                        hint: '100',
                        icon: Icons.straighten,
                        color: AppColors.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.md),
                Row(
                  children: [
                    Expanded(
                      child: _buildMeasurementField(
                        controller: _chestController,
                        label: 'Peitoral',
                        hint: '95',
                        icon: Icons.straighten,
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    Expanded(
                      child: _buildMeasurementField(
                        controller: _armController,
                        label: 'Braço',
                        hint: '35',
                        icon: Icons.straighten,
                        color: AppColors.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.md),
                _buildMeasurementField(
                  controller: _thighController,
                  label: 'Coxa',
                  hint: '60',
                  icon: Icons.straighten,
                  color: AppColors.primary,
                ),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Consumer<AuthProvider>(
            builder: (context, auth, _) => SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: provider.isAnalyzing
                    ? null
                    : () => _saveRecord(context, provider, auth),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.warning,
                  shape: const RoundedRectangleBorder(
                    borderRadius: AppRadius.lgRadius,
                  ),
                ),
                child: provider.isAnalyzing
                    ? const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          ),
                          SizedBox(width: AppSpacing.sm),
                          Text('Analisando com IA...'),
                        ],
                      )
                    : const Text('Salvar e Analisar'),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCompleteStep(BuildContext context, ScanbodyProvider provider) {
    final latest = provider.latestRecord;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: AppColors.secondary.withOpacity(0.1),
                borderRadius: AppRadius.fullRadius,
              ),
              child: const Icon(
                Icons.check_circle,
                color: AppColors.secondary,
                size: 60,
              ),
            ),
            const SizedBox(height: AppSpacing.xl),
            const Text(
              'ScanBody Salvo!',
              style: AppTextStyles.headlineLarge,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'Seu registro foi salvo e analisado pela Babi.',
              style: AppTextStyles.bodyLarge.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            if (latest?.aiAnalysis != null) ...[
              const SizedBox(height: AppSpacing.xl),
              Container(
                padding: const EdgeInsets.all(AppSpacing.lg),
                decoration: BoxDecoration(
                  color: const Color(0xFF7C3AED).withOpacity(0.05),
                  borderRadius: AppRadius.xlRadius,
                  border: Border.all(
                      color: const Color(0xFF7C3AED).withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Text('🤖', style: TextStyle(fontSize: 20)),
                        SizedBox(width: AppSpacing.sm),
                        Text(
                          'Análise da Babi',
                          style: TextStyle(
                            fontFamily: 'Inter',
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF7C3AED),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      latest!.aiAnalysis!,
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textPrimary,
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: AppSpacing.xl),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  provider.resetScan();
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.warning,
                  minimumSize: const Size(0, 52),
                  shape: const RoundedRectangleBorder(
                    borderRadius: AppRadius.lgRadius,
                  ),
                ),
                child: const Text('Concluir'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepProgress(int current, int total) {
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      color: AppColors.surface,
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Passo $current de $total',
                style: AppTextStyles.labelMedium,
              ),
              Text(
                '${((current / total) * 100).round()}%',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.warning,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.xs),
          LinearProgressIndicator(
            value: current / total,
            backgroundColor: AppColors.border,
            valueColor:
                const AlwaysStoppedAnimation<Color>(AppColors.warning),
            minHeight: 6,
            borderRadius: AppRadius.fullRadius,
          ),
        ],
      ),
    );
  }

  Widget _buildMeasurementField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    required Color color,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.labelMedium),
        const SizedBox(height: AppSpacing.xs),
        TextFormField(
          controller: controller,
          keyboardType:
              const TextInputType.numberWithOptions(decimal: true),
          style: AppTextStyles.bodyLarge,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon, color: color, size: 20),
            filled: true,
            fillColor: AppColors.surfaceVariant,
            border: OutlineInputBorder(
              borderRadius: AppRadius.lgRadius,
              borderSide: const BorderSide(color: AppColors.border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: AppRadius.lgRadius,
              borderSide: const BorderSide(color: AppColors.border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: AppRadius.lgRadius,
              borderSide: BorderSide(color: color, width: 2),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.lg,
              vertical: AppSpacing.md,
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _saveRecord(
    BuildContext context,
    ScanbodyProvider provider,
    AuthProvider auth,
  ) async {
    final weightText = _weightController.text.trim();
    if (weightText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, informe seu peso atual.')),
      );
      return;
    }

    final weight = double.tryParse(weightText.replaceAll(',', '.'));
    if (weight == null || weight <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Peso inválido.')),
      );
      return;
    }

    provider.setWeight(weight);

    final waist = double.tryParse(_waistController.text.replaceAll(',', '.'));
    final hip = double.tryParse(_hipController.text.replaceAll(',', '.'));
    final chest = double.tryParse(_chestController.text.replaceAll(',', '.'));
    final arm = double.tryParse(_armController.text.replaceAll(',', '.'));
    final thigh = double.tryParse(_thighController.text.replaceAll(',', '.'));

    if (waist != null || hip != null || chest != null) {
      provider.setMeasurements(BodyMeasurements(
        waist: waist,
        hip: hip,
        chest: chest,
        leftArm: arm,
        rightArm: arm,
        leftThigh: thigh,
        rightThigh: thigh,
      ));
    }

    await provider.analyzeAndSave(auth.user?.id ?? 'user');
  }
}
