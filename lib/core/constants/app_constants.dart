class AppConstants {
  // App Info
  static const String appName = 'Barifit+';
  static const String appVersion = '1.0.0';
  static const String appTagline = 'Sua jornada pós-bariátrica inteligente';

  // API
  static const String baseUrl = 'https://api.barifit.pro/v1';
  static const String openAiBaseUrl = 'https://api.openai.com/v1';
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;

  // Storage Keys
  static const String keyAuthToken = 'auth_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserId = 'user_id';
  static const String keyUserProfile = 'user_profile';
  static const String keyOnboardingDone = 'onboarding_done';
  static const String keyThemeMode = 'theme_mode';
  static const String keyNotificationsEnabled = 'notifications_enabled';
  static const String keyLastSync = 'last_sync';

  // Hive Boxes
  static const String boxWorkouts = 'workouts';
  static const String boxMeals = 'meals';
  static const String boxScanbody = 'scanbody';
  static const String boxProgress = 'progress';
  static const String boxChat = 'chat';
  static const String boxRecipes = 'recipes';

  // Program
  static const int programDays = 93;
  static const int phase1Weeks = 4;
  static const int phase2Weeks = 8;
  static const int phase3Weeks = 13;

  // Nutrition targets (base)
  static const double minProtein = 150;
  static const double maxProtein = 175;
  static const double minCalories = 1900;
  static const double maxCalories = 2500;
  static const double waterTarget = 3.0; // litros

  // Babi AI
  static const String babiSystemPrompt = '''
Você é Babi, a assistente de IA especializada em saúde pós-bariátrica do app Barifit+.
Você é empática, motivadora e altamente especializada em:
- Nutrição pós-cirurgia bariátrica
- Treinos adaptados para pacientes bariátricos
- Monitoramento de progresso corporal
- Suplementação adequada
- Bem-estar mental e motivação

Sempre responda em português brasileiro, de forma clara, acolhedora e baseada em evidências científicas.
Nunca forneça diagnósticos médicos. Sempre recomende consultar profissionais de saúde para decisões médicas.
Seja concisa mas completa. Use emojis moderadamente para tornar a conversa mais amigável.
''';

  // Notification Channels
  static const String channelWorkouts = 'workouts_channel';
  static const String channelMeals = 'meals_channel';
  static const String channelProgress = 'progress_channel';
  static const String channelGeneral = 'general_channel';

  // Animation Durations
  static const Duration animFast = Duration(milliseconds: 200);
  static const Duration animNormal = Duration(milliseconds: 350);
  static const Duration animSlow = Duration(milliseconds: 500);

  // Pagination
  static const int pageSize = 20;
}

class AppRoutes {
  static const String splash = '/';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String home = '/home';
  static const String dashboard = '/home/dashboard';
  static const String scanbody = '/home/scanbody';
  static const String scanbodyCamera = '/home/scanbody/camera';
  static const String scanbodyResult = '/home/scanbody/result';
  static const String scanbodyHistory = '/home/scanbody/history';
  static const String workouts = '/home/workouts';
  static const String workoutDetail = '/home/workouts/detail';
  static const String workoutActive = '/home/workouts/active';
  static const String meals = '/home/meals';
  static const String mealDetail = '/home/meals/detail';
  static const String mealLog = '/home/meals/log';
  static const String recipes = '/home/meals/recipes';
  static const String chat = '/home/chat';
  static const String profile = '/home/profile';
  static const String settings = '/home/settings';
  static const String progress = '/home/progress';
}

class AppAssets {
  // Images
  static const String logo = 'assets/images/logo.png';
  static const String logoWhite = 'assets/images/logo_white.png';
  static const String onboarding1 = 'assets/images/onboarding_1.png';
  static const String onboarding2 = 'assets/images/onboarding_2.png';
  static const String onboarding3 = 'assets/images/onboarding_3.png';
  static const String babiAvatar = 'assets/images/babi_avatar.png';
  static const String bodyPlaceholder = 'assets/images/body_placeholder.png';

  // Animations
  static const String loadingAnim = 'assets/animations/loading.json';
  static const String successAnim = 'assets/animations/success.json';
  static const String workoutAnim = 'assets/animations/workout.json';
  static const String scanAnim = 'assets/animations/scan.json';
  static const String chatTypingAnim = 'assets/animations/typing.json';
}
