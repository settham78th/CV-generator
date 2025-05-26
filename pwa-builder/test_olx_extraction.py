#!/usr/bin/env python3
"""
Test extraction from OLX job posting
"""

import requests
from bs4 import BeautifulSoup

def test_olx_extraction():
    url = "https://www.olx.pl/oferta/praca/przedstawiciel-handlowy-auto-land-poznan-CID4-ID15HhB4.html"
    
    print(f"🔍 Testowanie wyciągania z: {url}")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pl,en-US;q=0.5",
            "Connection": "keep-alive"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Status kod: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sprawdź różne selektory dla OLX
            print("\n📋 Szukanie tytułu stanowiska:")
            title_selectors = [
                'h1[data-cy="ad_title"]',
                '.css-1juynto',
                'h1',
                '.ad-title',
                '[data-testid="ad-title"]'
            ]
            
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    print(f"  ✅ {selector}: '{title}'")
                else:
                    print(f"  ❌ {selector}: nie znaleziono")
            
            print("\n📝 Szukanie opisu:")
            desc_selectors = [
                '[data-cy="ad_description"]',
                '.css-g5mtl5',
                '.description',
                '.ad-description',
                '[data-testid="ad-description"]'
            ]
            
            for selector in desc_selectors:
                elem = soup.select_one(selector)
                if elem:
                    desc = elem.get_text(strip=True)
                    print(f"  ✅ {selector}: '{desc[:100]}...'")
                else:
                    print(f"  ❌ {selector}: nie znaleziono")
            
            # Sprawdź czy strona w ogóle ma treść
            page_text = soup.get_text()
            print(f"\n📊 Długość strony: {len(page_text)} znaków")
            if "przedstawiciel" in page_text.lower():
                print("✅ Słowo 'przedstawiciel' znalezione na stronie")
            else:
                print("❌ Słowo 'przedstawiciel' NIE znalezione - możliwy problem z dostępem")
                
        else:
            print(f"❌ Błąd HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Błąd: {str(e)}")

if __name__ == "__main__":
    test_olx_extraction()