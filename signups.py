import requests
from faker import Faker

fake = Faker()
num = 1000
url = "http://0.0.0.0:5000/signup"

for i in range(num):
    username = fake.user_name() + str(i)
    password = fake.password(length=12)  # Generates a random password with 12 characters
    email = fake.email()
    
    payload = {
        'username': username,
        'password': password,
        'email': email
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print(f"Number {i}, User {username} signed up successfully with password: {password}")
    else:
        print(f"Failed to sign up Number {i}, user {username}. Status code: {response.status_code}")

print(f"Finished signing up {num} users.")
