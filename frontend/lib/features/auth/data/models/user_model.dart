import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/user_entity.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    required String id,
    required String email,
    @JsonKey(name: 'is_active') required bool isActive,
    @JsonKey(name: 'is_verified') required bool isVerified,
    @JsonKey(name: 'vouch_score') required double vouchScore,
    @JsonKey(name: 'is_mfa_enabled') required bool isMfaEnabled,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);

  const UserModel._();

  UserEntity toEntity() => UserEntity(
        id: id,
        email: email,
        isActive: isActive,
        isVerified: isVerified,
        vouchScore: vouchScore,
        isMfaEnabled: isMfaEnabled,
      );
}
