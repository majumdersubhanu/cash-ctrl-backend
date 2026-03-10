import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import 'package:cash_ctrl/core/di/injection.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async => getIt.init();
