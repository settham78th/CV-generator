// PWA functionality for CV Optimizer Pro

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/sw.js')
      .then(registration => {
        console.log('PWA: Service Worker registered successfully');
        
        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              showUpdateNotification();
            }
          });
        });
      })
      .catch(error => {
        console.log('PWA: Service Worker registration failed');
      });
  });
}

// Install prompt handling
let deferredPrompt;
const installButton = document.createElement('button');
installButton.textContent = 'Zainstaluj aplikację';
installButton.className = 'btn btn-primary install-btn';
installButton.style.display = 'none';

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  showInstallButton();
});

function showInstallButton() {
  const navbar = document.querySelector('.navbar .container');
  if (navbar && !document.querySelector('.install-btn')) {
    installButton.style.display = 'block';
    installButton.addEventListener('click', installApp);
    navbar.appendChild(installButton);
  }
}

function installApp() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('PWA: App installed successfully');
        hideInstallButton();
      }
      deferredPrompt = null;
    });
  }
}

function hideInstallButton() {
  installButton.style.display = 'none';
}

// Update notification
function showUpdateNotification() {
  const notification = document.createElement('div');
  notification.className = 'update-notification';
  notification.innerHTML = `
    <div class="alert alert-info alert-dismissible fade show" role="alert">
      <i class="fas fa-download me-2"></i>
      <strong>Nowa wersja dostępna!</strong> Kliknij aby zaktualizować aplikację.
      <button type="button" class="btn btn-sm btn-outline-primary ms-2" onclick="updateApp()">
        Aktualizuj
      </button>
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `;
  
  document.body.insertBefore(notification, document.body.firstChild);
}

function updateApp() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistration().then(registration => {
      if (registration && registration.waiting) {
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        window.location.reload();
      }
    });
  }
}

// Offline/Online status handling
function updateOnlineStatus() {
  const statusIndicator = document.querySelector('.online-status');
  if (navigator.onLine) {
    if (statusIndicator) statusIndicator.remove();
  } else {
    if (!statusIndicator) {
      showOfflineIndicator();
    }
  }
}

function showOfflineIndicator() {
  const indicator = document.createElement('div');
  indicator.className = 'online-status offline-indicator';
  indicator.innerHTML = `
    <div class="alert alert-warning mb-0" role="alert">
      <i class="fas fa-wifi me-2"></i>
      Jesteś offline. Niektóre funkcje mogą być niedostępne.
    </div>
  `;
  
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    navbar.insertAdjacentElement('afterend', indicator);
  }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Background sync for failed uploads
if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
  window.addEventListener('cv-upload-failed', () => {
    navigator.serviceWorker.ready.then(registration => {
      return registration.sync.register('cv-upload-retry');
    });
  });
}

// Push notifications setup
function initializePushNotifications() {
  if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.ready.then(registration => {
      return registration.pushManager.getSubscription();
    }).then(subscription => {
      if (!subscription) {
        // User is not subscribed to push notifications
        console.log('PWA: Push notifications not subscribed');
      } else {
        console.log('PWA: Push notifications already subscribed');
      }
    });
  }
}

// Enhanced offline form caching
function cacheFormData(formData) {
  if ('localStorage' in window) {
    try {
      localStorage.setItem('cv-optimizer-form-backup', JSON.stringify(formData));
    } catch (e) {
      console.log('PWA: Failed to cache form data');
    }
  }
}

function restoreFormData() {
  if ('localStorage' in window) {
    try {
      const cached = localStorage.getItem('cv-optimizer-form-backup');
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (e) {
      console.log('PWA: Failed to restore form data');
    }
  }
  return null;
}

// Initialize PWA features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  updateOnlineStatus();
  initializePushNotifications();
  
  // Restore form data if available
  const cachedData = restoreFormData();
  if (cachedData) {
    // Populate form fields with cached data
    Object.keys(cachedData).forEach(key => {
      const field = document.getElementById(key);
      if (field) {
        field.value = cachedData[key];
      }
    });
  }
  
  // Auto-save form data
  const form = document.getElementById('cv-upload-form');
  if (form) {
    form.addEventListener('input', debounce(() => {
      const formData = new FormData(form);
      const data = {};
      for (let [key, value] of formData.entries()) {
        data[key] = value;
      }
      cacheFormData(data);
    }, 1000));
  }
});

// Utility function for debouncing
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