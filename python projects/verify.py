from cryptography.fernet import Fernet
import base64

SECRET_KEY = b'3pmSNgjmiQcjqpFQPnAoc86_H24ToQoMTgW7Wd_6HHk='  # Your existing secret key
cipher = Fernet(SECRET_KEY)

activation_key = "your_actual_activation_key"  # Replace with your chosen key
encrypted_key = cipher.encrypt(activation_key.encode())  # Encrypt the activation key
encoded_key = base64.urlsafe_b64encode(encrypted_key).decode()  # Encode in base64

print("VALID_ENCRYPTED_KEY:", encoded_key)
# Z0FBQUFBQm52Z2JyTFJsYWo0Mnpnd196aVdjUWJxQWhEalg3X01tZFJpLS12VERVNkxmLUtCVGRGRnBpeElTTy02ZXJPV05DRlplUkg0OVJvVkNnd2lTcFljTERXS2NzN2Y2WWdRQUdzSzFjc29rNHcwbXdKaWc9