#!/usr/bin/env python3
"""
Test script for CV Optimizer Pro AI functions
"""

import sys
import os
sys.path.append('.')

from utils.openrouter_api import (
    analyze_cv_score, 
    optimize_cv, 
    generate_recruiter_feedback,
    generate_cover_letter,
    ats_optimization_check,
    generate_interview_questions,
    analyze_keywords_match,
    check_grammar_and_style,
    optimize_for_position,
    generate_interview_tips
)

# Test CV data
test_cv = """
Jan Kowalski
Senior Software Developer

DOŚWIADCZENIE:
• 5 lat programowania w Python, JavaScript
• Praca w zespołach Agile/Scrum
• Tworzenie aplikacji webowych (Django, React)
• Bazy danych: PostgreSQL, MongoDB

WYKSZTAŁCENIE:
• Informatyka, Politechnika Warszawska (2018-2022)

UMIEJĘTNOŚCI:
• Python, JavaScript, TypeScript, React, Node.js
• Git, Docker, AWS
• SQL, NoSQL databases
"""

test_job_description = """
Poszukujemy Senior Python Developera do naszego zespołu backend.

WYMAGANIA:
• Min. 4 lata doświadczenia w Python
• Znajomość Django/FastAPI
• Doświadczenie z bazami danych (PostgreSQL)
• Znajomość Docker i chmury (AWS/GCP)
• Praca w metodykach Agile

OFERUJEMY:
• Konkurencyjne wynagrodzenie
• Praca zdalna/hybrydowa
• Rozwój zawodowy
"""

def test_function(func_name, func, *args):
    """Test a single AI function"""
    print(f"\n{'='*50}")
    print(f"TESTOWANIE: {func_name}")
    print(f"{'='*50}")
    
    try:
        result = func(*args)
        print(f"✅ SUKCES: {func_name}")
        print(f"Wynik (pierwsze 200 znaków):")
        print(f"{str(result)[:200]}...")
        print(f"Długość odpowiedzi: {len(str(result))} znaków")
        return True
    except Exception as e:
        print(f"❌ BŁĄD w {func_name}: {str(e)}")
        return False

def main():
    """Test all AI functions"""
    print("🤖 TESTOWANIE WSZYSTKICH FUNKCJI AI CV OPTIMIZER PRO")
    print("=" * 60)
    
    # Lista funkcji do przetestowania
    test_cases = [
        ("Analiza punktowa CV", analyze_cv_score, test_cv, test_job_description, 'pl'),
        ("Optymalizacja CV", optimize_cv, test_cv, test_job_description, 'pl'),
        ("Opinia rekrutera", generate_recruiter_feedback, test_cv, test_job_description, 'pl'),
        ("List motywacyjny", generate_cover_letter, test_cv, test_job_description, 'pl'),
        ("Test ATS", ats_optimization_check, test_cv, test_job_description, 'pl'),
        ("Pytania na rozmowę", generate_interview_questions, test_cv, test_job_description, 'pl'),
        ("Analiza słów kluczowych", analyze_keywords_match, test_cv, test_job_description, 'pl'),
        ("Sprawdzenie gramatyki", check_grammar_and_style, test_cv, 'pl'),
        ("Optymalizacja pozycyjna", optimize_for_position, test_cv, "Senior Python Developer", test_job_description, 'pl'),
        ("Porady na rozmowę", generate_interview_tips, test_cv, test_job_description, 'pl')
    ]
    
    # Statystyki
    passed = 0
    failed = 0
    
    # Wykonaj testy
    for test_name, func, *args in test_cases:
        if test_function(test_name, func, *args):
            passed += 1
        else:
            failed += 1
    
    # Podsumowanie
    print(f"\n{'='*60}")
    print(f"📊 PODSUMOWANIE TESTÓW")
    print(f"{'='*60}")
    print(f"✅ Funkcje działające: {passed}")
    print(f"❌ Funkcje z błędami: {failed}")
    print(f"📈 Procent sukcesu: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print(f"\n🎉 WSZYSTKIE FUNKCJE AI DZIAŁAJĄ POPRAWNIE!")
    else:
        print(f"\n⚠️ Niektóre funkcje wymagają sprawdzenia konfiguracji API")

if __name__ == "__main__":
    main()