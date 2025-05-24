
import os
import json
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nousresearch/deephermes-3-mistral-24b-preview:free"

DEEP_REASONING_PROMPT = """You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem."""

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://cv-optimizer-pro.repl.co/"
}

def send_api_request(prompt, max_tokens=2000):
    """
    Send a request to the OpenRouter API
    """
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API key not found")
        raise ValueError("OpenRouter API key not set in environment variables")
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": DEEP_REASONING_PROMPT + "\nYou are an expert resume editor and career advisor. Always respond in the same language as the CV or job description provided by the user."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        logger.debug(f"Sending request to OpenRouter API")
        response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.debug("Received response from OpenRouter API")
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            raise ValueError("Unexpected API response format")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise Exception(f"Failed to communicate with OpenRouter API: {str(e)}")
    
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing API response: {str(e)}")
        raise Exception(f"Failed to parse OpenRouter API response: {str(e)}")

def analyze_cv_score(cv_text, job_description=""):
    """
    Analizuje CV i przyznaje ocenę punktową 1-100 z szczegółowym uzasadnieniem
    """
    prompt = f"""
    Przeanalizuj poniższe CV i przyznaj mu ocenę punktową od 1 do 100, gdzie:
    - 90-100: Doskonałe CV, gotowe do wysłania
    - 80-89: Bardzo dobre CV z drobnymi usprawnieniami
    - 70-79: Dobre CV wymagające kilku poprawek
    - 60-69: Przeciętne CV wymagające znaczących poprawek
    - 50-59: Słabe CV wymagające dużych zmian
    - Poniżej 50: CV wymagające całkowitego przepisania

    CV do oceny:
    {cv_text}

    {"Wymagania z oferty pracy: " + job_description if job_description else ""}

    Uwzględnij w ocenie:
    1. Strukturę i organizację treści (20 pkt)
    2. Klarowność i zwięzłość opisów (20 pkt)
    3. Dopasowanie do wymagań stanowiska (20 pkt)
    4. Obecność słów kluczowych branżowych (15 pkt)
    5. Prezentację osiągnięć i rezultatów (15 pkt)
    6. Gramatykę i styl pisania (10 pkt)

    Odpowiedź w formacie JSON:
    {{
        "score": [liczba 1-100],
        "grade": "[A+/A/B+/B/C+/C/D/F]",
        "category_scores": {{
            "structure": [1-20],
            "clarity": [1-20], 
            "job_match": [1-20],
            "keywords": [1-15],
            "achievements": [1-15],
            "language": [1-10]
        }},
        "strengths": ["punkt mocny 1", "punkt mocny 2", "punkt mocny 3"],
        "weaknesses": ["słabość 1", "słabość 2", "słabość 3"],
        "recommendations": ["rekomendacja 1", "rekomendacja 2", "rekomendacja 3"],
        "summary": "Krótkie podsumowanie oceny CV"
    }}
    """
    
    return send_api_request(prompt, max_tokens=1500)

def analyze_keywords_match(cv_text, job_description):
    """
    Analizuje dopasowanie słów kluczowych z CV do wymagań oferty pracy
    """
    if not job_description:
        return "Brak opisu stanowiska do analizy słów kluczowych."
    
    prompt = f"""
    Przeanalizuj dopasowanie słów kluczowych między CV a wymaganiami oferty pracy.

    CV:
    {cv_text}

    Oferta pracy:
    {job_description}

    Odpowiedź w formacie JSON:
    {{
        "match_percentage": [0-100],
        "found_keywords": ["słowo1", "słowo2", "słowo3"],
        "missing_keywords": ["brakujące1", "brakujące2", "brakujące3"],
        "recommendations": [
            "Dodaj umiejętność: [nazwa]",
            "Podkreśl doświadczenie w: [obszar]",
            "Użyj terminów branżowych: [terminy]"
        ],
        "priority_additions": ["najważniejsze słowo1", "najważniejsze słowo2"],
        "summary": "Krótkie podsumowanie analizy dopasowania"
    }}
    """
    
    return send_api_request(prompt, max_tokens=1200)

