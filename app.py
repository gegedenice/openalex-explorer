from flask import Flask, jsonify, abort, render_template,url_for,request, send_from_directory, make_response
from flask_cors import CORS, cross_origin
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json
import pandas as pd
from collections import defaultdict
import re
import os
from datetime import datetime


app = Flask(__name__)
CORS(app)

class JSONMetadataParser:
    def __init__(self, email):
        self.email = email
        self.base_url = "https://api.openalex.org/works/"

    def merge_and_deduplicate(self, data):
        print("Entering merge_and_deduplicate with data:", data)  # Debug statement
        merged_data = defaultdict(set)
        for key, value in data.items():
            print(f"Processing key: {key}, value: {value}")  # Debug statement
            if re.search(r'\[\d+\]', key):
                normalized_key = re.sub(r'\[\d+\]', '', key)
                merged_data[normalized_key].add(value)
            else:
                merged_data[key] = {value}
        print("Merged data:", merged_data)  # Debug statement
        return {k: '|'.join(sorted(v)) if len(v) > 1 else next(iter(v)) for k, v in merged_data.items()}

    def find_display_names(self, obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if "display_name" in key:
                    yield new_path, value
                else:
                    yield from self.find_display_names(value, new_path)
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                new_path = f"{path}[{index}]"
                yield from self.find_display_names(item, new_path)

    def extract_unique_country_codes(self, authorships):
        country_codes = set()
        for author in authorships:
            country_codes.update(author.get('countries', []))
        return '|'.join(sorted(country_codes))

    def convert_publication_date(self,publication_date_str):
      """Converts a publication date string (YYYY-MM-DD) to datetime format.

      Args:
        publication_date_str: The publication date string.

      Returns:
        A datetime object representing the publication date, or None if the string
        is invalid.
      """
      try:
        dt = datetime.strptime(publication_date_str, '%Y-%m-%d')
        return dt.isoformat() + 'Z'
      except ValueError:
        return None

    def parse_json(self, json_obj):
        parsed_data = {}
        try:
            print("Parsing id...")
            parsed_data["id"] = json_obj.get("id")
        except Exception as e:
            print(f"Error parsing id: {e}")

        try:
            print("Parsing doi...")
            parsed_data["doi"] = json_obj.get("doi", "")
        except Exception as e:
            print(f"Error parsing doi: {e}")

        try:
            print("Parsing pmid...")
            parsed_data["pmid"] = json_obj.get("ids", {}).get("pmid", "")
        except Exception as e:
            print(f"Error parsing pmid: {e}")
        
        try:
            print("Parsing mag...")
            parsed_data["mag"] = json_obj.get("ids", {}).get("mag", "")
        except Exception as e:
            print(f"Error parsing mag: {e}")

        try:
            print("Parsing title...")
            parsed_data["title"] = json_obj.get("title")
        except Exception as e:
            print(f"Error parsing title: {e}")

        try:
            print("Parsing publication_year...")
            parsed_data["publication_year"] = json_obj.get("publication_year")
        except Exception as e:
            print(f"Error parsing publication_year: {e}")

        try:
            print("Parsing language...")
            parsed_data["language"] = json_obj.get("language")
        except Exception as e:
            print(f"Error parsing language: {e}")
        
        try:
            print("Parsing type...")
            parsed_data["type"] = json_obj.get("type")
        except Exception as e:
            print(f"Error parsing type: {e}")

        try:
            print("Parsing apc_paid...")
            apc_paid_value = json_obj.get("apc_paid")
            if isinstance(apc_paid_value, dict):
                parsed_data["apc_paid"] = apc_paid_value.get("value_usd")
            else:
                parsed_data["apc_paid"] = apc_paid_value
        except Exception as e:
            print(f"Error parsing apc_paid: {e}")
        
        try:
            print("Parsing referenced_works_count...")
            parsed_data["referenced_works_count"] = json_obj.get("referenced_works_count")
        except Exception as e:
            print(f"Error parsing referenced_works_count: {e}")

        try:
            print("Parsing cited_by_count...")
            parsed_data["cited_by_count"] = json_obj.get("cited_by_count")
        except Exception as e:
            print(f"Error parsing cited_by_count: {e}")

        try:
            print("Parsing countries_distinct_count...")
            parsed_data["countries_distinct_count"] = json_obj.get("countries_distinct_count")
        except Exception as e:
            print(f"Error parsing countries_distinct_count: {e}")

        try:
            print("Parsing institutions_distinct_count...")
            parsed_data["institutions_distinct_count"] = json_obj.get("institutions_distinct_count")
        except Exception as e:
            print(f"Error parsing institutions_distinct_count: {e}")

        try:
            print("Parsing locations_count...")
            parsed_data["locations_count"] = json_obj.get("locations_count")
        except Exception as e:
            print(f"Error parsing locations_count: {e}")

        try:
            print("Parsing fwci...")
            parsed_data["fwci"] = json_obj.get("fwci")
        except Exception as e:
            print(f"Error parsing fwci: {e}")


        try:
            print("Parsing primary_location...")
            primary_location = json_obj.get("primary_location", {}).get("source", {})
            parsed_data["primary_location_display_name"] = primary_location.get("display_name")
            parsed_data["primary_location_host_organization_name"] = primary_location.get("host_organization_name")
        except Exception as e:
            print(f"Error parsing primary_location: {e}")
        
        try:
            print("Parsing publication_date...")
            publication_date = json_obj.get("publication_date")
            if publication_date:
                parsed_data["publication_date"] = self.convert_publication_date(publication_date)
        except Exception as e:
            print(f"Error parsing publication_date: {e}")

        try:
            print("Parsing citation_normalized_percentile...")
            percentiles = json_obj.get("citation_normalized_percentile", {})
            for key, value in percentiles.items():
                parsed_data[f"percentiles_{key}"] = value
        except Exception as e:
            print(f"Error parsing citation_normalized_percentile: {e}")

        try:
            print("Parsing open_access...")
            open_access = json_obj.get("open_access", {})
            parsed_data["open_access_is_oa"] = open_access.get("is_oa")
            parsed_data["open_access_oa_status"] = open_access.get("oa_status")
        except Exception as e:
            print(f"Error parsing open_access: {e}")

        try:
            print("Parsing grants...")
            grants = json_obj.get("grants", [])
            for i, grant in enumerate(grants):
                parsed_data[f"grants[{i}]_funder_display_name"] = grant.get("funder_display_name")
        except Exception as e:
            print(f"Error parsing grants: {e}")

        try:
            print("Parsing countries_codes...")
            parsed_data["countries_codes"] = self.extract_unique_country_codes(json_obj.get("authorships", []))
        except Exception as e:
            print(f"Error parsing countries_codes: {e}")
        
        try:
            print("Parsing display_names...")
            display_names = {}
            for path, value in self.find_display_names(json_obj):
                if ("authorships" in path or "concepts" in path or "topics" in path or "keywords" in path or "sustainable_development_goals" in path) and "display_name" in path:
                  if path not in display_names:
                      display_names[path] = []
                  display_names[path].append(value)
        
            for path, values in display_names.items():
              parsed_data[path.replace(".","_")] = "|".join(values)
        except Exception as e:
            print(f"Error parsing display_names: {e}")
        return parsed_data

    def process_work(self, work_id):
        try:
            params = {
                'mailto': self.email
            }
            response = requests.get(f"{self.base_url}{work_id}", params=params)
            response.raise_for_status()
            work_data = response.json()
            parsed_data = self.parse_json(work_data)
            deduplicated_data = self.merge_and_deduplicate(parsed_data)
            return deduplicated_data
        except Exception as e:
            print(f"Error processing work {work_id}: {e}")
            return None

class OpenAlexHarvester:
    def __init__(self, api_url, email):
        self.email = email
        self.api_url = self.remove_page_params(api_url)
        self.parser = JSONMetadataParser(email)
        print(self.api_url)

    def remove_page_params(self,url):
        # Parse the URL
        parsed_url = urlparse(url)        
        # Parse the query parameters
        query_params = parse_qs(parsed_url.query)        
        # Remove 'page' and 'per_page' if they exist
        query_params.pop('page', None)
        query_params.pop('per_page', None)        
        # Rebuild the query string
        new_query_string = urlencode(query_params, doseq=True)        
        # Rebuild the URL without the removed parameters
        new_url = urlunparse(parsed_url._replace(query=new_query_string))        
        return new_url

    def fetch_works(self, page=1, per_page=25):
        try:
            params = {
                'page': page,
                'per-page': per_page,
                'mailto': self.email
            }
            print(f"Fetching works from page {page} with per_page={per_page}")
            response = requests.get(f"{self.api_url}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching works: {e}")
            return None

    def harvest_metadata(self, per_page=25):
        # First request to get the total count of works
        initial_response = self.fetch_works(page=1, per_page=1)
        if not initial_response or 'meta' not in initial_response or 'count' not in initial_response['meta']:
            print("Failed to get the total count of works.")
            return []

        total_count = initial_response['meta']['count']
        print(f"Total count of works: {total_count}")
        total_pages = (total_count + per_page - 1) // per_page
        print(f"Total pages: {total_pages}")

        all_metadata = []
        current_page = 1

        while current_page <= total_pages + 1:
            works_data = self.fetch_works(page=current_page, per_page=per_page)
            if not works_data:
                break

            for work in works_data['results']:
                work_id = work['id'].split('/')[-1]
                metadata = self.parser.process_work(work_id)
                if metadata:
                    all_metadata.append(metadata)

            current_page += 1

        return all_metadata
    
@app.route('/process-data', methods=['GET', 'POST'])
def process_data():
    if request.method == 'POST':
        # Get the URL from the POST request
        url = request.form.get('url')
        email = request.form.get('email')
        # Perform your internal data processing here
        harvester = OpenAlexHarvester(api_url=url,email=email)
        metadata_list = harvester.harvest_metadata(per_page=50)
        return jsonify(metadata_list)  # Return the processed data as JSON 

@app.route('/')
def homePage():
    return render_template('home.html') 
                             
if __name__ == '__main__':
    app.run(debug=True,port=5000, host='0.0.0.0')  