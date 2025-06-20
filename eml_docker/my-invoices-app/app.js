function showAlert() {
    alert('JavaScript działa! 🎉\n\nAplikacja została załadowana z pliku EML.');
}

// Animacja ładowania
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Aplikacja załadowana z EML+Dockerfile');

    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });

    // Pokaż informację o ładowaniu
    setTimeout(() => {
        const notice = document.createElement('div');
        notice.innerHTML = '🚀 Aplikacja uruchomiona z samoekstraktującego się skryptu EML!';
        notice.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00b894;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 300px;
            animation: slideIn 0.5s ease;
        `;

        // CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(notice);

        // Usuń po 5 sekundach
        setTimeout(() => {
            notice.style.transition = 'all 0.5s ease';
            notice.style.transform = 'translateX(100%)';
            notice.style.opacity = '0';
            setTimeout(() => notice.remove(), 500);
        }, 5000);
    }, 2000);
});
