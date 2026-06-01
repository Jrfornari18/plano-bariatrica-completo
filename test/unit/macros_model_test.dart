import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/data/models/meal_model.dart';

void main() {
  group('MacrosModel Tests', () {
    test('addition operator works correctly', () {
      const m1 = MacrosModel(protein: 20, carbs: 30, fat: 10, calories: 300, fiber: 5);
      const m2 = MacrosModel(protein: 10, carbs: 20, fat: 5, calories: 150, fiber: 2);
      
      final result = m1 + m2;
      
      expect(result.protein, 30);
      expect(result.carbs, 50);
      expect(result.fat, 15);
      expect(result.calories, 450);
      expect(result.fiber, 7);
    });
  });
}
