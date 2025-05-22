
import os
import json
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Get API key from environment variables with fallback
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nousresearch/deephermes-3-mistral-24b-preview:free"  # Zaawansowany model DeepHermes

# System prompt dla trybu głębokiego rozumowania
DEEP_REASONING_PROMPT = """You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem."""

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://cv-optimizer-pro.repl.co/"  # Replace with your actual domain
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
        logger.debug(f"Received response from OpenRouter API")
        
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
    4. DODAJ faktyczne mierzalne osiągnięcia do każdego stanowiska (% poprawy, liczby, rezultaty)
    5. NIE WYMYŚLAJ doświadczenia, stanowisk, pracodawców czy dat - używaj TYLKO firm i stanowisk z oryginalnego CV

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
          - Dodaj branżowy kontekst do każdego punktu (skala operacji, liczba przesyłek, obszary)
          - Zamień ogólnikowe opisy na KONKRETNE osiągnięcia
          - Pokaż wpływ pracy na firmę (oszczędność czasu/kosztów, poprawa efektywności)
       * Wzór dla KAŻDEGO bullet pointu:
          - [Mocny czasownik] + [konkretne zadanie] + [skala/kontekst] + [mierzalny rezultat]
          - Przykład: "Optymalizowałem dzienne trasy dostaw dla obszaru 150 km², skracając czas doręczeń o 15% i zwiększając liczbę obsługiwanych paczek o 25 dziennie"

    3. UMIEJĘTNOŚCI (CAŁKOWICIE PRZEPRACOWANE):
       * Stwórz profesjonalny podział umiejętności na kategorie:
          - Umiejętności techniczne (systemy logistyczne, skanery, oprogramowanie)
          - Umiejętności branżowe (znajomość przepisów drogowych, planowanie tras)
          - Umiejętności miękkie (komunikacja, praca pod presją czasu)
       * Dla KAŻDEJ umiejętności dodaj krótkie uzasadnienie, jak była wykorzystywana
       * Uwzględnij umiejętności techniczne związane z logistyką i transportem

    4. UPORZĄDKOWANIE I DODANIE BRAKUJĄCYCH SEKCJI:
       * Dodaj sekcję "Certyfikaty i uprawnienia" (prawo jazdy, inne)
       * Uporządkuj wszystkie sekcje w logicznej kolejności
       * Przenieś wszystkie doświadczenia zawodowe do właściwej sekcji
       * Dodaj sekcję "Osiągnięcia zawodowe" z konkretnymi wynikami

    5. FORMATOWANIE I PREZENTACJA:
       * Użyj przejrzystej struktury z odpowiednimi nagłówkami
       * Zastosuj spójny sposób formatowania bullet pointów
       * Zadbaj o profesjonalny układ i hierarchię informacji
       * Zapewnij czytelność dla systemów ATS

    ZASADY TWORZENIA OPISÓW STANOWISK (KLUCZOWE):
    1. Dla pracy jako kierowca dostawczy (DHL/DPD), KONKRETNE punkty jak:
       * "Zarządzałem codziennie flotą 30+ przesyłek w obszarze wielkomiejskim Poznania, utrzymując 99% terminowość dostaw"
       * "Optymalizowałem trasy dostawcze w czasie rzeczywistym, redukując koszty paliwa o około 12% miesięcznie"
       * "Obsługiwałem zaawansowane systemy logistyczne i skanery, precyzyjnie dokumentując status 80+ przesyłek dziennie"
       * "Rozwiązywałem problemy związane z dostawami w trudnych lokalizacjach, utrzymując wskaźnik pomyślnych doręczeń na poziomie 97%"
       * "Zarządzałem płatnościami gotówkowymi i bezgotówkowymi, rozliczając średnio 15,000 PLN tygodniowo z zerowym marginesem błędu"

    2. Dla pracy jako Load Master / Welcome Airport Services:
       * "Nadzorowałem załadunek i rozładunek statków powietrznych, zapewniając zgodność z procedurami bezpieczeństwa i optymalne rozmieszczenie ładunku"
       * "Koordynowałem pracę zespołu 6 osób odpowiedzialnych za transport bagażu i ładunku cargo"
       * "Tworzyłem i realizowałem plany załadunku, zwiększając efektywność procesu o 20%"
       * "Weryfikowałem dokumentację przewozową i celną dla 30+ lotów tygodniowo"
       * "Monitorowałem wagę i rozkład ładunku, zapewniając bezpieczeństwo i optymalne zużycie paliwa"

    3. Dla pracy jako magazynier:
       * "Kompleksowo zarządzałem procesem kompletacji zamówień z użyciem zaawansowanych skanerów ręcznych i systemów WMS"
       * "Utrzymywałem 99.8% dokładność w przygotowywaniu 150+ zamówień dziennie"
       * "Optymalizowałem proces składowania, skracając czas realizacji zamówień o 15%"
       * "Współpracowałem z zespołem 20+ osób, koordynując przepływ towarów w magazynie o powierzchni 5000m²"
       * "Monitorowałem i raportowałem stany magazynowe, przyczyniając się do redukcji braków towarowych o 25%"

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
        context = f"Job description for context:\n{job_description}"
        
    prompt = f"""
    TASK: You are an experienced professional recruiter. Review this CV and provide detailed, actionable feedback.
    
    Include:
    1. Overall impression
    2. Strengths and weaknesses
    3. Formatting and structure assessment
    4. Content quality evaluation
    5. ATS compatibility
    6. Specific improvement suggestions
    7. Rating out of 10
    
    IMPORTANT: Respond in the same language as the CV. If the CV is in Polish, respond in Polish. If the CV is in English, respond in English.
    
    {context}
    
    CV:
    {cv_text}
    
    Provide detailed recruiter feedback. Be honest but constructive.
    """
    
    return send_api_request(prompt, max_tokens=2000)

