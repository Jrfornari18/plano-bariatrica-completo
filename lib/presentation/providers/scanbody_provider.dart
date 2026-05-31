import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';
import '../../data/models/scanbody_model.dart';

enum ScanStep { front, side, back, measurements, complete }

class ScanbodyProvider extends ChangeNotifier {
  final List<ScanbodyRecord> _records = [];
  bool _isLoading = false;
  bool _isAnalyzing = false;
  String? _error;
  ScanStep _currentStep = ScanStep.front;

  // Current scan session
  String? _frontPhotoPath;
  String? _sidePhotoPath;
  String? _backPhotoPath;
  double _currentWeight = 0;
  BodyMeasurements? _currentMeasurements;

  List<ScanbodyRecord> get records => _records;
  bool get isLoading => _isLoading;
  bool get isAnalyzing => _isAnalyzing;
  String? get error => _error;
  ScanStep get currentStep => _currentStep;
  String? get frontPhotoPath => _frontPhotoPath;
  String? get sidePhotoPath => _sidePhotoPath;
  String? get backPhotoPath => _backPhotoPath;
  double get currentWeight => _currentWeight;
  BodyMeasurements? get currentMeasurements => _currentMeasurements;

  ScanbodyRecord? get latestRecord =>
      _records.isEmpty ? null : _records.last;

  ScanbodyRecord? get previousRecord =>
      _records.length < 2 ? null : _records[_records.length - 2];

  double? get weightChange {
    if (latestRecord == null || previousRecord == null) return null;
    return latestRecord!.weight - previousRecord!.weight;
  }

  Future<void> loadRecords(String userId) async {
    _isLoading = true;
    notifyListeners();

    try {
      await Future.delayed(const Duration(milliseconds: 500));
      // Load from local storage / API
      // For demo, generate some sample records
      if (_records.isEmpty) {
        _generateDemoRecords(userId);
      }
    } catch (e) {
      _error = 'Erro ao carregar registros.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _generateDemoRecords(String userId) {
    const uuid = Uuid();
    final now = DateTime.now();

    _records.addAll([
      ScanbodyRecord(
        id: uuid.v4(),
        userId: userId,
        date: now.subtract(const Duration(days: 30)),
        weight: 95.0,
        measurements: const BodyMeasurements(
          waist: 102, hip: 115, chest: 108, leftArm: 38, rightArm: 38,
          leftThigh: 65, rightThigh: 65,
        ),
        composition: const BodyCompositionModel(
          bodyFatPercentage: 32.0,
          muscleMassKg: 58.0,
          fatMassKg: 30.4,
          bmi: 31.0,
        ),
        notes: 'Início do programa',
        isSynced: true,
      ),
      ScanbodyRecord(
        id: uuid.v4(),
        userId: userId,
        date: now.subtract(const Duration(days: 15)),
        weight: 90.5,
        measurements: const BodyMeasurements(
          waist: 97, hip: 111, chest: 104, leftArm: 39, rightArm: 39,
          leftThigh: 63, rightThigh: 63,
        ),
        composition: const BodyCompositionModel(
          bodyFatPercentage: 30.0,
          muscleMassKg: 59.5,
          fatMassKg: 27.2,
          bmi: 29.6,
        ),
        notes: 'Progresso semana 2',
        isSynced: true,
      ),
      ScanbodyRecord(
        id: uuid.v4(),
        userId: userId,
        date: now,
        weight: 87.0,
        measurements: const BodyMeasurements(
          waist: 93, hip: 108, chest: 101, leftArm: 40, rightArm: 40,
          leftThigh: 61, rightThigh: 61,
        ),
        composition: const BodyCompositionModel(
          bodyFatPercentage: 28.0,
          muscleMassKg: 61.0,
          fatMassKg: 24.4,
          bmi: 28.4,
        ),
        notes: 'Progresso semana 4',
        isSynced: true,
      ),
    ]);
  }

  Future<void> capturePhoto(ScanStep step) async {
    try {
      final picker = ImagePicker();
      final image = await picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
        maxWidth: 1080,
        maxHeight: 1920,
      );

      if (image != null) {
        switch (step) {
          case ScanStep.front:
            _frontPhotoPath = image.path;
            _currentStep = ScanStep.side;
            break;
          case ScanStep.side:
            _sidePhotoPath = image.path;
            _currentStep = ScanStep.back;
            break;
          case ScanStep.back:
            _backPhotoPath = image.path;
            _currentStep = ScanStep.measurements;
            break;
          default:
            break;
        }
        notifyListeners();
      }
    } catch (e) {
      _error = 'Erro ao capturar foto. Verifique as permissões de câmera.';
      notifyListeners();
    }
  }

