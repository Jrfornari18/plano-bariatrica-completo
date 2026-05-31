import 'package:equatable/equatable.dart';

enum WorkoutType { musculacao, natacao, corrida, calistenia, alongamento, funcional, descanso }
enum WorkoutTime { manha, meiodia, tarde, noite }
enum WorkoutStatus { pending, inProgress, completed, skipped }

class ExerciseModel extends Equatable {
  final String id;
  final String name;
  final String sets;
  final String? reps;
  final String? rest;
  final String? weight;
  final String? duration;
  final String? notes;
  final bool isCompleted;

  const ExerciseModel({
    required this.id,
    required this.name,
    required this.sets,
    this.reps,
    this.rest,
    this.weight,
    this.duration,
    this.notes,
    this.isCompleted = false,
  });

  ExerciseModel copyWith({
    String? id,
    String? name,
    String? sets,
    String? reps,
    String? rest,
    String? weight,
    String? duration,
    String? notes,
    bool? isCompleted,
  }) {
    return ExerciseModel(
      id: id ?? this.id,
      name: name ?? this.name,
      sets: sets ?? this.sets,
      reps: reps ?? this.reps,
      rest: rest ?? this.rest,
      weight: weight ?? this.weight,
      duration: duration ?? this.duration,
      notes: notes ?? this.notes,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'sets': sets,
        'reps': reps,
        'rest': rest,
        'weight': weight,
        'duration': duration,
        'notes': notes,
        'isCompleted': isCompleted,
      };

  factory ExerciseModel.fromJson(Map<String, dynamic> json) => ExerciseModel(
        id: json['id'] as String,
        name: json['name'] as String,
        sets: json['sets'] as String,
        reps: json['reps'] as String?,
        rest: json['rest'] as String?,
        weight: json['weight'] as String?,
        duration: json['duration'] as String?,
        notes: json['notes'] as String?,
        isCompleted: json['isCompleted'] as bool? ?? false,
      );

  @override
  List<Object?> get props => [id, name];
}

class WorkoutModel extends Equatable {
  final String id;
  final String title;
  final WorkoutType type;
  final WorkoutTime time;
  final WorkoutStatus status;
  final DateTime date;
  final String? scheduledTime;
  final int? durationMinutes;
  final List<ExerciseModel> exercises;
  final String? notes;
  final int? caloriesBurned;
  final bool isSynced;

  const WorkoutModel({
    required this.id,
    required this.title,
    required this.type,
    required this.time,
    this.status = WorkoutStatus.pending,
    required this.date,
    this.scheduledTime,
    this.durationMinutes,
    this.exercises = const [],
    this.notes,
    this.caloriesBurned,
    this.isSynced = false,
  });

  bool get isCompleted => status == WorkoutStatus.completed;
  bool get hasExercises => exercises.isNotEmpty;
  int get completedExercises => exercises.where((e) => e.isCompleted).length;
  double get completionRate =>
      exercises.isEmpty ? 0 : completedExercises / exercises.length;

  String get typeLabel {
    switch (type) {
      case WorkoutType.musculacao:
        return 'Musculação';
      case WorkoutType.natacao:
        return 'Natação';
      case WorkoutType.corrida:
        return 'Corrida';
      case WorkoutType.calistenia:
        return 'Calistenia';
      case WorkoutType.alongamento:
        return 'Alongamento';
      case WorkoutType.funcional:
        return 'Funcional';
      case WorkoutType.descanso:
        return 'Descanso';
    }
  }

  WorkoutModel copyWith({
    String? id,
    String? title,
    WorkoutType? type,
    WorkoutTime? time,
    WorkoutStatus? status,
    DateTime? date,
    String? scheduledTime,
    int? durationMinutes,
    List<ExerciseModel>? exercises,
    String? notes,
    int? caloriesBurned,
    bool? isSynced,
  }) {
    return WorkoutModel(
      id: id ?? this.id,
      title: title ?? this.title,
      type: type ?? this.type,
      time: time ?? this.time,
      status: status ?? this.status,
      date: date ?? this.date,
      scheduledTime: scheduledTime ?? this.scheduledTime,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      exercises: exercises ?? this.exercises,
      notes: notes ?? this.notes,
      caloriesBurned: caloriesBurned ?? this.caloriesBurned,
      isSynced: isSynced ?? this.isSynced,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'type': type.name,
        'time': time.name,
        'status': status.name,
        'date': date.toIso8601String(),
        'scheduledTime': scheduledTime,
        'durationMinutes': durationMinutes,
        'exercises': exercises.map((e) => e.toJson()).toList(),
        'notes': notes,
        'caloriesBurned': caloriesBurned,
        'isSynced': isSynced,
      };

  factory WorkoutModel.fromJson(Map<String, dynamic> json) => WorkoutModel(
        id: json['id'] as String,
        title: json['title'] as String,
        type: WorkoutType.values.byName(json['type'] as String),
        time: WorkoutTime.values.byName(json['time'] as String),
        status: WorkoutStatus.values.byName(json['status'] as String? ?? 'pending'),
        date: DateTime.parse(json['date'] as String),
        scheduledTime: json['scheduledTime'] as String?,
        durationMinutes: json['durationMinutes'] as int?,
        exercises: (json['exercises'] as List<dynamic>?)
                ?.map((e) => ExerciseModel.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        notes: json['notes'] as String?,
        caloriesBurned: json['caloriesBurned'] as int?,
        isSynced: json['isSynced'] as bool? ?? false,
      );

  @override
  List<Object?> get props => [id, date, type];
}
