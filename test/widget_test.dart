import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/main.dart';

void main() {
  testWidgets('Barifit+ app smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const BarifitApp());
    expect(find.byType(BarifitApp), findsOneWidget);
  });
}
