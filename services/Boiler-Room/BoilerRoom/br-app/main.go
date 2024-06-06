package main

import (
    "github.com/andreika47/BoilerRoom/app"
)

func main() {
    var a app.App

    sqlErr := a.CreateConnection()

    if sqlErr != nil {
    	panic(sqlErr)
    }
    
    a.CreateRoutes()
    a.Run()
}