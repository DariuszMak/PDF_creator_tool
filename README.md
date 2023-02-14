After finishing the course please process this small assignment. 
Estimated time to complete this is 1-2 days. 


## Task overview:
You are asked to build a REST API service with a database.
The application should allow **authorized** users to access data about companies and users from a database with use of REST-API. 
At least basic test cases should be implemented for each endpoint. 
Some kind of documentation should be created for the project. 

**Data format:**
- Company:
  - id
  - name
- User:
  - name
  - surname
  - email

User model should contain a hash of the provided password to allow authentication.

Each user can join at least one company. 

### Functional requirements:

- As an **unauthenticated** user I should be able to: 
  - get a JWT token by providing name and password. 
  - create a new user by providing name, surname, email and password.


- As an **authenticated** user I should be able to: 
  - list all companies and see their names and also how many users belong to each company. 
  - get a company with a specified id and see its name and also how many users it has. 
  - create a new company with a specified company name, but only if I’m not already associated with a company. 
  - assign myself to a company but only if I’m not already associated with a company. 
  - unassign myself from a company but if I was the only member of a company, the company should be removed. 
  - see a list of all users with information to which company they belong to. 


### Non-functional requirements:
- jwt authentication
- pagination
- at least functional testing (one for each defined endpoint)
- dynamic documentation from swagger is nice to have
- extending models with audit data is nice to have


```bash
pip virtualenv venv
```

Setup default local `venv` interpreter in Pycharm

```bash
pip install -r requirements.txt
```

Run tests

```bash
pytest .
```


Docker

```bash
docker build -t python-training-excercise .
```

```bash
docker run -dp 5005:5000 -w /app -v "$(pwd):/app" python-training-excercise
```
