// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format width=80

// **************************************************************************
// InjectableConfigGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:cash_ctrl/core/di/storage_module.dart' as _i1062;
import 'package:cash_ctrl/core/network/auth_interceptor.dart' as _i980;
import 'package:cash_ctrl/core/network/network_module.dart' as _i756;
import 'package:cash_ctrl/features/auth/data/datasources/auth_remote_data_source.dart'
    as _i1023;
import 'package:cash_ctrl/features/auth/data/repositories/auth_repository_impl.dart'
    as _i381;
import 'package:cash_ctrl/features/auth/domain/repositories/auth_repository.dart'
    as _i836;
import 'package:cash_ctrl/features/auth/domain/usecases/login_use_case.dart'
    as _i951;
import 'package:dio/dio.dart' as _i361;
import 'package:get_it/get_it.dart' as _i174;
import 'package:injectable/injectable.dart' as _i526;
import 'package:shared_preferences/shared_preferences.dart' as _i460;

extension GetItInjectableX on _i174.GetIt {
  // initializes the registration of main-scope dependencies inside of GetIt
  Future<_i174.GetIt> init({
    String? environment,
    _i526.EnvironmentFilter? environmentFilter,
  }) async {
    final gh = _i526.GetItHelper(this, environment, environmentFilter);
    final storageModule = _$StorageModule();
    final networkModule = _$NetworkModule();
    await gh.factoryAsync<_i460.SharedPreferences>(
      () => storageModule.prefs,
      preResolve: true,
    );
    gh.lazySingleton<_i980.AuthInterceptor>(
      () => _i980.AuthInterceptor(gh<_i460.SharedPreferences>()),
    );
    gh.lazySingleton<_i361.Dio>(
      () => networkModule.dio(gh<_i980.AuthInterceptor>()),
    );
    gh.lazySingleton<_i1023.AuthRemoteDataSource>(
      () => networkModule.provideAuthRemoteDataSource(gh<_i361.Dio>()),
    );
    gh.lazySingleton<_i836.AuthRepository>(
      () => _i381.AuthRepositoryImpl(
        gh<_i1023.AuthRemoteDataSource>(),
        gh<_i460.SharedPreferences>(),
      ),
    );
    gh.lazySingleton<_i951.LoginUseCase>(
      () => _i951.LoginUseCase(gh<_i836.AuthRepository>()),
    );
    return this;
  }
}

class _$StorageModule extends _i1062.StorageModule {}

class _$NetworkModule extends _i756.NetworkModule {}
