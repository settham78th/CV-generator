#!/usr/bin/env python3
"""
Test bezpośredniego wyciągania z OLX
"""

import sys
sys.path.append('.')

from utils.enhanced_job_extractor import extract_job_info_from_url

def test_direct_extraction():
    url = "https://www.olx.pl/oferta/praca/przedstawiciel-handlowy-auto-land-poznan-CID4-ID15HhB4.html"
    
    print(f"🚀 Testowanie pełnej funkcji wyciągania dla: {url}")
    
    try:
        result = extract_job_info_from_url(url)
        
        print(f"\n✅ WYNIK:")
        print(f"📋 Tytuł: '{result.get('job_title', 'BRAK')}'")
        print(f"📝 Opis ({len(result.get('job_description', ''))} znaków):")
        print(f"   {result.get('job_description', 'BRAK')[:200]}...")
        print(f"🏢 Firma: '{result.get('company', 'BRAK')}'")
        
        if result.get('job_title') and result.get('job_description'):
            print(f"\n🎉 SUKCES! Funkcja działa poprawnie!")
        else:
            print(f"\n⚠️ Częściowy sukces - brakuje niektórych danych")
            
    except Exception as e:
        print(f"\n❌ BŁĄD: {str(e)}")

if __name__ == "__main__":
    test_direct_extraction()