import bcrypt

class Password:
    @staticmethod
    def make_hash(password: str) -> str:
        # Convert to bytes
        bytes = password.encode('utf-8')

        # Generate salt and hash
        salt = bcrypt.gensalt()

        hash_bytes = bcrypt.hashpw(bytes, salt)
        return hash_bytes.decode('utf-8')

    @staticmethod
    def check_hash(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
