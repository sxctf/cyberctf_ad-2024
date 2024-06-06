package main

import (
	"fmt"
	"smb/app/handler"
	_ "github.com/lib/pq"
	log "github.com/sirupsen/logrus"
	lumberjack "gopkg.in/natefinch/lumberjack.v2"
)
	
func main(){

	logPath := "./log/smr.log"
	logger := &lumberjack.Logger{
        Filename: logPath,
        MaxSize: 1,
        MaxBackups: 2,
        MaxAge: 10,
        Compress: true,
    }
	log.SetFormatter(&log.JSONFormatter{})
	log.SetOutput(logger)

	// Start Gin Server
	hanlers := new(handler.Handler)
	fmt.Println("Starting Gin server...")
	srv := new(handler.Server)
	if err := srv.Run("8080", hanlers.InitRoutes()); err != nil {
		log.Fatalf("error occured while running http server:% s", err.Error())
	}
}

