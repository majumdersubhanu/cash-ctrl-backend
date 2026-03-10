import 'package:flutter/material.dart';
import 'package:cash_ctrl/core/theme/app_theme.dart';

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.dashboard_outlined, size: 80, color: AppTheme.primaryColor),
            const SizedBox(height: 16),
            Text(
              'Dashboard Coming Soon',
              style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 24),
            ),
            const SizedBox(height: 8),
            const Text('The premium finance experience is being built.'),
          ],
        ),
      ),
    );
  }
}
