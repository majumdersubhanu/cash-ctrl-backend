from rest_framework import serializers
from .models import KYCProfile, KYCDocument

class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ('id', 'document_type', 'document_file', 'is_verified', 'uploaded_at')
        read_only_fields = ('id', 'is_verified', 'uploaded_at')

class KYCProfileSerializer(serializers.ModelSerializer):
    documents = KYCDocumentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = KYCProfile
        fields = (
            'id', 'status', 'status_display', 'first_name', 'last_name', 
            'date_of_birth', 'address', 'verified_at', 'documents', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'verified_at', 'created_at', 'updated_at')
