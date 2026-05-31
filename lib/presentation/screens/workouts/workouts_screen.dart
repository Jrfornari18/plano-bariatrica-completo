import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/workout_provider.dart';
import '../../../data/models/workout_model.dart';
import 'workout_detail_screen.dart';

class WorkoutsScreen extends StatefulWidget {
  const WorkoutsScreen({super.key});

  @override
  State<WorkoutsScreen> createState() => _WorkoutsScreenState();
}

class _WorkoutsScreenState extends State<WorkoutsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Treinos'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Hoje'),
            Tab(text: 'Semana'),
            Tab(text: 'Programa'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _TodayTab(selectedDate: _selectedDate),
          const _WeekTab(),
          const _ProgramTab(),
        ],
      ),
    );
  }
}

// ─── Today Tab ─────────────────────────────────────────────────────────────

class _TodayTab extends StatelessWidget {
  final DateTime selectedDate;

  const _TodayTab({required this.selectedDate});

  @override
  Widget build(BuildContext context) {
    return Consumer<WorkoutProvider>(
      builder: (context, provider, _) {
        final workouts = provider.todayWorkouts;

        return CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: _buildDateHeader(context, provider),
            ),
            if (workouts.isEmpty)
              const SliverFillRemaining(
                child: _EmptyWorkoutsState(),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final workout = workouts[index];
                      return Padding(
                        padding:
                            const EdgeInsets.only(bottom: AppSpacing.md),
                        child: _WorkoutCard(workout: workout),
                      );
                    },
                    childCount: workouts.length,
                  ),
                ),
              ),
          ],
        );
      },
    );
  }

  Widget _buildDateHeader(BuildContext context, WorkoutProvider provider) {
    return Container(
      color: AppColors.surface,
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            DateFormat('EEEE, d de MMMM', 'pt_BR').format(selectedDate),
            style: AppTextStyles.headlineSmall,
          ),
          const SizedBox(height: AppSpacing.sm),
          _buildWeekDays(context, provider),
        ],
      ),
    );
  }

  Widget _buildWeekDays(BuildContext context, WorkoutProvider provider) {
    final today = DateTime.now();
    final startOfWeek = today.subtract(Duration(days: today.weekday - 1));

    return SizedBox(
      height: 64,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: 7,
        separatorBuilder: (_, __) =>
            const SizedBox(width: AppSpacing.sm),
        itemBuilder: (context, index) {
          final date = startOfWeek.add(Duration(days: index));
          final isToday = date.day == today.day &&
              date.month == today.month &&
              date.year == today.year;
          final isSelected = date.day == selectedDate.day;

          return GestureDetector(
            onTap: () => provider.loadWorkoutsForDate(date),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 44,
              decoration: BoxDecoration(
                color: isSelected
                    ? AppColors.primary
                    : isToday
                        ? AppColors.primary.withOpacity(0.1)
                        : Colors.transparent,
                borderRadius: AppRadius.lgRadius,
                border: isToday && !isSelected
                    ? Border.all(color: AppColors.primary)
                    : null,
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    DateFormat('E', 'pt_BR').format(date).substring(0, 1),
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: isSelected
                          ? Colors.white
                          : AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    date.day.toString(),
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: isSelected
                          ? Colors.white
                          : AppColors.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

// ─── Week Tab ──────────────────────────────────────────────────────────────

class _WeekTab extends StatelessWidget {
  const _WeekTab();

  @override
  Widget build(BuildContext context) {
    return Consumer<WorkoutProvider>(
      builder: (context, provider, _) {
        final weekWorkouts = provider.weekWorkouts;

        return ListView.builder(
          padding: const EdgeInsets.all(AppSpacing.lg),
          itemCount: 7,
          itemBuilder: (context, dayIndex) {
            final today = DateTime.now();
            final startOfWeek =
                today.subtract(Duration(days: today.weekday - 1));
            final date = startOfWeek.add(Duration(days: dayIndex));
            final dayWorkouts = weekWorkouts.where((w) =>
                w.date.year == date.year &&
                w.date.month == date.month &&
                w.date.day == date.day).toList();

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(
                      bottom: AppSpacing.sm, top: AppSpacing.md),
                  child: Row(
                    children: [
                      Text(
                        DateFormat('EEEE', 'pt_BR').format(date),
                        style: AppTextStyles.titleLarge,
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      Text(
                        DateFormat('d/MM').format(date),
                        style: AppTextStyles.bodySmall,
                      ),
                    ],
                  ),
                ),
                if (dayWorkouts.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(AppSpacing.md),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: AppRadius.lgRadius,
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Text(
                      'Descanso ativo — alongamento e caminhada leve',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  )
                else
                  ...dayWorkouts.map((w) => Padding(
                        padding:
                            const EdgeInsets.only(bottom: AppSpacing.sm),
                        child: _WorkoutCard(workout: w, compact: true),
                      )),
              ],
            );
          },
        );
      },
    );
  }
}

// ─── Program Tab ───────────────────────────────────────────────────────────

class _ProgramTab extends StatelessWidget {
  const _ProgramTab();

  @override
  Widget build(BuildContext context) {
    final phases = [
      _PhaseInfo(
        number: 1,
        title: 'Fase 1: Fundação',
        days: 'Dias 1–31',
        description:
            'Adaptação neuromuscular, aprendizado dos movimentos e construção da base aeróbica.',
        color: AppColors.phase1,
        workoutTypes: ['Musculação 3x/sem', 'Natação 2x/sem', 'Calistenia diária'],
      ),
      _PhaseInfo(
        number: 2,
        title: 'Fase 2: Hipertrofia',
        days: 'Dias 32–62',
        description:
            'Aumento de volume e intensidade para maximizar o ganho de massa muscular.',
        color: AppColors.phase2,
        workoutTypes: ['Musculação 4x/sem', 'Corrida 2x/sem', 'Natação 2x/sem'],
      ),
      _PhaseInfo(
        number: 3,
        title: 'Fase 3: Definição',
        days: 'Dias 63–93',
        description:
            'Foco em definição muscular com treinos de alta intensidade e cardio estratégico.',
        color: AppColors.phase3,
        workoutTypes: ['Musculação 5x/sem', 'HIIT 2x/sem', 'Corrida 3x/sem'],
      ),
    ];

    return ListView(
      padding: const EdgeInsets.all(AppSpacing.lg),
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: AppColors.primaryGradient,
            ),
            borderRadius: AppRadius.xlRadius,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Programa Barifit+ 93 Dias',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                'Programa completo de transformação corporal pós-bariátrica com 3 fases progressivas.',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 14,
                  color: Colors.white.withOpacity(0.85),
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.xl),
        ...phases.map((phase) => Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.lg),
              child: _PhaseCard(phase: phase),
            )),
        const SizedBox(height: AppSpacing.lg),
        _buildWorkoutTypes(),
      ],
    );
  }

  Widget _buildWorkoutTypes() {
    final types = [
      {'icon': '🏋️', 'title': 'Musculação', 'desc': 'Hipertrofia e força'},
      {'icon': '🏊', 'title': 'Natação', 'desc': 'Cardio de baixo impacto'},
      {'icon': '🏃', 'title': 'Corrida', 'desc': 'Resistência aeróbica'},
      {'icon': '💪', 'title': 'Calistenia', 'desc': 'Peso corporal'},
      {'icon': '🧘', 'title': 'Alongamento', 'desc': 'Flexibilidade e recuperação'},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Tipos de Treino', style: AppTextStyles.headlineSmall),
        const SizedBox(height: AppSpacing.md),
        ...types.map((t) => Container(
              margin: const EdgeInsets.only(bottom: AppSpacing.sm),
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: AppRadius.lgRadius,
                border: Border.all(color: AppColors.border),
              ),
              child: Row(
                children: [
                  Text(t['icon']!, style: const TextStyle(fontSize: 28)),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(t['title']!, style: AppTextStyles.titleMedium),
                        Text(t['desc']!, style: AppTextStyles.bodySmall),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios,
                      size: 14, color: AppColors.textHint),
                ],
              ),
            )),
      ],
    );
  }
}

