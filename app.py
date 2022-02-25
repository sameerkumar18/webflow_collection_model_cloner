# -*- coding: utf-8 -*-

import re
import flask
import requests
from flask import jsonify, request
from flask_cors import CORS
from helpers import WebflowCollectionSchema

from lxml import html

app = flask.Flask(__name__)
CORS(app)


@app.route('/v1/clone_schema', methods=["post"])
def main():
    input_data = request.get_json()
    print(input_data, type(input_data))
    wf_clone = WebflowCollectionSchema(
        origin_config=input_data['origin'],
        destination_config=input_data['destination'])
    try:
        collection_dict = wf_clone.get_collection_schema(
            input_data['origin']['collection_id'])
        updated_collection_dict = wf_clone.check_and_update_refrences(
            collection_dict)
        # print('collection for req: ', updated_collection_dict)

        print('==============')
        new_collection_dict = wf_clone.create_collection(
            updated_collection_dict)
        print('new collection for req: ', new_collection_dict)

        print('==============')
        return jsonify(new_collection_dict)
    except requests.exceptions.HTTPError as httperr:
        print(httperr)
        print(httperr.response.text)
        return jsonify(httperr.response.json()), httperr.response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
