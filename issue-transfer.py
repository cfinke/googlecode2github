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
    google_client = gdata.projecthosting.client.ProjectHostingClient()
    github_client = Github(username=github_username, api_token=github_api_token, requests_per_second=1)
    
    start = 1
    
    # The Google projecthosting API has a limit of 25 results per call
    limit = 25
    
    while True:
        query = gdata.projecthosting.client.Query(start_index=start, max_results=limit)
        
        feed = google_client.get_issues(google_project, query=query)
        
        for issue in feed.entry:
            new_issue_body = u""
            
            if issue.content.text:
                new_issue_body += issue.content.text.strip()
                new_issue_body += "\n"
            
            if issue.owner:
                new_issue_body += "\n* Owner: [" + issue.owner.username.text + "](http://code.google.com" + issue.owner.uri.text + ")\n"
            
            new_issue_body += "\n\n---\n"
            new_issue_body += "Issue imported from Google Code\n"
            new_issue_body += "Author: [" + issue.author[0].name.text + "](http://code.google.com" + issue.author[0].uri.text + ")\n"
            new_issue_body += "Published: " + issue.published.text + "\n"
            new_issue_body += "Link: " + issue.link[0].href + "\n"
            new_issue_body += "Status: " + issue.status.text
            
            # new_issue = github_client.issues.open(github_project, title=issue.title.text, body=issue.content.text)
            
            # Unused fields from Google:
                # control
                # cc
                # contributor
                # category
                # source
                # _other_elements
                # stars
                # updated
                # rights
    
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
        
                new_comment_body = u""
            
                if comment.content.text:
                    new_comment_body += comment.content.text.strip()
                    new_comment_body = re.sub('(\W)r([0-9]+)(\W)', "\\1[r\\2](http://code.google.com/p/"+google_project+"/source/detail?r=\\2)\\3", new_comment_body)
        
                new_comment_body += "\n"
        
                if comment.updates:
                    if comment.updates.status:
                        new_comment_body += "\n* Status changed to _" + comment.updates.status.text + "_"
        
                    if comment.updates.label:
                        for label in comment.updates.label:
                            if label.text[0] == '-':
                                new_comment_body += "\n* Label removed: _" + label.text[1:] + "_"
                            else:
                                new_comment_body += "\n* Label added: _" + label.text + "_"
                    
                new_comment_body += "\n\n---\n"
                new_comment_body += "Comment imported from Google Code\n"
                new_comment_body += "Author: [" + comment.author[0].name.text + "](http://code.google.com" + comment.author[0].uri.text + ")\n"
                new_comment_body += "Published: " + comment.published.text + "\n"
                new_comment_body += "Link: " + comment.link[0].href
                        
                #print new_comment_body.encode("utf-8")
        
                # github_client.issues.comment(github_project, new_issue.number, comment.content.text)
            
            
            # Possibly close the issue
            if issue.state.text == "closed":
                # github.issues.close(github_project, new_issue.number)
                print "This issue is closed."
    
            #break
        
        if len(feed.entry) < limit:
            break
        else:
            start += len(feed.entry)
    
    return

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
