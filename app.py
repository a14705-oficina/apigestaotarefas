# Inicio da aplicação (app.py)
from flask import Flask
from flask_restful import Api
from resources.tarefa import Tarefas, Tarefa
from resources.user import UserRegister, UserLogin, UserLogout
from con_sql_alchemy import bd
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from datetime import timedelta
from models.user import UserModel

# NOTA IMPORTANTE: antes de correr o programa temos de entrar no ambiente virtual
# (se ainda não estivermos) ". venv/bin/activate"
# depois podemos iniciar o servidor "python app.py"

app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

# Configurações
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "a_minha_chave_secreta_longa_e_intransmissivel"
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)


@jwt.token_in_blocklist_loader
def verifica_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BLOCKLIST


@jwt.revoked_token_loader
def token_invalido(jwt_header, jwt_payload):
    return {"mensagem": "Logout efetuado! Faça login para aceder novamente!"}, 401


# Rotas (endpoints)
api.add_resource(UserRegister, "/registo")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(Tarefas, "/tarefas")
api.add_resource(Tarefa, "/tarefas/<int:tarefa_id>")


def criar_admin_inicial():
    """Cria um utilizador admin se ainda não existir nenhum."""
    admin = UserModel.find_by_email("admin@escola.pt")
    if not admin:
        admin = UserModel(
            username="admin",
            email="admin@escola.pt",
            password="admin123",
            tipo="admin"
        )
        admin.save_user()
        print("Utilizador admin criado: admin@escola.pt / admin123")


if __name__ == "__main__":
    bd.init_app(app)
    with app.app_context():
        bd.create_all()  # Cria as tabelas automaticamente
        criar_admin_inicial()
    app.run(debug=True)
