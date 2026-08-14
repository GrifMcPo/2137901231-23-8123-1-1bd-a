document.addEventListener('DOMContentLoaded', () => {
    // Переключение табов
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = {
        login: document.getElementById('login'),
        register: document.getElementById('register')
    };

    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            tabs.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            Object.keys(contents).forEach(key => {
                contents[key].classList.toggle('active', key === btn.dataset.tab);
            });
        });
    });

    // Регистрация
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = document.getElementById('registerMessage');
        
        const data = {
            nick: document.getElementById('regNick').value,
            id: document.getElementById('regId').value,
            username: document.getElementById('regUsername').value,
            email: document.getElementById('regEmail').value,
            password: document.getElementById('regPassword').value
        };

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                message.className = 'message success';
                message.textContent = 'Регистрация успешна!';
                setTimeout(() => {
                    document.querySelector('[data-tab="login"]').click();
                }, 1500);
            } else {
                message.className = 'message error';
                message.textContent = result.error || 'Ошибка регистрации';
            }
        } catch (error) {
            message.className = 'message error';
            message.textContent = 'Ошибка соединения с сервером';
        }
    });

    // Вход
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = document.getElementById('loginMessage');
        
        const data = {
            login: document.getElementById('loginUsername').value,
            password: document.getElementById('loginPassword').value
        };

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                message.className = 'message success';
                message.textContent = 'Вход выполнен!';
                // Сохраняем сессию
                localStorage.setItem('session', JSON.stringify(result.user));
            } else {
                message.className = 'message error';
                message.textContent = result.error || 'Ошибка входа';
            }
        } catch (error) {
            message.className = 'message error';
            message.textContent = 'Ошибка соединения с сервером';
        }
    });
});
