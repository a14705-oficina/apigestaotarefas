from con_sql_alchemy import bd


class TarefaModel(bd.Model):
    __tablename__ = "tarefas"

    id = bd.Column(bd.Integer, primary_key=True)
    titulo = bd.Column(bd.String(100), nullable=False)
    descricao = bd.Column(bd.Text, nullable=True)
    estado = bd.Column(bd.String(20), nullable=False, default="Pendente")  # Pendente, Em curso, Concluída
    user_id = bd.Column(bd.Integer, bd.ForeignKey("utilizadores.id"), nullable=False)

    def __init__(self, titulo, descricao, estado, user_id):
        self.titulo = titulo
        self.descricao = descricao
        self.estado = estado
        self.user_id = user_id

    def json(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "estado": self.estado,
            "user_id": self.user_id
        }

    @classmethod
    def find_by_id(cls, tarefa_id):
        return cls.query.filter_by(id=tarefa_id).first()

    @classmethod
    def find_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_tarefa(self):
        bd.session.add(self)
        bd.session.commit()

    def update_tarefa(self, titulo, descricao, estado):
        self.titulo = titulo
        self.descricao = descricao
        self.estado = estado

    def delete_tarefa(self):
        bd.session.delete(self)
        bd.session.commit()
