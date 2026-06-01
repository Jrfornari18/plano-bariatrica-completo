import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/data/models/scanbody_model.dart';

void main() {
  group('ScanbodyRecord Tests', () {
    test('creates correctly with required fields', () {
      final record = ScanbodyRecord(
        id: '1',
        userId: 'user1',
        date: DateTime.now(),
        weight: 80.0,
      );

      expect(record.id, '1');
      expect(record.weight, 80.0);
      expect(record.measurements, isNull);
    });

    test('BodyMeasurements stores values correctly', () {
      const measurements = BodyMeasurements(
        waist: 80.0,
        hip: 100.0,
        chest: 95.0,
      );

      expect(measurements.waist, 80.0);
      expect(measurements.hip, 100.0);
    });

    test('toJson and fromJson roundtrip', () {
      final original = ScanbodyRecord(
        id: '1',
        userId: 'user1',
        date: DateTime(2025, 1, 1),
        weight: 75.5,
        measurements: const BodyMeasurements(waist: 80.0, hip: 100.0),
      );

      final json = original.toJson();
      final restored = ScanbodyRecord.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.weight, original.weight);
      expect(restored.measurements?.waist, original.measurements?.waist);
    });

    test('isSynced defaults to false', () {
      final record = ScanbodyRecord(
        id: '1',
        userId: 'user1',
        date: DateTime.now(),
        weight: 70.0,
      );

      expect(record.isSynced, isFalse);
    });
  });
}