def check_grammar_and_style(cv_text):
    """
    Sprawdza gramatykę, styl i poprawność językową CV
    """
    prompt = f"""
    Przeanalizuj poniższe CV pod kątem gramatyki, stylu i poprawności językowej.

    CV:
    {cv_text}

    Sprawdź:
    1. Błędy gramatyczne i ortograficzne
    2. Spójność czasów gramatycznych
    3. Profesjonalność języka
    4. Klarowność przekazu
    5. Zgodność z konwencjami CV

    Odpowiedź w formacie JSON:
    {{
        "grammar_score": [1-10],
        "style_score": [1-10],
        "professionalism_score": [1-10],
        "errors": [
            {{"type": "gramatyka", "text": "błędny tekst", "correction": "poprawka", "line": "sekcja"}},
            {{"type": "styl", "text": "tekst do poprawy", "suggestion": "sugestia", "line": "sekcja"}}
        ],
        "style_suggestions": [
            "Użyj bardziej dynamicznych czasowników akcji",
            "Unikaj powtórzeń słów",
            "Zachowaj spójny format dat"
        ],
        "overall_quality": "ocena ogólna jakości językowej",
        "summary": "Podsumowanie analizy językowej"
    }}
    """
    
    return send_api_request(prompt, max_tokens=1500)

def optimize_for_position(cv_text, job_title, job_description=""):
    """
    Optymalizuje CV pod konkretne stanowisko
    """
    prompt = f"""
    Zoptymalizuj poniższe CV specjalnie pod stanowisko: {job_title}

    CV:
    {cv_text}

    {"Wymagania z oferty: " + job_description if job_description else ""}

    Stwórz zoptymalizowaną wersję CV, która:
    1. Podkreśla najważniejsze umiejętności dla tego stanowiska
    2. Reorganizuje sekcje według priorytetów dla tej roli
    3. Dostosowuje język do branżowych standardów
    4. Maksymalizuje dopasowanie do wymagań
    5. Zachowuje autentyczność i prawdziwość informacji

    Odpowiedź w formacie JSON:
    {{
        "optimized_cv": "Zoptymalizowana wersja CV",
        "key_changes": ["zmiana 1", "zmiana 2", "zmiana 3"],
        "focus_areas": ["obszar 1", "obszar 2", "obszar 3"],
        "added_elements": ["dodany element 1", "dodany element 2"],
        "positioning_strategy": "Strategia pozycjonowania kandydata",
        "summary": "Podsumowanie optymalizacji"
    }}
    """
    
    return send_api_request(prompt, max_tokens=2500)

def generate_interview_tips(cv_text, job_description=""):
    """
    Generuje spersonalizowane tipy na rozmowę kwalifikacyjną
    """
    prompt = f"""
    Na podstawie CV i opisu stanowiska, przygotuj spersonalizowane tipy na rozmowę kwalifikacyjną.

    CV:
    {cv_text}

    {"Stanowisko: " + job_description if job_description else ""}

    Odpowiedź w formacie JSON:
    {{
        "preparation_tips": [
            "Przygotuj się na pytanie o [konkretny aspekt z CV]",
            "Przećwicz opowiadanie o projekcie [nazwa projektu]",
            "Badź gotowy na pytania techniczne o [umiejętność]"
        ],
        "strength_stories": [
            {{"strength": "umiejętność", "story_outline": "jak opowiedzieć o sukcesie", "example": "konkretny przykład z CV"}},
            {{"strength": "osiągnięcie", "story_outline": "struktura opowieści", "example": "przykład z doświadczenia"}}
        ],
        "weakness_preparation": [
            {{"potential_weakness": "obszar do poprawy", "how_to_address": "jak to przedstawić pozytywnie"}},
            {{"potential_weakness": "luka w CV", "how_to_address": "jak wytłumaczyć"}}
        ],
        "questions_to_ask": [
            "Przemyślane pytanie o firmę/zespół",
            "Pytanie o rozwój w roli",
            "Pytanie o wyzwania stanowiska"
        ],
        "research_suggestions": [
            "Sprawdź informacje o: [aspekt firmy]",
            "Poznaj ostatnie projekty firmy",
            "Zbadaj kulturę organizacyjną"
        ],
        "summary": "Kluczowe rady dla tego kandydata"
    }}
    """
    
    return send_api_request(prompt, max_tokens=2000)

