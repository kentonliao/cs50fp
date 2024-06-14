import requests

def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + token}
    data = {'message': message}
    response = requests.post(url, headers=headers, data=data)
    return response.status_code

def main():
    line_token = 'C6mYWNZkEa9hRwlFyvMpYQDRot1N0wfmi9wlUgUMc9g'
    message = '\nThank you for using iCRYPTO!\nEverything is fine!'
    status = send_line_notify(message, line_token)
    if status == 200:
        print('Success!')
    else:
        print('Failed...')

if __name__ == "__main__":
    main()