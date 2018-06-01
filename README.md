# fussball-elo
API endpoints to calculate ELO rating for a set of fussball matches

* Can be deployed to Heroku

## Startup instructions
```
python server.py [port-number]
```

## Endpoints

### GET /
Simplified scoreboard

### GET /ratings
#### Request
empty
#### Response
JSON list of ELO ratings

##### Example
```json
{
    "Alice": 1216,
    "Bob": 1216,
    "Clyde": 1184,
    "Dave": 1184
}
```

### GET /matches
#### Request
empty
#### Response
JSON list of logged matches
##### Example
```json
{
    "matches": [
        {
            "a_off": "Alice",
            "a_def": "Bob",
            "a_score": 10,
            "b_off": "Clyde",
            "b_def": "Dave",
            "b_score": 0
        }
    ]
}
```

## POST /matches
#### Request
A new match.
##### Example
```json
{
	"a_off": "Alice",
	"a_def": "Bob",
	"a_score": 10,
	"b_off": "Clyde",
	"b_def": "Dave",
	"b_score": 0
}
```

#### Response
```json
{
    "result": {}
}
```
