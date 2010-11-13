import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

from github2.client import Github

closed_statuses = ["fixed","closed","invalid","wontfix","cantfix","verified","duplicate","worksforme"]

google_client = gdata.projecthosting.client.ProjectHostingClient()
github_client = Github(username="cfinke", api_token="24425e093655337e06a497ed7ee6d5aa", requests_per_second=1)

google_project="url-fixer"
github_project="cfinke/URL-Fixer"

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
    print issue.cc
    # Add labels
    # for l in issue.label:
    #     github.issues.add_label(github_project, new_issue.number, l.text)
    # Add comments
    comments = google_client.get_comments(google_project, 3)#issue.id.text.split("/").pop())
    
    for comment in comments.entry:
        # category
        # control
        # updated
        # author
        # rights
        # _other_attributes
        # summary
        # content
        # source
        # _other_elements
        # etag
        # link
        # updates
        # published
        # contributor
        # title
        # id
        print comment.__dict__
    break
    
    # Possibly close the issue
    # if issue.state.text in closed_statuses:
    #     github.issues.close(github_project, new_issue.number)
    
    #break
