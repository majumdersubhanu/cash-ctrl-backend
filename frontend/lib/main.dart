import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:cash_ctrl/core/di/injection.dart';
import 'package:cash_ctrl/core/theme/app_theme.dart';
import 'package:cash_ctrl/routes/router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Dependency Injection
  await configureDependencies();
  
  runApp(
    const ProviderScope(
      child: CashCtrlApp(),
    ),
  );
}

class CashCtrlApp extends ConsumerWidget {
  const CashCtrlApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'CashCtrl',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: router,
    );
  }
}
