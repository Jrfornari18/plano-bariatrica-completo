import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/workout_provider.dart';
import '../../../data/models/workout_model.dart';

class WorkoutDetailScreen extends StatelessWidget {
  final WorkoutModel workout;

  const WorkoutDetailScreen({super.key, required this.workout});

  @override
  Widget build(BuildContext context) {
    final typeColors = {
      WorkoutType.strength: AppColors.primary,
      WorkoutType.swimming: const Color(0xFF0EA5E9),
      WorkoutType.running: AppColors.secondary,
      WorkoutType.calisthenics: AppColors.warning,
      WorkoutType.stretching: const Color(0xFF7C3AED),
      WorkoutType.hiit: AppColors.danger,
      WorkoutType.rest: AppColors.textHint,
    };
    final color = typeColors[workout.type] ?? AppColors.primary;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [color, color.withOpacity(0.7)],
                  ),
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        workout.typeEmoji,
                        style: const TextStyle(fontSize: 60),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      Text(
                        workout.title,
                        style: const TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 22,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Stats row
                Row(
                  children: [
                    Expanded(
                      child: _StatChip(
                        icon: Icons.timer,
                        label: '${workout.durationMinutes} min',
                        color: color,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(
                      child: _StatChip(
                        icon: Icons.local_fire_department,
                        label: '${workout.caloriesBurned ?? 0} kcal',
                        color: AppColors.warning,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(
                      child: _StatChip(
                        icon: Icons.fitness_center,
                        label: '${workout.exercises.length} exerc.',
                        color: AppColors.secondary,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: AppSpacing.lg),

                // Description
                if (workout.description != null) ...[
                  const Text('Sobre o Treino',
                      style: AppTextStyles.headlineSmall),
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    workout.description!,
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textSecondary,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),
                ],

                // Exercises
                if (workout.exercises.isNotEmpty) ...[
                  const Text('Exercícios', style: AppTextStyles.headlineSmall),
                  const SizedBox(height: AppSpacing.md),
                  ...workout.exercises.asMap().entries.map(
                        (entry) => Padding(
                          padding:
                              const EdgeInsets.only(bottom: AppSpacing.sm),
                          child: _ExerciseCard(
                            exercise: entry.value,
                            index: entry.key + 1,
                            color: color,
                          ),
                        ),
                      ),
                ],

                const SizedBox(height: AppSpacing.xxxl),
              ]),
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(AppSpacing.lg),
        decoration: BoxDecoration(
          color: AppColors.surface,
          boxShadow: AppShadows.md,
        ),
        child: SafeArea(
          child: Consumer<WorkoutProvider>(
            builder: (context, provider, _) => SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: workout.isCompleted
                    ? null
                    : () async {
                        await provider.markWorkoutComplete(workout.id);
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: const Text(
                                  '🎉 Treino concluído! Parabéns!'),
                              backgroundColor: AppColors.secondary,
                              behavior: SnackBarBehavior.floating,
                              shape: RoundedRectangleBorder(
                                borderRadius: AppRadius.lgRadius,
                              ),
                            ),
                          );
                          Navigator.pop(context);
                        }
                      },
                style: ElevatedButton.styleFrom(
                  backgroundColor:
                      workout.isCompleted ? AppColors.textHint : color,
                  shape: const RoundedRectangleBorder(
                    borderRadius: AppRadius.lgRadius,
                  ),
                ),
                child: Text(
                  workout.isCompleted
                      ? '✅ Treino Concluído'
                      : 'Marcar como Concluído',
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

class _StatChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _StatChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md, vertical: AppSpacing.sm),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: AppRadius.lgRadius,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 16),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Inter',
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _ExerciseCard extends StatelessWidget {
  final ExerciseModel exercise;
  final int index;
  final Color color;

  const _ExerciseCard({
    required this.exercise,
    required this.index,
    required this.color,
  });

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
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: AppRadius.mdRadius,
            ),
            child: Center(
              child: Text(
                '$index',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: color,
                ),
              ),
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(exercise.name, style: AppTextStyles.titleMedium),
                const SizedBox(height: 2),
                Row(
                  children: [
                    if (exercise.sets != null) ...[
                      Text(
                        '${exercise.sets} séries',
                        style: AppTextStyles.caption,
                      ),
                      const Text(' × ', style: AppTextStyles.caption),
                    ],
                    if (exercise.reps != null)
                      Text(
                        '${exercise.reps} reps',
                        style: AppTextStyles.caption,
                      )
                    else if (exercise.durationSeconds != null)
                      Text(
                        '${exercise.durationSeconds}s',
                        style: AppTextStyles.caption,
                      ),
                    if (exercise.restSeconds != null) ...[
                      const SizedBox(width: AppSpacing.sm),
                      Text(
                        '• ${exercise.restSeconds}s descanso',
                        style: AppTextStyles.caption,
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          if (exercise.muscleGroup != null)
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.sm, vertical: 2),
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: AppRadius.fullRadius,
              ),
              child: Text(
                exercise.muscleGroup!,
                style: AppTextStyles.caption,
              ),
            ),
        ],
      ),
    );
  }
}
