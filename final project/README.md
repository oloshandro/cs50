# MyMoney: a simple tool to keep track of your finance

##### Video Demo: https://youtu.be/vH0mGJ_l8IY

### It's a client-server web applications built using Flask, Bootstrap, SQLite. The use of JS is limited to standart Bootstrap features (none). 

### The aim with this web application is to make finance tracking in an easy and quick way. Due to the limited time frame only basic feature where implemented.

## How it works:

1. While using the web app for the first time, a user has to register via `register` form with the required email,  password and password confirmation.
If the user has already created the account, they can easily `login` with their email and password ( and stayed logged in til they  `log out`)

2. Once on the homepage the user can navigate through `Expenses` and `Income` tabs, where introduced a simple way to either `Add new expense` or `Add new income` by choosing the options in dropdown fields `Category` and `Account` and filling in the `Description` and `Amount` fields.

3. In the navigation bar, tabs `MyAccounts` and `MyCategories`, the user can customise the info about the existing accounts and categories for expenses or income.
`MyAccounts` supports unlimited number of accounts with the posibility to choose out of 5 currencies available at the moment. All the newly created accounts will be visible below after the paged was refrashed.
`MyCategories` has pre-defined list of categories, though new categories can be added to the list.

4. All the personal customised data is to be stored in `MyMoney` database in a couple of tables, amoung which are `users`, `accounts`, `categories`, `transactions`.

5. With `MyTransactions` the user can view all the transactions made, including income anf expenses (shown with '-' in tha table)

6. The user is also given the hints if something isn't filled in properly or signals about the successful action with flash messages. 

### The next steps in developing this web application:

1. Better security and storing system for the user's data.
2. Improved checking for errors system based on testing of the web application.
3. Implementing new features such as `General overview` with visual data (e.g. graphs), possibility to sort transactions
4. Better visual design and user exerience 
