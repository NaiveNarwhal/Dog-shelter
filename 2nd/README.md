## SECOND task
### Running
You need to have docker and docker-compose installed  
To build and run:
 

docker-compose build  

docker-compose up -d  
  
Ports 5000 and 81 are used for the services.  

### Queries for the second task
1. GET all visits from the used web service:
```
curl -i http://localhost:5000/visits
```  
2. GET visits that belong to the dog by its guardians ID
```
curl -i http://localhost:5000/dogs/<dog_id>/visits
```  
3. POST a new visit and add it to the list of visits of the dog
```
curl -i -X POST http://localhost:5000/dogs/<dog_id>/visits
```
4. DELETE an exisiting visit from the visit service and from the dogs' list of visits by the visit ID
```
curl -i -X DELETE http://localhost:5000/dogs/<dog_id>/visits/<visit_id>
```  

### Query examples

2. 
```
curl -i http://localhost:5000/dogs/4/visits
```  

3.
```
curl -i -X POST http://localhost:5000/dogs/4/visits
```

4.
```
curl -i -X DELETE http://localhost:5000/dogs/4/visits/1
```  