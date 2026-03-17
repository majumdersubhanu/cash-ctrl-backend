import re

def custom_postprocessing_hook(result, generator, **kwargs):
    """
    Hook to clean up operation IDs to be more human-readable.
    Example: 'api_v1_auth_login_create' -> 'login'
    """
    for path, path_obj in result.get('paths', {}).items():
        for method, operation in path_obj.items():
            # Force "Authentication" tag for all auth and registration paths
            if '/auth/' in path or '/register/' in path:
                operation['tags'] = ['Authentication']

            if 'operationId' in operation:
                old_id = operation['operationId']
                
                # Logic to simplify operation IDs
                new_id = re.sub(r'^api_v1_', '', old_id)
                new_id = new_id.replace('auth_', '')
                
                # Further simplification for common auth patterns
                if 'password_reset_confirm' in new_id:
                    new_id = 'password_reset_confirm'
                elif 'password_reset' in new_id:
                    new_id = 'password_reset'
                elif 'login' in new_id:
                    new_id = 'login'
                elif 'logout' in new_id:
                    new_id = 'logout'
                elif 'user_retrieve' in new_id:
                    new_id = 'get_user'
                elif 'user_update' in new_id:
                    new_id = 'update_user'
                elif 'phone_request_otp_create' in new_id:
                    new_id = 'request_otp'
                elif 'phone_verify_otp_create' in new_id:
                    new_id = 'verify_otp'
                elif 'registration_create' in new_id:
                    new_id = 'register_alt'
                elif 'registration_verify_email_create' in new_id:
                    new_id = 'verify_email'
                
                operation['operationId'] = new_id

    return result

def custom_preprocessing_hook(endpoints):
    """
    Hook to group all dj-rest-auth endpoints under 'Authentication'.
    """
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        # Check if it's a dj-rest-auth endpoint
        if 'auth' in path:
            # We can't easily change tags here, tags are usually in the view
            pass
        filtered.append((path, path_regex, method, callback))
    return filtered