// ─── Workout Card ──────────────────────────────────────────────────────────

class _WorkoutCard extends StatelessWidget {
  final WorkoutModel workout;
  final bool compact;

  const _WorkoutCard({required this.workout, this.compact = false});

  @override
  Widget build(BuildContext context) {
    final typeColors = {
      WorkoutType.musculacao: AppColors.primary,
      WorkoutType.natacao: const Color(0xFF0EA5E9),
      WorkoutType.corrida: AppColors.secondary,
      WorkoutType.calistenia: AppColors.warning,
      WorkoutType.alongamento: const Color(0xFF7C3AED),
      WorkoutType.funcional: AppColors.danger,
      WorkoutType.descanso: AppColors.textHint,
    };

    final typeIcons = {
      WorkoutType.musculacao: '🏋️',
      WorkoutType.natacao: '🏊',
      WorkoutType.corrida: '🏃',
      WorkoutType.calistenia: '💪',
      WorkoutType.alongamento: '🧘',
      WorkoutType.funcional: '⚡',
      WorkoutType.descanso: '😴',
    };

    final color = typeColors[workout.type] ?? AppColors.primary;
    final icon = typeIcons[workout.type] ?? '🏋️';

    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => WorkoutDetailScreen(workout: workout),
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: AppRadius.xlRadius,
          border: Border.all(
            color: workout.isCompleted
                ? AppColors.secondary.withOpacity(0.3)
                : AppColors.border,
          ),
          boxShadow: AppShadows.sm,
        ),
        child: Row(
          children: [
            Container(
              width: compact ? 44 : 56,
              height: compact ? 44 : 56,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: AppRadius.lgRadius,
              ),
              child: Center(
                child: Text(
                  icon,
                  style: TextStyle(fontSize: compact ? 22 : 28),
                ),
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    workout.title,
                    style: compact
                        ? AppTextStyles.titleMedium
                        : AppTextStyles.titleLarge,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      if (workout.scheduledTime != null) ...[
                        Icon(Icons.access_time,
                            size: 12, color: AppColors.textHint),
                        const SizedBox(width: 2),
                        Text(
                          workout.scheduledTime!,
                          style: AppTextStyles.caption,
                        ),
                        const SizedBox(width: AppSpacing.sm),
                      ],
                      Icon(Icons.timer_outlined,
                          size: 12, color: AppColors.textHint),
                      const SizedBox(width: 2),
                      Text(
                        '${workout.durationMinutes} min',
                        style: AppTextStyles.caption,
                      ),
                      if (workout.exercises.isNotEmpty) ...[
                        const SizedBox(width: AppSpacing.sm),
                        Icon(Icons.list_alt,
                            size: 12, color: AppColors.textHint),
                        const SizedBox(width: 2),
                        Text(
                          '${workout.exercises.length} exercícios',
                          style: AppTextStyles.caption,
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),
            if (workout.isCompleted)
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.sm, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.secondary.withOpacity(0.1),
                  borderRadius: AppRadius.fullRadius,
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle,
                        color: AppColors.secondary, size: 14),
                    SizedBox(width: 4),
                    Text(
                      'Feito',
                      style: TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.secondary,
                      ),
                    ),
                  ],
                ),
              )
            else
              const Icon(Icons.arrow_forward_ios,
                  size: 14, color: AppColors.textHint),
          ],
        ),
      ),
    );
  }
}

