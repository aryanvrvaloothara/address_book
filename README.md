step 1:
Create virtual environment and activate the environment.

step 2:
Install packages in requirements.txt file 

    pip install requirements.txt

step 3:
Change directory path to the file where the 'main.py' file exists.

step 4:
Run the app using 

    uvicorn main:app --reload


Swagger api documentation can be seen in the url http://localhost:8000/docs#/

**Api details**

The app has four apis

1. _/user/signup/_  -  for user signup
2. _/user/login/_  -  for user login, tokengeneration
3. _/address/_  =  for adding address
4. /address/{radius}/{latitude}/{longitude}/  -  for finding the nearest address.
    
    radius - The distance to within which the addresses to be taken.
    latitude, longitude - The coordinates of the user location around which the address to be found.