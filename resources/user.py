from flask_restful import Resource, reqparse
from models.user import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from blocklist import BLOCKLIST


class UserRegister(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("username", type=str, required=True, help="O username é obrigatório")
    argumentos.add_argument("email", type=str, required=True, help="O email é obrigatório")
    argumentos.add_argument("password", type=str, required=True, help="A password é obrigatória")

    def post(self):
        dados = UserRegister.argumentos.parse_args()

        # Não permitir emails já existentes
        if UserModel.find_by_email(dados["email"]):
            return {"mensagem": "Já existe um utilizador com este email."}, 400

        # Todos os novos registos recebem automaticamente o tipo "utilizador"
        # Não é possível escolher o tipo admin através do registo
        novo_utilizador = UserModel(
            username=dados["username"],
            email=dados["email"],
            password=dados["password"],
            tipo="utilizador"
        )

        try:
            novo_utilizador.save_user()
            return {"mensagem": "Utilizador criado com sucesso."}, 201
        except Exception:
            return {"mensagem": "Erro interno do servidor."}, 500


class UserLogin(Resource):
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("email", type=str, required=True, help="O email é obrigatório")
    argumentos.add_argument("password", type=str, required=True, help="A password é obrigatória")

    def post(self):
        dados = UserLogin.argumentos.parse_args()
        user = UserModel.find_by_email(dados["email"])

        if user and user.check_password(dados["password"]):
            # Token com identity = id do utilizador e claims adicionais com o tipo
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"tipo": user.tipo, "username": user.username}
            )
            return {
                "access_token": access_token,
                "mensagem": "Login efetuado com sucesso.",
                "tipo": user.tipo,
                "username": user.username
            }, 200

        return {"mensagem": "Email ou password incorretos."}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"mensagem": "Logout efetuado com sucesso!"}, 200
