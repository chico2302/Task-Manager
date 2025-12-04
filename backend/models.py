import mysql.connector
import traceback
from mysql.connector import Error
from config import Config
from datetime import datetime

config = Config()

# conectador OwO
def get_db_connection():
    """Cria uma conexão com o BD >**<"""
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except mysql.connector.Error as e:
        print("Erro ao conectar ao MySQL", e)
        return None

# testador xD
def test_connection():
    """Testa a conexão com o BD"""
    try:
        connection = get_db_connection()
        if connection:
            print("Conectado ao BD")
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            print("Conectado ao BD com sucesso!")
            return True
        else:
            print("Problema na conexão")
            return False
    except Exception as e:
        print(f"Erro no teste de conexão: {e}")
        return  False

# formatador de horarioss
def format_datetime(dt):
    """converte datetimes para strings ou retorna bulhufas"""
    if dt is None:
        return None
    try:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(dt)

# formatador de tarefitas
def format_tarefa(tarefa_dict):
    """formata uma tarefa pra json usando a funcao anterior pra formatar datinhas"""
    if not tarefa_dict:
        return None

    return {
        'id': tarefa_dict.get('id'),
        'titulo': tarefa_dict.get('titulo', ''),
        'descricao': tarefa_dict.get('descricao', '') or '',
        'completo': bool(tarefa_dict.get('completo', False)),
        'prioridade': tarefa_dict.get('prioridade', 'media'),
        'criado': format_datetime(tarefa_dict.get('criado')),
        'atualizado': format_datetime(tarefa_dict.get('atualizado'))
    }


class TarefaModel:
    @staticmethod
    def get_all(completo=None):
        """Busca todas as tarefas ou filtra elas"""
        connection = get_db_connection()
        if not connection:
            print("Sem conexão ao BD")
            return []

        try:
            cursor = connection.cursor(dictionary=True)

            if completo is None:
                #comando do sql arrasante
                query = "SELECT * FROM tarefas ORDER BY criado DESC"
                cursor.execute(query)
            else:
                query = "SELECT * FROM tarefas WHERE completo = %s ORDER BY criado DESC"
                cursor.execute(query, (completo,))


            tarefas = cursor.fetchall()
            print(f"Foram encontradas {len(tarefas)} tarefas no banco de dados")

            cursor.close()
            connection.close()

            # transformando essas bombas em string
            tarefas_formatadas = []
            for tarefa in tarefas:
                tarefa_formatada = format_tarefa(tarefa)
                if tarefa_formatada:
                    tarefas_formatadas.append(tarefa_formatada)

            print(f"Retornando {len(tarefas_formatadas)} tarefas formatadas")
            return tarefas_formatadas


        except Exception as e:
            print(f"Erro em TarefaModel.get_all: {e}")
            import traceback
            traceback.print_exc()
            if connection:
                connection.close()
            return []

    @staticmethod
    def create(titulo, descricao="", prioridade='media'):
        """Criador de novas tarefas"""
        connection = get_db_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)

            query= """
                INSERT INTO tarefas (titulo, descricao, prioridade)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (titulo, descricao, prioridade))
            connection.commit()

            tarefa_id = cursor.lastrowid
            print(f"Tarefa criada com o ID: {tarefa_id}")

            # buscando tarefas >__<
            cursor.execute("SELECT * FROM tarefas WHERE id = %s", (tarefa_id,))
            nova_tarefa = cursor.fetchone()

            cursor.close()
            connection.close()

            return format_tarefa(nova_tarefa) if nova_tarefa else None

        except Error as e:
            print("Erro ao criar tarefa", e)
            import traceback
            traceback.print_exc()
            if connection:
                connection.callback()
                connection.close()
            return None

    @staticmethod
    def update(tarefa_id, titulo, descricao="", completo=False, prioridade='media'):
        """Atualiza 1 tarefinha"""
        connection = get_db_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)

            query = """
            UPDATE tarefas
            set titulo = %s, descricao = %s, completo = %s, prioridade = %s,
                atualizado = CURRENT_TIMESTAMP()
            WHERE id = %s
            """
            cursor.execute(query, (titulo, descricao, completo, prioridade, tarefa_id))
            connection.commit()

            if cursor.rowcount == 0:
                print(f"Nenhuma tarefa encontrada com ID: {tarefa_id}")
                cursor.close()
                connection.close()
                return None # pq nao achou || nao tem

            print(f"Tarefa {tarefa_id} atualizado")

            # cata a atualizada
            cursor.execute("SELECT * FROM tarefas WHERE id = %s", (tarefa_id,))
            tarefa_atualizada = cursor.fetchone()

            return format_tarefa(tarefa_atualizada) if tarefa_atualizada else None

        except Exception as e:
            print(f"Erro ao atualizar tarefa: {e}")
            import traceback
            traceback.print_exc()
            if connection:
                connection.rollback()
                connection.close()
            return None

    @staticmethod
    def delete(tarefa_id):
        """removedor de tarefas `^_^´"""
        connection = get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            query = "DELETE FROM tarefas WHERE id = %s"
            cursor.execute(query, (tarefa_id,))
            connection.commit()

            linhas_afetadas = cursor.rowcount
            cursor.close()
            connection.close()

            if linhas_afetadas > 0:
                print(f"Tarefa {tarefa_id} removido")
                return True
            else:
                print(f"Tarefa {tarefa_id} não encontrado para deletar")
                return False

        except Exception as e:
            print("Erro ao deletar tarefa", e)
            import traceback
            traceback.print_exc()
            if connection:
                connection.rollback()
                connection.close()
            return False

    @staticmethod
    def toggle_complete(tarefa_id):
        """ ^0>0^ muda o status da tarefa pelo id dela"""
        connection = get_db_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(dictionary=True)

            # verificando a quantas anda pra poder mexer direito
            cursor.execute("SELECT completo FROM tarefas WHERE id = %s",(tarefa_id,))
            resultado = cursor.fetchone()

            if not resultado:
                print(f"Tarefa {tarefa_id} não encontrada para atualizar")
                cursor.close()
                connection.close()
                return None #tarefa sumidinha||nao achadinha

            novo_estado = not bool(resultado['completo'])
            print(f"Alternando a tarefa {tarefa_id} {resultado['completo']} --> {novo_estado}")

            #atualizando o que foi achado antes pq meio q eh a funcao ne bbs
            query = """UPDATE tarefas SET completo = %s, atualizado = CURRENT_TIMESTAMP() WHERE id = %s"""
            cursor.execute(query, (novo_estado, tarefa_id))
            connection.commit()

            # indo atras dela APÓÓÓS atualizar
            cursor.execute("SELECT * FROM tarefas WHERE id = %s", (tarefa_id,))
            tarefa_atualizada = cursor.fetchone()

            cursor.close()
            connection.close()

            return format_tarefa(tarefa_atualizada) if tarefa_atualizada else None

        except Error as e:
            print("Erro ao atualizar estado da tarefa", e)
            import traceback
            traceback.print_exc()
            if connection:
                connection.rollback()
                connection.close()
            return None

    @staticmethod
    def get_by_id(tarefa_id):
        """Busca uma tarefa por ID"""
        connection = get_db_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor(Dictionary=True)
            cursor.execute("SELECT * FROM tarefas WHERE id = %s", (tarefa_id,))
            tarefa = cursor.fetchone()

            cursor.close()
            connection.close()

            return format_tarefa(tarefa) if tarefa else None

        except Exception as e:
            print("Erro ao buscar da tarefa", e)
            if connection:
                connection.close()
            return None
