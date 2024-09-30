from flask import Flask, request, render_template
from jinja2 import Environment, FileSystemLoader
import os
import requests
import logging

app = Flask(__name__)

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 5000))

template_env = Environment(loader=FileSystemLoader('template'))
logging.basicConfig(level=logging.INFO) 

@app.route('/gitlab-webhook', methods=['POST'])
def gitlab_webhook():
    data = request.json
    message = format_message(data)
    response = send_to_wechat(message)
    return response.text, response.status_code, {'Content-Type': 'application/json'}

def format_message(data):
    event_name = data.get('object_kind', 'unknown event')
    event_handlers = {
        'push': handle_push_event,
        'pipeline': handle_pipeline_event,
    }
    handler = event_handlers.get(event_name, handle_generic_event)
    handler(data)

    templates = {
        'push': 'push.md',
        'merge_request': 'merge_request_event.md',
        'issue': 'issue_event.md',
        'pipeline': 'pipeline_event.md',
        'tag_push': 'tag_push_event.md',
        'deployment': 'deployment_event.md'
    }
    template_name = templates.get(event_name, 'generic_event.md')
    return render_template(template_env.get_template(template_name),**data)

# 处理参数
def handle_push_event(data):
    if 'ref' in data:
        data['handle_branch'] = data['ref'].replace('refs/heads/', '')
        if data['before'] == '0000000000000000000000000000000000000000':
            data['handle_option'] = '新建分支'
        elif data['after'] == '0000000000000000000000000000000000000000':
            data['handle_option'] = '删除分支'
        else:
            data['handle_option'] = '代码推至'

def handle_pipeline_event(data):
    if 'ref' in data:
        data['handle_branch'] = data['ref'].replace('refs/heads/', '')

def handle_generic_event(data):
    if 'ref' in data:
        data['handle_branch'] = data['ref'].replace('refs/heads/', '')

# 发送至企业微信
def send_to_wechat(message):
    wechat_message = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }
    logging.info("Sending message: %s", wechat_message)
    response = requests.post(WEBHOOK_URL, json=wechat_message)
    return response 

if __name__ == '__main__':
    app.run(port=PORT)