import 'package:equatable/equatable.dart';

enum MessageRole { user, assistant, system }
enum MessageStatus { sending, sent, error }

class ChatMessage extends Equatable {
  final String id;
  final String content;
  final MessageRole role;
  final MessageStatus status;
  final DateTime timestamp;
  final String? imageUrl;
  final Map<String, dynamic>? metadata;

  const ChatMessage({
    required this.id,
    required this.content,
    required this.role,
    this.status = MessageStatus.sent,
    required this.timestamp,
    this.imageUrl,
    this.metadata,
  });

  bool get isUser => role == MessageRole.user;
  bool get isAssistant => role == MessageRole.assistant;
  bool get isSending => status == MessageStatus.sending;
  bool get hasError => status == MessageStatus.error;

  ChatMessage copyWith({
    String? id,
    String? content,
    MessageRole? role,
    MessageStatus? status,
    DateTime? timestamp,
    String? imageUrl,
    Map<String, dynamic>? metadata,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      content: content ?? this.content,
      role: role ?? this.role,
      status: status ?? this.status,
      timestamp: timestamp ?? this.timestamp,
      imageUrl: imageUrl ?? this.imageUrl,
      metadata: metadata ?? this.metadata,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'content': content,
        'role': role.name,
        'status': status.name,
        'timestamp': timestamp.toIso8601String(),
        'imageUrl': imageUrl,
        'metadata': metadata,
      };

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        id: json['id'] as String,
        content: json['content'] as String,
        role: MessageRole.values.byName(json['role'] as String),
        status: MessageStatus.values.byName(json['status'] as String? ?? 'sent'),
        timestamp: DateTime.parse(json['timestamp'] as String),
        imageUrl: json['imageUrl'] as String?,
        metadata: json['metadata'] as Map<String, dynamic>?,
      );

  // Formato para API OpenAI
  Map<String, String> toApiFormat() => {
        'role': role.name,
        'content': content,
      };

  @override
  List<Object?> get props => [id, content, role, timestamp];
}

class ChatSession extends Equatable {
  final String id;
  final String userId;
  final List<ChatMessage> messages;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String? title;

  const ChatSession({
    required this.id,
    required this.userId,
    this.messages = const [],
    required this.createdAt,
    this.updatedAt,
    this.title,
  });

  ChatSession copyWith({
    String? id,
    String? userId,
    List<ChatMessage>? messages,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? title,
  }) {
    return ChatSession(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      messages: messages ?? this.messages,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      title: title ?? this.title,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'userId': userId,
        'messages': messages.map((m) => m.toJson()).toList(),
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt?.toIso8601String(),
        'title': title,
      };

  factory ChatSession.fromJson(Map<String, dynamic> json) => ChatSession(
        id: json['id'] as String,
        userId: json['userId'] as String,
        messages: (json['messages'] as List<dynamic>?)
                ?.map((m) => ChatMessage.fromJson(m as Map<String, dynamic>))
                .toList() ??
            [],
        createdAt: DateTime.parse(json['createdAt'] as String),
        updatedAt: json['updatedAt'] != null
            ? DateTime.parse(json['updatedAt'] as String)
            : null,
        title: json['title'] as String?,
      );

  @override
  List<Object?> get props => [id, userId];
}
