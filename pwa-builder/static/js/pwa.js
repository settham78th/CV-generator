// PWA Installation and Management
let deferredPrompt;

// Install button
const installButton = document.createElement('button');
installButton.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 25px;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    cursor: pointer;
    z-index: 1000;
    display: none;
    transition: all 0.3s ease;
`;
installButton.innerHTML = '<i class="fas fa-download me-2"></i>Zainstaluj aplikację';
installButton.id = 'install-pwa-btn';
document.body.appendChild(installButton);

// Show install button when PWA can be installed
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallButton();
});

function showInstallButton() {
    installButton.style.display = 'block';
    installButton.addEventListener('click', installApp);
}

function installApp() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('PWA installed');
                hideInstallButton();
            }
            deferredPrompt = null;
        });
    }
}

function hideInstallButton() {
    installButton.style.display = 'none';
}

// Handle app installation
window.addEventListener('appinstalled', (evt) => {
    console.log('PWA was installed');
    hideInstallButton();
    showNotification('Aplikacja została zainstalowana!', 'success');
});

// Check for updates
let updateAvailable = false;

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (updateAvailable) {
            showUpdateNotification();
        }
    });

    navigator.serviceWorker.ready.then((registration) => {
        registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    updateAvailable = true;
                    showUpdateNotification();
                }
            });
        });
    });
}

function showUpdateNotification() {
    const updateBanner = document.createElement('div');
    updateBanner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        padding: 15px;
        text-align: center;
        z-index: 1001;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    updateBanner.innerHTML = `
        <div>
            <i class="fas fa-sync me-2"></i>
            Dostępna jest nowa wersja aplikacji!
            <button onclick="updateApp()" style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 8px 16px; border-radius: 15px; margin-left: 15px; cursor: pointer;">
                Zaktualizuj
            </button>
        </div>
    `;
    document.body.prepend(updateBanner);
}

function updateApp() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then((registrations) => {
            registrations.forEach((registration) => {
                registration.update();
            });
        });
        window.location.reload();
    }
}

// Online/Offline status
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

function updateOnlineStatus() {
    if (navigator.onLine) {
        hideOfflineIndicator();
        // Retry any failed uploads
        retryFailedOperations();
    } else {
        showOfflineIndicator();
    }
}

function showOfflineIndicator() {
    let offlineIndicator = document.getElementById('offline-indicator');
    if (!offlineIndicator) {
        offlineIndicator = document.createElement('div');
        offlineIndicator.id = 'offline-indicator';
        offlineIndicator.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: #dc3545;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            z-index: 1002;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
        `;
        offlineIndicator.innerHTML = '<i class="fas fa-wifi me-2"></i>Tryb offline';
        document.body.appendChild(offlineIndicator);
    }
    offlineIndicator.style.display = 'block';
}

function hideOfflineIndicator() {
    const offlineIndicator = document.getElementById('offline-indicator');
    if (offlineIndicator) {
        offlineIndicator.style.display = 'none';
    }
}

// Initialize push notifications
function initializePushNotifications() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
        Notification.requestPermission().then((permission) => {
            if (permission === 'granted') {
                console.log('Push notifications enabled');
            }
        });
    }
}

// Form data caching for offline use
function cacheFormData(formData) {
    if ('localStorage' in window) {
        localStorage.setItem('cv_form_backup', JSON.stringify(formData));
    }
}

function restoreFormData() {
    if ('localStorage' in window) {
        const backup = localStorage.getItem('cv_form_backup');
        if (backup) {
            return JSON.parse(backup);
        }
    }
    return null;
}

function retryFailedOperations() {
    // Implement retry logic for failed uploads/operations
    console.log('Retrying failed operations...');
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 1003;
        min-width: 300px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Initialize PWA features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    updateOnlineStatus();
    initializePushNotifications();
    
    // Restore form data if available
    const backup = restoreFormData();
    if (backup) {
        console.log('Form backup available');
        // You can implement form restoration logic here
    }
    
    // Auto-save form data
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('input', debounce(() => {
            const formData = new FormData(form);
            cacheFormData(Object.fromEntries(formData));
        }, 1000));
    });
});