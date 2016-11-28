# -*- coding: utf-8 -*-

import json

from flask import Flask, request

import popuko.slack.commands
from popuko import github
from popuko.conf import settings

app = Flask(__name__)
app.debug = True


@app.route('/slack', methods=['POST'])
def slack_app():
    args = request.form
    if args.get('token') != settings['slack']['token']:
        return '', 403

    (bot_name, command, *args) = args.get('text').split(' ')
    if bot_name != settings['slack']['bot_name']:
        return '{"text": "who?"}'
    method = getattr(popuko.slack.commands, command, None)
    if not method:
        return '{"text":"nothing"}'
    return '{"text":"%s"}' % method(*args)


@app.route('/github', methods=['POST'])
def github_app():
    req = request.json
    # from pprint import pprint
    # pprint(req)

    if not github.is_valid_signature(
            request.data,
            request.headers.get('X-Hub-Signature')):
        return 'Invalid Signature'

    if req['action'] != 'created':
        return 'PASS'
    (trigger, command, *args) = req['comment']['body'].split(' ')

    print('trigger: %s' % trigger)
    print('command: %s' % command)
    print('args: %s' % args)

    if trigger in settings['github']['reviewers'] and command == 'r?':
        assignee = trigger[1:]
        print('assign the issue to %s' % assignee)
        owner = req['repository']['owner']['login']
        repo_name = req['repository']['name']
        issue_number = req['issue']['number']

        issue = github.get_issue(owner, repo_name, issue_number)
        labels = [x['name'] for x in issue.labels if not x['name'].startswith('S-')]
        labels.append('S-awaiting-review')

        github.edit_issue(owner, repo_name, issue_number, labels=labels, assignees=[assignee])
        return 'ASSIGNED'

    if trigger != settings['github']['trigger']:
        print(settings['github']['trigger'])
        return 'PASS'
    if command == 'r+':
        sender = '@%s' % req['comment']['user']['login']
        print('sender: %s' % sender)

        if not is_reviewer(sender):
            return 'UNKNOWN_REVIEWER'

        owner = req['repository']['owner']['login']
        repo_name = req['repository']['name']
        issue_number = req['issue']['number']
        issue = github.get_issue(owner, repo_name, issue_number)
        pr = github.get_pr(owner, repo_name, issue_number)

        labels = [x['name'] for x in issue.labels if x['name'] != 'S-awaiting-review']
        labels.append('S-awaiting-merge')
        github.edit_issue(owner, repo_name, issue_number, labels=labels)
        github.merge_pr(owner, repo_name, issue_number)

        pr_head_label = pr.head['label'].split(':')
        github.delete_branch(pr_head_label[0], repo_name, pr_head_label[1])
        return 'MERGE'
    if command.startswith('r='):
        sender = '@%s' % req['comment']['user']['login']
        print('sender: %s' % sender)

        if not is_reviewer(sender):
            return 'UNKNOWN_REVIEWER'

        actual_reviewer = command.rstrip('=')
        if not is_reviewer(actual_reviewer):
            return 'UNKNOWN_REVIEWER'

        owner = req['repository']['owner']['login']
        repo_name = req['repository']['name']
        issue_number = req['issue']['number']
        issue = github.get_issue(owner, repo_name, issue_number)
        pr = github.get_pr(owner, repo_name, issue_number)

        labels = [x['name'] for x in issue.labels if x['name'] != 'S-awaiting-review']
        labels.append('S-awaiting-merge')
        github.edit_issue(owner, repo_name, issue_number, labels=labels)
        github.merge_pr(owner, repo_name, issue_number)

        pr_head_label = pr.head['label'].split(':')
        github.delete_branch(pr_head_label[0], repo_name, pr_head_label[1])
        return 'MERGE'
    return 'WHO'


def is_reviewer(person):
    if person not in settings['github']['reviewers']:
        return False
    else:
        return True


@app.route('/travis', methods=['POST'])
def travis_app():
    req = json.loads(request.form.get('payload'))
    from pprint import pprint
    pprint(req)
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0')
