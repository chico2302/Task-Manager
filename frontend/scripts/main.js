document.addEventListener('DOMContentLoaded', () => {
    // configurando a API
    const API_BASE_URL = 'http://localhost:3000/api/tarefas';
    
    // ref aos elementos do DOM
    const taskInput = document.getElementById('task-input');
    const addTaskBtn = document.getElementById('add-task-btn');
    const taskList = document.getElementById('task-list');
    const filtersSection = document.querySelector('.filters-section');
    const clearAllBtn = document.getElementById('clear-all-btn');
    const taskDescription = document.getElementById('task-description');

    // Estado da aplicação
    let tasks = [];
    let currentFilter = 'all';

    /**
     * Faz requisição para a API
     */
    async function apiRequest(endpoint, options = {}) {
        try {
            let url;
        if (endpoint === '' || endpoint === '/') {
            url = API_BASE_URL; // http://localhost:3000/api/tarefas
        } else if (endpoint.startsWith('/')) {
            url = `${API_BASE_URL}${endpoint}`; // http://localhost:3000/api/tarefas/1
        } else {
            url = `${API_BASE_URL}/${endpoint}`; // http://localhost:3000/api/tarefas/1
        }
            
            console.log(`Fazendo requisição: ${options.method || 'GET'} ${url}`);
            
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            console.log(`Response status: ${response.status}`);
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            
            const result = response.status === 204 ? null : await response.json();
            console.log(`Response data:`, result);
            return result;
        } catch (error) {
            console.error('Erro na API:', error);
            alert(`Erro ao conectar com o servidor: ${error.message}`);
            throw error;
        }
    }

    /**
     * Carrega as tarefas da API
     */
    async function loadTasks() {
        try {
            console.log('Carregando tarefas da API...');
            const data = await apiRequest('');
            tasks = data || [];
            renderTasks();
            console.log(`${tasks.length} tarefas carregadas:`, tasks);
        } catch (error) {
            console.error('Erro ao carregar tarefas:', error);
            tasks = []; 
            renderTasks();
        }
    }

    /**
     * Adiciona uma nova tarefa
     */
    async function addTask() {
        const titulo = taskInput.value.trim();
        const descricao = taskDescription ? taskDescription.value.trim(): '';
        
        if (!titulo) {
            alert('Por favor, digite um título para a tarefa!');
            return;
        }
        
        try {
            console.log('Criando nova tarefa:', { titulo, descricao });
            
            const novaTarefa = await apiRequest('', {
                method: 'POST',
                body: JSON.stringify({ 
                    titulo: titulo,
                    descricao: descricao,
                    prioridade: 'media'
                })
            });
            
            console.log('Tarefa criada:', novaTarefa);
            
            // Adicionar na lista local
            tasks.unshift(novaTarefa); 
            
            // Limpar campos
            taskInput.value = '';
            if (taskDescription) taskDescription.value = '';
            
            renderTasks();
        } catch (error) {
            console.error('Erro ao adicionar tarefa:', error);
        }
    }

    /**
     * Alterna o status de conclusão de uma tarefa
     */
    async function toggleComplete(taskId) {
        try {
            console.log('Alternando status da tarefa:', taskId);
            
            const tarefaAtualizada = await apiRequest(`/${taskId}/toggle`, {
                method: 'PATCH'
            });
            
            console.log('Status atualizado:', tarefaAtualizada);
            
            // Atualizar no array local
            const index = tasks.findIndex(task => task.id == taskId);
            if (index > -1) {
                tasks[index] = tarefaAtualizada;
            }
            
            renderTasks();
        } catch (error) {
            console.error('Erro ao alternar status:', error);
        }
    }

    /**
     * Edita uma tarefa
     */
    async function editTask(taskId) {
        const task = tasks.find(t => t.id == taskId);
        if (!task) return;
        
        const novoTitulo = prompt('Editar título da tarefa:', task.titulo);
        if (novoTitulo === null) return; // cancelou!!!
        
        if (!novoTitulo.trim()) {
            alert('O título não pode ser vazio!');
            return;
        }
        
        const novaDescricao = prompt('Editar descrição da tarefa (opcional):', task.descricao || '');
        if (novaDescricao === null) return; // cancelou!!!
        
        try {
            console.log('Editando tarefa:', taskId);
            
            const tarefaAtualizada = await apiRequest(`/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify({
                    titulo: novoTitulo.trim(),
                    descricao: novaDescricao.trim(),
                    completo: task.completo,
                    prioridade: task.prioridade || 'media'
                })
            });
            
            console.log('Tarefa editada:', tarefaAtualizada);
            
            // Atualizar no array local
            const index = tasks.findIndex(t => t.id == taskId);
            if (index > -1) {
                tasks[index] = tarefaAtualizada;
            }
            
            renderTasks();
        } catch (error) {
            console.error('Erro ao editar tarefa:', error);
        }
    }

    /**
     * Remove uma tarefa
     */
    async function deleteTask(taskId) {
        if (!confirm('Tem certeza que deseja remover esta tarefa?')) return;
        
        try {
            console.log('Deletando tarefa:', taskId);
            
            await apiRequest(`/${taskId}`, { method: 'DELETE' });
            
            console.log('Tarefa deletada');
            
            // Remover do array local
            tasks = tasks.filter(task => task.id != taskId);
            renderTasks();
        } catch (error) {
            console.error('Erro ao deletar tarefa:', error);
        }
    }

    /**
     * Renderiza as tarefas na lista
     */
    function renderTasks() {
        taskList.innerHTML = '';

        const filteredTasks = tasks.filter(task => {
            if (currentFilter === 'pending') {
                return !task.completo;
            } else if (currentFilter === 'completed') {
                return task.completo;
            }
            return true;
        });

        if (filteredTasks.length === 0) {
            const noTasksMessage = document.createElement('li');
            noTasksMessage.classList.add('task-item', 'no-tasks-message');
            noTasksMessage.style.justifyContent = 'center';
            noTasksMessage.style.fontStyle = 'italic';
            noTasksMessage.style.color = 'var(--light-text-color)';
            
            if (tasks.length === 0) {
                noTasksMessage.textContent = 'Nenhuma tarefa adicionada ainda. Que tal começar uma nova?';
            } else {
                noTasksMessage.textContent = `Nenhuma tarefa ${currentFilter === 'pending' ? 'pendente' : 'concluída'} encontrada.`;
            }
            
            taskList.appendChild(noTasksMessage);
            return;
        }

        filteredTasks.forEach(task => {
            const listItem = document.createElement('li');
            listItem.classList.add('task-item');
            if (task.completo) {
                listItem.classList.add('completed');
            }
            listItem.dataset.id = task.id;

            const descriptionHTML = task.descricao ? 
                `<div class="task-description-display">${task.descricao}</div>` : '';

            listItem.innerHTML = `
                <input type="checkbox" class="task-checkbox" ${task.completo ? 'checked' : ''} aria-label="Marcar tarefa como concluída">
                <div class="task-content">
                    <div class="task-title">${task.titulo}</div>
                    ${descriptionHTML}
                </div>
                <div class="task-actions">
                    <button class="edit-btn" aria-label="Editar Tarefa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-btn" aria-label="Remover Tarefa">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            `;
            taskList.appendChild(listItem);
        });
    }

    /**
     * Define o filtro atual
     */
    function setFilter(filter) {
        currentFilter = filter;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            if (btn.dataset.filter === filter) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        renderTasks();
    }

    /**
     * Limpa todas as tarefas
     */
    async function clearAllTasks() {
        if (!confirm('Tem certeza que deseja remover TODAS as tarefas?')) return;
        
        try {
            console.log('🧹 Limpando todas as tarefas...');
            
            // Deletar uma por uma
            for (const task of tasks) {
                await apiRequest(`/${task.id}`, { method: 'DELETE' });
            }
            
            tasks = [];
            renderTasks();
            console.log('Todas as tarefas foram removidas');
        } catch (error) {
            console.error('Erro ao limpar tarefas:', error);
        }
    }

    // Event Listeners
    addTaskBtn.addEventListener('click', addTask);
    
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });

    if (taskDescription) {
        taskDescription.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) addTask();
        });
    }

    taskList.addEventListener('click', (e) => {
        const listItem = e.target.closest('.task-item');
        if (!listItem || !listItem.dataset.id) return;

        const taskId = listItem.dataset.id;

        if (e.target.classList.contains('task-checkbox')) {
            toggleComplete(taskId);
        } else if (e.target.closest('.edit-btn')) {
            editTask(taskId);
        } else if (e.target.closest('.delete-btn')) {
            deleteTask(taskId);
        }
    });

    if (filtersSection) {
        filtersSection.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                setFilter(e.target.dataset.filter);
            }
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllTasks);
    }

    // carregando tarefinhas da API ao abrir a página
    console.log('Iniciando a aplicação...');
    loadTasks();
});