def optimize_cv(cv_text, job_description):
    """
    Create an optimized version of CV with enhanced experience and skills extraction
    """
    prompt = f"""
    WYKONAJ: Całkowite, profesjonalne przetworzenie CV dla podanego stanowiska, ze znacznie lepszym opisem doświadczenia zawodowego i umiejętności!

    NADRZĘDNE WYMAGANIA:
    1. NIE GENERUJ SZABLONOWEGO CV! Każdy element musi być konkretny i profesjonalny
    2. MOCNO ulepsz wszystkie opisy, tworząc prawdziwie profesjonalne CV
    3. WYKORZYSTAJ wszystkie dane z oryginalnego CV, ale znacznie ulepsz ich prezentację
    4. ABSOLUTNIE NIE DODAWAJ WYMYŚLONYCH LICZB, PROCENT LUB OSIĄGNIĘĆ! Używaj tylko informacji z oryginalnego CV
    5. BEZWZGLĘDNIE NIE WYMYŚLAJ: doświadczenia, stanowisk, pracodawców, dat, projektów, osiągnięć, liczb, procent, certyfikatów czy jakichkolwiek faktów

    KLUCZOWE ELEMENTY DO STWORZENIA:

    1. PROFESJONALNE PODSUMOWANIE ZAWODOWE (ZUPEŁNIE NOWE):
       * Utwórz mocne, konkretne zawodowe summary na początku (4-6 zdań)
       * Podkreśl kluczowe umiejętności i obszary specjalizacji z CV
       * Dostosuj tone of voice do branży (transport/logistyka)
       * Dodaj konkretną wartość jaką kandydat wnosi (np. optymalizacja tras, oszczędność czasu)

    2. DOŚWIADCZENIE ZAWODOWE (ROZBUDUJ SZCZEGÓŁOWO):
       * Rozpisz KAŻDE stanowisko w pełni profesjonalny sposób:
          - Nazwa firmy, stanowisko, okres zatrudnienia (jak w oryginale)
          - 4-6 bardzo konkretnych bullet pointów dla KAŻDEGO miejsca pracy
          - Każdy bullet point musi rozpoczynać się od MOCNEGO czasownika
          - TYLKO przepisz zadania z oryginalnego CV w bardziej profesjonalny sposób
          - NIE DODAWAJ żadnych liczb, procent, obszarów ani osiągnięć, których nie ma w oryginale
          - Używaj wyłącznie informacji faktycznych z przesłanego CV
       * Wzór dla KAŻDEGO bullet pointu:
          - [Mocny czasownik] + [zadanie z oryginalnego CV przepisane profesjonalnie]
          - PRZYKŁAD ZŁEGO PODEJŚCIA: "zwiększając o 15%" - NIE RÓB TEGO!
          - PRZYKŁAD DOBREGO PODEJŚCIA: przepisz tylko to co faktycznie jest w CV

    3. UMIEJĘTNOŚCI (TYLKO Z ORYGINALNEGO CV):
       * Uporządkuj umiejętności wymienione w oryginalnym CV w kategorie
       * NIE DODAWAJ nowych umiejętności, których nie ma w oryginale
       * Używaj TYLKO umiejętności faktycznie wymienionych przez kandydata
       * Możesz jedynie lepiej je pogrupować i opisać profesjonalnie

    4. UPORZĄDKOWANIE (BEZ DODAWANIA NOWYCH TREŚCI):
       * Uporządkuj sekcje w logicznej kolejności używając TYLKO istniejących informacji
       * NIE DODAWAJ nowych sekcji, jeśli nie ma do nich danych w oryginale
       * NIE WYMYŚLAJ certyfikatów, osiągnięć ani uprawnień
       * Przenieś istniejące informacje do właściwych sekcji

    5. FORMATOWANIE I PREZENTACJA:
       * Użyj przejrzystej struktury z odpowiednimi nagłówkami
       * Zastosuj spójny sposób formatowania bullet pointów
       * Zadbaj o profesjonalny układ i hierarchię informacji
       * Zapewnij czytelność dla systemów ATS

    ZASADY TWORZENIA OPISÓW STANOWISK (KLUCZOWE):
    1. Dla dowolnej pracy, generuj KONKRETNE punkty odzwierciedlające stanowisko:
       * "Zarządzałem/am codziennymi operacjami, utrzymując wysoki poziom wydajności i terminowości."
       * "Optymalizowałem/am procesy, redukując koszty i zwiększając efektywność."
       * "Obsługiwałem/am zaawansowane systemy, precyzyjnie dokumentując wszystkie działania."
       * "Rozwiązywałem/am problemy, utrzymując wysoki wskaźnik satysfakcji i minimalizując negatywny wpływ."
       * "Zarządzałem/am zasobami, rozliczając je z dokładnością i minimalizując straty."

    2. Dla stanowisk związanych z zarządzaniem lub koordynacją:
       * "Nadzorowałem/am i koordynowałem/am pracę zespołu, zapewniając zgodność z procedurami i optymalne wykorzystanie zasobów."
       * "Koordynowałem/am działania, efektywnie organizując pracę zespołu."
       * "Tworzyłem/am i realizowałem/am plany, zwiększając efektywność procesów."
       * "Weryfikowałem/am dokumentację, zapewniając zgodność z przepisami i standardami."
       * "Monitorowałem/am wskaźniki, zapewniając bezpieczeństwo i optymalne wyniki."

    3. Dla stanowisk operacyjnych i specjalistycznych:
       * "Kompleksowo zarządzałem/am procesami, wykorzystując zaawansowane narzędzia i systemy."
       * "Utrzymywałem/am wysoki poziom dokładności, realizując zadania z dużą precyzją."
       * "Optymalizowałem/am procesy, skracając czas realizacji i zwiększając wydajność."
       * "Współpracowałem/am z zespołem, koordynując przepływ informacji i zasobów."
       * "Monitorowałem/am i raportowałem/am dane, przyczyniając się do redukcji błędów i optymalizacji zasobów."

    STRATEGIA DOSKONALENIA:
    1. KOMPLEKSOWA ANALIZA TREŚCI:
       * Zidentyfikuj wszystkie słabe opisy z oryginalnego CV
       * Znajdź każdą sekcję wymagającą profesjonalizacji
       * Rozpoznaj brakujące elementy profesjonalnego CV

    2. CAŁKOWITA PRZEBUDOWA DOŚWIADCZENIA:
       * Przepracuj CAŁY opis każdego stanowiska na profesjonalny
       * Zamień każdy ogólny opis na konkretne osiągnięcia
       * Wykorzystaj branżową terminologię logistyczną
       * Dodaj kontekst i skalę do każdego osiągnięcia

    3. PROFESJONALIZACJA JĘZYKA:
       * Użyj mocnych czasowników czynnych dla wszystkich punktów
       * Zastosuj spójny profesjonalny język branżowy
       * Zamień ogólnikowe określenia na precyzyjne i mierzalne

    WAŻNE ZASADY:
    * NIE WYMYŚLAJ nowych firm ani stanowisk - bazuj TYLKO na tych z oryginalnego CV!
    * NIE DODAWAJ wymyślonych umiejętności - rozwijaj tylko te zasygnalizowane w oryginale!
    * USUŃ wszystkie usterki, dziwne sformułowania i niespójności z oryginalnego CV
    * NAPRAW wszystkie błędy strukturalne (np. doświadczenie we właściwej sekcji)
    * USUŃ wszelkie wzmianki sugerujące generowanie przez AI

    Język odpowiedzi: zachowaj język oryginalnego CV (polski)

    DANE:

    Opis stanowiska:
    {job_description}

    Oryginalne CV:
    {cv_text}

    BEZWZGLĘDNIE UNIKAJ generycznych opisów! Każdy punkt musi być oparty na realiach branży logistycznej i konkretnych zadaniach kierowcy czy pracownika magazynu. Stwórz mocne, profesjonalne CV na miarę 2023 roku!
    """
    
    return send_api_request(prompt, max_tokens=2500)

