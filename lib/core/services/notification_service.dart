import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  Future<void> initialize() async {
    tz.initializeTimeZones();

    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _notifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _onNotificationTap,
    );
  }

  void _onNotificationTap(NotificationResponse response) {
    // Handle notification tap — navigate to relevant screen
  }

  Future<void> requestPermissions() async {
    await _notifications
        .resolvePlatformSpecificImplementation<
            IOSFlutterLocalNotificationsPlugin>()
        ?.requestPermissions(alert: true, badge: true, sound: true);

    await _notifications
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
  }

  // ─── Workout Reminders ──────────────────────────────────────────────────

  Future<void> scheduleWorkoutReminder({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledTime,
  }) async {
    await _notifications.zonedSchedule(
      id,
      title,
      body,
      tz.TZDateTime.from(scheduledTime, tz.local),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'workout_reminders',
          'Lembretes de Treino',
          channelDescription: 'Notificações de lembretes de treino',
          importance: Importance.high,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          color: const Color(0xFF2563EB),
        ),
        iOS: DarwinNotificationDetails(
          categoryIdentifier: 'workout',
        ),
      ),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
    );
  }

  // ─── Meal Reminders ─────────────────────────────────────────────────────

  Future<void> scheduleMealReminder({
    required int id,
    required String mealName,
    required String scheduledTime,
  }) async {
    final now = DateTime.now();
    final parts = scheduledTime.split(':');
    var scheduled = DateTime(
      now.year,
      now.month,
      now.day,
      int.parse(parts[0]),
      int.parse(parts[1]),
    );

    if (scheduled.isBefore(now)) {
      scheduled = scheduled.add(const Duration(days: 1));
    }

    await _notifications.zonedSchedule(
      id + 100,
      '🍽️ Hora da $mealName!',
      'Não esqueça de registrar sua refeição no Barifit+.',
      tz.TZDateTime.from(scheduled, tz.local),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'meal_reminders',
          'Lembretes de Refeição',
          channelDescription: 'Notificações de lembretes de refeição',
          importance: Importance.defaultImportance,
          priority: Priority.defaultPriority,
          color: const Color(0xFF10B981),
        ),
        iOS: DarwinNotificationDetails(
          categoryIdentifier: 'meal',
        ),
      ),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      matchDateTimeComponents: DateTimeComponents.time,
    );
  }

  // ─── Water Reminders ────────────────────────────────────────────────────

  Future<void> scheduleWaterReminders() async {
    final waterTimes = [8, 10, 12, 14, 16, 18, 20];
    for (int i = 0; i < waterTimes.length; i++) {
      final now = DateTime.now();
      var scheduled = DateTime(now.year, now.month, now.day, waterTimes[i]);
      if (scheduled.isBefore(now)) {
        scheduled = scheduled.add(const Duration(days: 1));
      }

      await _notifications.zonedSchedule(
        200 + i,
        '💧 Hora de se hidratar!',
        'Beba um copo de água agora. Meta diária: 3L.',
        tz.TZDateTime.from(scheduled, tz.local),
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'water_reminders',
            'Lembretes de Hidratação',
            channelDescription: 'Notificações de lembretes de água',
            importance: Importance.low,
            priority: Priority.low,
            color: const Color(0xFF0EA5E9),
          ),
          iOS: DarwinNotificationDetails(
            categoryIdentifier: 'water',
          ),
        ),
        androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.time,
      );
    }
  }

  // ─── ScanBody Reminder ──────────────────────────────────────────────────

  Future<void> scheduleScanBodyReminder() async {
    final now = DateTime.now();
    final nextMonday = now.add(Duration(days: 8 - now.weekday));
    final scheduled = DateTime(
        nextMonday.year, nextMonday.month, nextMonday.day, 8, 0);

    await _notifications.zonedSchedule(
      300,
      '📸 Hora do ScanBody semanal!',
      'Registre seu progresso corporal desta semana.',
      tz.TZDateTime.from(scheduled, tz.local),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'scanbody_reminders',
          'Lembretes ScanBody',
          channelDescription: 'Notificações de lembretes de ScanBody',
          importance: Importance.high,
          priority: Priority.high,
          color: const Color(0xFFF59E0B),
        ),
        iOS: DarwinNotificationDetails(
          categoryIdentifier: 'scanbody',
        ),
      ),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      matchDateTimeComponents: DateTimeComponents.dayOfWeekAndTime,
    );
  }

  // ─── Supplement Reminders ───────────────────────────────────────────────

  Future<void> scheduleSupplementReminders() async {
    final supplements = [
      {'id': 400, 'time': 8, 'name': 'Multivitamínico + Vitamina B12'},
      {'id': 401, 'time': 12, 'name': 'Cálcio + Vitamina D'},
      {'id': 402, 'time': 20, 'name': 'Ômega-3'},
    ];

    for (final supp in supplements) {
      final now = DateTime.now();
      var scheduled = DateTime(
          now.year, now.month, now.day, supp['time'] as int);
      if (scheduled.isBefore(now)) {
        scheduled = scheduled.add(const Duration(days: 1));
      }

      await _notifications.zonedSchedule(
        supp['id'] as int,
        '💊 ${supp['name']}',
        'Hora de tomar seu suplemento!',
        tz.TZDateTime.from(scheduled, tz.local),
        const NotificationDetails(
          android: AndroidNotificationDetails(
            'supplement_reminders',
            'Lembretes de Suplementos',
            channelDescription: 'Notificações de lembretes de suplementos',
            importance: Importance.defaultImportance,
            priority: Priority.defaultPriority,
            color: const Color(0xFF7C3AED),
          ),
          iOS: DarwinNotificationDetails(
            categoryIdentifier: 'supplement',
          ),
        ),
        androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.time,
      );
    }
  }

  Future<void> cancelAll() async {
    await _notifications.cancelAll();
  }

  Future<void> cancel(int id) async {
    await _notifications.cancel(id);
  }

  Future<void> setupDefaultReminders() async {
    await cancelAll();
    await scheduleWaterReminders();
    await scheduleScanBodyReminder();
    await scheduleSupplementReminders();
  }
}
