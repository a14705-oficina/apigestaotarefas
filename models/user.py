from con_sql_alchemy import bd
from hmac import compare_digest


class UserModel(bd.Model):
    __tablename__ = "utilizadores"

    id = bd.Column(bd.Integer, primary_key=True)
    username = bd.Column(bd.String(80), nullable=False)
    email = bd.Column(bd.String(120), unique=True, nullable=False)
    password = bd.Column(bd.String(80), nullable=False)
    tipo = bd.Column(bd.String(20), nullable=False, default="utilizador")  # admin ou utilizador

    # Relacionamento: um utilizador pode ter várias tarefas
    tarefas = bd.relationship("TarefaModel", backref="utilizador", lazy=True)

    def __init__(self, username, email, password, tipo="utilizador"):
        self.username = username
        self.email = email
        self.password = password
        self.tipo = tipo

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "tipo": self.tipo
        }

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def check_password(self, password):
        return compare_digest(self.password, password)

    def save_user(self):
        bd.session.add(self)
        bd.session.commit()

    def delete_user(self):
        bd.session.delete(self)
        bd.session.commit()
