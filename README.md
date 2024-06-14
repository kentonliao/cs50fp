# iCRYPTO
#### Video Demo:  <URL HERE>
#### Description: This project is a web application designed to help users manage their cryptocurrency assets and receive real-time price alerts via LINE Notify. The application is built using Python, Flask, and SQLite.

## Features

- **User Authentication**: Secure login and registration system for users.
- **Asset Management**: Users can add, edit, and view their cryptocurrency assets.
- **Price Alerts**: Users can set conditions to receive price alerts for their chosen cryptocurrencies. Alerts are sent via LINE Notify.
- **Responsive Design**: The web application is designed to be responsive and user-friendly on all devices.

## Technologies Used

- **Python**: The core programming language used for the application.
- **Flask**: A lightweight WSGI web application framework for Python.
- **SQLite**: A lightweight database to store user data and asset information.
- **HTML/CSS**: For structuring and styling the web pages.
- **LINE Notify**: For sending real-time price alerts to users.

## Project Structure

Here is the structure of this project:

- **project**
  - **app.py**: Main Flask application
  - **helpers.py**: Collection of functions related to website operation
  - **getprice.py**: Check cryptocurrency prices through API
  - **linenotify.py**: Send real-time currency prices through LINE notify api
  - **pricealert.py**: Background script for price alerts
  - **requirements.txt**: List of dependencies
  - **icrypto.db**: 
  - **templates/**: HTML templates
    - **layout.html**: Set up the website appearance structure
    - **apology.html**: Handling system error feedback
    - **index.html**: Shows all assets with value increases and decreases
    - **login.html**: User login
    - **register.html**: Registration page, add new user
    - **deposit.html**: Record user’s increase in cryptocurrency assets
    - **withdraw.html**: Record user’s decrease in cryptocurrency assets
    - **history.html**: Show asset transaction records
    - **settoken.html**: Store the user's LINE notification token
    - **setalert.html**: Set currency price notification
    - **stopaler.html**: Delete the set currency price notification
    - **alertlist.html**: View currency price notification list
  - **static/**: Static files (CSS, images)
    - **images**: Logo and favicon
    - **style.css**: Custom stylesheet
  - **README.md**: Project documentation
  
## About the code

I've always wanted a web service to manage my cryptocurrency assets, and the Week 9 problem set "finance" covered most of the logic. However, stock trading and cryptocurrency trading operate differently, and I don't intend to rely on CS50's "training wheels" anymore. So, I learned how to connect to SQLite, applied for CoinMarketCap's API to get real-time cryptocurrency prices, and tried using the LINE Notify API to send price alerts. This is the most important feature of this project.

Below I will introduce the content of each function.

- **app.py**: 
  - **after_request()**: This code is borrowed from "finance," primarily to ensure that the response is not cached, using the response method.
  - **index()**: Since purchasing cryptocurrency assets often does not involve fiat currency transactions, recording them as cash and assets does not accurately reflect the real situation. After considering this, I added a "value" field to record them. This is because cryptocurrency assets are mostly traded as "pairs," meaning one type of cryptocurrency can be exchanged for another, unlike stock trading which is conducted in fiat currency. Visually, I also added logic to display profit and loss numbers in different colors.
  - **deposit()**: The operation of depositing cryptocurrency assets mainly involves checking fields and adding/modifying the database. Since there is no cash balance to refer to, I have to record the "value" field.
  - **withdraw()**: The operation of withdrawing cryptocurrency assets mainly involves checking fields and adding/modifying/deleting the database.
  - **history()**: Displaying transaction records after querying the database is the simplest function.
  - **login()**: Allow users to log in. To control the display/hide of certain main menu functions, I added a session for the LINE Notify token to determine this.
  - **logout()**: Log out the user and clear the session.
  - **register()**: Allow users to register as members, and log in automatically after registration.
  - **settoken()**: Allow users to input their LINE Notify token, with the previously saved value automatically filled if already entered. Here are the relevant links below.
  - **setalert()**: Users can enter the cryptocurrencies they want to follow and provide a threshold for price changes to complete the price notification setup.
  - **stopalert()**: To delete a configured price notification.
  - **alertlist()**: Displaying a list of all configured price notifications.
- **helpers.py**: 
  - **apology()**: Handling the response message after field validation.
  - **login_required()**: Decorate routes to require login.
  - **usd()**: Format value as USD.
  - **is_float()**: Because cryptocurrencies can accept decimal points, it's convenient to have a dedicated function to check this.
- **getprice.py**: 
  - **getprice()**: Register as a free member of CoinMarketCap, allowing up to 10,000 API calls per month to query real-time cryptocurrency prices. Simply provide the correct code function and it will return the price.
- **linenotify.py**:
  - **send_line_notify**: There are cost considerations with using the LINE Messaging API, so I chose to use the LINE Notify API instead. However, sending notifications requires the user's token.
- **pricealert.py**: 