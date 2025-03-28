// MegaPersonal - Script para melhorar a responsividade e interatividade

document.addEventListener('DOMContentLoaded', function() {
    // Menu responsivo para mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('show');
        });
    }
    
    // Fechar alertas/flash messages
    const closeButtons = document.querySelectorAll('.close-alert, .close-flash');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.flash-message, .alert');
        flashMessages.forEach(message => {
            message.style.opacity = '0';
            setTimeout(() => message.style.display = 'none', 500);
        });
    }, 5000);
    
    // Inicializar tooltips se existirem
    if (typeof tippy !== 'undefined') {
        tippy('[data-tippy-content]');
    }
    
    // Marcar item de menu atual como ativo
    const currentUrl = window.location.pathname;
    const navLinkItems = document.querySelectorAll('.nav-links a');
    
    navLinkItems.forEach(link => {
        if (link.getAttribute('href') === currentUrl || 
            (link.getAttribute('href') !== '/' && currentUrl.includes(link.getAttribute('href')))) {
            link.classList.add('active');
        }
    });
    
    // Tabelas responsivas - adicionar data-labels para visualização mobile
    const tables = document.querySelectorAll('.table-responsive-sm table');
    tables.forEach(table => {
        const headerCells = table.querySelectorAll('thead th');
        const headerTexts = Array.from(headerCells).map(cell => cell.textContent);
        
        const bodyRows = table.querySelectorAll('tbody tr');
        bodyRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                if (headerTexts[index]) {
                    cell.setAttribute('data-label', headerTexts[index]);
                }
            });
        });
    });
    
    // Pesquisa em tabelas e listas
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        const targetId = input.dataset.target;
        const target = document.getElementById(targetId);
        
        if (target) {
            input.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const items = target.querySelectorAll('.searchable-item');
                
                items.forEach(item => {
                    const text = item.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        }
    });
    
    // Confirmar exclusões
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        });
    });
    
    // Exibir/ocultar senha em formulários
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = document.getElementById(this.dataset.target);
            if (input.type === 'password') {
                input.type = 'text';
                this.textContent = 'Ocultar';
            } else {
                input.type = 'password';
                this.textContent = 'Mostrar';
            }
        });
    });
    
    // Adicionar classe 'fade-in' aos elementos da página para animação de entrada
    const fadeElements = document.querySelectorAll('.card, .stats-card, .alert');
    fadeElements.forEach((element, index) => {
        // Adiciona delay escalonado para criar efeito cascata
        setTimeout(() => {
            element.classList.add('fade-in');
        }, 100 * index);
    });
    
    // Tabs dinâmicas
    const tabLinks = document.querySelectorAll('.tab-link');
    tabLinks.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class de todas as tabs
            tabLinks.forEach(t => t.classList.remove('active'));
            
            // Adiciona active na tab clicada
            this.classList.add('active');
            
            // Esconde todos os conteúdos de tab
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Mostra o conteúdo da tab selecionada
            const targetId = this.getAttribute('href').substring(1);
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // Inicialização de campos datepicker, se disponível
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            dateFormat: 'd/m/Y',
            locale: 'pt',
            disableMobile: false
        });
    }
    
    // Ativar máscaras para campos específicos
    if (typeof IMask !== 'undefined') {
        // Máscara para telefone
        const phoneInputs = document.querySelectorAll('.phone-mask');
        phoneInputs.forEach(input => {
            IMask(input, {
                mask: '(00) 00000-0000'
            });
        });
        
        // Máscara para CPF
        const cpfInputs = document.querySelectorAll('.cpf-mask');
        cpfInputs.forEach(input => {
            IMask(input, {
                mask: '000.000.000-00'
            });
        });
        
        // Máscara para valores monetários
        const moneyInputs = document.querySelectorAll('.money-mask');
        moneyInputs.forEach(input => {
            IMask(input, {
                mask: 'R$ num',
                blocks: {
                    num: {
                        mask: Number,
                        scale: 2,
                        radix: ',',
                        thousandsSeparator: '.',
                        padFractionalZeros: true,
                        normalizeZeros: true
                    }
                }
            });
        });
    }
});

// Função para toggle do modo escuro (se implementado)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    
    // Salva preferência no localStorage
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Carrega preferência de modo escuro ao iniciar
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Função para exibir loading spinner
function showLoading(targetId) {
    const target = document.getElementById(targetId);
    if (target) {
        target.innerHTML = '<div class="loading-container"><div class="loader"></div><p>Carregando...</p></div>';
    }
}

// Função para limpar formulário
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        
        // Reset também campos select2 se existirem
        if (typeof $ !== 'undefined' && $.fn.select2) {
            $(form).find('select').val(null).trigger('change');
        }
    }
}

// Polyfill para suporte a mais navegadores
if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
}

if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        var el = this;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}