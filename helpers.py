import requests


class WebflowCollectionSchema(object):
    def __init__(self, origin_config, destination_config):
        self.origin = origin_config
        self.destination = destination_config

    def check_and_update_refrences(self, collection_dict):
        # 'ItemRef', 'ItemRefSet'
        for item in collection_dict['fields']:
            if item['type'] == 'ItemRef' or item['type'] == 'ItemRefSet':
                ref_id = item['validations']['collectionId']
                existing_collection_dict = self.check_and_update_refrences(
                    self.get_collection_schema(ref_id))
                # case where collection exists with same slug - do a lookup with cookie on /dom database.collections[x] matched with slug
                try:
                  item['validations']['collectionId'] = self.find_collection_id_by_slug(existing_collection_dict['slug'])
                except Exception as ex:
                  if self.destination['create_parents']:
                    item['validations']['collectionId'] = self.create_collection(
                    existing_collection_dict)['collection']['_id']
                    
                print('=======>>>>>>> ***** ', item['validations']['collectionId'])

        return collection_dict

    def get_collection_schema(self, collection_id):

        url = f"https://api.webflow.com/collections/{collection_id}"
        api_token = self.origin['api_key']
        headers = {
            'Authorization': f'Bearer {api_token}',
            'accept-version': '1.0.0'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_collection(self, collection_payload):
        url = f"https://webflow.com/api/sites/{self.destination['site_slug']}/collectionPage"

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua':
            '" Not A;Brand";v="99", "Chromium";v="96", "Sidekick";v="96"',
            'X-XSRF-Token': self.destination["X-XSRF-Token"],
            'sec-ch-ua-mobile': '?0',
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cookie': f'wfsession={self.destination["cookie"]["wfsession"]}'
        }

        response = requests.post(url, headers=headers, json=collection_payload)
        response.raise_for_status()
        return response.json()
    
    def find_collection_id_by_slug(self, collection_slug):
        url = f"https://webflow.com/api/sites/{self.destination['site_slug']}/dom"

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua':
            '" Not A;Brand";v="99", "Chromium";v="96", "Sidekick";v="96"',
            'X-XSRF-Token': self.destination["X-XSRF-Token"],
            'sec-ch-ua-mobile': '?0',
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cookie': f'wfsession={self.destination["cookie"]["wfsession"]}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        found_collection_id = [c for c in response.json()['database']['collections'] if c['slug'] == collection_slug][0]['_id']
        return found_collection_id