import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/meal_provider.dart';
import '../../../data/models/meal_model.dart';
import 'meal_detail_screen.dart';
import 'recipes_screen.dart';

class MealsScreen extends StatefulWidget {
  const MealsScreen({super.key});

  @override
  State<MealsScreen> createState() => _MealsScreenState();
}

class _MealsScreenState extends State<MealsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
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
        title: const Text('Refeições'),
        actions: [
          IconButton(
            icon: const Icon(Icons.menu_book_outlined),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const RecipesScreen()),
            ),
            tooltip: 'Receitas',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Hoje'),
            Tab(text: 'Macros'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          const _TodayMealsTab(),
          const _MacrosTab(),
        ],
      ),
    );
  }
}

// ─── Today Meals Tab ───────────────────────────────────────────────────────

class _TodayMealsTab extends StatelessWidget {
  const _TodayMealsTab();

  @override
  Widget build(BuildContext context) {
    return Consumer<MealProvider>(
      builder: (context, provider, _) {
        final meals = provider.todayMeals;
        final macros = provider.todayTotalMacros;

        return CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: _buildMacrosSummary(context, macros),
            ),
            SliverPadding(
              padding: const EdgeInsets.all(AppSpacing.lg),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final meal = meals[index];
                    return Padding(
                      padding:
                          const EdgeInsets.only(bottom: AppSpacing.md),
                      child: _MealCard(meal: meal),
                    );
                  },
                  childCount: meals.length,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildMacrosSummary(BuildContext context, MacrosModel macros) {
    return Container(
      margin: const EdgeInsets.all(AppSpacing.lg),
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.secondary, AppColors.secondaryDark],
        ),
        borderRadius: AppRadius.xlRadius,
        boxShadow: AppShadows.md,
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Macros do Dia',
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              Text(
                DateFormat('d MMM', 'pt_BR').format(DateTime.now()),
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 13,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _MacroItem(
                label: 'Calorias',
                value: '${macros.calories.round()}',
                unit: 'kcal',
                target: '1800',
                color: Colors.white,
              ),
              _MacroItem(
                label: 'Proteína',
                value: '${macros.protein.round()}',
                unit: 'g',
                target: '175',
                color: Colors.white,
              ),
              _MacroItem(
                label: 'Carbs',
                value: '${macros.carbs.round()}',
                unit: 'g',
                target: '200',
                color: Colors.white,
              ),
              _MacroItem(
                label: 'Gordura',
                value: '${macros.fat.round()}',
                unit: 'g',
                target: '60',
                color: Colors.white,
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          // Protein progress bar
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Meta Proteica',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 13,
                      color: Colors.white70,
                    ),
                  ),
                  Text(
                    '${macros.protein.round()}/175g',
                    style: const TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.xs),
              ClipRRect(
                borderRadius: AppRadius.fullRadius,
                child: LinearProgressIndicator(
                  value: (macros.protein / 175).clamp(0.0, 1.0),
                  backgroundColor: Colors.white.withOpacity(0.3),
                  valueColor:
                      const AlwaysStoppedAnimation<Color>(Colors.white),
                  minHeight: 8,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ─── Macros Tab ────────────────────────────────────────────────────────────

class _MacrosTab extends StatelessWidget {
  const _MacrosTab();

  @override
  Widget build(BuildContext context) {
    return Consumer<MealProvider>(
      builder: (context, provider, _) {
        final macros = provider.todayTotalMacros;
        final weekHistory = provider.weekMacrosHistory;

        return ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            _buildNutritionGoals(macros),
            const SizedBox(height: AppSpacing.lg),
            _buildWaterIntake(provider),
            const SizedBox(height: AppSpacing.lg),
            _buildSupplements(),
          ],
        );
      },
    );
  }

  Widget _buildNutritionGoals(MacrosModel macros) {
    final goals = [
      _NutritionGoal(
          label: 'Calorias',
          current: macros.calories,
          target: 1800,
          unit: 'kcal',
          color: AppColors.warning),
      _NutritionGoal(
          label: 'Proteína',
          current: macros.protein,
          target: 175,
          unit: 'g',
          color: AppColors.danger),
      _NutritionGoal(
          label: 'Carboidratos',
          current: macros.carbs,
          target: 200,
          unit: 'g',
          color: AppColors.primary),
      _NutritionGoal(
          label: 'Gorduras',
          current: macros.fat,
          target: 60,
          unit: 'g',
          color: AppColors.secondary),
      _NutritionGoal(
          label: 'Fibras',
          current: macros.fiber ?? 0,
          target: 25,
          unit: 'g',
          color: const Color(0xFF7C3AED)),
    ];

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
          const Text('Metas Nutricionais', style: AppTextStyles.headlineSmall),
          const SizedBox(height: AppSpacing.lg),
          ...goals.map((goal) => Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.md),
                child: _NutritionGoalRow(goal: goal),
              )),
        ],
      ),
    );
  }

  Widget _buildWaterIntake(MealProvider provider) {
    final glasses = provider.waterGlasses;
    const targetGlasses = 12;

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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Hidratação', style: AppTextStyles.headlineSmall),
              Text(
                '${glasses * 250}ml / 3000ml',
                style: AppTextStyles.bodySmall,
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: List.generate(
              targetGlasses,
              (index) => GestureDetector(
                onTap: () => provider.toggleWaterGlass(index),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: index < glasses
                        ? const Color(0xFF0EA5E9).withOpacity(0.15)
                        : AppColors.surfaceVariant,
                    borderRadius: AppRadius.mdRadius,
                    border: Border.all(
                      color: index < glasses
                          ? const Color(0xFF0EA5E9)
                          : AppColors.border,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      '💧',
                      style: TextStyle(
                        fontSize: index < glasses ? 22 : 18,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            '$glasses de $targetGlasses copos (${(glasses * 250 / 1000).toStringAsFixed(1)}L)',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSupplements() {
    final supplements = [
      {'name': 'Multivitamínico', 'time': 'Café da manhã', 'icon': '💊'},
      {'name': 'Cálcio + Vitamina D', 'time': 'Almoço', 'icon': '🦴'},
      {'name': 'Vitamina B12', 'time': 'Café da manhã', 'icon': '💉'},
      {'name': 'Whey Protein', 'time': 'Pós-treino', 'icon': '🥛'},
      {'name': 'Creatina', 'time': 'Qualquer hora', 'icon': '⚡'},
      {'name': 'Ômega-3', 'time': 'Jantar', 'icon': '🐟'},
    ];

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
          const Text('Suplementação', style: AppTextStyles.headlineSmall),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Suplementos recomendados para pós-bariátrica',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppSpacing.lg),
          ...supplements.map((s) => Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                child: Row(
                  children: [
                    Text(s['icon']!,
                        style: const TextStyle(fontSize: 24)),
                    const SizedBox(width: AppSpacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(s['name']!,
                              style: AppTextStyles.titleMedium),
                          Text(s['time']!,
                              style: AppTextStyles.bodySmall),
                        ],
                      ),
                    ),
                    const Icon(Icons.check_circle_outline,
                        color: AppColors.textHint, size: 20),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}

// ─── Meal Card ─────────────────────────────────────────────────────────────

class _MealCard extends StatelessWidget {
  final MealModel meal;

  const _MealCard({required this.meal});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => MealDetailScreen(meal: meal),
        ),
      ),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: AppRadius.xlRadius,
          border: Border.all(
            color: meal.isLogged
                ? AppColors.secondary.withOpacity(0.3)
                : AppColors.border,
          ),
          boxShadow: AppShadows.sm,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(meal.typeEmoji,
                    style: const TextStyle(fontSize: 32)),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(meal.typeLabel,
                          style: AppTextStyles.titleLarge),
                      Text(
                        meal.scheduledTime,
                        style: AppTextStyles.bodySmall,
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${meal.totalMacros.calories.round()} kcal',
                      style: AppTextStyles.titleMedium,
                    ),
                    Text(
                      '${meal.totalMacros.protein.round()}g prot.',
                      style: AppTextStyles.caption,
                    ),
                  ],
                ),
              ],
            ),
            if (meal.items.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.md),
              const Divider(height: 1),
              const SizedBox(height: AppSpacing.sm),
              ...meal.items.take(3).map((item) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      children: [
                        const Icon(Icons.circle,
                            size: 6, color: AppColors.textHint),
                        const SizedBox(width: AppSpacing.sm),
                        Expanded(
                          child: Text(
                            item.name,
                            style: AppTextStyles.bodySmall,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(
                          '${item.quantity}${item.unit}',
                          style: AppTextStyles.caption,
                        ),
                      ],
                    ),
                  )),
              if (meal.items.length > 3)
                Text(
                  '+${meal.items.length - 3} itens',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.primary,
                  ),
                ),
            ],
            const SizedBox(height: AppSpacing.sm),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.sm, vertical: 2),
                  decoration: BoxDecoration(
                    color: meal.isLogged
                        ? AppColors.secondary.withOpacity(0.1)
                        : AppColors.surfaceVariant,
                    borderRadius: AppRadius.fullRadius,
                  ),
                  child: Text(
                    meal.isLogged ? '✅ Registrado' : '⏳ Pendente',
                    style: TextStyle(
                      fontFamily: 'Inter',
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: meal.isLogged
                          ? AppColors.secondary
                          : AppColors.textSecondary,
                    ),
                  ),
                ),
                const Icon(Icons.arrow_forward_ios,
                    size: 14, color: AppColors.textHint),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Helper Widgets ────────────────────────────────────────────────────────

