import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/presentation/providers/workout_provider.dart';

void main() {
  group('WorkoutProvider Tests', () {
    late WorkoutProvider provider;

    setUp(() {
      provider = WorkoutProvider();
    });

    test('initial state is empty', () {
      expect(provider.workouts, isEmpty);
      expect(provider.isLoading, isFalse);
      expect(provider.completedTodayCount, 0);
    });

    test('weekWorkouts returns only current week workouts', () async {
      final today = DateTime.now();
      await provider.loadWorkoutsForDate(today);
      
      final week = provider.weekWorkouts;
      // All week workouts should be within the current week
      for (final w in week) {
        final startOfWeek = today.subtract(Duration(days: today.weekday - 1));
        final endOfWeek = startOfWeek.add(const Duration(days: 7));
        expect(w.date.isAfter(startOfWeek.subtract(const Duration(days: 1))), isTrue);
        expect(w.date.isBefore(endOfWeek), isTrue);
      }
    });

    test('loadWorkoutsForDate generates workouts for Monday', () async {
      final monday = DateTime(2025, 1, 6); // Monday
      await provider.loadWorkoutsForDate(monday);
      
      final mondayWorkouts = provider.workouts.where((w) =>
          w.date.year == monday.year &&
          w.date.month == monday.month &&
          w.date.day == monday.day).toList();
      
      expect(mondayWorkouts, isNotEmpty);
    });

    test('completedTodayCount increments when workout is completed', () async {
      final today = DateTime.now();
      await provider.loadWorkoutsForDate(today);
      
      final todayWorkouts = provider.todayWorkouts;
      if (todayWorkouts.isNotEmpty) {
        final initialCount = provider.completedTodayCount;
        await provider.completeWorkout(todayWorkouts.first.id);
        expect(provider.completedTodayCount, initialCount + 1);
      }
    });

    test('setSelectedDate updates selectedDate', () {
      final newDate = DateTime(2025, 6, 15);
      provider.setSelectedDate(newDate);
      expect(provider.selectedDate, newDate);
    });
  });
}
