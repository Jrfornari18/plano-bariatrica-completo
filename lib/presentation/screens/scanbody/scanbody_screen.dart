import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/scanbody_provider.dart';
import '../../providers/auth_provider.dart';
import '../../../data/models/scanbody_model.dart';
import 'scanbody_camera_screen.dart';

class ScanbodyScreen extends StatelessWidget {
  const ScanbodyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('ScanBody'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => _showHistory(context),
          ),
        ],
      ),
      body: Consumer<ScanbodyProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLatestRecord(context, provider),
                const SizedBox(height: AppSpacing.lg),
                _buildWeightChart(context, provider),
                const SizedBox(height: AppSpacing.lg),
                _buildBodyComposition(context, provider),
                const SizedBox(height: AppSpacing.lg),
                _buildMeasurements(context, provider),
                const SizedBox(height: AppSpacing.lg),
                _buildPhotos(context, provider),
                const SizedBox(height: AppSpacing.xxxl),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const ScanbodyCameraScreen()),
        ),
        backgroundColor: AppColors.warning,
        icon: const Icon(Icons.camera_alt, color: Colors.white),
        label: const Text(
          'Novo Scan',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }

  Widget _buildLatestRecord(BuildContext context, ScanbodyProvider provider) {
    final latest = provider.latestRecord;
    final weightChange = provider.weightChange;

    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.warning, AppColors.warningDark],
        ),
        borderRadius: AppRadius.xlRadius,
        boxShadow: AppShadows.md,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Último Registro',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 14,
                  color: Colors.white70,
                ),
              ),
              if (latest != null)
                Text(
                  DateFormat('dd/MM/yyyy').format(latest.date),
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 13,
                    color: Colors.white70,
                  ),
                ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      latest != null ? '${latest.weight}kg' : '--',
                      style: const TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 40,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                      ),
                    ),
                    if (weightChange != null)
                      Row(
                        children: [
                          Icon(
                            weightChange < 0
                                ? Icons.trending_down
                                : Icons.trending_up,
                            color: weightChange < 0
                                ? Colors.white
                                : Colors.white70,
                            size: 18,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${weightChange < 0 ? '' : '+'}${weightChange.toStringAsFixed(1)}kg',
                            style: const TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(width: 4),
                          const Text(
                            'desde o último',
                            style: TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 13,
                              color: Colors.white70,
                            ),
                          ),
                        ],
                      ),
                  ],
                ),
              ),
              if (latest?.composition?.bodyFatPercentage != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${latest!.composition!.bodyFatPercentage!.toStringAsFixed(1)}%',
                      style: const TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 28,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                    const Text(
                      'Gordura Corporal',
                      style: TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 12,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
            ],
          ),
          if (latest == null) ...[
            const SizedBox(height: AppSpacing.md),
            const Text(
              'Faça seu primeiro ScanBody para começar a monitorar sua evolução!',
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 14,
                color: Colors.white,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildWeightChart(BuildContext context, ScanbodyProvider provider) {
    final history = provider.weightHistory;
    if (history.length < 2) return const SizedBox.shrink();

    final spots = history.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), (e.value['weight'] as double));
    }).toList();

    final minY = history.map((h) => h['weight'] as double).reduce((a, b) => a < b ? a : b) - 2;
    final maxY = history.map((h) => h['weight'] as double).reduce((a, b) => a > b ? a : b) + 2;

    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.xlRadius,
        border: Border.all(color: AppColors.border),
        boxShadow: AppShadows.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Evolução do Peso', style: AppTextStyles.headlineSmall),
          const SizedBox(height: AppSpacing.lg),
          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: AppColors.border,
                    strokeWidth: 1,
                  ),
                ),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) => Text(
                        '${value.round()}kg',
                        style: AppTextStyles.caption,
                      ),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        final idx = value.toInt();
                        if (idx >= 0 && idx < history.length) {
                          return Text(
                            DateFormat('dd/MM')
                                .format(history[idx]['date'] as DateTime),
                            style: AppTextStyles.caption,
                          );
                        }
                        return const SizedBox.shrink();
                      },
                    ),
                  ),
                  rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                  topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                minY: minY,
                maxY: maxY,
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    color: AppColors.warning,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, bar, index) =>
                          FlDotCirclePainter(
                        radius: 5,
                        color: AppColors.warning,
                        strokeWidth: 2,
                        strokeColor: Colors.white,
                      ),
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.warning.withOpacity(0.1),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBodyComposition(
      BuildContext context, ScanbodyProvider provider) {
    final latest = provider.latestRecord;
    if (latest?.composition == null) return const SizedBox.shrink();

    final comp = latest!.composition!;
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.xlRadius,
        border: Border.all(color: AppColors.border),
        boxShadow: AppShadows.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Composição Corporal', style: AppTextStyles.headlineSmall),
          const SizedBox(height: AppSpacing.lg),
          Row(
            children: [
              if (comp.bodyFatPercentage != null)
                Expanded(
                  child: _CompositionItem(
                    label: 'Gordura',
                    value: '${comp.bodyFatPercentage!.toStringAsFixed(1)}%',
                    color: AppColors.danger,
                    icon: Icons.water_drop,
                  ),
                ),
              if (comp.muscleMassKg != null)
                Expanded(
                  child: _CompositionItem(
                    label: 'Músculo',
                    value: '${comp.muscleMassKg!.toStringAsFixed(1)}kg',
                    color: AppColors.primary,
                    icon: Icons.fitness_center,
                  ),
                ),
              if (comp.bmi != null)
                Expanded(
                  child: _CompositionItem(
                    label: 'IMC',
                    value: comp.bmi!.toStringAsFixed(1),
                    color: AppColors.secondary,
                    icon: Icons.monitor_weight,
                  ),
                ),
            ],
          ),
          if (latest.aiAnalysis != null) ...[
            const SizedBox(height: AppSpacing.lg),
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: const Color(0xFF7C3AED).withOpacity(0.05),
                borderRadius: AppRadius.lgRadius,
                border: Border.all(
                    color: const Color(0xFF7C3AED).withOpacity(0.2)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('🤖', style: TextStyle(fontSize: 20)),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Text(
                      'Análise da Babi disponível',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: const Color(0xFF7C3AED),
                      ),
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios,
                      size: 14, color: Color(0xFF7C3AED)),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMeasurements(BuildContext context, ScanbodyProvider provider) {
    final latest = provider.latestRecord;
    if (latest?.measurements == null) return const SizedBox.shrink();

    final m = latest!.measurements!;
    final items = <Map<String, dynamic>>[
      if (m.waist != null) {'label': 'Cintura', 'value': '${m.waist}cm'},
      if (m.hip != null) {'label': 'Quadril', 'value': '${m.hip}cm'},
      if (m.chest != null) {'label': 'Peitoral', 'value': '${m.chest}cm'},
      if (m.leftArm != null) {'label': 'Braço E', 'value': '${m.leftArm}cm'},
      if (m.rightArm != null) {'label': 'Braço D', 'value': '${m.rightArm}cm'},
      if (m.leftThigh != null) {'label': 'Coxa E', 'value': '${m.leftThigh}cm'},
      if (m.rightThigh != null) {'label': 'Coxa D', 'value': '${m.rightThigh}cm'},
    ];

    if (items.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.xlRadius,
        border: Border.all(color: AppColors.border),
        boxShadow: AppShadows.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Medidas Corporais', style: AppTextStyles.headlineSmall),
          const SizedBox(height: AppSpacing.lg),
          GridView.count(
            crossAxisCount: 3,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: AppSpacing.sm,
            mainAxisSpacing: AppSpacing.sm,
            childAspectRatio: 1.5,
            children: items.map((item) => Container(
              padding: const EdgeInsets.all(AppSpacing.sm),
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: AppRadius.mdRadius,
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    item['value'] as String,
                    style: AppTextStyles.titleMedium,
                  ),
                  Text(
                    item['label'] as String,
                    style: AppTextStyles.caption,
                  ),
                ],
              ),
            )).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildPhotos(BuildContext context, ScanbodyProvider provider) {
    final records = provider.records.where((r) => r.hasPhotos).toList();
    if (records.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.xlRadius,
        border: Border.all(color: AppColors.border),
        boxShadow: AppShadows.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Fotos de Progresso', style: AppTextStyles.headlineSmall),
          const SizedBox(height: AppSpacing.md),
          SizedBox(
            height: 120,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: records.length,
              separatorBuilder: (_, __) =>
                  const SizedBox(width: AppSpacing.sm),
              itemBuilder: (context, index) {
                final record = records[index];
                final path = record.frontPhotoPath;
                return Column(
                  children: [
                    ClipRRect(
                      borderRadius: AppRadius.mdRadius,
                      child: path != null
                          ? Image.file(
                              File(path),
                              width: 80,
                              height: 90,
                              fit: BoxFit.cover,
                            )
                          : Container(
                              width: 80,
                              height: 90,
                              color: AppColors.surfaceVariant,
                              child: const Icon(Icons.person,
                                  color: AppColors.textHint),
                            ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      DateFormat('dd/MM').format(record.date),
                      style: AppTextStyles.caption,
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _showHistory(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => const _HistorySheet(),
    );
  }
}

class _CompositionItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  final IconData icon;

  const _CompositionItem({
    required this.label,
    required this.value,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: AppRadius.mdRadius,
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(value, style: AppTextStyles.titleMedium),
        Text(label, style: AppTextStyles.caption),
      ],
    );
  }
}

class _HistorySheet extends StatelessWidget {
  const _HistorySheet();

  @override
  Widget build(BuildContext context) {
    return Consumer<ScanbodyProvider>(
      builder: (context, provider, _) {
        final records = provider.records.reversed.toList();
        return DraggableScrollableSheet(
          initialChildSize: 0.6,
          maxChildSize: 0.9,
          minChildSize: 0.4,
          expand: false,
          builder: (context, scrollController) => Column(
            children: [
              Container(
                margin: const EdgeInsets.only(top: AppSpacing.md),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.border,
                  borderRadius: AppRadius.fullRadius,
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: const Text(
                  'Histórico de Registros',
                  style: AppTextStyles.headlineMedium,
                ),
              ),
              Expanded(
                child: ListView.separated(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.lg),
                  itemCount: records.length,
                  separatorBuilder: (_, __) =>
                      const SizedBox(height: AppSpacing.sm),
                  itemBuilder: (context, index) {
                    final record = records[index];
                    return Container(
                      padding: const EdgeInsets.all(AppSpacing.md),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: AppRadius.lgRadius,
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: AppColors.warning.withOpacity(0.1),
                              borderRadius: AppRadius.mdRadius,
                            ),
                            child: const Icon(Icons.monitor_weight,
                                color: AppColors.warning),
                          ),
                          const SizedBox(width: AppSpacing.md),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  DateFormat('dd/MM/yyyy')
                                      .format(record.date),
                                  style: AppTextStyles.titleMedium,
                                ),
                                Text(
                                  '${record.weight}kg${record.composition?.bodyFatPercentage != null ? ' • ${record.composition!.bodyFatPercentage!.toStringAsFixed(1)}% gordura' : ''}',
                                  style: AppTextStyles.bodySmall,
                                ),
                              ],
                            ),
                          ),
                          const Icon(Icons.arrow_forward_ios,
                              size: 14, color: AppColors.textHint),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
