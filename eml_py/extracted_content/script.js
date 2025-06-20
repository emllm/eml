// Universal JavaScript - Cross-platform compatible
// Supports: Windows, macOS, Linux browsers

class UniversalDashboard {
    constructor() {
        this.invoices = [];
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.detectPlatform();
        this.loadInvoiceData();
        this.setupEventListeners();
        this.animateOnLoad();
        this.showWelcomeMessage();
    }

    detectPlatform() {
        const platform = this.getPlatform();
        const indicator = document.getElementById('platformIndicator');
        const platformName = document.getElementById('platformName');
        const platformIcon = document.getElementById('platformIcon');

        const platforms = {
            'windows': { icon: '🪟', name: 'Windows' },
            'macos': { icon: '🍎', name: 'macOS' },
            'linux': { icon: '🐧', name: 'Linux' },
            'android': { icon: '🤖', name: 'Android' },
            'ios': { icon: '📱', name: 'iOS' },
            'unknown': { icon: '🌍', name: 'Universal' }
        };

        const detected = platforms[platform] || platforms.unknown;
        platformIcon.textContent = detected.icon;
        platformName.textContent = detected.name;

        console.log(`🌍 Platform detected: ${detected.name}`);
    }

    getPlatform() {
        const userAgent = navigator.userAgent.toLowerCase();
        const platform = navigator.platform.toLowerCase();

        if (userAgent.includes('win') || platform.includes('win')) return 'windows';
        if (userAgent.includes('mac') || platform.includes('mac')) return 'macos';
        if (userAgent.includes('linux') || platform.includes('linux')) return 'linux';
        if (userAgent.includes('android')) return 'android';
        if (userAgent.includes('iphone') || userAgent.includes('ipad')) return 'ios';

        return 'unknown';
    }

    loadInvoiceData() {
        // Symulacja danych faktur
        this.invoices = [
            {
                id: '2025/05/001',
                company: 'Firma ABC Sp. z o.o.',
                description: 'Usługi IT - maj 2025',
                amount: 2500,
                status: 'paid',
                date: '2025-05-15',
                payment: 'Przelew'
            },
            {
                id: '2025/05/002', 
                company: 'XYZ Solutions',
                description: 'Konsultacje - maj 2025',
                amount: 1200,
                status: 'pending',
                date: '2025-05-20',
                payment: '5 dni'
            },
            {
                id: '2025/05/003',
                company: 'Tech Innovators Ltd',
                description: 'Rozwój aplikacji',
                amount: 3200,
                status: 'paid',
                date: '2025-05-10',
                payment: 'BLIK'
            },
            {
                id: '2025/05/004',
                company: 'Digital Marketing Pro',
                description: 'Kampania reklamowa',
                amount: 1800,
                status: 'pending',
                date: '2025-05-25',
                payment: '2 dni'
            },
            {
                id: '2025/05/005',
                company: 'Cloud Services Inc',
                description: 'Infrastruktura chmurowa',
                amount: 4200,
                status: 'paid',
                date: '2025-05-08',
                payment: 'Przelew'
            }
        ];

        this.updateStatistics();
    }

    updateStatistics() {
        const totalAmount = this.invoices.reduce((sum, inv) => sum + inv.amount, 0);
        const paidInvoices = this.invoices.filter(inv => inv.status == 'paid');
        const pendingInvoices = this.invoices.filter(inv => inv.status == 'pending');

        document.getElementById('totalAmount').textContent = 
            `${totalAmount.toLocaleString()} PLN`;
        document.getElementById('paidCount').textContent = 
            `${paidInvoices.length}/${this.invoices.length}`;
        document.getElementById('pendingCount').textContent = 
            pendingInvoices.length.toString();

        // Update progress bar
        const progressPercentage = Math.round((paidInvoices.length / this.invoices.length) * 100);
        const progressFill = document.querySelector('.progress-fill');
        const percentageSpan = document.querySelector('.percentage');

        if (progressFill && percentageSpan) {
            progressFill.style.width = `${progressPercentage}%`;
            percentageSpan.textContent = `${progressPercentage}%`;
        }
    }

