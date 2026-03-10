import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../domain/usecases/login_use_case.dart';
import 'login_state.dart';

class LoginViewModel extends StateNotifier<LoginState> {
  final LoginUseCase _loginUseCase;

  LoginViewModel(this._loginUseCase) : super(const LoginState.initial());

  Future<void> login(String email, String password) async {
    state = const LoginState.loading();
    
    final result = await _loginUseCase(email, password);
    
    result.fold(
      (failure) => state = LoginState.error(failure.message),
      (user) => state = LoginState.success(user),
    );
  }
}
