from pwdlib import PasswordHash
import models

password_hash = PasswordHash.recommended()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def authenticate_user(user: models.User, password: str):

    if not verify_password(password, user.hashed_password):
        return False
    return user
