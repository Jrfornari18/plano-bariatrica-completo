import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<_OnboardingPage> _pages = [
    _OnboardingPage(
      emoji: '🏋️',
      gradient: [AppColors.primary, AppColors.primaryDark],
      title: 'Treinos\nPersonalizados',
      subtitle:
          'Programa completo de 93 dias com musculação, natação, corrida e calistenia — adaptado para você.',
    ),
    _OnboardingPage(
      emoji: '🍽️',
      gradient: [AppColors.secondary, AppColors.secondaryDark],
      title: 'Nutrição\nInteligente',
      subtitle:
          'Cardápios diários personalizados com macros calculados para sua fase de recuperação bariátrica.',
    ),
    _OnboardingPage(
      emoji: '📸',
      gradient: [AppColors.warning, AppColors.warningDark],
      title: 'ScanBody\nIA',
      subtitle:
          'Registre sua evolução corporal com fotos e análise de IA. Veja sua transformação semana a semana.',
    ),
    _OnboardingPage(
      emoji: '🤖',
      gradient: [const Color(0xFF7C3AED), const Color(0xFF5B21B6)],
      title: 'Babi,\nSua Assistente IA',
      subtitle:
          'Tire dúvidas sobre nutrição, treinos e bem-estar a qualquer hora com a Babi, sua IA especializada.',
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentPage < _pages.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      Navigator.of(context).pushReplacementNamed('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          PageView.builder(
            controller: _pageController,
            onPageChanged: (index) => setState(() => _currentPage = index),
            itemCount: _pages.length,
            itemBuilder: (context, index) {
              final page = _pages[index];
              return _buildPage(page);
            },
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _buildBottomControls(),
          ),
        ],
      ),
    );
  }

  Widget _buildPage(_OnboardingPage page) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: page.gradient,
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xxxl),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Skip button
              Align(
                alignment: Alignment.topRight,
                child: TextButton(
                  onPressed: () =>
                      Navigator.of(context).pushReplacementNamed('/login'),
                  child: Text(
                    'Pular',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 16,
                    ),
                  ),
                ),
              ),

              const Spacer(),

              // Emoji illustration
              Container(
                width: 160,
                height: 160,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: AppRadius.xxlRadius,
                ),
                child: Center(
                  child: Text(
                    page.emoji,
                    style: const TextStyle(fontSize: 80),
                  ),
                ),
              ),

              const SizedBox(height: AppSpacing.xxxl),

              // Title
              Text(
                page.title,
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 36,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  height: 1.1,
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: AppSpacing.lg),

              // Subtitle
              Text(
                page.subtitle,
                style: TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 17,
                  fontWeight: FontWeight.w400,
                  color: Colors.white.withOpacity(0.85),
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),

              const Spacer(flex: 2),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBottomControls() {
    final isLast = _currentPage == _pages.length - 1;
    return Container(
      padding: const EdgeInsets.fromLTRB(
          AppSpacing.xxxl, AppSpacing.xl, AppSpacing.xxxl, AppSpacing.xxxl),
      child: Column(
        children: [
          // Page indicators
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(
              _pages.length,
              (index) => AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                width: _currentPage == index ? 24 : 8,
                height: 8,
                decoration: BoxDecoration(
                  color: _currentPage == index
                      ? Colors.white
                      : Colors.white.withOpacity(0.4),
                  borderRadius: AppRadius.fullRadius,
                ),
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.xl),

          // Next / Get Started button
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: _nextPage,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: _pages[_currentPage].gradient.first,
                elevation: 0,
                shape: const RoundedRectangleBorder(
                  borderRadius: AppRadius.lgRadius,
                ),
              ),
              child: Text(
                isLast ? 'Começar Agora' : 'Próximo',
                style: const TextStyle(
                  fontFamily: 'Inter',
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),

          if (!isLast) ...[
            const SizedBox(height: AppSpacing.md),
            TextButton(
              onPressed: () =>
                  Navigator.of(context).pushReplacementNamed('/login'),
              child: Text(
                'Já tenho uma conta',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.8),
                  fontSize: 15,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _OnboardingPage {
  final String emoji;
  final List<Color> gradient;
  final String title;
  final String subtitle;

  const _OnboardingPage({
    required this.emoji,
    required this.gradient,
    required this.title,
    required this.subtitle,
  });
}
