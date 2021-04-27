import requests
import json
import os


IntercomUrl = 'https://api.intercom.io/conversations/search'
AccessToken = os.environ.get('AccessToken')
headers = {
    'Authorization': 'Bearer ' + AccessToken,
    'Accept': 'application/json'
}

SearchQuery = {
    "query": {
        "operator": "AND",
        "value": [
            {
                "field": "team_assignee_id",
                "operator": "=",
                "value": 0
            },
            {
                "field": "state",
                "operator": "=",
                "value": 'open'
            }
        ]
    }
}


def close_conversations():
    conversation_ids = get_open_conversations()
    for conversation_id in conversation_ids:
        close_conversation_url = 'https://api.intercom.io/conversations/' + conversation_id + '/parts'
        params = {
            "message_type": "close",
            "type": "admin",
            "admin_id": 1201295,
        }
        r = requests.post(close_conversation_url, headers=headers, json=params)
        print(r.status_code)
        print(r.text)
        print(r.headers)
    return print(str(len(conversation_ids)) + ' conversations closed')


def get_open_conversations():
    r = requests.post(IntercomUrl, headers=headers, json=SearchQuery)
    conversation_json = json.loads(r.text)
    number_of_pages = conversation_json['pages']['total_pages']

    if number_of_pages > 1:
        print('More than one page')
        conversation_ids = multiple_pages_of_conversation_ids(conversation_json)
    else:
        print('One page or less')
        conversation_ids = one_page_of_conversation_ids(conversation_json)

    return conversation_ids


def one_page_of_conversation_ids(conversation_json):
    conversation_ids = []
    current_ids = get_conversation_ids(conversation_json)
    conversation_ids += current_ids
    return conversation_ids


def multiple_pages_of_conversation_ids(conversation_json):
    conversation_ids = []
    current_ids = get_conversation_ids(conversation_json)
    conversation_ids += current_ids

    number_of_pages = conversation_json['pages']['total_pages']
    print(str(number_of_pages) + ' pages of conversations')
    print('Page 1 ids gathered')
    for request in range(1, number_of_pages):
        starting_after_token = conversation_json['pages']['next']['starting_after']

        pagination = {
            "pagination": {
                "starting_after": starting_after_token
            }
        }
        SearchQuery.update(pagination)
        r = requests.post(IntercomUrl, headers=headers, json=SearchQuery)
        conversation_json = json.loads(r.text)
        current_ids = get_conversation_ids(conversation_json)
        conversation_ids += current_ids

        if 'next' in conversation_json['pages']:
            starting_after_token = conversation_json['pages']['next']['starting_after']
            print('Page ' + str(request + 1) + ' ids gathered')
        else:
            print('Page ' + str(request + 1) + ' ids gathered')
    print(conversation_ids)
    return conversation_ids


def get_conversation_ids(conversation_json):
    conversation_ids = []
    conversations = conversation_json['conversations']

    for conversation in conversations:
        current_id = conversation['id']
        conversation_ids.append(current_id)
    return conversation_ids


if __name__ == '__main__':
    close_conversations()
