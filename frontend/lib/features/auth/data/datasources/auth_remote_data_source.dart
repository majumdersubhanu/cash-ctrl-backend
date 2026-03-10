import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import 'package:injectable/injectable.dart';
import '../models/login_request_model.dart';
import '../models/login_response_model.dart';
import '../models/user_model.dart';

part 'auth_remote_data_source.g.dart';

@RestApi()
abstract class AuthRemoteDataSource {
  factory AuthRemoteDataSource(Dio dio) = _AuthRemoteDataSource;

  @POST('/api/v1/auth/jwt/login')
  @FormUrlEncoded()
  Future<LoginResponseModel> login(@Body() Map<String, dynamic> body);

  @GET('/api/v1/users/me')
  Future<UserModel> getMe();
}