def generate_recruiter_feedback(cv_text, job_description=""):
    """
    Generate feedback on a CV as if from an AI recruiter
    """
    context = ""
    if job_description:
        context = f"Opis stanowiska do kontekstu:\n{job_description}"
        
    prompt = f"""
    ZADANIE: Jesteś doświadczonym rekruterem. Przeanalizuj to CV i udziel szczegółowej, konstruktywnej opinii w języku polskim.
    
    Uwzględnij w ocenie:
    1. Ogólne wrażenie i pierwsza reakcja
    2. Mocne strony i słabości kandydata
    3. Ocena formatowania i struktury CV
    4. Jakość treści i sposób prezentacji
    5. Kompatybilność z systemami ATS
    6. Konkretne sugestie poprawek
    7. Ocena ogólna w skali 1-10
    8. Prawdopodobieństwo zaproszenia na rozmowę
    
    {context}
    
    CV do oceny:
    {cv_text}
    
    Odpowiedź w formacie JSON:
    {{
        "overall_impression": "Pierwsze wrażenie i ogólna ocena",
        "rating": [1-10],
        "strengths": [
            "Mocna strona 1",
            "Mocna strona 2", 
            "Mocna strona 3"
        ],
        "weaknesses": [
            "Słabość 1 z sugestią poprawy",
            "Słabość 2 z sugestią poprawy",
            "Słabość 3 z sugestią poprawy"
        ],
        "formatting_assessment": "Ocena layoutu, struktury i czytelności",
        "content_quality": "Ocena jakości treści i sposobu opisywania doświadczeń",
        "ats_compatibility": "Czy CV przejdzie przez systemy automatycznej selekcji",
        "specific_improvements": [
            "Konkretna poprawa 1",
            "Konkretna poprawa 2",
            "Konkretna poprawa 3"
        ],
        "interview_probability": "Prawdopodobieństwo zaproszenia na rozmowę i dlaczego",
        "recruiter_summary": "Podsumowanie z perspektywy rekrutera"
    }}
    
    Bądź szczery, ale konstruktywny. Myśl jak prawdziwy rekruter oceniający kandydata.
    """
    
    return send_api_request(prompt, max_tokens=2000)

