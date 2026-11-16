from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.tarefa import TarefaModel
from models.user import UserModel


class Tarefas(Resource):
    """Listar todas as tarefas (ou só as do utilizador) e criar nova tarefa"""
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("titulo", type=str, required=True, help="O título da tarefa é obrigatório")
    argumentos.add_argument("descricao", type=str, required=False, help="Descrição da tarefa")
    argumentos.add_argument("estado", type=str, required=False, default="Pendente",
                            help="Estado: Pendente, Em curso ou Concluída")

    @jwt_required()
    def get(self):
        claims = get_jwt()
        user_id = int(get_jwt_identity())
        tipo = claims.get("tipo", "utilizador")

        if tipo == "admin":
            tarefas = TarefaModel.find_all()
        else:
            tarefas = TarefaModel.find_by_user(user_id)

        return {"tarefas": [t.json() for t in tarefas]}, 200

    @jwt_required()
    def post(self):
        dados = Tarefas.argumentos.parse_args()
        user_id = int(get_jwt_identity())

        # Validar estado
        estados_validos = ["Pendente", "Em curso", "Concluída"]
        estado = dados.get("estado") or "Pendente"
        if estado not in estados_validos:
            return {"mensagem": "Estado inválido. Use: Pendente, Em curso ou Concluída."}, 400

        nova_tarefa = TarefaModel(
            titulo=dados["titulo"],
            descricao=dados.get("descricao") or "",
            estado=estado,
            user_id=user_id
        )

        try:
            nova_tarefa.save_tarefa()
            return nova_tarefa.json(), 201
        except Exception:
            return {"mensagem": "Erro interno do servidor."}, 500


class Tarefa(Resource):
    """Consultar, alterar ou eliminar uma tarefa específica"""
    argumentos = reqparse.RequestParser()
    argumentos.add_argument("titulo", type=str, required=False)
    argumentos.add_argument("descricao", type=str, required=False)
    argumentos.add_argument("estado", type=str, required=False)

    @jwt_required()
    def get(self, tarefa_id):
        claims = get_jwt()
        user_id = int(get_jwt_identity())
        tipo = claims.get("tipo", "utilizador")

        tarefa = TarefaModel.find_by_id(tarefa_id)
        if not tarefa:
            return {"mensagem": "Tarefa não encontrada."}, 404

        # Utilizador comum só pode ver as próprias tarefas
        if tipo != "admin" and tarefa.user_id != user_id:
            return {"mensagem": "Sem permissões para consultar esta tarefa."}, 403

        return tarefa.json(), 200

    @jwt_required()
    def put(self, tarefa_id):
        claims = get_jwt()
        user_id = int(get_jwt_identity())
        tipo = claims.get("tipo", "utilizador")

        tarefa = TarefaModel.find_by_id(tarefa_id)
        if not tarefa:
            return {"mensagem": "Tarefa não encontrada."}, 404

        # Utilizador comum só pode alterar as próprias tarefas
        if tipo != "admin" and tarefa.user_id != user_id:
            return {"mensagem": "Sem permissões para alterar esta tarefa."}, 403

        dados = Tarefa.argumentos.parse_args()

        # Atualizar apenas os campos fornecidos
        titulo = dados.get("titulo") if dados.get("titulo") is not None else tarefa.titulo
        descricao = dados.get("descricao") if dados.get("descricao") is not None else tarefa.descricao
        estado = dados.get("estado") if dados.get("estado") is not None else tarefa.estado

        estados_validos = ["Pendente", "Em curso", "Concluída"]
        if estado not in estados_validos:
            return {"mensagem": "Estado inválido. Use: Pendente, Em curso ou Concluída."}, 400

        try:
            tarefa.update_tarefa(titulo, descricao, estado)
            tarefa.save_tarefa()
            return tarefa.json(), 200
        except Exception:
            return {"mensagem": "Erro interno do servidor."}, 500

    @jwt_required()
    def delete(self, tarefa_id):
        claims = get_jwt()
        user_id = int(get_jwt_identity())
        tipo = claims.get("tipo", "utilizador")

        tarefa = TarefaModel.find_by_id(tarefa_id)
        if not tarefa:
            return {"mensagem": "Tarefa não encontrada."}, 404

        # Utilizador comum só pode eliminar as próprias tarefas
        if tipo != "admin" and tarefa.user_id != user_id:
            return {"mensagem": "Sem permissões para eliminar esta tarefa."}, 403

        try:
            tarefa.delete_tarefa()
            return {"mensagem": "Tarefa eliminada com sucesso."}, 200
        except Exception:
            return {"mensagem": "Erro interno do servidor."}, 500
