import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/constants/app_constants.dart';
import '../../providers/auth_provider.dart';
import '../../providers/workout_provider.dart';
import '../../providers/meal_provider.dart';
import '../../providers/scanbody_provider.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          _buildAppBar(context),
          SliverPadding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildProgramProgress(context),
                const SizedBox(height: AppSpacing.lg),
                _buildTodaySummary(context),
                const SizedBox(height: AppSpacing.lg),
                _buildQuickActions(context),
                const SizedBox(height: AppSpacing.lg),
                _buildTodayWorkouts(context),
                const SizedBox(height: AppSpacing.lg),
                _buildTodayMeals(context),
                const SizedBox(height: AppSpacing.lg),
                _buildBabiTip(context),
                const SizedBox(height: AppSpacing.xxxl),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 120,
      floating: true,
      pinned: true,
      backgroundColor: AppColors.surface,
      elevation: 0,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [AppColors.primary, AppColors.primaryDark],
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.lg, vertical: AppSpacing.md),
              child: Consumer<AuthProvider>(
                builder: (context, auth, _) {
                  final user = auth.user;
                  final greeting = _getGreeting();
                  return Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              '$greeting,',
                              style: TextStyle(
                                fontFamily: 'Inter',
                                fontSize: 14,
                                color: Colors.white.withOpacity(0.8),
                              ),
                            ),
                            Text(
                              user?.name.split(' ').first ?? 'Atleta',
                              style: const TextStyle(
                                fontFamily: 'Inter',
                                fontSize: 24,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: AppRadius.fullRadius,
                        ),
                        child: const Icon(
                          Icons.notifications_outlined,
                          color: Colors.white,
                          size: 22,
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProgramProgress(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        final user = auth.user;
        if (user == null) return const SizedBox.shrink();

        final dayNumber = user.programDayNumber.clamp(1, 93);
        final progress = dayNumber / 93;
        final phase = user.programPhase;
        final phaseColors = {
          1: [AppColors.phase1, AppColors.secondaryDark],
          2: [AppColors.phase2, AppColors.warningDark],
          3: [AppColors.phase3, AppColors.dangerDark],
        };
        final phaseTitles = {
          1: 'Fase 1: Fundação',
          2: 'Fase 2: Hipertrofia',
          3: 'Fase 3: Definição',
        };
        final colors = phaseColors[phase]!;

        return Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            gradient: LinearGradient(colors: colors),
            borderRadius: AppRadius.xlRadius,
            boxShadow: AppShadows.md,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        phaseTitles[phase]!,
                        style: const TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        DateFormat('EEEE, d MMM', 'pt_BR')
                            .format(DateTime.now()),
                        style: TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 13,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.md, vertical: AppSpacing.sm),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: AppRadius.lgRadius,
                    ),
                    child: Text(
                      'Dia $dayNumber/93',
                      style: const TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: AppRadius.fullRadius,
                      child: LinearProgressIndicator(
                        value: progress,
                        backgroundColor: Colors.white.withOpacity(0.3),
                        valueColor:
                            const AlwaysStoppedAnimation<Color>(Colors.white),
                        minHeight: 8,
                      ),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Text(
                    '${(progress * 100).round()}%',
                    style: const TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTodaySummary(BuildContext context) {
    return Consumer2<WorkoutProvider, MealProvider>(
      builder: (context, workouts, meals, _) {
        final completedWorkouts = workouts.completedTodayCount;
        final totalWorkouts = workouts.todayWorkouts.length;
        final loggedMeals = meals.loggedMealsCount;
        final totalMeals = meals.todayMeals.length;
        final macros = meals.todayTotalMacros;

        return Row(
          children: [
            Expanded(
              child: _SummaryCard(
                icon: Icons.fitness_center,
                iconColor: AppColors.primary,
                value: '$completedWorkouts/$totalWorkouts',
                label: 'Treinos',
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: _SummaryCard(
                icon: Icons.restaurant,
                iconColor: AppColors.secondary,
                value: '$loggedMeals/$totalMeals',
                label: 'Refeições',
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: _SummaryCard(
                icon: Icons.local_fire_department,
                iconColor: AppColors.warning,
                value: '${macros.calories.round()}',
                label: 'kcal',
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: _SummaryCard(
                icon: Icons.egg_alt_outlined,
                iconColor: AppColors.danger,
                value: '${macros.protein.round()}g',
                label: 'Proteína',
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Ações Rápidas', style: AppTextStyles.headlineSmall),
        const SizedBox(height: AppSpacing.md),
        Row(
          children: [
            Expanded(
              child: _QuickActionCard(
                icon: Icons.camera_alt,
                label: 'Novo\nScanBody',
                color: AppColors.warning,
                onTap: () {
                  // Navigate to scanbody
                  final homeState = context.findAncestorStateOfType<
                      _HomeScreenState>();
                  // ignore: invalid_use_of_protected_member
                  homeState?.setState(() => homeState._currentIndex = 3);
                },
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: _QuickActionCard(
                icon: Icons.smart_toy,
                label: 'Perguntar\npara Babi',
                color: const Color(0xFF7C3AED),
                onTap: () {
                  final homeState = context.findAncestorStateOfType<
                      _HomeScreenState>();
                  homeState?.setState(() => homeState._currentIndex = 4);
                },
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: _QuickActionCard(
                icon: Icons.add_circle_outline,
                label: 'Registrar\nRefeição',
                color: AppColors.secondary,
                onTap: () {
                  final homeState = context.findAncestorStateOfType<
                      _HomeScreenState>();
                  homeState?.setState(() => homeState._currentIndex = 2);
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTodayWorkouts(BuildContext context) {
    return Consumer<WorkoutProvider>(
      builder: (context, provider, _) {
        final workouts = provider.todayWorkouts;
        if (workouts.isEmpty) return const SizedBox.shrink();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Treinos de Hoje', style: AppTextStyles.headlineSmall),
                TextButton(
                  onPressed: () {
                    final homeState = context.findAncestorStateOfType<
                        _HomeScreenState>();
                    homeState?.setState(() => homeState._currentIndex = 1);
                  },
                  child: const Text('Ver todos'),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.sm),
            ...workouts.take(3).map((workout) => Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                  child: _WorkoutListItem(workout: workout),
                )),
          ],
        );
      },
    );
  }

  Widget _buildTodayMeals(BuildContext context) {
    return Consumer<MealProvider>(
      builder: (context, provider, _) {
        final meals = provider.todayMeals;
        if (meals.isEmpty) return const SizedBox.shrink();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Refeições de Hoje', style: AppTextStyles.headlineSmall),
                TextButton(
                  onPressed: () {
                    final homeState = context.findAncestorStateOfType<
                        _HomeScreenState>();
                    homeState?.setState(() => homeState._currentIndex = 2);
                  },
                  child: const Text('Ver todas'),
                ),
              ],
            ),
            const SizedBox(height: AppSpacing.sm),
            ...meals.take(4).map((meal) => Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                  child: _MealListItem(meal: meal),
                )),
          ],
        );
      },
    );
  }

  Widget _buildBabiTip(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF7C3AED), Color(0xFF5B21B6)],
        ),
        borderRadius: AppRadius.xlRadius,
        boxShadow: AppShadows.md,
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: AppRadius.fullRadius,
            ),
            child: const Center(
              child: Text('🤖', style: TextStyle(fontSize: 24)),
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Dica da Babi',
                  style: TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Colors.white70,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  _getDailyTip(),
                  style: const TextStyle(
                    fontFamily: 'Inter',
                    fontSize: 14,
                    color: Colors.white,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.arrow_forward_ios, color: Colors.white70, size: 16),
        ],
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  }

  String _getDailyTip() {
    final tips = [
      'Lembre-se de beber pelo menos 3L de água hoje! 💧',
      'Tome seu multivitamínico e cálcio após o café da manhã. 💊',
      'O sono é fundamental para a recuperação muscular. Durma 7-8h! 😴',
      'Proteína pós-treino nos primeiros 30 min maximiza os resultados! 💪',
      'Registre seu progresso no ScanBody esta semana! 📸',
      'Mastigar bem os alimentos melhora a absorção de nutrientes. 🍽️',
    ];
    return tips[DateTime.now().day % tips.length];
  }
}

// ─── Helper Widgets ────────────────────────────────────────────────────────

class _SummaryCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String value;
  final String label;

  const _SummaryCard({
    required this.icon,
    required this.iconColor,
    required this.value,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        border: Border.all(color: AppColors.border),
        boxShadow: AppShadows.sm,
      ),
      child: Column(
        children: [
          Icon(icon, color: iconColor, size: 22),
          const SizedBox(height: AppSpacing.xs),
          Text(
            value,
            style: AppTextStyles.titleMedium,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            label,
            style: AppTextStyles.caption,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: AppRadius.lgRadius,
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: AppSpacing.xs),
            Text(
              label,
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: color,
                height: 1.3,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _WorkoutListItem extends StatelessWidget {
  final dynamic workout;

  const _WorkoutListItem({required this.workout});

  @override
  Widget build(BuildContext context) {
    final isCompleted = workout.isCompleted as bool;
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        border: Border.all(
          color: isCompleted
              ? AppColors.secondary.withOpacity(0.3)
              : AppColors.border,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: isCompleted
                  ? AppColors.secondary.withOpacity(0.1)
                  : AppColors.primary.withOpacity(0.1),
              borderRadius: AppRadius.mdRadius,
            ),
            child: Icon(
              isCompleted
                  ? Icons.check_circle
                  : Icons.fitness_center,
              color: isCompleted ? AppColors.secondary : AppColors.primary,
              size: 20,
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  workout.title as String,
                  style: AppTextStyles.titleMedium,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  workout.scheduledTime != null
                      ? '${workout.scheduledTime} • ${workout.durationMinutes ?? 0} min'
                      : '${workout.durationMinutes ?? 0} min',
                  style: AppTextStyles.bodySmall,
                ),
              ],
            ),
          ),
          if (isCompleted)
            const Icon(Icons.check_circle,
                color: AppColors.secondary, size: 20),
        ],
      ),
    );
  }
}

class _MealListItem extends StatelessWidget {
  final dynamic meal;

  const _MealListItem({required this.meal});

  @override
  Widget build(BuildContext context) {
    final isLogged = meal.isLogged as bool;
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        border: Border.all(
          color: isLogged
              ? AppColors.secondary.withOpacity(0.3)
              : AppColors.border,
        ),
      ),
      child: Row(
        children: [
          Text(
            meal.typeEmoji as String,
            style: const TextStyle(fontSize: 24),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  meal.typeLabel as String,
                  style: AppTextStyles.titleMedium,
                ),
                Text(
                  meal.scheduledTime as String,
                  style: AppTextStyles.bodySmall,
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm, vertical: 2),
            decoration: BoxDecoration(
              color: isLogged
                  ? AppColors.secondary.withOpacity(0.1)
                  : AppColors.surfaceVariant,
              borderRadius: AppRadius.fullRadius,
            ),
            child: Text(
              isLogged ? 'Registrado' : 'Pendente',
              style: TextStyle(
                fontFamily: 'Inter',
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: isLogged ? AppColors.secondary : AppColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Expose the state for navigation
class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  set currentIndex(int value) => setState(() => _currentIndex = value);
}