def generate_cover_letter(cv_text, job_description):
    """
    Generate a cover letter based on a CV and job description
    """
    prompt = f"""
    TASK: Create a personalized cover letter based on this CV and job description.
    
    The cover letter should:
    - Be professionally formatted
    - Highlight relevant skills and experiences from the CV
    - Connect the candidate's background to the job requirements
    - Include a compelling introduction and conclusion
    - Be approximately 300-400 words
    
    IMPORTANT: Respond in the same language as the CV. If the CV is in Polish, respond in Polish. If the CV is in English, respond in English.
    
    Job description:
    {job_description}
    
    CV:
    {cv_text}
    
    Return only the cover letter in plain text format.
    """
    
    return send_api_request(prompt, max_tokens=2000)







def analyze_job_url(url):
    """
    Extract job description from a URL with improved handling for popular job sites
    """
    try:
        logger.debug(f"Analyzing job URL: {url}")
        
        # Validate URL
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Fetch the page
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the job description
        job_text = ""
        domain = parsed_url.netloc.lower()
        
        # Enhanced site-specific extraction for popular job boards
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
        
        # If no specific site pattern matched, use generic approach
        if not job_text:
            # Look for common containers for job descriptions
            potential_containers = soup.select('.job-description, .description, .details, article, .job-content, [class*=job], [class*=description], [class*=offer]')
            if potential_containers:
                # Get the longest container text as it's likely the main description
                for container in potential_containers:
                    container_text = container.get_text(separator='\n', strip=True)
                    if len(container_text) > len(job_text):
                        job_text = container_text
            
            # If still no container found, get the body text
            if not job_text and soup.body:
                # Remove navigation, header, footer and scripts
                for tag in soup.select('nav, header, footer, script, style, iframe'):
                    tag.decompose()
                
                job_text = soup.body.get_text(separator='\n', strip=True)
                
                # If body text is very long, try to extract the most relevant part
                if len(job_text) > 10000:
                    paragraphs = job_text.split('\n')
                    # Look for paragraphs with keywords likely to be in job descriptions
                    keywords = ['requirements', 'responsibilities', 'qualifications', 'skills', 'experience', 'about the job', 
                                'wymagania', 'obowiązki', 'kwalifikacje', 'umiejętności', 'doświadczenie', 'o pracy']
                    
                    relevant_paragraphs = []
                    found_relevant = False
                    
                    for paragraph in paragraphs:
                        if any(keyword.lower() in paragraph.lower() for keyword in keywords):
                            found_relevant = True
                        if found_relevant and len(paragraph.strip()) > 50:  # Only include substantive paragraphs
                            relevant_paragraphs.append(paragraph)
                    
                    if relevant_paragraphs:
                        job_text = '\n'.join(relevant_paragraphs)
        
        # Clean up the text - remove excessive whitespace but preserve paragraph breaks
        job_text = '\n'.join([' '.join(line.split()) for line in job_text.split('\n') if line.strip()])
        
        if not job_text:
            raise ValueError("Could not extract job description from the URL")
        
        logger.debug(f"Successfully extracted job description from URL")
        
        # If the text is too long, summarize it using the AI
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
    TASK: Extract and summarize the key information from this job posting.
    
    Include:
    1. Job title and company (if mentioned)
    2. Required skills and qualifications
    3. Responsibilities and duties
    4. Preferred experience
    5. Any other important details (benefits, location, etc.)
    6. TOP 5 keywords that are critically important for this position
    
    IMPORTANT: Detect the language of the job posting and respond in that same language.
    If the job posting is in Polish, respond in Polish.
    If the job posting is in English, respond in English.
    
    Job posting text:
    {job_text[:4000]}...
    
    Provide a concise but comprehensive summary of this job posting, focusing on information relevant for CV optimization.
    Format the TOP 5 keywords as a separate section at the end labeled "KLUCZOWE SŁOWA:" (in Polish) or "KEY KEYWORDS:" (in English).
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
