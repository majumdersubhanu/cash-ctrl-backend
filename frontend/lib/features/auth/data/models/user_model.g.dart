// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UserModel _$UserModelFromJson(Map<String, dynamic> json) => _UserModel(
  id: json['id'] as String,
  email: json['email'] as String,
  isActive: json['is_active'] as bool,
  isVerified: json['is_verified'] as bool,
  vouchScore: (json['vouch_score'] as num).toDouble(),
  isMfaEnabled: json['is_mfa_enabled'] as bool,
);

Map<String, dynamic> _$UserModelToJson(_UserModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'is_active': instance.isActive,
      'is_verified': instance.isVerified,
      'vouch_score': instance.vouchScore,
      'is_mfa_enabled': instance.isMfaEnabled,
    };
