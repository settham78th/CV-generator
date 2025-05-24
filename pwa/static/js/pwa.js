// PWA functionality for CV Optimizer Pro

// Window Controls Overlay support
if ('windowControlsOverlay' in navigator) {
  navigator.windowControlsOverlay.addEventListener('geometrychange', () => {
    const { x, y, width, height } = navigator.windowControlsOverlay.getTitlebarAreaRect();
    document.documentElement.style.setProperty('--titlebar-area-x', `${x}px`);
    document.documentElement.style.setProperty('--titlebar-area-y', `${y}px`);
    document.documentElement.style.setProperty('--titlebar-area-width', `${width}px`);
    document.documentElement.style.setProperty('--titlebar-area-height', `${height}px`);
  });
}

// File Handler API support
if ('launchQueue' in window) {
  window.launchQueue.setConsumer(async (launchParams) => {
    if (!launchParams.files.length) return;
    
    for (const fileHandle of launchParams.files) {
      const file = await fileHandle.getFile();
      if (file.type === 'application/pdf') {
        // Auto-fill the file input
        const fileInput = document.getElementById('cv-file');
        if (fileInput) {
          const dt = new DataTransfer();
          dt.items.add(file);
          fileInput.files = dt.files;
          
          // Show success message
          showNotification('Plik PDF został automatycznie załadowany!', 'success');
        }
      }
    }
  });
}

// Protocol Handler support
if ('registerProtocolHandler' in navigator) {
  try {
    navigator.registerProtocolHandler(
      'web+cvoptimizer',
      '/?action=%s',
      'CV Optimizer Pro'
    );
  } catch (e) {
    console.log('Protocol handler registration failed:', e);
  }
}

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

// Enhanced notification system
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    min-width: 300px;
    animation: slideInRight 0.3s ease-out;
  `;
  
  notification.innerHTML = `
    <div class="d-flex align-items-center">
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
      ${message}
    </div>
    <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
  `;
  
  document.body.appendChild(notification);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// Enhanced link handling for PWA
if ('windowControlsOverlay' in navigator && navigator.windowControlsOverlay.visible) {
  document.body.classList.add('window-controls-overlay');
}