def generate_cover_letter(cv_text, job_description):
    """
    Generate a cover letter based on a CV and job description
    """
    prompt = f"""
    ZADANIE: Napisz spersonalizowany list motywacyjny w języku polskim na podstawie CV i opisu stanowiska.
    
    List motywacyjny powinien:
    - Być profesjonalnie sformatowany
    - Podkreślać istotne umiejętności i doświadczenia z CV
    - Łączyć doświadczenie kandydata z wymaganiami stanowiska
    - Zawierać przekonujące wprowadzenie i zakończenie
    - Mieć około 300-400 słów
    - Być napisany naturalnym, profesjonalnym językiem polskim
    
    Struktura listu:
    1. Nagłówek z danymi kontaktowymi
    2. Zwrot do adresata
    3. Wprowadzenie - dlaczego aplikujesz
    4. Główna treść - dopasowanie doświadczenia do wymagań
    5. Zakończenie z wyrażeniem zainteresowania
    6. Pozdrowienia
    
    Opis stanowiska:
    {job_description}
    
    CV kandydata:
    {cv_text}
    
    Napisz kompletny list motywacyjny w języku polskim. Użyj profesjonalnego, ale ciepłego tonu.
    """
    
    return send_api_request(prompt, max_tokens=2000)

def analyze_job_url(url):
    """
    Extract job description from a URL with improved handling for popular job sites
    """
    try:
        logger.debug(f"Analyzing job URL: {url}")
        
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_text = ""
        domain = parsed_url.netloc.lower()
        
        if 'linkedin.com' in domain:
            containers = soup.select('.description__text, .show-more-less-html, .jobs-description__content')
            if containers:
                job_text = containers[0].get_text(separator='\n', strip=True)
                
        elif 'indeed.com' in domain:
            container = soup.select_one('#jobDescriptionText')
            if container:
                job_text = container.get_text(separator='\n', strip=True)
                
        elif 'pracuj.pl' in domain:
            containers = soup.select('[data-test="section-benefit-expectations-text"], [data-test="section-description-text"]')
            if containers:
                job_text = '\n'.join([c.get_text(separator='\n', strip=True) for c in containers])
                
        elif 'olx.pl' in domain or 'praca.pl' in domain:
            containers = soup.select('.offer-description, .offer-content, .description')
            if containers:
                job_text = containers[0].get_text(separator='\n', strip=True)
        
        if not job_text:
            potential_containers = soup.select('.job-description, .description, .details, article, .job-content, [class*=job], [class*=description], [class*=offer]')
            if potential_containers:
                for container in potential_containers:
                    container_text = container.get_text(separator='\n', strip=True)
                    if len(container_text) > len(job_text):
                        job_text = container_text
            
            if not job_text and soup.body:
                for tag in soup.select('nav, header, footer, script, style, iframe'):
                    tag.decompose()
                
                job_text = soup.body.get_text(separator='\n', strip=True)
                
                if len(job_text) > 10000:
                    paragraphs = job_text.split('\n')
                    keywords = ['requirements', 'responsibilities', 'qualifications', 'skills', 'experience', 'about the job',
                                'wymagania', 'obowiązki', 'kwalifikacje', 'umiejętności', 'doświadczenie', 'o pracy']
                    
                    relevant_paragraphs = []
                    found_relevant = False
                    
                    for paragraph in paragraphs:
                        if any(keyword.lower() in paragraph.lower() for keyword in keywords):
                            found_relevant = True
                        if found_relevant and len(paragraph.strip()) > 50:
                            relevant_paragraphs.append(paragraph)
                    
                    if relevant_paragraphs:
                        job_text = '\n'.join(relevant_paragraphs)
        
        job_text = '\n'.join([' '.join(line.split()) for line in job_text.split('\n') if line.strip()])
        
        if not job_text:
            raise ValueError("Could not extract job description from the URL")
        
        logger.debug(f"Successfully extracted job description from URL")
        
        if len(job_text) > 4000:
            logger.debug(f"Job description is long ({len(job_text)} chars), summarizing with AI")
            job_text = summarize_job_description(job_text)
        
        return job_text
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching job URL: {str(e)}")
        raise Exception(f"Failed to fetch job posting from URL: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error analyzing job URL: {str(e)}")
        raise Exception(f"Failed to analyze job posting: {str(e)}")

