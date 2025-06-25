import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

params = {
    'engine': "yelp",
    'find_desc': "restaurants",
    'find_loc': 'seattle, WA',
    'api_key': os.getenv('SERPAPI_API_KEY'),
    'output': 'json'
}

search = GoogleSearch(params)
results = search.get_dict()

if 'organic_results' in results:

           
    restaurants = []
    for result in results.get('organic_results', []):
        restaurant = {
            "title": result.get("title",""),
            "price": result.get("price",""),
            "neighborhoods": result.get("neighborhoods")
        }
        restaurants.append(restaurant)

        categories = result.get('categories', [])
        
        category_links = []
        for category in categories:
            category_links.append(category.get('link',""))
        
        print(category_links)


            
    print(json.dumps(restaurants, indent=2))


# for restaurant in restaurants:

print(json.dumps(results,indent=2))