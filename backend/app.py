from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import TarefaModel, test_connection
from datetime import datetime

# criando o Flask e tals
app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

config = Config()


# testando a rotinha >_<
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'mensagem': 'API TODO em Python funcionando!',
        'timestamp': str(datetime.now()),
        'versao': '1.0.0'
    })


# listando as tarefas nee
@app.route('/api/tarefas', methods=['GET'])
def get_tarefas():
    try:
        completo_param = request.args.get('completo')
        completo = None

        if completo_param is not None:
            completo = completo_param.lower() == 'true'

        tarefas = TarefaModel.get_all(completo)
        return jsonify(tarefas)

    except Exception as e:
        print(f"Erro em get_tarefas: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


# criando uma tarefinha
@app.route('/api/tarefas', methods=['POST'])
def create_tarefa():
    try:
        data = request.get_json()
        print(f"📥 Dados recebidos para criar: {data}")

        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        titulo = data.get('titulo', '').strip()
        descricao = data.get('descricao', '').strip()
        prioridade = data.get('prioridade', 'media')

        if not titulo:
            return jsonify({'erro': 'Título é obrigatório'}), 400

        nova_tarefa = TarefaModel.create(titulo, descricao, prioridade)

        if nova_tarefa:
            print(f"Tarefa criada: {nova_tarefa}")
            return jsonify(nova_tarefa), 201
        else:
            return jsonify({'erro': 'Erro ao criar tarefa'}), 500

    except Exception as e:
        print(f"Erro em create_tarefa: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


# atualizar uma tarefa =*
@app.route('/api/tarefas/<int:tarefa_id>', methods=['PUT'])
def update_tarefa(tarefa_id):
    try:
        data = request.get_json()
        print(f"📥 Dados recebidos para atualizar tarefa {tarefa_id}: {data}")

        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        titulo = data.get('titulo', '').strip()
        descricao = data.get('descricao', '').strip()
        completo = data.get('completo', False)
        prioridade = data.get('prioridade', 'media')

        if not titulo:
            return jsonify({'erro': 'Título é obrigatório'}), 400

        tarefa_atualizada = TarefaModel.update(tarefa_id, titulo, descricao, completo, prioridade)

        if tarefa_atualizada:
            print(f"Tarefa {tarefa_id} atualizada: {tarefa_atualizada}")
            return jsonify(tarefa_atualizada)
        else:
            print(f"Tarefa {tarefa_id} não encontrada")
            return jsonify({'erro': 'Tarefa não encontrada'}), 404

    except Exception as e:
        print(f"Erro em update_tarefa: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


# deletar uma tarefa o.O
@app.route('/api/tarefas/<int:tarefa_id>', methods=['DELETE'])
def delete_tarefa(tarefa_id):
    try:
        print(f"🗑️ Tentando deletar tarefa {tarefa_id}")

        sucesso = TarefaModel.delete(tarefa_id)

        if sucesso:
            print(f"Tarefa {tarefa_id} deletada com sucesso")
            return '', 204
        else:
            print(f"Tarefa {tarefa_id} não encontrada para deletar")
            return jsonify({'erro': 'Tarefa não encontrada'}), 404

    except Exception as e:
        print(f"Erro em delete_tarefa: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


# transicionando ( o status !! )
@app.route('/api/tarefas/<int:tarefa_id>/toggle', methods=['PATCH'])
def toggle_tarefa(tarefa_id):
    try:
        print(f"🔄 Tentando alternar status da tarefa {tarefa_id}")

        tarefa_atualizada = TarefaModel.toggle_complete(tarefa_id)

        if tarefa_atualizada:
            print(f"Status da tarefa {tarefa_id} alternado: {tarefa_atualizada}")
            return jsonify(tarefa_atualizada)
        else:
            print(f"Tarefa {tarefa_id} não encontrada para alternar")
            return jsonify({'erro': 'Tarefa não encontrada'}), 404

    except Exception as e:
        print(f"Erro em toggle_tarefa: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


# procurar tarefa atraves do ID
@app.route('/api/tarefas/<int:tarefa_id>', methods=['GET'])
def get_tarefa_by_id(tarefa_id):
    try:
        print(f"Buscando tarefa {tarefa_id}")

        tarefa = TarefaModel.get_by_id(tarefa_id)

        if tarefa:
            return jsonify(tarefa)
        else:
            return jsonify({'erro': 'Tarefa não encontrada'}), 404

    except Exception as e:
        print(f"Erro em get_tarefa_by_id: {e}")
        return jsonify({'erro': 'Erro interno do servidor'}), 500


# rota de teste do banco
@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        print("DEBUG: Testando conexão com banco")

        from models import get_db_connection
        connection = get_db_connection()

        if not connection:
            return jsonify({'erro': 'Não foi possível conectar ao banco'}), 500

        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM tarefas")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'Conexão OK',
            'total_tarefas': result[0] if result else 0
        })

    except Exception as e:
        print(f"Erro no teste do banco: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': f'Erro no banco: {str(e)}'}), 500


# tratando o erro 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({'erro': 'Endpoint não encontrado'}), 404


# tratando o erro 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'erro': 'Erro interno do servidor'}), 500


# tratar requisições -- OPTIONS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,PATCH,OPTIONS")
        return response


if __name__ == '__main__':
    print("Iniciando servidor (clocking the tea)...")
    print(f"Servidor rodará em: http://localhost:{config.PORT}")

    # testando a conexão com o BD
    if test_connection():
        print("Servidor pronto para receber requisições!")
        app.run(debug=config.DEBUG, port=config.PORT, host='0.0.0.0')
    else:
        print("Não foi possível conectar ao banco de dados. Verifique as configurações.")
