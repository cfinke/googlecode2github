import sys
import re

import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

from github2.client import Github

def import_issues(google_project, github_project, github_username, github_api_token):
    closed_statuses = ["fixed","closed","invalid","wontfix","cantfix","verified","duplicate","worksforme"]

    google_client = gdata.projecthosting.client.ProjectHostingClient()
    github_client = Github(username=github_username, api_token=github_api_token, requests_per_second=1)

    feed = google_client.get_issues(google_project)

    for issue in feed.entry:
        # Create issue
        # new_issue = github_client.issues.open(github_project, title=issue.title.text, body=issue.content.text)
        # control
        # cc
        # contributor
        # owner
        # id
        # category
        # author
        # state
        # X label
        # X content
        # source
        # _other_elements
        # stars
        # status
        # updated
        # link
        # rights
        # X title
        # X summary
        # published
    
        # Add labels
        # for l in issue.label:
        #     github.issues.add_label(github_project, new_issue.number, l.text)
    
        # Add comments
        comments = google_client.get_comments(google_project, issue.id.text.split("/").pop())
    
        for comment in comments.entry:
            # Unused fields from Google:
                # category
                # control
                # updated
                # rights
                # _other_attributes
                # source
                # _other_elements
                # contributor
        
            new_comment_body = comment.content.text
            new_comment_body = re.sub('(\W)r([0-9]+)(\W)', "\\1[r\\2](http://code.google.com/p/"+google_project+"/source/detail?r=\\2)\\3", new_comment_body)
        
            new_comment_body += "\n"
        
            if comment.updates.status:
                new_comment_body += "\n* Status changed to _" + comment.updates.status.text + "_"
        
            for label in comment.updates.label:
                new_comment_body += "\n* Label added: _" + label.text + "_"
            
            new_comment_body += "\n\n---\n"
            new_comment_body += "Comment imported from Google Code\n"
            new_comment_body += "Author: [" + comment.author[0].name.text + "](http://code.google.com" + comment.author[0].uri.text + ")\n"
            new_comment_body += "Published: " + comment.published.text + "\n"
            new_comment_body += "Link: " + comment.link[0].href
        
            print new_comment_body
        
            print "\n\n"
            # github_client.issues.comment(github_project, new_issue.number, comment.content.text)
    
        # Possibly close the issue
        # if issue.state.text in closed_statuses:
        #     github.issues.close(github_project, new_issue.number)
    
        #break

if __name__ == "__main__":
    args = sys.argv[1:]
    
    google_project = None
    github_project = None
    github_username = None
    github_api_token = None
    
    for arg in args:
        arg_name, arg_val = arg.split("=")
        
        if arg_name == '--google_project':
            google_project = arg_val
        elif arg_name == '--github_project':
            github_project = arg_val
        elif arg_name == '--github_username':
            github_username = arg_val
        elif arg_name == '--github_api_token':
            github_api_token = arg_val
        else:
            print "Unknown argument: " + arg_name
            sys.exit(2)
    
    if (not google_project) or (not github_project) or (not github_username) or (not github_api_token):
        print "Missing argument."
        sys.exit(2)
    
    import_issues(google_project, github_project, github_username, github_api_token)
