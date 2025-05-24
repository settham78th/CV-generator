# CV Optimizer Pro - PWA Version

Progressive Web App version of CV Optimizer Pro - profesjonalne narzędzie AI do optymalizacji CV.

## 🚀 Funkcje PWA

- **Offline Support** - Działanie bez internetu z cached content
- **App-like Experience** - Pełnoekranowy tryb bez paska przeglądarki
- **Install Prompt** - Możliwość instalacji jak natywna aplikacja
- **Push Notifications** - Powiadomienia o zakończeniu procesowania CV
- **Background Sync** - Automatyczna synchronizacja po powrocie online
- **Responsive Design** - Optymalizacja na wszystkie urządzenia

## 📱 Instalacja

### Wymagania
- Python 3.8+
- Flask
- Nowoczesna przeglądarka z obsługą Service Workers

### Kroki instalacji

1. **Klonowanie/Kopiowanie plików**
   ```bash
   cd pwa
   ```

2. **Instalacja dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfiguracja zmiennych środowiskowych**
   ```bash
   cp .env.example .env
   # Wypełnij .env swoimi kluczami API
   ```

4. **Uruchomienie aplikacji**
   ```bash
   python main.py
   ```

5. **Dostęp do aplikacji**
   - Otwórz http://localhost:5002 w przeglądarce
   - Aplikacja automatycznie wykryje obsługę PWA

## 🔧 Konfiguracja PWA

### Manifest (manifest.json)
- Konfiguruje nazwę, ikony, kolory aplikacji
- Definiuje tryb wyświetlania (standalone)
- Ustala shortcuts i screenshots

### Service Worker (static/js/sw.js)
- Cache Strategy: Cache First dla static files
- Network First dla API calls
- Offline fallback pages
- Background sync dla failed uploads

### PWA Features (static/js/pwa.js)
- Install prompt handling
- Update notifications
- Online/offline status
- Form data caching
- Push notifications setup

## 📋 Testowanie PWA

### Chrome DevTools
1. Otwórz DevTools (F12)
2. Zakładka "Application"
3. Sekcja "Manifest" - sprawdź konfigurację
4. Sekcja "Service Workers" - sprawdź status
5. Sekcja "Storage" - sprawdź cache

### Lighthouse Audit
1. DevTools → Lighthouse
2. Wybierz "Progressive Web App"
3. Kliknij "Generate report"
4. Sprawdź score i rekomendacje

### Manual Testing
- **Install Prompt**: Sprawdź czy pojawia się przycisk instalacji
- **Offline Mode**: Wyłącz internet, sprawdź funkcjonalność
- **App-like**: Zainstaluj i uruchom jako standalone app
- **Notifications**: Test push notifications (wymaga HTTPS)

## 🔐 Bezpieczeństwo

### HTTPS Requirement
- PWA wymaga HTTPS w production
- Localhost działa z HTTP dla development
- Service Workers wymagają bezpiecznego kontekstu

### Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net;
               font-src 'self' https://fonts.gstatic.com;
               img-src 'self' data: https:;">
```

## 📊 Performance

### Caching Strategy
- **Static Files**: Cache First (długoterminowe)
- **API Calls**: Network First (świeże dane)
- **Images**: Cache First z fallback
- **Dynamic Content**: Network First z cache backup

### Optimization
- Compressed assets
- Lazy loading dla obrazów
- Minified CSS/JS
- Service Worker precaching

## 🔧 Development

### File Structure
```
pwa/
├── app.py              # Flask app z PWA routes
├── main.py             # Entry point
├── manifest.json       # PWA manifest
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── templates/         # Jinja2 templates
│   ├── base.html      # Base template z PWA meta tags
│   ├── index.html     # Main page
│   └── offline.html   # Offline fallback page
├── static/
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   │   ├── main.js    # App logic
│   │   ├── pwa.js     # PWA functionality
│   │   └── sw.js      # Service Worker
│   └── icons/         # PWA icons (72x72 to 512x512)
└── utils/             # Backend utilities
```

### Adding New Features
1. Update Service Worker cache list
2. Add offline fallbacks if needed
3. Update manifest.json if adding new pages
4. Test offline functionality
5. Update PWA audit score

## 🚀 Deployment

### Production Checklist
- [ ] HTTPS enabled
- [ ] Environment variables set
- [ ] Icons generated (all sizes)
- [ ] Manifest.json validated
- [ ] Service Worker tested
- [ ] Lighthouse PWA score > 90
- [ ] Cross-browser testing
- [ ] Mobile testing

### Hosting Recommendations
- **Replit Deployments**: Automatic HTTPS, easy setup
- **Vercel**: Excellent PWA support
- **Netlify**: Built-in PWA features
- **Railway**: Simple deployment with domains

## 📱 Browser Support

### Fully Supported
- Chrome 67+
- Firefox 62+
- Safari 12.1+
- Edge 79+

### Partial Support
- Safari iOS 11.3+ (limited PWA features)
- Samsung Internet 8.0+

## 🐛 Troubleshooting

### Common Issues

**Service Worker not registering**
- Check browser console for errors
- Verify HTTPS in production
- Clear browser cache and reload

**Install prompt not showing**
- Check PWA requirements in DevTools
- Ensure manifest.json is valid
- Verify all required icons exist

**Offline mode not working**
- Check Service Worker status
- Verify cache strategy in DevTools
- Test network throttling

**Push notifications not working**
- HTTPS required for production
- Check notification permissions
- Verify Service Worker registration

## 📞 Support

Jeśli napotkasz problemy z wersją PWA:
1. Sprawdź console przeglądarki
2. Użyj DevTools do debugowania
3. Zweryfikuj wszystkie pliki PWA
4. Przetestuj w trybie incognito