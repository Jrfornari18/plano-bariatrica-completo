import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/meal_provider.dart';
import '../../../data/models/meal_model.dart';

class MealDetailScreen extends StatelessWidget {
  final MealModel meal;

  const MealDetailScreen({super.key, required this.meal});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(meal.typeLabel),
        actions: [
          Consumer<MealProvider>(
            builder: (context, provider, _) => IconButton(
              icon: Icon(
                meal.isLogged
                    ? Icons.check_circle
                    : Icons.check_circle_outline,
                color: meal.isLogged ? AppColors.secondary : null,
              ),
              onPressed: () {
                provider.toggleMealLogged(meal.id);
                Navigator.pop(context);
              },
              tooltip: meal.isLogged ? 'Marcar como não feito' : 'Marcar como feito',
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header card
            Container(
              padding: const EdgeInsets.all(AppSpacing.lg),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.secondary, AppColors.secondaryDark],
                ),
                borderRadius: AppRadius.xlRadius,
              ),
              child: Row(
                children: [
                  Text(meal.typeEmoji,
                      style: const TextStyle(fontSize: 48)),
                  const SizedBox(width: AppSpacing.lg),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          meal.typeLabel,
                          style: const TextStyle(
                            fontFamily: 'Inter',
                            fontSize: 22,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          meal.scheduledTime,
                          style: const TextStyle(
                            fontFamily: 'Inter',
                            fontSize: 14,
                            color: Colors.white70,
                          ),
                        ),
                        const SizedBox(height: AppSpacing.sm),
                        Row(
                          children: [
                            _MacroBadge(
                              value:
                                  '${meal.totalMacros.calories.round()} kcal',
                              color: Colors.white,
                            ),
                            const SizedBox(width: AppSpacing.sm),
                            _MacroBadge(
                              value:
                                  '${meal.totalMacros.protein.round()}g prot',
                              color: Colors.white,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppSpacing.xl),

            // Macros breakdown
            const Text('Macronutrientes', style: AppTextStyles.headlineSmall),
            const SizedBox(height: AppSpacing.md),
            Row(
              children: [
                Expanded(
                  child: _MacroCard(
                    label: 'Proteína',
                    value: meal.totalMacros.protein,
                    unit: 'g',
                    color: AppColors.danger,
                    icon: Icons.egg_alt_outlined,
                  ),
                ),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: _MacroCard(
                    label: 'Carbs',
                    value: meal.totalMacros.carbs,
                    unit: 'g',
                    color: AppColors.primary,
                    icon: Icons.grain,
                  ),
                ),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: _MacroCard(
                    label: 'Gordura',
                    value: meal.totalMacros.fat,
                    unit: 'g',
                    color: AppColors.warning,
                    icon: Icons.water_drop_outlined,
                  ),
                ),
              ],
            ),

            const SizedBox(height: AppSpacing.xl),

            // Food items
            if (meal.items.isNotEmpty) ...[
              const Text('Alimentos', style: AppTextStyles.headlineSmall),
              const SizedBox(height: AppSpacing.md),
              ...meal.items.map((item) => Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                    child: _FoodItemCard(item: item),
                  )),
            ],

            // Notes
            if (meal.notes != null) ...[
              const SizedBox(height: AppSpacing.lg),
              const Text('Observações', style: AppTextStyles.headlineSmall),
              const SizedBox(height: AppSpacing.sm),
              Container(
                padding: const EdgeInsets.all(AppSpacing.md),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: AppRadius.lgRadius,
                ),
                child: Text(
                  meal.notes!,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                    height: 1.5,
                  ),
                ),
              ),
            ],

            const SizedBox(height: AppSpacing.xxxl),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(AppSpacing.lg),
        decoration: BoxDecoration(
          color: AppColors.surface,
          boxShadow: AppShadows.md,
        ),
        child: SafeArea(
          child: Consumer<MealProvider>(
            builder: (context, provider, _) => SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () {
                  provider.toggleMealLogged(meal.id);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        meal.isLogged
                            ? 'Refeição desmarcada'
                            : '🍽️ Refeição registrada!',
                      ),
                      backgroundColor: AppColors.secondary,
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: AppRadius.lgRadius,
                      ),
                    ),
                  );
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: meal.isLogged
                      ? AppColors.textHint
                      : AppColors.secondary,
                  shape: const RoundedRectangleBorder(
                    borderRadius: AppRadius.lgRadius,
                  ),
                ),
                child: Text(
                  meal.isLogged
                      ? 'Desmarcar Refeição'
                      : 'Registrar Refeição',
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MacroBadge extends StatelessWidget {
  final String value;
  final Color color;

  const _MacroBadge({required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding:
          const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: AppRadius.fullRadius,
      ),
      child: Text(
        value,
        style: TextStyle(
          fontFamily: 'Inter',
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}

class _MacroCard extends StatelessWidget {
  final String label;
  final double value;
  final String unit;
  final Color color;
  final IconData icon;

  const _MacroCard({
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: AppRadius.lgRadius,
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: AppSpacing.xs),
          Text(
            '${value.round()}$unit',
            style: TextStyle(
              fontFamily: 'Inter',
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
          Text(label, style: AppTextStyles.caption),
        ],
      ),
    );
  }
}

class _FoodItemCard extends StatelessWidget {
  final FoodItem item;

  const _FoodItemCard({required this.item});

  @override
  Widget build(BuildContext context) {
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
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.secondary.withOpacity(0.1),
              borderRadius: AppRadius.mdRadius,
            ),
            child: const Icon(Icons.restaurant,
                color: AppColors.secondary, size: 20),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.name, style: AppTextStyles.titleMedium),
                Text(
                  '${item.quantity}${item.unit}',
                  style: AppTextStyles.bodySmall,
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${item.macros.calories.round()} kcal',
                style: AppTextStyles.titleMedium,
              ),
              Text(
                '${item.macros.protein.round()}g prot',
                style: AppTextStyles.caption,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
