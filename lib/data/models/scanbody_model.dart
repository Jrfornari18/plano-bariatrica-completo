import 'package:equatable/equatable.dart';

class BodyMeasurements extends Equatable {
  final double? waist;
  final double? hip;
  final double? chest;
  final double? leftArm;
  final double? rightArm;
  final double? leftThigh;
  final double? rightThigh;
  final double? neck;
  final double? abdomen;

  const BodyMeasurements({
    this.waist,
    this.hip,
    this.chest,
    this.leftArm,
    this.rightArm,
    this.leftThigh,
    this.rightThigh,
    this.neck,
    this.abdomen,
  });

  double? get waistHipRatio {
    if (waist == null || hip == null || hip == 0) return null;
    return waist! / hip!;
  }

  Map<String, dynamic> toJson() => {
        'waist': waist,
        'hip': hip,
        'chest': chest,
        'leftArm': leftArm,
        'rightArm': rightArm,
        'leftThigh': leftThigh,
        'rightThigh': rightThigh,
        'neck': neck,
        'abdomen': abdomen,
      };

  factory BodyMeasurements.fromJson(Map<String, dynamic> json) =>
      BodyMeasurements(
        waist: (json['waist'] as num?)?.toDouble(),
        hip: (json['hip'] as num?)?.toDouble(),
        chest: (json['chest'] as num?)?.toDouble(),
        leftArm: (json['leftArm'] as num?)?.toDouble(),
        rightArm: (json['rightArm'] as num?)?.toDouble(),
        leftThigh: (json['leftThigh'] as num?)?.toDouble(),
        rightThigh: (json['rightThigh'] as num?)?.toDouble(),
        neck: (json['neck'] as num?)?.toDouble(),
        abdomen: (json['abdomen'] as num?)?.toDouble(),
      );

  @override
  List<Object?> get props =>
      [waist, hip, chest, leftArm, rightArm, leftThigh, rightThigh];
}

class BodyCompositionModel extends Equatable {
  final double? bodyFatPercentage;
  final double? muscleMassKg;
  final double? fatMassKg;
  final double? bmi;
  final double? visceralFat;
  final double? metabolicAge;
  final String? analysisNotes;

  const BodyCompositionModel({
    this.bodyFatPercentage,
    this.muscleMassKg,
    this.fatMassKg,
    this.bmi,
    this.visceralFat,
    this.metabolicAge,
    this.analysisNotes,
  });

  Map<String, dynamic> toJson() => {
        'bodyFatPercentage': bodyFatPercentage,
        'muscleMassKg': muscleMassKg,
        'fatMassKg': fatMassKg,
        'bmi': bmi,
        'visceralFat': visceralFat,
        'metabolicAge': metabolicAge,
        'analysisNotes': analysisNotes,
      };

  factory BodyCompositionModel.fromJson(Map<String, dynamic> json) =>
      BodyCompositionModel(
        bodyFatPercentage: (json['bodyFatPercentage'] as num?)?.toDouble(),
        muscleMassKg: (json['muscleMassKg'] as num?)?.toDouble(),
        fatMassKg: (json['fatMassKg'] as num?)?.toDouble(),
        bmi: (json['bmi'] as num?)?.toDouble(),
        visceralFat: (json['visceralFat'] as num?)?.toDouble(),
        metabolicAge: (json['metabolicAge'] as num?)?.toDouble(),
        analysisNotes: json['analysisNotes'] as String?,
      );

  @override
  List<Object?> get props => [bodyFatPercentage, muscleMassKg, bmi];
}

class ScanbodyRecord extends Equatable {
  final String id;
  final String userId;
  final DateTime date;
  final double weight;
  final BodyMeasurements? measurements;
  final BodyCompositionModel? composition;
  final String? frontPhotoPath;
  final String? sidePhotoPath;
  final String? backPhotoPath;
  final String? frontPhotoUrl;
  final String? sidePhotoUrl;
  final String? backPhotoUrl;
  final String? aiAnalysis;
  final String? notes;
  final bool isSynced;

  const ScanbodyRecord({
    required this.id,
    required this.userId,
    required this.date,
    required this.weight,
    this.measurements,
    this.composition,
    this.frontPhotoPath,
    this.sidePhotoPath,
    this.backPhotoPath,
    this.frontPhotoUrl,
    this.sidePhotoUrl,
    this.backPhotoUrl,
    this.aiAnalysis,
    this.notes,
    this.isSynced = false,
  });

  bool get hasPhotos =>
      frontPhotoPath != null || sidePhotoPath != null || backPhotoPath != null;

  ScanbodyRecord copyWith({
    String? id,
    String? userId,
    DateTime? date,
    double? weight,
    BodyMeasurements? measurements,
    BodyCompositionModel? composition,
    String? frontPhotoPath,
    String? sidePhotoPath,
    String? backPhotoPath,
    String? frontPhotoUrl,
    String? sidePhotoUrl,
    String? backPhotoUrl,
    String? aiAnalysis,
    String? notes,
    bool? isSynced,
  }) {
    return ScanbodyRecord(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      date: date ?? this.date,
      weight: weight ?? this.weight,
      measurements: measurements ?? this.measurements,
      composition: composition ?? this.composition,
      frontPhotoPath: frontPhotoPath ?? this.frontPhotoPath,
      sidePhotoPath: sidePhotoPath ?? this.sidePhotoPath,
      backPhotoPath: backPhotoPath ?? this.backPhotoPath,
      frontPhotoUrl: frontPhotoUrl ?? this.frontPhotoUrl,
      sidePhotoUrl: sidePhotoUrl ?? this.sidePhotoUrl,
      backPhotoUrl: backPhotoUrl ?? this.backPhotoUrl,
      aiAnalysis: aiAnalysis ?? this.aiAnalysis,
      notes: notes ?? this.notes,
      isSynced: isSynced ?? this.isSynced,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'userId': userId,
        'date': date.toIso8601String(),
        'weight': weight,
        'measurements': measurements?.toJson(),
        'composition': composition?.toJson(),
        'frontPhotoPath': frontPhotoPath,
        'sidePhotoPath': sidePhotoPath,
        'backPhotoPath': backPhotoPath,
        'frontPhotoUrl': frontPhotoUrl,
        'sidePhotoUrl': sidePhotoUrl,
        'backPhotoUrl': backPhotoUrl,
        'aiAnalysis': aiAnalysis,
        'notes': notes,
        'isSynced': isSynced,
      };

  factory ScanbodyRecord.fromJson(Map<String, dynamic> json) => ScanbodyRecord(
        id: json['id'] as String,
        userId: json['userId'] as String,
        date: DateTime.parse(json['date'] as String),
        weight: (json['weight'] as num).toDouble(),
        measurements: json['measurements'] != null
            ? BodyMeasurements.fromJson(
                json['measurements'] as Map<String, dynamic>)
            : null,
        composition: json['composition'] != null
            ? BodyCompositionModel.fromJson(
                json['composition'] as Map<String, dynamic>)
            : null,
        frontPhotoPath: json['frontPhotoPath'] as String?,
        sidePhotoPath: json['sidePhotoPath'] as String?,
        backPhotoPath: json['backPhotoPath'] as String?,
        frontPhotoUrl: json['frontPhotoUrl'] as String?,
        sidePhotoUrl: json['sidePhotoUrl'] as String?,
        backPhotoUrl: json['backPhotoUrl'] as String?,
        aiAnalysis: json['aiAnalysis'] as String?,
        notes: json['notes'] as String?,
        isSynced: json['isSynced'] as bool? ?? false,
      );

  @override
  List<Object?> get props => [id, userId, date];
}
