import requests


def get_user_tasks(token, **kwargs):
    """Get tasks for user
    
    Arguments:
        token {string} -- Todoist personal API token or OAuth API token
    """
    return requests.get(
        "https://beta.todoist.com/API/v8/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        }).json()
