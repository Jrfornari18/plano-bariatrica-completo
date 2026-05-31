import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../../data/models/meal_model.dart';

class MealProvider extends ChangeNotifier {
  final List<MealModel> _meals = [];
  final List<RecipeModel> _recipes = [];
  bool _isLoading = false;
  String? _error;
  DateTime _selectedDate = DateTime.now();

  List<MealModel> get meals => _meals;
  List<RecipeModel> get recipes => _recipes;
  bool get isLoading => _isLoading;
  String? get error => _error;
  DateTime get selectedDate => _selectedDate;

  List<MealModel> get todayMeals {
    final today = DateTime.now();
    return _meals.where((m) =>
        m.date.year == today.year &&
        m.date.month == today.month &&
        m.date.day == today.day).toList()
      ..sort((a, b) => a.scheduledTime.compareTo(b.scheduledTime));
  }

  List<MealModel> get selectedDateMeals {
    return _meals.where((m) =>
        m.date.year == _selectedDate.year &&
        m.date.month == _selectedDate.month &&
        m.date.day == _selectedDate.day).toList()
      ..sort((a, b) => a.scheduledTime.compareTo(b.scheduledTime));
  }

  MacrosModel get todayTotalMacros {
    final logged = todayMeals.where((m) => m.isLogged);
    if (logged.isEmpty) {
      return const MacrosModel(protein: 0, carbs: 0, fat: 0, calories: 0);
    }
    return logged.fold(
      const MacrosModel(protein: 0, carbs: 0, fat: 0, calories: 0),
      (prev, meal) => prev + meal.totalMacros,
    );
  }

  int get loggedMealsCount => todayMeals.where((m) => m.isLogged).length;
  double get mealCompletionRate =>
      todayMeals.isEmpty ? 0 : loggedMealsCount / todayMeals.length;

  void setSelectedDate(DateTime date) {
    _selectedDate = date;
    notifyListeners();
  }

