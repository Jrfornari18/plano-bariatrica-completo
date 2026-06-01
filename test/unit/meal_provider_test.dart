import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/presentation/providers/meal_provider.dart';
import 'package:barifit_app/data/models/meal_model.dart';

void main() {
  group('MealProvider Tests', () {
    late MealProvider provider;

    setUp(() {
      provider = MealProvider();
    });

    test('initial state is empty', () {
      expect(provider.meals, isEmpty);
      expect(provider.recipes, isEmpty);
      expect(provider.isLoading, isFalse);
      expect(provider.waterGlasses, 0);
    });

    test('waterGlasses increments correctly', () {
      provider.toggleWaterGlass(0); // tap glass 1
      expect(provider.waterGlasses, 1);

      provider.toggleWaterGlass(1); // tap glass 2
      expect(provider.waterGlasses, 2);

      provider.toggleWaterGlass(2); // tap glass 3
      expect(provider.waterGlasses, 3);
    });

    test('waterGlasses decrements when tapping below current', () {
      provider.toggleWaterGlass(0);
      provider.toggleWaterGlass(1);
      provider.toggleWaterGlass(2);
      expect(provider.waterGlasses, 3);

      provider.toggleWaterGlass(1); // tap glass 2 when 3 are filled → resets to 1
      expect(provider.waterGlasses, 1);
    });

    test('todayTotalMacros returns zero when no meals', () {
      final macros = provider.todayTotalMacros;
      expect(macros.protein, 0);
      expect(macros.calories, 0);
    });

    test('weekMacrosHistory returns 7 items', () {
      final history = provider.weekMacrosHistory;
      expect(history.length, 7);
    });

    test('filteredRecipes returns all when query is empty', () async {
      await provider.loadRecipes();
      final all = provider.filteredRecipes('');
      final filtered = provider.filteredRecipes('', category: 'Todos');
      expect(all.length, filtered.length);
    });

    test('loadMealsForDate generates meals for a weekday', () async {
      final monday = DateTime(2025, 1, 6); // Monday
      await provider.loadMealsForDate(monday, 1);
      expect(provider.meals, isNotEmpty);
    });

    test('logMeal toggles isLogged state', () async {
      final monday = DateTime(2025, 1, 6);
      await provider.loadMealsForDate(monday, 1);
      
      final meal = provider.meals.first;
      expect(meal.isLogged, isFalse);
      
      await provider.logMeal(meal.id);
      expect(provider.meals.first.isLogged, isTrue);
      
      await provider.logMeal(meal.id);
      expect(provider.meals.first.isLogged, isFalse);
    });

    test('toggleMealLogged is alias for logMeal', () async {
      final monday = DateTime(2025, 1, 6);
      await provider.loadMealsForDate(monday, 1);
      
      final meal = provider.meals.first;
      await provider.toggleMealLogged(meal.id);
      expect(provider.meals.first.isLogged, isTrue);
    });
  });
}
