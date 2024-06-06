package handler


import (
    "github.com/google/uuid"
)


// type Users struct {
// 	id       int
// 	username string
// 	password string
// }


func GenerateUUID() string {
    id := uuid.New()
    return id.String()
}


