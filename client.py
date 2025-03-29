import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import pandas as pd
import numpy as np
from collections import defaultdict
import ast, os, re, json
from datetime import datetime

columns_mapping_dict = {
  'id': 'id',
  'doi': 'ids.doi',
  'pmid': 'ids.pmid',
  'mag': 'ids.mag',
  'title': 'title',
  'publication_year': 'publication_year',
  'language': 'language',
  'type': 'type',
  'apc_paid': 'apc_paid',
  'referenced_works_count': 'referenced_works_count',
  'cited_by_count': 'cited_by_count',
  'countries_distinct_count': 'countries_distinct_count',
  'institutions_distinct_count': 'institutions_distinct_count',
  'locations_count': 'locations_count',
  'fwci': 'fwci',
  'primary_location_display_name': 'primary_location.source.display_name',
  'primary_location_host_organization_name': 'primary_location.source.host_organization_name',
  'publication_date': 'publication_date',
  'percentiles_value': 'citation_normalized_percentile.value',
  'percentiles_is_in_top_1_percent': 'citation_normalized_percentile.is_in_top_1_percent',
  'percentiles_is_in_top_10_percent': 'citation_normalized_percentile.is_in_top_10_percent',
  'open_access_is_oa': 'open_access.is_oa',
  'open_access_oa_status': 'open_access.oa_status',
  'grants_funder_display_name': 'grants.funder_display_name',
  'countries_codes': 'institution_assertions.country_code',
  'authorships_author_display_name': 'authorships.author.display_name',
  'authorships_institutions_display_name': 'authorships.institutions',
  'topics_display_name': 'topics.display_name',
  'topics_subfield_display_name': 'topics.subfield.display_name',
  'topics_field_display_name': 'topics.field.display_name',
  'topics_domain_display_name': 'topics.domain.display_name',
  'sustainable_development_goals_display_name': 'sustainable_development_goals.display_name',
  'keywords_display_name': 'keywords.display_name'
}

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
                if ("authorships" in path or "topics" in path or "keywords" in path or "sustainable_development_goals" in path) and "display_name" in path:
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
    def __init__(self, email=None, api_url=None, csv_filepath=None):
        self.email = email
        self.api_url = self.remove_page_params(api_url) if api_url else None
        self.csv_filepath = csv_filepath
        self.parser = JSONMetadataParser(email)
        self.columns_mapping_dict = columns_mapping_dict
        self.csv_data = pd.read_csv(self.csv_filepath, encoding="utf-8") if csv_filepath else None

    def _map_df_columns(self, df):
      """Maps dataframe columns to new names based on a dictionary.

      Args:
        df: The input pandas DataFrame.
        columns_mapping_dict: A dictionary where keys are the new column names
                              and values are the old column names.

      Returns:
        A new pandas DataFrame with the mapped columns, or None if any errors occur.
      """

      new_columns = {}
      for key, value in self.columns_mapping_dict.items():
          if value in df.columns:
              new_columns[value] = key

      if not new_columns:
        print("Warning: No matching columns found in the dataframe.")
        return None

      try:
        return df[list(new_columns.keys())].rename(columns=new_columns)
      except KeyError as e:
        print(f"Error: Column '{e}' not found in DataFrame.")
        return None

    def _clean_pipe_separated_string(self,text):
      """
      Cleans a pipe (|) separated string by removing extra pipes at the beginning, 
      end, and reducing multiple pipes to single pipes as separators.
      Then converts the string to a list of dictionaries.
      """
      # Remove leading and trailing pipes
      text = text.strip('|')
      
      # Replace multiple consecutive pipes with single pipes
      text = re.sub(r'\|\|+', '|', text)

      # Split the string by pipes
      parts = text.split('|')
      
      # Convert each part to a dictionary using ast.literal_eval and append it to the result list
      result = []
      for part in parts:
        try:
          result.append(ast.literal_eval(part))
        except (ValueError, SyntaxError):
          print(f"Warning: Could not convert '{part}' to a dictionary. Skipping.")
          # Handle the case where a part isn't a valid dictionary representation
          # You could add logging, raise an exception, or ignore the bad part as done above
          pass

      return result

    def _extract_df_display_names(self,df,column):
      def extract_unique_display_names(x):
          try:
            # Safely evaluate the string as a list of dictionaries
            list_of_dicts = self._clean_pipe_separated_string(x)
            if not isinstance(list_of_dicts, list):
              list_of_dicts = [list_of_dicts]
            #print(list_of_dicts)
            display_names = []
            for d in list_of_dicts:
                #d = ast.literal_eval(d)
                if isinstance(d, dict) and 'display_name' in d:
                    display_names.append(d['display_name'])
                elif isinstance(d, str):
                    try:
                      # Attempt to parse the string as a dictionary
                      item_dict = json.loads(json.dumps(d))
                      display_names.append(item_dict['display_name'])
                    except json.JSONDecodeError:
                      print(f"Warning: Could not parse string as JSON: {d}")
            return "|".join(set(display_names))
          except (SyntaxError, ValueError):
              return ''  # Return empty string if parsing fails

      df[column] = df[column].astype(str).apply(extract_unique_display_names)
      return df

    def process_csv_data(self):
        """
        Process CSV data using the parser
        """
        try:
            # Convert DataFrame to dictionary format if it's a DataFrame
            df = self._map_df_columns(self.csv_data)
            df = df.replace({np.nan: None})
            all_metadata = self._extract_df_display_names(df,'authorships_institutions_display_name').to_dict('records')
            return all_metadata
        except Exception as e:
            print(f"Error processing CSV data: {e}")
            return []

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