  Future<void> pickFromGallery(ScanStep step) async {
    try {
      final picker = ImagePicker();
      final image = await picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
      );

      if (image != null) {
        switch (step) {
          case ScanStep.front:
            _frontPhotoPath = image.path;
            break;
          case ScanStep.side:
            _sidePhotoPath = image.path;
            break;
          case ScanStep.back:
            _backPhotoPath = image.path;
            break;
          default:
            break;
        }
        notifyListeners();
      }
    } catch (e) {
      _error = 'Erro ao selecionar foto.';
      notifyListeners();
    }
  }

  void setWeight(double weight) {
    _currentWeight = weight;
    notifyListeners();
  }

  void setMeasurements(BodyMeasurements measurements) {
    _currentMeasurements = measurements;
    notifyListeners();
  }

  void goToStep(ScanStep step) {
    _currentStep = step;
    notifyListeners();
  }

  Future<ScanbodyRecord?> analyzeAndSave(String userId) async {
    if (_currentWeight <= 0) {
      _error = 'Por favor, informe seu peso atual.';
      notifyListeners();
      return null;
    }

    _isAnalyzing = true;
    notifyListeners();

    try {
      await Future.delayed(const Duration(seconds: 2));

      const uuid = Uuid();
      final record = ScanbodyRecord(
        id: uuid.v4(),
        userId: userId,
        date: DateTime.now(),
        weight: _currentWeight,
        measurements: _currentMeasurements,
        frontPhotoPath: _frontPhotoPath,
        sidePhotoPath: _sidePhotoPath,
        backPhotoPath: _backPhotoPath,
        aiAnalysis: _generateAIAnalysis(),
        isSynced: false,
      );

      _records.add(record);
      _currentStep = ScanStep.complete;
      return record;
    } catch (e) {
      _error = 'Erro ao analisar e salvar registro.';
      return null;
    } finally {
      _isAnalyzing = false;
      notifyListeners();
    }
  }

  String _generateAIAnalysis() {
    final prev = previousRecord;
    final latest = latestRecord;

    if (prev == null || latest == null) {
      return '📊 **Análise Corporal — Babi IA**\n\n'
          'Este é o seu primeiro registro! Parabéns por começar a monitorar seu progresso. '
          'Continue registrando semanalmente para acompanhar sua evolução. '
          'Foque em manter a meta proteica e os treinos programados. 💪';
    }

    final weightDiff = latest.weight - prev.weight;
    final sign = weightDiff < 0 ? '' : '+';

    return '📊 **Análise Corporal — Babi IA**\n\n'
        '**Variação de Peso**: $sign${weightDiff.toStringAsFixed(1)}kg\n\n'
        '${weightDiff < 0 ? "✅ Excelente progresso! Você perdeu ${weightDiff.abs().toStringAsFixed(1)}kg desde o último registro." : "⚠️ Houve um pequeno aumento. Revise sua alimentação e hidratação."}\n\n'
        '**Recomendações**:\n'
        '• Mantenha a meta proteica de 150-175g/dia\n'
        '• Continue com os treinos programados\n'
        '• Hidrate-se com 2,5-3,5L de água por dia\n'
        '• Durma 7-8 horas por noite\n\n'
        '**Próximo registro**: Em 7-14 dias para acompanhar a evolução. 🌟';
  }

  void resetScan() {
    _frontPhotoPath = null;
    _sidePhotoPath = null;
    _backPhotoPath = null;
    _currentWeight = 0;
    _currentMeasurements = null;
    _currentStep = ScanStep.front;
    _error = null;
    notifyListeners();
  }

  List<Map<String, dynamic>> get weightHistory {
    return _records
        .map((r) => {
              'date': r.date,
              'weight': r.weight,
            })
        .toList();
  }

  List<Map<String, dynamic>> get bodyFatHistory {
    return _records
        .where((r) => r.composition?.bodyFatPercentage != null)
        .map((r) => {
              'date': r.date,
              'bodyFat': r.composition!.bodyFatPercentage,
            })
        .toList();
  }
}