    setupEventListeners() {
        // Platform-specific keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            const isMac = this.getPlatform() == 'macos';
            const cmdKey = isMac ? e.metaKey : e.ctrlKey;

            if (cmdKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.showAll();
                        break;
                    case '2':
                        e.preventDefault();
                        this.filterByStatus('paid');
                        break;
                    case '3':
                        e.preventDefault();
                        this.filterByStatus('pending');
                        break;
                    case 'i':
                        e.preventDefault();
                        this.showStats();
                        break;
                }
            }
        });

        // Touch/click handlers for mobile
        if ('ontouchstart' in window) {
            this.setupTouchHandlers();
        }
    }

    setupTouchHandlers() {
        const cards = document.querySelectorAll('.invoice-card');
        cards.forEach(card => {
            card.addEventListener('touchstart', (e) => {
                card.style.transform = 'scale(0.98)';
            });

            card.addEventListener('touchend', (e) => {
                card.style.transform = '';
            });
        });
    }

    showAll() {
        const cards = document.querySelectorAll('.invoice-card');
        cards.forEach(card => {
            card.style.display = 'block';
            card.classList.add('animate-fade-in');
        });
        this.currentFilter = 'all';
        this.updateFilterButtons();
    }

    filterByStatus(status) {
        const cards = document.querySelectorAll('.invoice-card');
        cards.forEach(card => {
            if (card.dataset.status == status) {
                card.style.display = 'block';
                card.classList.add('animate-slide-in');
            } else {
                card.style.display = 'none';
            }
        });
        this.currentFilter = status;
        this.updateFilterButtons();
    }

    updateFilterButtons() {
        const buttons = document.querySelectorAll('nav button');
        buttons.forEach(btn => btn.classList.remove('active'));

        // Add visual feedback for active filter
        const activeButton = document.querySelector(`button[onclick*="${this.currentFilter}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }

    showStats() {
        const stats = this.calculateDetailedStats();
        this.showNotification('Statystyki', JSON.stringify(stats, null, 2));
    }

    calculateDetailedStats() {
        const paid = this.invoices.filter(inv => inv.status == 'paid');
        const pending = this.invoices.filter(inv => inv.status == 'pending');

        return {
            total_invoices: this.invoices.length,
            paid_invoices: paid.length,
            pending_invoices: pending.length,
            total_amount: this.invoices.reduce((sum, inv) => sum + inv.amount, 0),
            paid_amount: paid.reduce((sum, inv) => sum + inv.amount, 0),
            pending_amount: pending.reduce((sum, inv) => sum + inv.amount, 0),
            average_invoice: Math.round(this.invoices.reduce((sum, inv) => sum + inv.amount, 0) / this.invoices.length)
        };
    }

    showNotification(title, message) {
        // Universal notification system
        if ('Notification' in window && Notification.permission == 'granted') {
            new Notification(title, { body: message });
        } else if ('Notification' in window && Notification.permission != 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission == 'granted') {
                    new Notification(title, { body: message });
                }
            });
        } else {
            // Fallback: console log or custom modal
            console.log(`📱 ${title}: ${message}`);
            this.showCustomNotification(title, message);
        }
    }

    showCustomNotification(title, message) {
        // Create custom notification element
        const notification = document.createElement('div');
        notification.className = 'custom-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <h4>${title}</h4>
                <p>${message}</p>
                <button onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            padding: 20px;
            max-width: 300px;
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    animateOnLoad() {
        // Staggered animation for cards
        const cards = document.querySelectorAll('.invoice-card');
        const statCards = document.querySelectorAll('.stat-card');

        // Animate stats first
        statCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';

            setTimeout(() => {
                card.style.transition = 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Then animate invoice cards
        setTimeout(() => {
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';

                setTimeout(() => {
                    card.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 120);
            });
        }, 400);
    }

    showWelcomeMessage() {
        setTimeout(() => {
            const platform = this.getPlatform();
            const platformNames = {
                'windows': 'Windows',
                'macos': 'macOS', 
                'linux': 'Linux',
                'android': 'Android',
                'ios': 'iOS',
                'unknown': 'Universal Platform'
            };

            const message = `Witaj w Universal Dashboard!\nPlatforma: ${platformNames[platform] || 'Universal'}\nWszystko działa poprawnie! 🎉`;

            console.log('🎯 Universal EML WebApp loaded successfully');
            console.log(`📱 Platform: ${platformNames[platform] || 'Universal'}`);
            console.log('🌍 Cross-platform compatibility: ✅');

            // Show welcome notification
            this.showNotification('Universal Dashboard', 'Aplikacja załadowana pomyślnie!');

        }, 1500);
    }
}

// Global functions for button callbacks
function showAll() {
    window.dashboard.showAll();
}

function filterByStatus(status) {
    window.dashboard.filterByStatus(status);
}

function showStats() {
    window.dashboard.showStats();
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new UniversalDashboard();

    console.log('🌍 Universal EML WebApp - Ready for all platforms!');
    console.log('🎯 Commands available: showAll(), filterByStatus(), showStats()');
    console.log('⌨️  Keyboard shortcuts: Ctrl/Cmd + 1,2,3,i');
});

// Service Worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Only register if we're not in file:// protocol
        if (location.protocol != 'file:') {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('SW registered'))
                .catch(error => console.log('SW registration failed'));
        }
    });
}
