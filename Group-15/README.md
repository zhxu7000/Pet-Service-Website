
## migration

```shell
python manage.py makemigrations

python manage.py migrate
```
## test

```shell
python manage.py test pets.tests 
```

## Coverage report
```shell
coverage run manage.py test pets.tests

coverage report

coverage html
```
## funcition

- user
  - [x] register
  - [x] login
  - [x] Pet service reservation
  - [x] Merchandise purchase
  - [x] Settlement
  - [x] Place an order
  - [x] View my order
  - [x] Order evaluation
  - [x] Personal home page maintenance
    - [x] User information maintenance
    - [x] Pet information maintenance
    - [x] IP address maintenance
  - [x] Pet Story Sharing Area (Rich text)
  - [x] Forum (visitors can see, login to comment)

- Service provider
  - [x] Register
    - [x] Log in
    - [x] Logout
    - [x] Order
      - [x] View all orders
      - [x] Process the order
  - [x] Commodity management
    - [x] Adds
    - [x] Modifies
    - [x] Delete
  - [x] Service management
    - [x] Adds
    - [x] Modifies
    - [x] Delete
  - [x] View comments (client)

- Administrator.
  - [x] admin Background management system  
    - [x] Type management 