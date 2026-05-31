import 'package:equatable/equatable.dart';

enum MealType { cafeDaManha, lanchesManha, almoco, lancheTarde, jantar, ceia, posTreino, preTreino }

class MacrosModel extends Equatable {
  final double protein;
  final double carbs;
  final double fat;
  final double calories;
  final double? fiber;

  const MacrosModel({
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.calories,
    this.fiber,
  });

  MacrosModel operator +(MacrosModel other) => MacrosModel(
        protein: protein + other.protein,
        carbs: carbs + other.carbs,
        fat: fat + other.fat,
        calories: calories + other.calories,
        fiber: (fiber ?? 0) + (other.fiber ?? 0),
      );

  Map<String, dynamic> toJson() => {
        'protein': protein,
        'carbs': carbs,
        'fat': fat,
        'calories': calories,
        'fiber': fiber,
      };

  factory MacrosModel.fromJson(Map<String, dynamic> json) => MacrosModel(
        protein: (json['protein'] as num).toDouble(),
        carbs: (json['carbs'] as num).toDouble(),
        fat: (json['fat'] as num).toDouble(),
        calories: (json['calories'] as num).toDouble(),
        fiber: (json['fiber'] as num?)?.toDouble(),
      );

  @override
  List<Object?> get props => [protein, carbs, fat, calories];
}

class FoodItemModel extends Equatable {
  final String id;
  final String name;
  final double quantity;
  final String unit;
  final MacrosModel macros;
  final bool isLogged;

  const FoodItemModel({
    required this.id,
    required this.name,
    required this.quantity,
    required this.unit,
    required this.macros,
    this.isLogged = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'quantity': quantity,
        'unit': unit,
        'macros': macros.toJson(),
        'isLogged': isLogged,
      };

  factory FoodItemModel.fromJson(Map<String, dynamic> json) => FoodItemModel(
        id: json['id'] as String,
        name: json['name'] as String,
        quantity: (json['quantity'] as num).toDouble(),
        unit: json['unit'] as String,
        macros: MacrosModel.fromJson(json['macros'] as Map<String, dynamic>),
        isLogged: json['isLogged'] as bool? ?? false,
      );

  @override
  List<Object?> get props => [id, name];
}

class MealModel extends Equatable {
  final String id;
  final MealType type;
  final String scheduledTime;
  final DateTime date;
  final List<FoodItemModel> items;
  final bool isLogged;
  final String? notes;
  final bool isSynced;

  const MealModel({
    required this.id,
    required this.type,
    required this.scheduledTime,
    required this.date,
    this.items = const [],
    this.isLogged = false,
    this.notes,
    this.isSynced = false,
  });

  MacrosModel get totalMacros {
    if (items.isEmpty) {
      return const MacrosModel(protein: 0, carbs: 0, fat: 0, calories: 0);
    }
    return items.fold(
      const MacrosModel(protein: 0, carbs: 0, fat: 0, calories: 0),
      (prev, item) => prev + item.macros,
    );
  }

  String get typeLabel {
    switch (type) {
      case MealType.cafeDaManha:
        return 'Café da Manhã';
      case MealType.lanchesManha:
        return 'Lanche da Manhã';
      case MealType.almoco:
        return 'Almoço';
      case MealType.lancheTarde:
        return 'Lanche da Tarde';
      case MealType.jantar:
        return 'Jantar';
      case MealType.ceia:
        return 'Ceia';
      case MealType.posTreino:
        return 'Pós-Treino';
      case MealType.preTreino:
        return 'Pré-Treino';
    }
  }

  String get typeEmoji {
    switch (type) {
      case MealType.cafeDaManha:
        return '🌅';
      case MealType.lanchesManha:
        return '🍎';
      case MealType.almoco:
        return '🍽️';
      case MealType.lancheTarde:
        return '🥗';
      case MealType.jantar:
        return '🌙';
      case MealType.ceia:
        return '🌛';
      case MealType.posTreino:
        return '💪';
      case MealType.preTreino:
        return '⚡';
    }
  }

  MealModel copyWith({
    String? id,
    MealType? type,
    String? scheduledTime,
    DateTime? date,
    List<FoodItemModel>? items,
    bool? isLogged,
    String? notes,
    bool? isSynced,
  }) {
    return MealModel(
      id: id ?? this.id,
      type: type ?? this.type,
      scheduledTime: scheduledTime ?? this.scheduledTime,
      date: date ?? this.date,
      items: items ?? this.items,
      isLogged: isLogged ?? this.isLogged,
      notes: notes ?? this.notes,
      isSynced: isSynced ?? this.isSynced,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type.name,
        'scheduledTime': scheduledTime,
        'date': date.toIso8601String(),
        'items': items.map((i) => i.toJson()).toList(),
        'isLogged': isLogged,
        'notes': notes,
        'isSynced': isSynced,
      };

  factory MealModel.fromJson(Map<String, dynamic> json) => MealModel(
        id: json['id'] as String,
        type: MealType.values.byName(json['type'] as String),
        scheduledTime: json['scheduledTime'] as String,
        date: DateTime.parse(json['date'] as String),
        items: (json['items'] as List<dynamic>?)
                ?.map((i) => FoodItemModel.fromJson(i as Map<String, dynamic>))
                .toList() ??
            [],
        isLogged: json['isLogged'] as bool? ?? false,
        notes: json['notes'] as String?,
        isSynced: json['isSynced'] as bool? ?? false,
      );

  @override
  List<Object?> get props => [id, date, type];
}

class RecipeModel extends Equatable {
  final String id;
  final String name;
  final String category;
  final String prepTime;
  final int servings;
  final MacrosModel macros;
  final List<String> ingredients;
  final List<String> instructions;
  final String? tips;
  final String? imageUrl;
  final bool isFavorite;

  const RecipeModel({
    required this.id,
    required this.name,
    required this.category,
    required this.prepTime,
    required this.servings,
    required this.macros,
    required this.ingredients,
    required this.instructions,
    this.tips,
    this.imageUrl,
    this.isFavorite = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'category': category,
        'prepTime': prepTime,
        'servings': servings,
        'macros': macros.toJson(),
        'ingredients': ingredients,
        'instructions': instructions,
        'tips': tips,
        'imageUrl': imageUrl,
        'isFavorite': isFavorite,
      };

  factory RecipeModel.fromJson(Map<String, dynamic> json) => RecipeModel(
        id: json['id'] as String,
        name: json['name'] as String,
        category: json['category'] as String,
        prepTime: json['prepTime'] as String,
        servings: json['servings'] as int,
        macros: MacrosModel.fromJson(json['macros'] as Map<String, dynamic>),
        ingredients: List<String>.from(json['ingredients'] as List),
        instructions: List<String>.from(json['instructions'] as List),
        tips: json['tips'] as String?,
        imageUrl: json['imageUrl'] as String?,
        isFavorite: json['isFavorite'] as bool? ?? false,
      );

  @override
  List<Object?> get props => [id, name];
}
