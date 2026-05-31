import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../../data/models/workout_model.dart';

class WorkoutProvider extends ChangeNotifier {
  final List<WorkoutModel> _workouts = [];
  bool _isLoading = false;
  String? _error;
  DateTime _selectedDate = DateTime.now();

  List<WorkoutModel> get workouts => _workouts;
  bool get isLoading => _isLoading;
  String? get error => _error;
  DateTime get selectedDate => _selectedDate;

  List<WorkoutModel> get todayWorkouts {
    final today = DateTime.now();
    return _workouts.where((w) =>
        w.date.year == today.year &&
        w.date.month == today.month &&
        w.date.day == today.day).toList();
  }

  List<WorkoutModel> get selectedDateWorkouts {
    return _workouts.where((w) =>
        w.date.year == _selectedDate.year &&
        w.date.month == _selectedDate.month &&
        w.date.day == _selectedDate.day).toList();
  }

  int get completedTodayCount =>
      todayWorkouts.where((w) => w.isCompleted).length;

  void setSelectedDate(DateTime date) {
    _selectedDate = date;
    notifyListeners();
  }

  Future<void> loadWorkoutsForDate(DateTime date) async {
    _isLoading = true;
    notifyListeners();

    try {
      await Future.delayed(const Duration(milliseconds: 500));
      final dayWorkouts = _generateWorkoutsForDay(date);

      // Remove workouts for that date and re-add
      _workouts.removeWhere((w) =>
          w.date.year == date.year &&
          w.date.month == date.month &&
          w.date.day == date.day);
      _workouts.addAll(dayWorkouts);
    } catch (e) {
      _error = 'Erro ao carregar treinos.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  List<WorkoutModel> _generateWorkoutsForDay(DateTime date) {
    const uuid = Uuid();
    final dayOfWeek = date.weekday; // 1=Mon ... 7=Sun
    final List<WorkoutModel> workouts = [];

    switch (dayOfWeek) {
      case 1: // Segunda
        workouts.addAll([
          WorkoutModel(
            id: uuid.v4(),
            title: 'Musculação: Peito + Tríceps',
            type: WorkoutType.musculacao,
            time: WorkoutTime.manha,
            scheduledTime: '07:00',
            date: date,
            durationMinutes: 60,
            exercises: _chestTricepsExercises(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Musculação: Ombros + Abdômen',
            type: WorkoutType.musculacao,
            time: WorkoutTime.meiodia,
            scheduledTime: '12:00',
            date: date,
            durationMinutes: 45,
            exercises: _shoulderAbsExercises(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Calistenia Diária',
            type: WorkoutType.calistenia,
            time: WorkoutTime.tarde,
            scheduledTime: '17:00',
            date: date,
            durationMinutes: 20,
            exercises: _calisthenicsExercises(uuid, dayOfWeek),
          ),
        ]);
        break;
      case 2: // Terça
        workouts.addAll([
          WorkoutModel(
            id: uuid.v4(),
            title: 'Natação: Técnica + Resistência',
            type: WorkoutType.natacao,
            time: WorkoutTime.manha,
            scheduledTime: '07:00',
            date: date,
            durationMinutes: 60,
            exercises: _swimmingExercises(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Calistenia Diária',
            type: WorkoutType.calistenia,
            time: WorkoutTime.tarde,
            scheduledTime: '17:00',
            date: date,
            durationMinutes: 20,
            exercises: _calisthenicsExercises(uuid, dayOfWeek),
          ),
        ]);
        break;
      case 3: // Quarta
        workouts.addAll([
          WorkoutModel(
            id: uuid.v4(),
            title: 'Corrida: Intervalado',
            type: WorkoutType.corrida,
            time: WorkoutTime.manha,
            scheduledTime: '07:00',
            date: date,
            durationMinutes: 45,
            exercises: _runningIntervals(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Musculação: Costas + Bíceps',
            type: WorkoutType.musculacao,
            time: WorkoutTime.meiodia,
            scheduledTime: '12:00',
            date: date,
            durationMinutes: 60,
            exercises: _backBicepsExercises(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Musculação: Pernas — Posterior',
            type: WorkoutType.musculacao,
            time: WorkoutTime.noite,
            scheduledTime: '18:00',
            date: date,
            durationMinutes: 50,
            exercises: _legsPosteriorExercises(uuid),
          ),
        ]);
        break;
      case 4: // Quinta
        workouts.addAll([
          WorkoutModel(
            id: uuid.v4(),
            title: 'Natação: Velocidade + Força',
            type: WorkoutType.natacao,
            time: WorkoutTime.manha,
            scheduledTime: '07:00',
            date: date,
            durationMinutes: 60,
            exercises: _swimmingExercises(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Calistenia Diária',
            type: WorkoutType.calistenia,
            time: WorkoutTime.tarde,
            scheduledTime: '17:00',
            date: date,
            durationMinutes: 20,
            exercises: _calisthenicsExercises(uuid, dayOfWeek),
          ),
        ]);
        break;
      case 5: // Sexta
        workouts.addAll([
          WorkoutModel(
            id: uuid.v4(),
            title: 'Musculação: Pernas — Anterior',
            type: WorkoutType.musculacao,
            time: WorkoutTime.manha,
            scheduledTime: '07:00',
            date: date,
            durationMinutes: 60,
            exercises: _legsAnteriorExercises(uuid),
          ),
          WorkoutModel(
            id: uuid.v4(),
            title: 'Musculação: Abdômen + Core',
            type: WorkoutType.musculacao,
            time: WorkoutTime.meiodia,
            scheduledTime: '12:00',
            date: date,
            durationMinutes: 30,
            exercises: _coreExercises(uuid),
          ),
        ]);
        break;
      case 6: // Sábado
        workouts.add(WorkoutModel(
          id: uuid.v4(),
          title: 'Corrida Longa (60 min)',
          type: WorkoutType.corrida,
          time: WorkoutTime.manha,
          scheduledTime: '07:00',
          date: date,
          durationMinutes: 60,
          exercises: _longRunExercises(uuid),
        ));
        break;
      case 7: // Domingo
        workouts.add(WorkoutModel(
          id: uuid.v4(),
          title: 'Descanso Ativo',
          type: WorkoutType.descanso,
          time: WorkoutTime.manha,
          scheduledTime: '09:00',
          date: date,
          durationMinutes: 30,
          exercises: [],
        ));
        break;
    }

    // Sempre adicionar alongamento
    workouts.add(WorkoutModel(
      id: uuid.v4(),
      title: 'Alongamento + Funcional',
      type: WorkoutType.alongamento,
      time: WorkoutTime.noite,
      scheduledTime: '20:00',
      date: date,
      durationMinutes: 15,
      exercises: _stretchingExercises(uuid),
    ));

    return workouts;
  }

  Future<void> completeExercise(String workoutId, String exerciseId) async {
    final workoutIndex = _workouts.indexWhere((w) => w.id == workoutId);
    if (workoutIndex == -1) return;

    final workout = _workouts[workoutIndex];
    final exercises = workout.exercises.map((e) {
      if (e.id == exerciseId) {
        return e.copyWith(isCompleted: !e.isCompleted);
      }
      return e;
    }).toList();

    final allCompleted = exercises.every((e) => e.isCompleted);
    _workouts[workoutIndex] = workout.copyWith(
      exercises: exercises,
      status: allCompleted ? WorkoutStatus.completed : WorkoutStatus.inProgress,
    );
    notifyListeners();
  }

  Future<void> completeWorkout(String workoutId) async {
    final index = _workouts.indexWhere((w) => w.id == workoutId);
    if (index == -1) return;
    _workouts[index] = _workouts[index].copyWith(
      status: WorkoutStatus.completed,
    );
    notifyListeners();
  }

  // ─── Exercise Generators ───────────────────────────────────────────────────

  List<ExerciseModel> _chestTricepsExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Supino Reto', sets: '4x10-12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Supino Inclinado', sets: '3x10-12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Crucifixo', sets: '3x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Tríceps Pulley', sets: '4x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Tríceps Francês', sets: '3x10-12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Mergulho (Dips)', sets: '3x10-15', rest: '90s'),
      ];

  List<ExerciseModel> _shoulderAbsExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Desenvolvimento com Halteres', sets: '4x10-12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Elevação Lateral', sets: '3x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Elevação Frontal', sets: '3x12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Remada Alta', sets: '3x12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Prancha Frontal', sets: '3x60s', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Abdominal Crunch', sets: '4x20', rest: '45s'),
      ];

  List<ExerciseModel> _backBicepsExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Puxada Frontal', sets: '4x10-12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Remada Curvada', sets: '4x10-12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Remada Unilateral', sets: '3x12 cada', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Rosca Direta', sets: '4x10-12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Rosca Martelo', sets: '3x12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Rosca Concentrada', sets: '3x12 cada', rest: '60s'),
      ];

  List<ExerciseModel> _legsPosteriorExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Leg Press', sets: '4x12-15', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Cadeira Flexora', sets: '4x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Stiff', sets: '3x12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Glúteo no Cabo', sets: '3x15 cada', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Panturrilha em Pé', sets: '4x20-25', rest: '45s'),
      ];

  List<ExerciseModel> _legsAnteriorExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Agachamento Livre', sets: '4x10-12', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Cadeira Extensora', sets: '4x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Avanço com Halteres', sets: '3x12 cada', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Agachamento Búlgaro', sets: '3x10 cada', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Leg Press 45°', sets: '3x15', rest: '90s'),
      ];

  List<ExerciseModel> _coreExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Prancha Frontal', sets: '3x60s', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Prancha Lateral', sets: '3x45s cada', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Abdominal Infra', sets: '4x20', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Russian Twist', sets: '3x20', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Mountain Climbers', sets: '3x30s', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Hollow Body Hold', sets: '3x30s', rest: '45s'),
      ];

  List<ExerciseModel> _swimmingExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Aquecimento (crawl leve)', sets: '200m', rest: '1min'),
        ExerciseModel(id: uuid.v4(), name: 'Séries de Crawl', sets: '8x50m', rest: '30s'),
        ExerciseModel(id: uuid.v4(), name: 'Peito (braquiação)', sets: '4x100m', rest: '1min'),
        ExerciseModel(id: uuid.v4(), name: 'Pernada com prancha', sets: '4x50m', rest: '30s'),
        ExerciseModel(id: uuid.v4(), name: 'Volta calma', sets: '100m', rest: '-'),
      ];

  List<ExerciseModel> _runningIntervals(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Aquecimento (caminhada)', sets: '5min', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Corrida moderada', sets: '5min', rest: '2min'),
        ExerciseModel(id: uuid.v4(), name: 'Sprint (80%)', sets: '8x30s', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Corrida contínua', sets: '15min', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Desaceleração', sets: '5min', rest: '-'),
      ];

  List<ExerciseModel> _longRunExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Aquecimento', sets: '5min caminhada', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Corrida longa (Z2)', sets: '50min', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Desaceleração', sets: '5min', rest: '-'),
      ];

  List<ExerciseModel> _calisthenicsExercises(Uuid uuid, int dayOfWeek) {
    final Map<int, List<ExerciseModel>> exercises = {
      1: [
        ExerciseModel(id: uuid.v4(), name: 'Flexões Diamante', sets: '4x10-12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Dips (banco)', sets: '4x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Pike Push-ups', sets: '3x10-12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Prancha Lateral', sets: '3x45s cada', rest: '45s'),
      ],
      2: [
        ExerciseModel(id: uuid.v4(), name: 'Burpees', sets: '4x10-12', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Jump Squats', sets: '3x15-20', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'High Knees', sets: '3x30s', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Prancha com toque no ombro', sets: '3x20', rest: '45s'),
      ],
      3: [
        ExerciseModel(id: uuid.v4(), name: 'Pull-ups / Australian Pull-ups', sets: '4x8-10', rest: '90s'),
        ExerciseModel(id: uuid.v4(), name: 'Inverted Rows', sets: '3x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Hollow Body Hold', sets: '3x30-45s', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Leg Raises', sets: '3x15-20', rest: '45s'),
      ],
      4: [
        ExerciseModel(id: uuid.v4(), name: 'Pistol Squats (assistido)', sets: '3x8-10 cada', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Bulgarian Split Squats', sets: '3x12 cada', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Calf Raises', sets: '4x20-25', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Wall Sit', sets: '3x45-60s', rest: '60s'),
      ],
      5: [
        ExerciseModel(id: uuid.v4(), name: 'Archer Push-ups', sets: '3x8-10 cada', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Decline Push-ups', sets: '3x12-15', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Handstand Hold (parede)', sets: '3x20-30s', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'L-Sit (progressão)', sets: '3x15-20s', rest: '45s'),
      ],
      6: [
        ExerciseModel(id: uuid.v4(), name: 'Circuito: Flexões', sets: '3 rounds x 15', rest: '90s entre rounds'),
        ExerciseModel(id: uuid.v4(), name: 'Circuito: Agachamentos', sets: '3 rounds x 20', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Circuito: Pull-ups', sets: '3 rounds x 8', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Circuito: Burpees', sets: '3 rounds x 10', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Circuito: Prancha', sets: '3 rounds x 45s', rest: '-'),
      ],
      7: [
        ExerciseModel(id: uuid.v4(), name: 'Flexões', sets: '3x15-20', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Agachamento Livre', sets: '3x20-25', rest: '60s'),
        ExerciseModel(id: uuid.v4(), name: 'Prancha', sets: '3x60s', rest: '45s'),
        ExerciseModel(id: uuid.v4(), name: 'Mountain Climbers', sets: '3x20', rest: '45s'),
      ],
    };
    return exercises[dayOfWeek] ?? exercises[7]!;
  }

  List<ExerciseModel> _stretchingExercises(Uuid uuid) => [
        ExerciseModel(id: uuid.v4(), name: 'Peitorais (braço na parede)', sets: '30s cada', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Ombros (braço cruzado)', sets: '30s cada', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Quadríceps (puxar pé ao glúteo)', sets: '30s cada', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Posteriores (perna estendida)', sets: '30s cada', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Glúteos (figura 4)', sets: '30s cada', rest: '-'),
        ExerciseModel(id: uuid.v4(), name: 'Bird Dog', sets: '10 reps cada lado', rest: '30s'),
        ExerciseModel(id: uuid.v4(), name: 'Ponte de Glúteo', sets: '15 reps', rest: '30s'),
        ExerciseModel(id: uuid.v4(), name: 'Cat-Cow', sets: '10 reps', rest: '-'),
      ];
}
