import 'package:flutter_test/flutter_test.dart';
import 'package:barifit_app/data/models/chat_model.dart';

void main() {
  group('ChatModel Tests', () {
    test('ChatMessage creates correctly for user role', () {
      final message = ChatMessage(
        id: '1',
        role: MessageRole.user,
        content: 'Olá Babi!',
        timestamp: DateTime.now(),
      );
      
      expect(message.role, MessageRole.user);
      expect(message.content, 'Olá Babi!');
      expect(message.isUser, isTrue);
      expect(message.isAssistant, isFalse);
    });

    test('ChatMessage creates correctly for assistant role', () {
      final message = ChatMessage(
        id: '2',
        role: MessageRole.assistant,
        content: 'Olá! Como posso ajudar?',
        timestamp: DateTime.now(),
      );
      
      expect(message.isAssistant, isTrue);
      expect(message.isUser, isFalse);
    });

    test('toJson and fromJson roundtrip', () {
      final original = ChatMessage(
        id: '1',
        role: MessageRole.user,
        content: 'Quantas proteínas devo comer?',
        timestamp: DateTime(2025, 1, 1, 12, 0),
      );
      
      final json = original.toJson();
      final restored = ChatMessage.fromJson(json);
      
      expect(restored.id, original.id);
      expect(restored.role, original.role);
      expect(restored.content, original.content);
    });
  });
}
