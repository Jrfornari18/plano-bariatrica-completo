import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

/// SyncService handles local caching and background sync with the remote API.
/// Uses SharedPreferences for local persistence and connectivity_plus to detect
/// network availability before attempting remote operations.
class SyncService {
  static final SyncService _instance = SyncService._internal();
  factory SyncService() => _instance;
  SyncService._internal();

  static const String _prefix = 'barifit_';
  late SharedPreferences _prefs;
  bool _initialized = false;

  Future<void> initialize() async {
    if (_initialized) return;
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
  }

  // ─── Connectivity ────────────────────────────────────────────────────────

  Future<bool> get isOnline async {
    final result = await Connectivity().checkConnectivity();
    return result != ConnectivityResult.none;
  }

  // ─── Generic Cache Operations ────────────────────────────────────────────

  Future<void> saveLocal(String key, dynamic data) async {
    await _prefs.setString(
      '$_prefix$key',
      jsonEncode(data),
    );
    await _prefs.setInt(
      '${_prefix}${key}_ts',
      DateTime.now().millisecondsSinceEpoch,
    );
  }

  dynamic loadLocal(String key) {
    final raw = _prefs.getString('$_prefix$key');
    if (raw == null) return null;
    return jsonDecode(raw);
  }

  DateTime? getLastSyncTime(String key) {
    final ts = _prefs.getInt('${_prefix}${key}_ts');
    if (ts == null) return null;
    return DateTime.fromMillisecondsSinceEpoch(ts);
  }

  bool isCacheStale(String key, {Duration maxAge = const Duration(hours: 1)}) {
    final lastSync = getLastSyncTime(key);
    if (lastSync == null) return true;
    return DateTime.now().difference(lastSync) > maxAge;
  }

  Future<void> clearLocal(String key) async {
    await _prefs.remove('$_prefix$key');
    await _prefs.remove('${_prefix}${key}_ts');
  }

  // ─── User Data ───────────────────────────────────────────────────────────

  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await saveLocal('user_data', userData);
  }

  Map<String, dynamic>? loadUserData() {
    final data = loadLocal('user_data');
    if (data == null) return null;
    return Map<String, dynamic>.from(data as Map);
  }

  Future<void> saveAuthToken(String token) async {
    await _prefs.setString('${_prefix}auth_token', token);
  }

  String? loadAuthToken() {
    return _prefs.getString('${_prefix}auth_token');
  }

  Future<void> clearAuthToken() async {
    await _prefs.remove('${_prefix}auth_token');
  }

  // ─── Workouts ────────────────────────────────────────────────────────────

  Future<void> saveWorkouts(List<Map<String, dynamic>> workouts) async {
    await saveLocal('workouts', workouts);
  }

  List<Map<String, dynamic>>? loadWorkouts() {
    final data = loadLocal('workouts');
    if (data == null) return null;
    return (data as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  Future<void> markWorkoutComplete(String workoutId) async {
    final completed = _prefs.getStringList('${_prefix}completed_workouts') ?? [];
    if (!completed.contains(workoutId)) {
      completed.add(workoutId);
      await _prefs.setStringList('${_prefix}completed_workouts', completed);
    }
  }

  List<String> getCompletedWorkouts() {
    return _prefs.getStringList('${_prefix}completed_workouts') ?? [];
  }

  // ─── Meals ───────────────────────────────────────────────────────────────

  Future<void> saveMeals(List<Map<String, dynamic>> meals) async {
    await saveLocal('meals', meals);
  }

  List<Map<String, dynamic>>? loadMeals() {
    final data = loadLocal('meals');
    if (data == null) return null;
    return (data as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  Future<void> markMealLogged(String mealId) async {
    final logged = _prefs.getStringList('${_prefix}logged_meals') ?? [];
    if (!logged.contains(mealId)) {
      logged.add(mealId);
      await _prefs.setStringList('${_prefix}logged_meals', logged);
    } else {
      logged.remove(mealId);
      await _prefs.setStringList('${_prefix}logged_meals', logged);
    }
  }

  List<String> getLoggedMeals() {
    return _prefs.getStringList('${_prefix}logged_meals') ?? [];
  }

  // ─── Water Intake ────────────────────────────────────────────────────────

  Future<void> saveWaterGlasses(int glasses) async {
    final today = DateTime.now();
    final key = '${_prefix}water_${today.year}_${today.month}_${today.day}';
    await _prefs.setInt(key, glasses);
  }

  int loadWaterGlasses() {
    final today = DateTime.now();
    final key = '${_prefix}water_${today.year}_${today.month}_${today.day}';
    return _prefs.getInt(key) ?? 0;
  }

  // ─── ScanBody Records ────────────────────────────────────────────────────

  Future<void> saveScanbodyRecords(
      List<Map<String, dynamic>> records) async {
    await saveLocal('scanbody_records', records);
  }

  List<Map<String, dynamic>>? loadScanbodyRecords() {
    final data = loadLocal('scanbody_records');
    if (data == null) return null;
    return (data as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  // ─── Chat History ────────────────────────────────────────────────────────

  Future<void> saveChatHistory(
      List<Map<String, dynamic>> messages) async {
    // Keep only last 50 messages to avoid excessive storage
    final trimmed = messages.length > 50
        ? messages.sublist(messages.length - 50)
        : messages;
    await saveLocal('chat_history', trimmed);
  }

  List<Map<String, dynamic>>? loadChatHistory() {
    final data = loadLocal('chat_history');
    if (data == null) return null;
    return (data as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  // ─── Pending Sync Queue ──────────────────────────────────────────────────

  Future<void> addToPendingSync(Map<String, dynamic> operation) async {
    final queue = _prefs.getStringList('${_prefix}pending_sync') ?? [];
    queue.add(jsonEncode(operation));
    await _prefs.setStringList('${_prefix}pending_sync', queue);
  }

  Future<List<Map<String, dynamic>>> getPendingSyncQueue() async {
    final queue = _prefs.getStringList('${_prefix}pending_sync') ?? [];
    return queue
        .map((e) => Map<String, dynamic>.from(jsonDecode(e) as Map))
        .toList();
  }

  Future<void> clearPendingSyncQueue() async {
    await _prefs.remove('${_prefix}pending_sync');
  }

  // ─── Full Sync ───────────────────────────────────────────────────────────

  Future<void> syncAll({
    required String userId,
    required String authToken,
  }) async {
    if (!await isOnline) return;

    try {
      // Process pending operations
      final pending = await getPendingSyncQueue();
      if (pending.isNotEmpty) {
        // In a real app, batch-send to API
        await clearPendingSyncQueue();
      }
    } catch (e) {
      // Silently fail — will retry on next sync
    }
  }

  // ─── Clear All ───────────────────────────────────────────────────────────

  Future<void> clearAll() async {
    final keys = _prefs.getKeys()
        .where((k) => k.startsWith(_prefix))
        .toList();
    for (final key in keys) {
      await _prefs.remove(key);
    }
  }
}
