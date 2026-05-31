import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/constants/app_constants.dart';
import '../../data/models/user_model.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

class AuthProvider extends ChangeNotifier {
  AuthStatus _status = AuthStatus.initial;
  UserModel? _user;
  String? _errorMessage;
  String? _token;

  AuthStatus get status => _status;
  UserModel? get user => _user;
  String? get errorMessage => _errorMessage;
  String? get token => _token;
  bool get isAuthenticated => _status == AuthStatus.authenticated;
  bool get isLoading => _status == AuthStatus.loading;

  Future<void> initialize() async {
    _status = AuthStatus.loading;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString(AppConstants.keyAuthToken);
      final userJson = prefs.getString(AppConstants.keyUserProfile);

      if (token != null && userJson != null) {
        _token = token;
        // TODO: Validate token with server and load user
        // For now, create a demo user
        _user = UserModel(
          id: 'demo_user',
          name: 'João Carlos',
          email: 'joao@barifit.pro',
          programStartDate: DateTime(2025, 10, 13),
          weight: 85.0,
          height: 175.0,
          createdAt: DateTime(2025, 10, 13),
        );
        _status = AuthStatus.authenticated;
      } else {
        _status = AuthStatus.unauthenticated;
      }
    } catch (e) {
      _status = AuthStatus.unauthenticated;
    }

    notifyListeners();
  }

  Future<bool> signIn({required String email, required String password}) async {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      // TODO: Implement real API call
      await Future.delayed(const Duration(seconds: 1));

      if (email.isNotEmpty && password.length >= 6) {
        final prefs = await SharedPreferences.getInstance();
        const fakeToken = 'barifit_token_demo';
        await prefs.setString(AppConstants.keyAuthToken, fakeToken);

        _token = fakeToken;
        _user = UserModel(
          id: 'user_${email.hashCode}',
          name: email.split('@').first,
          email: email,
          programStartDate: DateTime(2025, 10, 13),
          weight: 85.0,
          height: 175.0,
          createdAt: DateTime.now(),
        );
        _status = AuthStatus.authenticated;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Email ou senha inválidos.';
        _status = AuthStatus.error;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Erro ao fazer login. Tente novamente.';
      _status = AuthStatus.error;
      notifyListeners();
      return false;
    }
  }

  Future<bool> signUp({
    required String name,
    required String email,
    required String password,
    DateTime? surgeryDate,
  }) async {
    _status = AuthStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      await Future.delayed(const Duration(seconds: 1));

      final prefs = await SharedPreferences.getInstance();
      const fakeToken = 'barifit_token_new';
      await prefs.setString(AppConstants.keyAuthToken, fakeToken);

      _token = fakeToken;
      _user = UserModel(
        id: 'user_${email.hashCode}',
        name: name,
        email: email,
        surgeryDate: surgeryDate,
        programStartDate: DateTime.now(),
        createdAt: DateTime.now(),
      );
      _status = AuthStatus.authenticated;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Erro ao criar conta. Tente novamente.';
      _status = AuthStatus.error;
      notifyListeners();
      return false;
    }
  }

  Future<void> signOut() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.keyAuthToken);
    await prefs.remove(AppConstants.keyUserProfile);
    _user = null;
    _token = null;
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  Future<void> updateUser(UserModel updatedUser) async {
    _user = updatedUser;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    if (_status == AuthStatus.error) {
      _status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }
}
