import re
import urllib.parse
import os
from dotenv import load_dotenv
import json
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with only the required parameter
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ApolloFilterGenerator:
    # Base URL with email status verified as default
    BASE_URL = "https://app.apollo.io/#/people?page=1&sortAscending=false&sortByField=recommendations_score&contactEmailStatusV2[]=verified"
    
    # Filter mappings
    FILTER_PARAMS = {
        "job_title": {
            "param": "personTitles[]",
            "encoder": urllib.parse.quote
        },
        "seniority": {
            "param": "personSeniorities[]",
            "values": {
                "vp": "vp",
                "director": "director",
                "manager": "manager",
                "c-level": "cxo",
                "founder": "founder",
                "partner": "partner",
                "owner": "owner",
                "executive": "executive"
            }
        },
        "department": {
            "param": "personDepartmentOrSubdepartments[]",
            "values": {
                "finance": "master_finance",
                "marketing": "master_marketing",
                "sales": "master_sales",
                "engineering": "master_engineering",
                "hr": "master_hr",
                "operations": "master_operations",
                "it": "master_it",
                "legal": "master_legal",
                "product": "master_product",
                "supply chain": "master_supply_chain",
                "import": "master_supply_chain", # Mapping import to supply chain
                "export": "master_supply_chain"  # Mapping export to supply chain
            }
        },
        "location": {
            "param": "personLocations[]",
            "encoder": urllib.parse.quote_plus
        },
        "company_size": {
            "param": "organizationNumEmployeesRanges[]",
            "values": {
                "1-10": "1,10",
                "11-20": "11,20",
                "21-50": "21,50",
                "51-200": "51,200",
                "201-500": "201,500",
                "501-1000": "501,1000",
                "1001-5000": "1001,5000",
                "5001-10000": "5001,10000",
                "10001+": "10001,0"
            },
            "keywords": {
                "small": ["1,10", "11,20", "21,50"],
                "medium": ["51,200", "201,500", "501,1000"],
                "large": ["1001,5000", "5001,10000", "10001,0"]
            }
        }
    }
    
    def extract_entities(self, query: str) -> dict:
        """
        Use OpenAI to extract entities from a natural language query
        """
        prompt = f"""
        Extract the following entities from this query: "{query}"
        
        - primary_job_titles (list of EXACT job titles as they should appear in the "include" filter, like 'importer', 'supply chain manager', 'procurement specialist', etc.)
        - seniority (level like vp, director, manager, c-level, founder, partner, owner, executive)
        - departments (like finance, marketing, sales, engineering, HR, operations, IT, supply chain, import, export)
        - locations (countries, states, cities mentioned)
        - company_size_keywords (any mentions of small companies, medium companies, large companies)
        - limit (number of results requested, like "top 10")

        For primary_job_titles, extract the EXACT job roles that would be searched for - not general categories.
        For example:
        - From "importers from USA to India" -> extract "importer" as the primary job title, NOT "supply chain" as a department
        - From "marketing manager" -> extract "marketing manager" as the primary job title
        - From "VP of Finance" -> extract "VP of Finance" as the primary job title
        
        Return a JSON object with these fields. If a field is not mentioned, set it to an empty list or null.
        Format your response as valid JSON only, with no additional text.
        """
        
        try:
            # Use the OpenAI client with the latest API version
            response = client.chat.completions.create(
                model="gpt-4",  # Changed to gpt-4 as gpt-4o might not be available everywhere
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from queries and returns only valid JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the content as JSON
            content = response.choices[0].message.content.strip()
            
            # Handle any text before or after the JSON
            try:
                # Try to parse as-is first
                return json.loads(content)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the text
                match = re.search(r'({.*})', content, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
                else:
                    print(f"Could not extract JSON from response: {content}")
                    return {}
                
        except Exception as e:
            print(f"Error in entity extraction: {e}")
            return {}
                
        except Exception as e:
            print(f"Error in entity extraction: {e}")
            return {}
    
    def build_url(self, entities: dict) -> str:
        """
        Build Apollo.io URL based on extracted entities
        """
        filters = []
        
        # ALWAYS PRIORITIZE THE "INCLUDE" FILTER FIRST
        # Process primary job titles for "include" filter
        if entities.get("primary_job_titles"):
            for title in entities.get("primary_job_titles", []):
                encoded_title = urllib.parse.quote(title)
                filters.append(f"{self.FILTER_PARAMS['job_title']['param']}={encoded_title}")
                
            # If we have primary job titles, we skip departments to avoid over-filtering
            # This prevents the issue with "importers" turning into "master_supply_chain"
            skip_departments = True
        else:
            skip_departments = False
        
        # Process seniority if explicitly mentioned (secondary filter)
        if entities.get("seniority"):
            for seniority in entities.get("seniority", []):
                seniority_lower = seniority.lower()
                if seniority_lower in self.FILTER_PARAMS["seniority"]["values"]:
                    value = self.FILTER_PARAMS["seniority"]["values"][seniority_lower]
                    filters.append(f"{self.FILTER_PARAMS['seniority']['param']}={value}")
        
        # Process departments ONLY if no primary job titles were found or for very specific cases
        if not skip_departments and entities.get("departments"):
            for dept in entities.get("departments", []):
                dept_lower = dept.lower()
                if dept_lower in self.FILTER_PARAMS["department"]["values"]:
                    value = self.FILTER_PARAMS["department"]["values"][dept_lower]
                    filters.append(f"{self.FILTER_PARAMS['department']['param']}={value}")
        
        # Process locations
        if entities.get("locations"):
            for location in entities.get("locations", []):
                encoded_location = urllib.parse.quote_plus(location)
                filters.append(f"{self.FILTER_PARAMS['location']['param']}={encoded_location}")
        
        # Process company size keywords
        if entities.get("company_size_keywords"):
            size_ranges = []
            for keyword in entities.get("company_size_keywords", []):
                keyword_lower = keyword.lower()
                # Check if it's one of our predefined size keywords
                for size_keyword, ranges in self.FILTER_PARAMS["company_size"]["keywords"].items():
                    if size_keyword in keyword_lower:
                        size_ranges.extend(ranges)
            
            # Apply unique size ranges
            for size_range in set(size_ranges):
                filters.append(f"{self.FILTER_PARAMS['company_size']['param']}={size_range}")
        
        # Combine all filters with the base URL
        if filters:
            return f"{self.BASE_URL}&{'&'.join(filters)}"
        else:
            return self.BASE_URL
    
    def generate_filter_url(self, query: str) -> str:
        """
        Generate Apollo.io filter URL from a natural language query
        """
        entities = self.extract_entities(query)
        print("Extracted entities:", json.dumps(entities, indent=2))
        return self.build_url(entities)
