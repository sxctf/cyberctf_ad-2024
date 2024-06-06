package handler

import (
	"fmt"
	"os"
	"time"

	"github.com/golang-jwt/jwt/v4"
	log "github.com/sirupsen/logrus"
)


func generateJWT(username string) (string, error) {

	key, err := os.ReadFile("/application/cert/7a8e6b16-dec5-4500-873a-937f0d8e0c0a")

	if err != nil {
		log.Println("create: parse key:", err)
	}

	token := jwt.New(jwt.SigningMethodHS256)
	claims := token.Claims.(jwt.MapClaims)

	claims["authorized"] = true
	claims["sub"] = username
	claims["exp"] = time.Now().Add(time.Minute * 30).Unix()
	claims["aud"] = "intern"

	tokenString, err := token.SignedString(key)

	if err != nil {
		fmt.Printf("Something Went Wrong: %s", err.Error())
		return "", err
	}
	return tokenString, nil
}


func verifyJWT(tokenString string) (string, error){

	key, err := os.ReadFile("/application/cert/7a8e6b16-dec5-4500-873a-937f0d8e0c0a")

	if err != nil {
		log.Println("create: parse key:", err)
	}


	token, err := jwt.Parse(tokenString, func (token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			t := time.Now().Format("2006-01-02 15:04:05")
			event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Failed to parse JWT sign method", "user": "", "req": "/dashboard","reqdata": "%s"}`, t, tokenString)
			agent := fmt.Sprintf(`{"name" : "docker", "ip" : "", "type": "app"}`)
			log.WithFields(log.Fields{
				"event":    string(event),
				"agent":    string(agent),
				"fromhost": "",
			}).Info("Failed to parse JWT sign method")
			return nil, fmt.Errorf("there was an error in parsing")
		}
		return key, nil
	})


	if err != nil {
		return "", nil
	}

	if token.Valid {
		claims, ok := token.Claims.(jwt.MapClaims)

		if !ok {
			return "", nil
		}
		return claims["aud"].(string), nil
	}else {
		return "", nil
	}
	
}



