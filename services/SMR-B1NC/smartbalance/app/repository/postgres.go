package repository

import (
	"fmt"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	log "github.com/sirupsen/logrus"
)

type Config struct{
	Host 		string
	Port 		string
	Username	string
	Password 	string
	DBName 		string
	SSLMode		string
}


func NewPangolinDB(cfg Config) (*sqlx.DB, error){
	db, err := sqlx.Open("postgres", fmt.Sprintf("host=%s port=%s user=%s dbname=%s password=%s sslmode=%s", 
		cfg.Host, cfg.Port, cfg.Username, cfg.DBName, cfg.Password, cfg.SSLMode))

	if err != nil{
		log.Println("NE TUT", err)
		return nil, err
	}

	err = db.Ping()
	if err != nil {
		log.Println("YA TUT", err)
		return nil, err
	}else {
		
		fmt.Println("Database connection successful...")
		return db, nil
	}
}