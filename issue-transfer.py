import sys
import re
import getpass

# gdata library available at http://code.google.com/p/gdata-python-client/downloads/list
import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

# github2 library available at https://github.com/ask/python-github2
from github2.client import Github

def import_issues(google_project, github_project, github_username, github_api_token, google_username=None, google_password=None):
    """Import issues from a Google Code project to a GitHub project."""
    
    google_client = gdata.projecthosting.client.ProjectHostingClient()
    
    if google_username and google_password:
        # Authenticate the Google client if we're going to be making any changes on the Google side.
        try:
            google_client.client_login(google_username, google_password, source="googlecode2github", service="code")
        except gdata.client.BadAuthentication:
            print "Invalid Google username/password pair."
            sys.exit(2)
        
        google_authenticated = True
    
    github_client = Github(username=github_username, api_token=github_api_token, requests_per_second=1)
    
    try:
        # Confirm that the GitHub client authenticated properly.
        github_client.users.show(github_username)
    except:
        print "Invalid GitHub username/token pair (or GitHub is down)."
    
    # The Google projecthosting API has a limit of 25 results per call
    start = 1
    limit = 25
    
    while True:
        query = gdata.projecthosting.client.Query(start_index=start, max_results=limit)
        feed = google_client.get_issues(google_project, query=query)
        
        for issue in feed.entry:
            print "Transferring issue " + issue.id.text
            
            issue_id = issue.id.text.split("/").pop()
            
            # Build an issue body that contains all of the information that doesn't map 1:1 from Google to GitHub.
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
            new_issue_body += "Status: " + issue.status.text + "\n"
            new_issue_body += "Link: http://code.google.com/p/" + google_project + "/issues/detail?id=" + issue_id
            
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
    
            # Add comments to the issue.
            comments = google_client.get_comments(google_project, issue_id)
            
            # We get the comments before posting the issue so that we can check for a "This issue moved to GitHub"
            # comment in case this script gets run multiple times. It only works that way if you chose to authenticate
            # with Google though.
            
            do_transfer_issue = True
            
            for comment in comments.entry:
                if comment.content.text:
                    if re.match("This issue has been moved to GitHub", comment.content.text.strip()):
                        do_transfer_issue = False
                        break
            
            if not do_transfer_issue:
                print "This issue has already been transferred."
                continue
            
            new_issue = github_client.issues.open(github_project, title=issue.title.text.encode("utf-8"), body=new_issue_body.encode("utf-8"))
            
            # Add labels
            for l in issue.label:
                github_client.issues.add_label(github_project, new_issue.number, l.text)
            
            for comment in comments.entry:
                print "Transferring comment " + comment.link[0].href
                
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
                        
                github_client.issues.comment(github_project, new_issue.number, new_comment_body.encode("utf-8"))
            
            if issue.state.text == "closed":
                # Close the issue on GitHub
                print "Closing issue."
                github_client.issues.close(github_project, new_issue.number)
            
            if google_authenticated:
                # Leave a comment on the Google ticket directing users to GitHub. This also serves to allow the script
                # to tell if the issue has already been transferred, if the script is run twice.
                print "Leaving comment on Google Code issue."
                google_client.update_issue(
                    google_project,
                    issue_id,
                    google_username,
                    comment="This issue has been moved to GitHub: http://github.com/"+github_project+"/issues/issue/"+str(new_issue.number))
                    
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
    google_username = None
    google_password = None
    
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
        elif arg_name == '--google_username':
            google_username = arg_val
        else:
            print "Unknown argument: " + arg_name
            sys.exit(2)
    
    if google_username:
        google_password = getpass.getpass("Google Account Password: ")
        
        if not google_password:
            google_username = None
    
    if not google_username:
        should_continue = raw_input("You did not specify a Google Account username/password.  Google Code issues will not be annotated as having been moved to GitHub, and running this script twice will cause duplicate issues in GitHub. Continue? (y/n) ")
        
        if should_continue.lower() == "n":
            sys.exit(2)
    
    if (not google_project) or (not github_project) or (not github_username) or (not github_api_token):
        print "Missing argument."
        sys.exit(2)
    
    import_issues(google_project, github_project, github_username, github_api_token, google_username=google_username, google_password=google_password)
