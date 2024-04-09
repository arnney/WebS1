# Web Service Task 1 using Python Flask & Mongo DB
Supplement store. Entities: 1) Brand, 2) Supplement

You can test API  on 
> http://localhost:5000/swagger

Usage:
```
git clone https://github.com/arnney/WebS1
cd WebS1
docker-compose up --build
```


Brand object:
```
  {
    "country": "string",
    "id": "string",
    "name": "string"
  }
```

Supplement object:
```
  {
    "brand_id": "string",
    "description": "string",
    "id": "string",
    "name": "string",
    "price": 0
  }
```



