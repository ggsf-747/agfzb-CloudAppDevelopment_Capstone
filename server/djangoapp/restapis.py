import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if "apikey" in kwargs:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"] 
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
        # Call get method of requests library with URL and parameters
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(
                url, headers={'Content-Type': 'application/json'}, params=kwargs)  
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)  
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print("json_data", json_data)
    print("response_text", response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    print(json_payload)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        print(json_data)
        return json_data
    except:
        print("Network exception occurred")

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        print("Cf json result", json_result)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_from_cf_by_id(url, dealer_id):
    json_result = get_request(url, id=dealer_id)
    print("Cf opid", json_result)
    if json_result:
        dealer = json_result[dealer_id-1]["doc"]
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                               id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], zip=dealer["zip"])
    return dealer_obj


def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    id = dealer_id
    # url = url + "?id="+ str(dealer_id)
    print("test123 url", url)
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)

    if json_result:
        reviews = json_result["data"]
        num = -1
        try:
            for dealer_review in reviews:
                num = num + 1
                dealer_review = reviews["docs"][num]
                print("dealer review", dealer_review)
            
                review_obj = DealerReview(dealership=dealer_review["dealership"],
                                   name=dealer_review["name"],
                                   purchase=dealer_review["purchase"],
                                   car_year = dealer_review["car_year"],
                                   review=dealer_review["review"])
                if "id" in dealer_review:
                    review_obj.id = dealer_review["id"]
                if "purchase_date" in dealer_review:
                    review_obj.purchase_date = dealer_review["purchase_date"]
                if "car_make" in dealer_review:
                    review_obj.car_make = dealer_review["car_make"]
                if "car_model" in dealer_review:
                    review_obj.car_model = dealer_review["car_model"]
                if "car_year" in dealer_review:
                    review_obj.car_year = dealer_review["car_year"]
            
                sentiment = analyze_review_sentiments(review_obj.review)
                print("sentiment 9867", sentiment)
                review_obj.sentiment = sentiment
                results.append(review_obj)
        except:
            pass

    return results    

# def get_dealer_reviews_from_cf(url, dealer_id):
#     results = []
#     id = dealer_id
#     if id:
#         json_result = get_request(url, id=dealer_id)
#     else:
#         json_result = get_request(url, id=dealer_id)
#     print(json_result)
#     if json_result:
#         print("line 105",json_result)
#         reviews = json_result["data"]["docs"]
#         print("reviews", reviews)
#         for dealer_review in reviews:
#             print(dealer_review)
#             # review_obj = DealerReview(dealership=dealer_review["dealership"],
#             #                        name=dealer_review["name"],
#             #                        purchase=dealer_review["purchase"],
#             #                        review=dealer_review["review"])
#             # if "id" in dealer_review:
#             #     review_obj.id = dealer_review["id"]
#             # if "purchase_date" in dealer_review:
#             #     review_obj.purchase_date = dealer_review["purchase_date"]
#             # if "car_make" in dealer_review:
#             #     review_obj.car_make = dealer_review["car_make"]
#             # if "car_model" in dealer_review:
#             #     review_obj.car_model = dealer_review["car_model"]
#             # if "car_year" in dealer_review:
#             #     review_obj.car_year = dealer_review["car_year"]

#             # sentiment = analyze_review_sentiments(review_obj.review)          
#             # print(sentiment)
#             # review_obj.sentiment = sentiment
#             # results.append(review_obj)
#             sentiment = analyze_review_sentiments(dealer_review["review"])
#             print("sentiment", sentiment)
#             print("Done")


#     return reviews
#     # return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

# def analyze_review_sentiments(dealer_review):
#     API_KEY = "KXuydxd2P-N5a9ELuNJ--mQjJYOAAcAK4oO2onzajeYM"
#     NLU_URL = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/4a9491d9-2c8b-49a9-954e-d1c8cb2a627a'
#     authenticator = IAMAuthenticator(API_KEY)
#     natural_language_understanding = NaturalLanguageUnderstandingV1(
#         version='2021-08-01', authenticator=authenticator)
#     natural_language_understanding.set_service_url(NLU_URL)
#     response = natural_language_understanding.analyze(text=dealer_review, features=Features(
#         sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
#     label = json.dumps(response, indent=2)
#     label = response['sentiment']['document']['label']
#     return(label)

def analyze_review_sentiments(dealer_review):
    API_KEY = "KXuydxd2P-N5a9ELuNJ--mQjJYOAAcAK4oO2onzajeYM"
    NLU_URL = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/4a9491d9-2c8b-49a9-954e-d1c8cb2a627a'
    authenticator = IAMAuthenticator(API_KEY) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
    natural_language_understanding.set_service_url(NLU_URL) 
    text1 = dealer_review + " " + dealer_review
    response = natural_language_understanding.analyze( text=text1 ,features=Features(sentiment=SentimentOptions(targets=[text1]))).get_result() 
    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 
    return(label) 