  Future<void> loadMealsForDate(DateTime date, int dayOfWeek) async {
    _isLoading = true;
    notifyListeners();

    try {
      await Future.delayed(const Duration(milliseconds: 300));

      _meals.removeWhere((m) =>
          m.date.year == date.year &&
          m.date.month == date.month &&
          m.date.day == date.day);

      final dayMeals = _generateMealsForDay(date, dayOfWeek);
      _meals.addAll(dayMeals);
    } catch (e) {
      _error = 'Erro ao carregar refeições.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadRecipes() async {
    if (_recipes.isNotEmpty) return;
    _isLoading = true;
    notifyListeners();

    try {
      await Future.delayed(const Duration(milliseconds: 300));
      _recipes.addAll(_generateRecipes());
    } catch (e) {
      _error = 'Erro ao carregar receitas.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logMeal(String mealId) async {
    final index = _meals.indexWhere((m) => m.id == mealId);
    if (index == -1) return;
    _meals[index] = _meals[index].copyWith(isLogged: !_meals[index].isLogged);
    notifyListeners();
  }

  List<RecipeModel> searchRecipes(String query) {
    if (query.isEmpty) return _recipes;
    final lower = query.toLowerCase();
    return _recipes.where((r) =>
        r.name.toLowerCase().contains(lower) ||
        r.category.toLowerCase().contains(lower)).toList();
  }

  List<RecipeModel> getRecipesByCategory(String category) {
    if (category == 'Todos') return _recipes;
    return _recipes.where((r) => r.category == category).toList();
  }

  List<String> get recipeCategories {
    final cats = _recipes.map((r) => r.category).toSet().toList();
    return ['Todos', ...cats];
  }

  // ─── Meal Generators ───────────────────────────────────────────────────────

  List<MealModel> _generateMealsForDay(DateTime date, int dayOfWeek) {
    const uuid = Uuid();

    // dayOfWeek: 1=Mon, 7=Sun
    if (dayOfWeek == 7) {
      return _sundayMeals(uuid, date);
    } else if (dayOfWeek == 3) {
      return _threeSessions(uuid, date);
    } else if (dayOfWeek == 1 || dayOfWeek == 5) {
      return _twoSessions(uuid, date);
    } else {
      return _oneSession(uuid, date);
    }
  }

  List<MealModel> _oneSession(Uuid uuid, DateTime date) => [
        MealModel(
          id: uuid.v4(), type: MealType.cafeDaManha,
          scheduledTime: '06:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Whey Protein (30g)', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 24, carbs: 3, fat: 1, calories: 120)),
            FoodItemModel(id: uuid.v4(), name: 'Pão Integral (2 fatias)', quantity: 60, unit: 'g',
                macros: const MacrosModel(protein: 6, carbs: 28, fat: 2, calories: 150)),
            FoodItemModel(id: uuid.v4(), name: 'Ovos Mexidos (2)', quantity: 100, unit: 'g',
                macros: const MacrosModel(protein: 12, carbs: 1, fat: 10, calories: 140)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.posTreino,
          scheduledTime: '08:30', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Whey Protein', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 24, carbs: 3, fat: 1, calories: 120)),
            FoodItemModel(id: uuid.v4(), name: 'Batata Doce Cozida', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 2, carbs: 30, fat: 0, calories: 130)),
            FoodItemModel(id: uuid.v4(), name: 'Maçã', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 0, carbs: 20, fat: 0, calories: 78)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.almoco,
          scheduledTime: '12:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Frango Grelhado', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 45, carbs: 0, fat: 5, calories: 225)),
            FoodItemModel(id: uuid.v4(), name: 'Arroz Integral', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 4, carbs: 35, fat: 1, calories: 165)),
            FoodItemModel(id: uuid.v4(), name: 'Salada Verde + Azeite', quantity: 100, unit: 'g',
                macros: const MacrosModel(protein: 2, carbs: 5, fat: 10, calories: 110)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.lancheTarde,
          scheduledTime: '15:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Iogurte Proteico', quantity: 170, unit: 'g',
                macros: const MacrosModel(protein: 17, carbs: 8, fat: 0, calories: 100)),
            FoodItemModel(id: uuid.v4(), name: 'Amêndoas (10 un)', quantity: 15, unit: 'g',
                macros: const MacrosModel(protein: 3, carbs: 2, fat: 9, calories: 90)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.jantar,
          scheduledTime: '18:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Salmão Assado', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 34, carbs: 0, fat: 14, calories: 270)),
            FoodItemModel(id: uuid.v4(), name: 'Batata Doce', quantity: 120, unit: 'g',
                macros: const MacrosModel(protein: 2, carbs: 24, fat: 0, calories: 104)),
            FoodItemModel(id: uuid.v4(), name: 'Aspargos Grelhados', quantity: 100, unit: 'g',
                macros: const MacrosModel(protein: 3, carbs: 4, fat: 0, calories: 27)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.ceia,
          scheduledTime: '22:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Queijo Cottage', quantity: 100, unit: 'g',
                macros: const MacrosModel(protein: 12, carbs: 3, fat: 4, calories: 98)),
          ],
        ),
      ];

  List<MealModel> _twoSessions(Uuid uuid, DateTime date) => [
        MealModel(
          id: uuid.v4(), type: MealType.cafeDaManha,
          scheduledTime: '06:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Whey Protein', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 24, carbs: 3, fat: 1, calories: 120)),
            FoodItemModel(id: uuid.v4(), name: 'Pão Integral (3 fatias)', quantity: 90, unit: 'g',
                macros: const MacrosModel(protein: 9, carbs: 42, fat: 3, calories: 225)),
            FoodItemModel(id: uuid.v4(), name: 'Ovos + Clara', quantity: 120, unit: 'g',
                macros: const MacrosModel(protein: 18, carbs: 1, fat: 10, calories: 162)),
            FoodItemModel(id: uuid.v4(), name: 'Banana', quantity: 120, unit: 'g',
                macros: const MacrosModel(protein: 1, carbs: 27, fat: 0, calories: 107)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.posTreino,
          scheduledTime: '08:30', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Whey Protein', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 24, carbs: 3, fat: 1, calories: 120)),
            FoodItemModel(id: uuid.v4(), name: 'Batata Doce (200g)', quantity: 200, unit: 'g',
                macros: const MacrosModel(protein: 3, carbs: 40, fat: 0, calories: 172)),
            FoodItemModel(id: uuid.v4(), name: 'Pasta de Amendoim (1 col)', quantity: 15, unit: 'g',
                macros: const MacrosModel(protein: 4, carbs: 3, fat: 8, calories: 94)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.almoco,
          scheduledTime: '11:30', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Frango Grelhado', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 45, carbs: 0, fat: 5, calories: 225)),
            FoodItemModel(id: uuid.v4(), name: 'Arroz Integral', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 4, carbs: 35, fat: 1, calories: 165)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.posTreino,
          scheduledTime: '14:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Whey Protein', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 24, carbs: 3, fat: 1, calories: 120)),
            FoodItemModel(id: uuid.v4(), name: '2 Bananas', quantity: 240, unit: 'g',
                macros: const MacrosModel(protein: 2, carbs: 54, fat: 0, calories: 214)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.jantar,
          scheduledTime: '18:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Carne Magra (patinho)', quantity: 180, unit: 'g',
                macros: const MacrosModel(protein: 40, carbs: 0, fat: 8, calories: 232)),
            FoodItemModel(id: uuid.v4(), name: 'Batata Doce', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 2, carbs: 30, fat: 0, calories: 130)),
            FoodItemModel(id: uuid.v4(), name: 'Brócolis + Couve-flor', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 5, carbs: 10, fat: 0, calories: 55)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.ceia,
          scheduledTime: '22:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Queijo Cottage (150g)', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 18, carbs: 4, fat: 6, calories: 147)),
            FoodItemModel(id: uuid.v4(), name: 'Nozes (10 un)', quantity: 15, unit: 'g',
                macros: const MacrosModel(protein: 2, carbs: 2, fat: 9, calories: 93)),
          ],
        ),
      ];

  List<MealModel> _threeSessions(Uuid uuid, DateTime date) =>
      _twoSessions(uuid, date); // Simplificado, pode ser expandido

  List<MealModel> _sundayMeals(Uuid uuid, DateTime date) => [
        MealModel(
          id: uuid.v4(), type: MealType.cafeDaManha,
          scheduledTime: '06:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Whey Protein', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 24, carbs: 3, fat: 1, calories: 120)),
            FoodItemModel(id: uuid.v4(), name: 'Pão Integral (2 fatias)', quantity: 60, unit: 'g',
                macros: const MacrosModel(protein: 6, carbs: 28, fat: 2, calories: 150)),
            FoodItemModel(id: uuid.v4(), name: 'Ovos Mexidos', quantity: 100, unit: 'g',
                macros: const MacrosModel(protein: 12, carbs: 1, fat: 10, calories: 140)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.lanchesManha,
          scheduledTime: '09:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Iogurte Proteico', quantity: 170, unit: 'g',
                macros: const MacrosModel(protein: 17, carbs: 8, fat: 0, calories: 100)),
            FoodItemModel(id: uuid.v4(), name: 'Frutas Vermelhas', quantity: 100, unit: 'g',
                macros: const MacrosModel(protein: 1, carbs: 14, fat: 0, calories: 57)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.almoco,
          scheduledTime: '12:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Proteína Magra', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 35, carbs: 0, fat: 5, calories: 185)),
            FoodItemModel(id: uuid.v4(), name: 'Arroz Integral', quantity: 120, unit: 'g',
                macros: const MacrosModel(protein: 3, carbs: 28, fat: 1, calories: 132)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.lancheTarde,
          scheduledTime: '15:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Mix de Castanhas (30g)', quantity: 30, unit: 'g',
                macros: const MacrosModel(protein: 5, carbs: 5, fat: 18, calories: 190)),
          ],
        ),
        MealModel(
          id: uuid.v4(), type: MealType.jantar,
          scheduledTime: '18:00', date: date,
          items: [
            FoodItemModel(id: uuid.v4(), name: 'Peixe ou Frango', quantity: 150, unit: 'g',
                macros: const MacrosModel(protein: 35, carbs: 0, fat: 5, calories: 185)),
            FoodItemModel(id: uuid.v4(), name: 'Salada Grande', quantity: 200, unit: 'g',
                macros: const MacrosModel(protein: 3, carbs: 10, fat: 5, calories: 93)),
          ],
        ),
      ];

  List<RecipeModel> _generateRecipes() {
    const uuid = Uuid();
    return [
      RecipeModel(
        id: uuid.v4(),
        name: 'Omelete Proteica de Claras',
        category: 'Café da Manhã',
        prepTime: '10 min',
        servings: 1,
        macros: const MacrosModel(protein: 28, carbs: 5, fat: 8, calories: 200),
        ingredients: [
          '3 claras de ovo', '1 ovo inteiro', '30g de queijo cottage',
          '1 tomate picado', 'Espinafre à vontade', 'Sal e pimenta',
        ],
        instructions: [
          'Bata os ovos com as claras em uma tigela',
          'Adicione o queijo cottage e misture bem',
          'Aqueça frigideira antiaderente',
          'Despeje a mistura com tomate e espinafre',
          'Cozinhe em fogo baixo até firmar',
          'Dobre ao meio e sirva',
        ],
        tips: 'Pode adicionar cogumelos ou pimentão para mais sabor.',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Panqueca de Banana e Aveia Proteica',
        category: 'Café da Manhã',
        prepTime: '15 min',
        servings: 1,
        macros: const MacrosModel(protein: 25, carbs: 35, fat: 6, calories: 290),
        ingredients: [
          '1 banana madura', '2 ovos', '30g de aveia em flocos',
          '1 scoop de whey protein (baunilha)', '1 col chá de canela',
        ],
        instructions: [
          'Amasse a banana em uma tigela',
          'Adicione os ovos e bata bem',
          'Misture aveia, whey e canela',
          'Deixe descansar 2 minutos',
          'Faça panquecas pequenas em frigideira aquecida',
          'Cozinhe 2-3 min cada lado',
        ],
        tips: 'Sirva com frutas vermelhas ou mel (opcional).',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Frango Grelhado com Legumes Assados',
        category: 'Almoço/Jantar',
        prepTime: '35 min',
        servings: 1,
        macros: const MacrosModel(protein: 45, carbs: 30, fat: 10, calories: 400),
        ingredients: [
          '150g peito de frango', '100g batata doce em cubos',
          '1 abobrinha fatiada', '1 cenoura em rodelas',
          'Brócolis à vontade', '1 col sopa azeite', 'Alho, limão, ervas',
        ],
        instructions: [
          'Tempere o frango com alho, limão, sal e pimenta',
          'Marine por 15 min',
          'Pré-aqueça o forno a 200°C',
          'Disponha os legumes em assadeira com azeite',
          'Grelhe o frango em frigideira 5-6 min cada lado',
          'Asse os legumes por 20-25 min',
        ],
        tips: 'Prepare em dobro para ter almoço e jantar prontos.',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Shake Pós-Treino Completo',
        category: 'Pós-Treino',
        prepTime: '5 min',
        servings: 1,
        macros: const MacrosModel(protein: 35, carbs: 45, fat: 5, calories: 365),
        ingredients: [
          '1 scoop whey protein', '1 banana congelada',
          '200ml leite desnatado', '1 col sopa pasta amendoim',
          '1 col chá canela', 'Gelo a gosto',
        ],
        instructions: [
          'Coloque todos os ingredientes no liquidificador',
          'Bata por 30-40 segundos',
          'Sirva imediatamente após o treino',
        ],
        tips: 'Consuma nos primeiros 30 min após o treino para melhor absorção.',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Bowl de Açaí Proteico',
        category: 'Lanches',
        prepTime: '10 min',
        servings: 1,
        macros: const MacrosModel(protein: 20, carbs: 40, fat: 8, calories: 310),
        ingredients: [
          '100g polpa de açaí sem açúcar', '1 scoop whey protein',
          '1/2 banana', '50ml leite de amêndoas',
          'Granola sem açúcar (30g)', 'Frutas vermelhas para decorar',
        ],
        instructions: [
          'Bata o açaí com whey, banana e leite de amêndoas',
          'Despeje em uma tigela',
          'Adicione granola e frutas por cima',
          'Sirva imediatamente',
        ],
        tips: 'Use açaí sem adição de açúcar para controlar as calorias.',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Mousse de Chocolate Proteico',
        category: 'Sobremesas',
        prepTime: '15 min + 2h geladeira',
        servings: 2,
        macros: const MacrosModel(protein: 22, carbs: 15, fat: 6, calories: 202),
        ingredients: [
          '200g queijo cottage', '1 scoop whey chocolate',
          '2 col sopa cacau em pó', '2 col sopa mel',
          '1 col chá essência de baunilha',
        ],
        instructions: [
          'Bata o cottage no liquidificador até ficar cremoso',
          'Adicione whey, cacau, mel e baunilha',
          'Bata novamente até homogêneo',
          'Distribua em taças e leve à geladeira por 2h',
        ],
        tips: 'Decore com raspas de chocolate 70% cacau.',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Overnight Oats Proteico',
        category: 'Café da Manhã',
        prepTime: '5 min + 8h geladeira',
        servings: 1,
        macros: const MacrosModel(protein: 30, carbs: 40, fat: 8, calories: 350),
        ingredients: [
          '40g aveia em flocos', '1 scoop whey protein',
          '200ml leite desnatado', '1 col sopa chia',
          '1/2 banana fatiada', 'Canela a gosto',
        ],
        instructions: [
          'Misture aveia, whey e chia em um pote',
          'Adicione o leite e misture bem',
          'Coloque a banana fatiada por cima',
          'Polvilhe canela, tampe e leve à geladeira overnight',
          'Pela manhã, misture e está pronto',
        ],
        tips: 'Prepare na noite anterior para economizar tempo.',
      ),
      RecipeModel(
        id: uuid.v4(),
        name: 'Salmão com Quinoa e Aspargos',
        category: 'Almoço/Jantar',
        prepTime: '30 min',
        servings: 1,
        macros: const MacrosModel(protein: 42, carbs: 35, fat: 15, calories: 435),
        ingredients: [
          '150g filé de salmão', '80g quinoa cozida',
          '100g aspargos', '1 col sopa azeite',
          'Limão, alho, ervas finas', 'Sal e pimenta',
        ],
        instructions: [
          'Tempere o salmão com limão, alho e ervas',
          'Grelhe em frigideira antiaderente 4-5 min cada lado',
          'Cozinhe a quinoa conforme embalagem',
          'Grelhe os aspargos com azeite por 5 min',
          'Monte o prato e sirva',
        ],
        tips: 'O salmão é rico em ômega-3, excelente para recuperação muscular.',
      ),
    ];
  }
}
