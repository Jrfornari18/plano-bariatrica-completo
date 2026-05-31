import 'package:equatable/equatable.dart';

class UserModel extends Equatable {
  final String id;
  final String name;
  final String email;
  final String? photoUrl;
  final DateTime? birthDate;
  final double? weight;
  final double? height;
  final DateTime? surgeryDate;
  final String? surgeryType;
  final DateTime programStartDate;
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  const UserModel({
    required this.id,
    required this.name,
    required this.email,
    this.photoUrl,
    this.birthDate,
    this.weight,
    this.height,
    this.surgeryDate,
    this.surgeryType,
    required this.programStartDate,
    this.isActive = true,
    required this.createdAt,
    this.updatedAt,
  });

  int get programDayNumber {
    final now = DateTime.now();
    final diff = now.difference(programStartDate).inDays;
    return diff + 1;
  }

  int get programWeek => ((programDayNumber - 1) ~/ 7) + 1;

  int get programPhase {
    if (programWeek <= 4) return 1;
    if (programWeek <= 8) return 2;
    return 3;
  }

  double get bmi {
    if (weight == null || height == null || height == 0) return 0;
    final heightM = height! / 100;
    return weight! / (heightM * heightM);
  }

  UserModel copyWith({
    String? id,
    String? name,
    String? email,
    String? photoUrl,
    DateTime? birthDate,
    double? weight,
    double? height,
    DateTime? surgeryDate,
    String? surgeryType,
    DateTime? programStartDate,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      photoUrl: photoUrl ?? this.photoUrl,
      birthDate: birthDate ?? this.birthDate,
      weight: weight ?? this.weight,
      height: height ?? this.height,
      surgeryDate: surgeryDate ?? this.surgeryDate,
      surgeryType: surgeryType ?? this.surgeryType,
      programStartDate: programStartDate ?? this.programStartDate,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'email': email,
        'photoUrl': photoUrl,
        'birthDate': birthDate?.toIso8601String(),
        'weight': weight,
        'height': height,
        'surgeryDate': surgeryDate?.toIso8601String(),
        'surgeryType': surgeryType,
        'programStartDate': programStartDate.toIso8601String(),
        'isActive': isActive,
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt?.toIso8601String(),
      };

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id: json['id'] as String,
        name: json['name'] as String,
        email: json['email'] as String,
        photoUrl: json['photoUrl'] as String?,
        birthDate: json['birthDate'] != null
            ? DateTime.parse(json['birthDate'] as String)
            : null,
        weight: (json['weight'] as num?)?.toDouble(),
        height: (json['height'] as num?)?.toDouble(),
        surgeryDate: json['surgeryDate'] != null
            ? DateTime.parse(json['surgeryDate'] as String)
            : null,
        surgeryType: json['surgeryType'] as String?,
        programStartDate:
            DateTime.parse(json['programStartDate'] as String),
        isActive: json['isActive'] as bool? ?? true,
        createdAt: DateTime.parse(json['createdAt'] as String),
        updatedAt: json['updatedAt'] != null
            ? DateTime.parse(json['updatedAt'] as String)
            : null,
      );

  @override
  List<Object?> get props => [id, email];
}
