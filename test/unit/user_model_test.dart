import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/data/models/user_model.dart';

void main() {
  group('UserModel Tests', () {
    final testDate = DateTime(2024, 1, 1);
    
    test('programDayNumber calculates correctly', () {
      final user = UserModel(
        id: '1',
        name: 'Test User',
        email: 'test@test.com',
        programStartDate: DateTime.now().subtract(const Duration(days: 10)),
        createdAt: DateTime.now(),
      );
      
      expect(user.programDayNumber, 11);
    });

    test('programWeek calculates correctly', () {
      final user = UserModel(
        id: '1',
        name: 'Test User',
        email: 'test@test.com',
        programStartDate: DateTime.now().subtract(const Duration(days: 15)), // Day 16 = Week 3
        createdAt: DateTime.now(),
      );
      
      expect(user.programWeek, 3);
    });

    test('bmi calculates correctly', () {
      final user = UserModel(
        id: '1',
        name: 'Test User',
        email: 'test@test.com',
        weight: 80.0,
        height: 180.0,
        programStartDate: DateTime.now(),
        createdAt: DateTime.now(),
      );
      
      // 80 / (1.8 * 1.8) = 24.69
      expect(user.bmi, closeTo(24.69, 0.01));
    });
  });
}
