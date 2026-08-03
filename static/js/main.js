document.addEventListener('DOMContentLoaded', () => {
    const formColeta = document.getElementById('form-coleta');
    
    if (formColeta) {
        formColeta.addEventListener('submit', async function(e) {
            e.preventDefault(); // Impede o reload padrão do formulário

            const urlInput = document.getElementById('url-input').value;
            const btnSubmit = document.getElementById('btn-submit');
            const containerProgresso = document.getElementById('container-progresso');
            const barraFill = document.getElementById('barra-fill');
            const statusTexto = document.getElementById('status-texto');

            // 1. Inicia Interface de Carregamento
            btnSubmit.disabled = true;
            containerProgresso.style.display = 'block';
            
            // Passo 1: Início
            barraFill.style.width = '20%';
            statusTexto.innerText = '⚙️ Iniciando processo de coleta de sopetão...';
            statusTexto.style.color = '#007bff';

            setTimeout(() => {
                // Passo 2: Conexão
                barraFill.style.width = '50%';
                statusTexto.innerText = '🌐 Conectando com Playwright Stealth nativo...';
            }, 600);

            try {
                // Prepara os dados para envio via POST
                const formData = new FormData();
                formData.append('url', urlInput);

                // Envia a requisição assíncrona para a rota do Flask
                const response = await fetch('/coletar', {
                    method: 'POST',
                    body: formData
                });

                const resultado = await response.json();

                if (response.ok && resultado.sucesso) {
                    // Passo 3: Finalização no SQLite
                    barraFill.style.width = '90%';
                    statusTexto.innerText = '💾 Gravando HTML bruto no banco SQLite...';

                    setTimeout(() => {
                        // Passo 4: Concluído
                        barraFill.style.width = '100%';
                        statusTexto.innerText = '✅ Concluído com sucesso!';
                        statusTexto.style.color = '#28a745';

                        // Recarrega a página após 1 segundo para atualizar o histórico na tabela
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }, 400);

                } else {
                    throw new Error(resultado.erro || 'Erro ao processar coleta');
                }

            } catch (err) {
                barraFill.style.width = '100%';
                barraFill.style.background = '#dc3545';
                statusTexto.innerText = '❌ Erro: ' + err.message;
                statusTexto.style.color = '#dc3545';
                btnSubmit.disabled = false;
            }
        });
    }
});