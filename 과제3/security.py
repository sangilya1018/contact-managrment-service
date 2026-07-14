from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# TRD NFR-03 규격에 따른 pwdlib[argon2] 비밀번호 단방향 암호화 처리
password_context = PasswordHash((Argon2Hasher(),))

def get_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)