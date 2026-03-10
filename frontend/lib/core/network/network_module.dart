import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:cash_ctrl/core/logging/logger.dart';
import 'package:cash_ctrl/core/network/auth_interceptor.dart';
import 'package:cash_ctrl/features/auth/data/datasources/auth_remote_data_source.dart';

@module
abstract class NetworkModule {
  @lazySingleton
  Dio dio(AuthInterceptor authInterceptor) {
    final dio = Dio(
      BaseOptions(
        baseUrl: 'http://127.0.0.1:8000',
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    dio.interceptors.addAll([
      authInterceptor,
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (o) => logger.d(o),
      ),
    ]);

    return dio;
  }

  @lazySingleton
  AuthRemoteDataSource provideAuthRemoteDataSource(Dio dio) => AuthRemoteDataSource(dio);
}
