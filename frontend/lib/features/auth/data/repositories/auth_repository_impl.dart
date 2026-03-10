import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cash_ctrl/core/error/failures.dart';
import 'package:cash_ctrl/features/auth/domain/entities/user_entity.dart';
import 'package:cash_ctrl/features/auth/domain/repositories/auth_repository.dart';
import 'package:cash_ctrl/features/auth/data/datasources/auth_remote_data_source.dart';

@LazySingleton(as: AuthRepository)
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final SharedPreferences _prefs;

  AuthRepositoryImpl(this._remoteDataSource, this._prefs);

  @override
  Future<Either<Failure, UserEntity>> login(String email, String password) async {
    try {
      final response = await _remoteDataSource.login({
        'username': email,
        'password': password,
      });
      
      await _prefs.setString('access_token', response.accessToken);
      
      final userModel = await _remoteDataSource.getMe();
      return Right(userModel.toEntity());
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        return const Left(ServerFailure('Invalid email or password'));
      }
      return Left(ServerFailure(e.message ?? 'Unknown server error'));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, UserEntity>> getCurrentUser() async {
    try {
      final userModel = await _remoteDataSource.getMe();
      return Right(userModel.toEntity());
    } on DioException catch (e) {
      return Left(ServerFailure(e.message ?? 'Unknown server error'));
    } catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }

  @override
  Future<void> logout() async {
    await _prefs.remove('access_token');
  }
}