// ─── Phase Card ────────────────────────────────────────────────────────────

class _PhaseCard extends StatelessWidget {
  final _PhaseInfo phase;

  const _PhaseCard({required this.phase});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.xlRadius,
        border: Border.all(color: phase.color.withOpacity(0.3)),
        boxShadow: AppShadows.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: phase.color.withOpacity(0.1),
                  borderRadius: AppRadius.mdRadius,
                ),
                child: Center(
                  child: Text(
                    '${phase.number}',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: phase.color,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(phase.title, style: AppTextStyles.titleLarge),
                    Text(phase.days, style: AppTextStyles.bodySmall),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            phase.description,
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: phase.workoutTypes
                .map((t) => Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.sm, vertical: 4),
                      decoration: BoxDecoration(
                        color: phase.color.withOpacity(0.1),
                        borderRadius: AppRadius.fullRadius,
                      ),
                      child: Text(
                        t,
                        style: TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: phase.color,
                        ),
                      ),
                    ))
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _PhaseInfo {
  final int number;
  final String title;
  final String days;
  final String description;
  final Color color;
  final List<String> workoutTypes;

  const _PhaseInfo({
    required this.number,
    required this.title,
    required this.days,
    required this.description,
    required this.color,
    required this.workoutTypes,
  });
}

class _EmptyWorkoutsState extends StatelessWidget {
  const _EmptyWorkoutsState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('😴', style: TextStyle(fontSize: 64)),
          const SizedBox(height: AppSpacing.lg),
          const Text('Dia de Descanso', style: AppTextStyles.headlineMedium),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Aproveite para recuperar os músculos.\nFaça um alongamento leve se quiser.',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