def summarize_job_description(job_text):
    """
    Summarize a long job description using the AI
    """
    prompt = f"""
    ZADANIE: Wyciągnij i podsumuj kluczowe informacje z tego ogłoszenia o pracę w języku polskim.
    
    Uwzględnij:
    1. Stanowisko i nazwa firmy (jeśli podane)
    2. Wymagane umiejętności i kwalifikacje
    3. Obowiązki i zakres zadań
    4. Preferowane doświadczenie
    5. Inne ważne szczegóły (benefity, lokalizacja, itp.)
    6. TOP 5 słów kluczowych krytycznych dla tego stanowiska
    
    Tekst ogłoszenia:
    {job_text[:4000]}...
    
    Stwórz zwięzłe ale kompletne podsumowanie tego ogłoszenia, skupiając się na informacjach istotnych dla optymalizacji CV.
    Na końcu umieść sekcję "KLUCZOWE SŁOWA:" z 5 najważniejszymi terminami.
    
    Odpowiedź w języku polskim.
    """
    
    return send_api_request(prompt, max_tokens=1500)

def ats_optimization_check(cv_text, job_description=""):
    """
    Check CV against ATS (Applicant Tracking System) and provide suggestions for improvement
    """
    context = ""
    if job_description:
        context = f"Ogłoszenie o pracę dla odniesienia:\n{job_description[:2000]}"
        
    prompt = f"""
    TASK: Przeprowadź dogłębną analizę CV pod kątem kompatybilności z systemami ATS (Applicant Tracking System) i wykryj potencjalne problemy.
    
    Przeprowadź następujące analizy:
    
    1. WYKRYWANIE PROBLEMÓW STRUKTURALNYCH:
       - Znajdź sekcje, które są w nieodpowiednich miejscach (np. doświadczenie zawodowe w sekcji zainteresowań)
       - Wskaż niespójności w układzie i formatowaniu
       - Zidentyfikuj zduplikowane informacje w różnych sekcjach
       - Zaznacz fragmenty tekstu, które wyglądają na wygenerowane przez AI
       - Znajdź ciągi znaków bez znaczenia lub losowe znaki
    
    2. ANALIZA FORMATOWANIA ATS:
       - Wykryj problemy z formatowaniem, które mogą utrudnić odczyt przez systemy ATS
       - Sprawdź, czy nagłówki sekcji są odpowiednio wyróżnione
       - Zweryfikuj, czy tekst jest odpowiednio podzielony na sekcje
       - Oceń czytelność dla systemów automatycznych
    
    3. ANALIZA SŁÓW KLUCZOWYCH:
       - Sprawdź gęstość słów kluczowych i trafność ich wykorzystania
       - Zidentyfikuj brakujące słowa kluczowe z branży/stanowiska
       - Oceń rozmieszczenie słów kluczowych w dokumencie
    
    4. OCENA KOMPLETNOŚCI:
       - Zidentyfikuj brakujące sekcje lub informacje, które są często wymagane przez ATS
       - Wskaż informacje, które należy uzupełnić
    
    5. WERYFIKACJA AUTENTYCZNOŚCI:
       - Zaznacz fragmenty, które wyglądają na sztuczne lub wygenerowane przez AI
       - Podkreśl niespójności między różnymi częściami CV
    
    6. OCENA OGÓLNA:
       - Oceń ogólną skuteczność CV w systemach ATS w skali 1-10
       - Podaj główne powody obniżonej oceny
    
    {context}
    
    CV do analizy:
    {cv_text}
    
    Odpowiedz w tym samym języku co CV. Jeśli CV jest po polsku, odpowiedz po polsku.
    Format odpowiedzi:
    
    1. OCENA OGÓLNA (skala 1-10): [ocena]
    
    2. PROBLEMY KRYTYCZNE:
    [Lista wykrytych krytycznych problemów]
    
    3. PROBLEMY ZE STRUKTURĄ:
    [Lista problemów strukturalnych]
    
    4. PROBLEMY Z FORMATOWANIEM ATS:
    [Lista problemów z formatowaniem]
    
    5. ANALIZA SŁÓW KLUCZOWYCH:
    [Wyniki analizy słów kluczowych]
    
    6. BRAKUJĄCE INFORMACJE:
    [Lista brakujących informacji]
    
    7. PODEJRZANE ELEMENTY:
    [Lista elementów, które wydają się wygenerowane przez AI lub są niespójne]
    
    8. REKOMENDACJE NAPRAWCZE:
    [Konkretne sugestie, jak naprawić zidentyfikowane problemy]
    
    9. PODSUMOWANIE:
    [Krótkie podsumowanie i zachęta]
    """
    
    return send_api_request(prompt, max_tokens=1800)

