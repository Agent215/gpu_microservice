## GPU MICRO SERVICE

### A service for finding available GPUS from bestbuy

API swagger documentation:
https://agent215.github.io/gpu_microservice/


### Database config
I am using a postgresql datbase being hosted on https://www.elephantsql.com/ for free.
once you have created your account you can replace with your credentials in to the database_copy.ini file.
remove the "copy" string so that the file name is now just database.ini

then create a table called gpu  in your new table with the fields listed below.
## postgresql talblename : gpus  
- sku_value : # this is the primary key
- card_name :
- available : 


### Install dependencies

- install vitrual environment for python ``` python3 -m venv env ``` 
- if on macOS/Linux ```source env/bin/activate```
- other wise if on windows ```.\env\Scripts\activate```
- while in the root directory run ```pip install -r requirements.txt``` to install python module dependencies
 
### Instructions to run

- to run the application ```uvicorn main:app --reload```


- to exit virtual environment ```deactivate```
