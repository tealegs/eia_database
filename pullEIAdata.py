import requests as r
import json

API_KEY = '91468dc73356f3ac1084390ed186f535'

def get_data(url, key = API_KEY):
    print(url.replace('YOUR_API_KEY',API_KEY))
    data = r.get(url.replace('YOUR_API_KEY_HERE',API_KEY))
    return data.json()

def save_json(json_dump, filename): #pass in filename string
    
    #if filename:
        # Writing JSON data
    with open(filename, 'w') as f:
        #print(json.dumps(json_dump))
        json.dump(json_dump, f)
    #else:


if __name__ == "__main__":
    
    plantdata = 'http://api.eia.gov/category/?api_key=YOUR_API_KEY_HERE&category_id=902963'
    test = get_data(plantdata)
    print(test)
    save_json(test, 'test.json')
 