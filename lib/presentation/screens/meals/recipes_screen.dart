import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/meal_provider.dart';
import '../../../data/models/meal_model.dart';

class RecipesScreen extends StatefulWidget {
  const RecipesScreen({super.key});

  @override
  State<RecipesScreen> createState() => _RecipesScreenState();
}

class _RecipesScreenState extends State<RecipesScreen> {
  String _searchQuery = '';
  String? _selectedCategory;

  final List<String> _categories = [
    'Todas',
    'Café da manhã',
    'Almoço',
    'Lanche',
    'Jantar',
    'Pós-treino',
    'Proteica',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Receitas'),
      ),
      body: Consumer<MealProvider>(
        builder: (context, provider, _) {
          final recipes = provider.filteredRecipes(
            query: _searchQuery,
            category: _selectedCategory == 'Todas' ? null : _selectedCategory,
          );

          return Column(
            children: [
              // Search bar
              Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: TextField(
                  onChanged: (value) =>
                      setState(() => _searchQuery = value),
                  decoration: InputDecoration(
                    hintText: 'Buscar receitas...',
                    prefixIcon: const Icon(Icons.search,
                        color: AppColors.textSecondary),
                    filled: true,
                    fillColor: AppColors.surfaceVariant,
                    border: OutlineInputBorder(
                      borderRadius: AppRadius.lgRadius,
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.lg,
                      vertical: AppSpacing.md,
                    ),
                  ),
                ),
              ),

              // Categories
              SizedBox(
                height: 40,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.lg),
                  itemCount: _categories.length,
                  separatorBuilder: (_, __) =>
                      const SizedBox(width: AppSpacing.sm),
                  itemBuilder: (context, index) {
                    final cat = _categories[index];
                    final isSelected = _selectedCategory == cat ||
                        (cat == 'Todas' && _selectedCategory == null);
                    return GestureDetector(
                      onTap: () => setState(() => _selectedCategory =
                          cat == 'Todas' ? null : cat),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        padding: const EdgeInsets.symmetric(
                            horizontal: AppSpacing.md),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? AppColors.secondary
                              : AppColors.surfaceVariant,
                          borderRadius: AppRadius.fullRadius,
                        ),
                        child: Center(
                          child: Text(
                            cat,
                            style: TextStyle(
                              fontFamily: 'Inter',
                              fontSize: 13,
                              fontWeight: isSelected
                                  ? FontWeight.w600
                                  : FontWeight.w400,
                              color: isSelected
                                  ? Colors.white
                                  : AppColors.textSecondary,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: AppSpacing.md),

              // Recipes grid
              Expanded(
                child: recipes.isEmpty
                    ? const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text('🍽️',
                                style: TextStyle(fontSize: 48)),
                            SizedBox(height: AppSpacing.md),
                            Text('Nenhuma receita encontrada',
                                style: AppTextStyles.headlineSmall),
                          ],
                        ),
                      )
                    : GridView.builder(
                        padding: const EdgeInsets.all(AppSpacing.lg),
                        gridDelegate:
                            const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: AppSpacing.md,
                          mainAxisSpacing: AppSpacing.md,
                          childAspectRatio: 0.8,
                        ),
                        itemCount: recipes.length,
                        itemBuilder: (context, index) =>
                            _RecipeCard(recipe: recipes[index]),
                      ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _RecipeCard extends StatelessWidget {
  final RecipeModel recipe;

  const _RecipeCard({required this.recipe});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => _showRecipeDetail(context, recipe),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: AppRadius.xlRadius,
          border: Border.all(color: AppColors.border),
          boxShadow: AppShadows.sm,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Recipe image / emoji
            Container(
              height: 100,
              decoration: BoxDecoration(
                color: AppColors.secondary.withOpacity(0.1),
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(16),
                ),
              ),
              child: Center(
                child: Text(
                  recipe.emoji,
                  style: const TextStyle(fontSize: 48),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(AppSpacing.sm),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    recipe.name,
                    style: AppTextStyles.titleMedium,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.timer_outlined,
                          size: 12, color: AppColors.textHint),
                      const SizedBox(width: 2),
                      Text(
                        '${recipe.prepTimeMinutes} min',
                        style: AppTextStyles.caption,
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.danger.withOpacity(0.1),
                          borderRadius: AppRadius.fullRadius,
                        ),
                        child: Text(
                          '${recipe.macros.protein.round()}g prot',
                          style: const TextStyle(
                            fontFamily: 'Inter',
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                            color: AppColors.danger,
                          ),
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${recipe.macros.calories.round()} kcal',
                        style: AppTextStyles.caption,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showRecipeDetail(BuildContext context, RecipeModel recipe) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.95,
        minChildSize: 0.5,
        expand: false,
        builder: (context, scrollController) => SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.border,
                    borderRadius: AppRadius.fullRadius,
                  ),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
              Center(
                child: Text(recipe.emoji,
                    style: const TextStyle(fontSize: 64)),
              ),
              const SizedBox(height: AppSpacing.md),
              Text(recipe.name, style: AppTextStyles.headlineMedium),
              const SizedBox(height: AppSpacing.sm),
              Row(
                children: [
                  const Icon(Icons.timer_outlined,
                      size: 16, color: AppColors.textHint),
                  const SizedBox(width: 4),
                  Text('${recipe.prepTimeMinutes} min',
                      style: AppTextStyles.bodySmall),
                  const SizedBox(width: AppSpacing.md),
                  const Icon(Icons.people_outline,
                      size: 16, color: AppColors.textHint),
                  const SizedBox(width: 4),
                  Text('${recipe.servings} porção(ões)',
                      style: AppTextStyles.bodySmall),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _RecipeMacro(
                      label: 'Calorias',
                      value:
                          '${recipe.macros.calories.round()} kcal',
                      color: AppColors.warning),
                  _RecipeMacro(
                      label: 'Proteína',
                      value: '${recipe.macros.protein.round()}g',
                      color: AppColors.danger),
                  _RecipeMacro(
                      label: 'Carbs',
                      value: '${recipe.macros.carbs.round()}g',
                      color: AppColors.primary),
                  _RecipeMacro(
                      label: 'Gordura',
                      value: '${recipe.macros.fat.round()}g',
                      color: AppColors.secondary),
                ],
              ),
              const SizedBox(height: AppSpacing.xl),
              const Text('Ingredientes', style: AppTextStyles.headlineSmall),
              const SizedBox(height: AppSpacing.md),
              ...recipe.ingredients.map((ing) => Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
                    child: Row(
                      children: [
                        const Icon(Icons.circle,
                            size: 6, color: AppColors.secondary),
                        const SizedBox(width: AppSpacing.sm),
                        Expanded(
                          child: Text(ing,
                              style: AppTextStyles.bodyMedium),
                        ),
                      ],
                    ),
                  )),
              const SizedBox(height: AppSpacing.xl),
              const Text('Modo de Preparo',
                  style: AppTextStyles.headlineSmall),
              const SizedBox(height: AppSpacing.md),
              ...recipe.instructions.asMap().entries.map((e) => Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.md),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 28,
                          height: 28,
                          decoration: BoxDecoration(
                            color: AppColors.secondary.withOpacity(0.1),
                            borderRadius: AppRadius.fullRadius,
                          ),
                          child: Center(
                            child: Text(
                              '${e.key + 1}',
                              style: const TextStyle(
                                fontFamily: 'Inter',
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: AppColors.secondary,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: AppSpacing.md),
                        Expanded(
                          child: Text(
                            e.value,
                            style: AppTextStyles.bodyMedium.copyWith(
                              height: 1.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  )),
              const SizedBox(height: AppSpacing.xxxl),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecipeMacro extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _RecipeMacro({
    required this.label,
    required this.value,
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
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: color,
          ),
        ),
        Text(label, style: AppTextStyles.caption),
      ],
    );
  }
}