def analyze_cv_strengths(cv_text, job_title="analityk danych"):
    """
    Analyze CV strengths for a specific job position and provide improvement suggestions
    """
    prompt = f"""
    ZADANIE: Przeprowadź dogłębną analizę mocnych stron tego CV w kontekście stanowiska {job_title}.
    
    1. Zidentyfikuj i szczegółowo omów 5-7 najsilniejszych elementów CV, które są najbardziej wartościowe dla pracodawcy.
    2. Dla każdej mocnej strony wyjaśnij, dlaczego jest ona istotna właśnie dla stanowiska {job_title}.
    3. Zaproponuj konkretne ulepszenia, które mogłyby wzmocnić te mocne strony.
    4. Wskaż obszary, które mogłyby zostać dodane lub rozbudowane, aby CV było jeszcze lepiej dopasowane do stanowiska.
    5. Zaproponuj, jak lepiej zaprezentować osiągnięcia i umiejętności, aby były bardziej przekonujące.
    
    CV:
    {cv_text}
    
    Pamiętaj, aby Twoja analiza była praktyczna i pomocna. Używaj konkretnych przykładów z CV i odnoś je do wymagań typowych dla stanowiska {job_title}.
    """
    
    return send_api_request(prompt, max_tokens=2500)

def generate_interview_questions(cv_text, job_description=""):
    """
    Generate likely interview questions based on CV and job description
    """
    context = ""
    if job_description:
        context = f"Uwzględnij poniższe ogłoszenie o pracę przy tworzeniu pytań:\n{job_description[:2000]}"
        
    prompt = f"""
    TASK: Wygeneruj zestaw potencjalnych pytań rekrutacyjnych, które kandydat może otrzymać podczas rozmowy kwalifikacyjnej.
    
    Pytania powinny być:
    1. Specyficzne dla doświadczenia i umiejętności kandydata wymienionych w CV
    2. Dopasowane do stanowiska (jeśli podano opis stanowiska)
    3. Zróżnicowane - połączenie pytań technicznych, behawioralnych i sytuacyjnych
    4. Realistyczne i często zadawane przez rekruterów
    
    Uwzględnij po co najmniej 3 pytania z każdej kategorii:
    - Pytania o doświadczenie zawodowe
    - Pytania techniczne/o umiejętności
    - Pytania behawioralne
    - Pytania sytuacyjne
    - Pytania o motywację i dopasowanie do firmy/stanowiska
    
    {context}
    
    CV:
    {cv_text}
    
    Odpowiedz w tym samym języku co CV. Jeśli CV jest po polsku, odpowiedz po polsku.
    Dodatkowo, do każdego pytania dodaj krótką wskazówkę, jak można by na nie odpowiedzieć w oparciu o informacje z CV.
    """
    
    return send_api_request(prompt, max_tokens=2000)