class _MacroItem extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final String target;
  final Color color;

  const _MacroItem({
    required this.label,
    required this.value,
    required this.unit,
    required this.target,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontFamily: 'Inter',
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: color,
          ),
        ),
        Text(
          unit,
          style: TextStyle(
            fontFamily: 'Inter',
            fontSize: 12,
            color: color.withOpacity(0.8),
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'Inter',
            fontSize: 11,
            color: Colors.white70,
          ),
        ),
        Text(
          'meta: $target$unit',
          style: const TextStyle(
            fontFamily: 'Inter',
            fontSize: 10,
            color: Colors.white54,
          ),
        ),
      ],
    );
  }
}

class _NutritionGoal {
  final String label;
  final double current;
  final double target;
  final String unit;
  final Color color;

  const _NutritionGoal({
    required this.label,
    required this.current,
    required this.target,
    required this.unit,
    required this.color,
  });
}

class _NutritionGoalRow extends StatelessWidget {
  final _NutritionGoal goal;

  const _NutritionGoalRow({required this.goal});

  @override
  Widget build(BuildContext context) {
    final progress = (goal.current / goal.target).clamp(0.0, 1.0);
    final isOver = goal.current > goal.target;

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(goal.label, style: AppTextStyles.labelMedium),
            Text(
              '${goal.current.round()}/${goal.target.round()}${goal.unit}',
              style: AppTextStyles.labelMedium.copyWith(
                color: isOver ? AppColors.danger : AppColors.textSecondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.xs),
        ClipRRect(
          borderRadius: AppRadius.fullRadius,
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: goal.color.withOpacity(0.1),
            valueColor: AlwaysStoppedAnimation<Color>(
              isOver ? AppColors.danger : goal.color,
            ),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}
