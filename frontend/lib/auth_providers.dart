import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cash_ctrl/core/di/injection.dart';
import 'features/auth/domain/usecases/login_use_case.dart';
import 'features/auth/presentation/view_model/login_view_model.dart';
import 'features/auth/presentation/view_model/login_state.dart';

final loginUseCaseProvider = Provider((ref) => getIt<LoginUseCase>());

final loginViewModelProvider = StateNotifierProvider.autoDispose<LoginViewModel, LoginState>((ref) {
  final loginUseCase = ref.watch(loginUseCaseProvider);
  return LoginViewModel(loginUseCase);
});
