from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from urllib.parse import quote
import re

app = Flask(__name__)
CORS(app)

@app.route('/research', methods=['POST'])
def research():
    try:
        data = request.json
        name = data.get('name', '').strip()
        city = data.get('city', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Name required'}), 400
        
        living = find_status(name, city)
        phone = find_phone(name, city)
        address = find_address(name, city)
        
        return jsonify({
            'success': True,
            'living': living,
            'phone': phone or '',
            'address': address or ''
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def find_status(name, city):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    living_searches = [
        f'"{name}" {city} wisconsin phone address',
        f'"{name}" {city} wisconsin 2025',
        f'"{name}" {city} wisconsin 2024',
        f'whitepages {name} {city}',
        f'"{name}" {city} wisconsin facebook',
    ]
    
    for query in living_searches:
        try:
            url = f"https://www.google.com/search?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=4)
            text = resp.text.lower()
            
            if any(word in text for word in ['phone', 'address', '2025', '2024', 'facebook', 'linkedin']):
                return 'Living'
        except:
            pass
    
    obituary_searches = [
        f'"{name}" obituary {city} wisconsin',
        f'wisconsin death records "{name}"',
        f'"{name}" died {city}',
        f'legacy.com {name} {city}',
        f'"{name}" funeral {city} wisconsin',
    ]
    
    for query in obituary_searches:
        try:
            url = f"https://www.google.com/search?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=4)
            text = resp.text.lower()
            
            if any(word in text for word in ['obituary', 'died', 'passed away', 'death', 'deceased', 'funeral']):
                return 'Deceased'
        except:
            pass
    
    return 'Unknown'

def find_phone(name, city):
    try:
        queries = [
            f'{name} {city} wisconsin phone',
            f'"{name}" {city} wisconsin',
            f'whitepages {name} {city}',
        ]
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for query in queries:
            url = f"https://www.google.com/search?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=4)
            pattern = r'\(\d{3}\)\s*\d{3}[-.]?\d{4}|\d{3}[-.]?\d{3}[-.]?\d{4}'
            matches = re.findall(pattern, resp.text)
            if matches:
                return matches[0]
    except:
        pass
    return None

def find_address(name, city):
    try:
        queries = [
            f'{name} {city} wisconsin address',
            f'"{name}" {city} wisconsin',
            f'whitepages {name} {city}',
        ]
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for query in queries:
            url = f"https://www.google.com/search?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=4)
            pattern = r'\d+\s+[\w\s]+(?:St|Ave|Rd|Blvd|Dr|Ln|Way|Ct|Pkwy)\.?(?:,|\s)+[\w\s]+(?:,|\s)+WI(?:,|\s)*\d{5}'
            matches = re.findall(pattern, resp.text)
            if matches:
                return matches[0]
    except:
        pass
    return None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=False, port=10000)
