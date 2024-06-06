package smartBalance

import (
	"context"
	"fmt"
	"grpc_server/handler"
	"grpc_server/pkg/api"
	"grpc_server/repository"

	_ "github.com/lib/pq"
	log "github.com/sirupsen/logrus"
)

type GRPCserver struct {
	api.UnimplementedSmartBalanceServiceServer
}


// Insert info from CoolingSystem
func (s *GRPCserver) CoolingSystem(ctx context.Context, req *api.CoolingSystemRequest) (*api.CoolingSystemResponse, error) {

	db, err := repository.NewPangolinDB(repository.Config{
		Host:     "172.26.0.2",
		Port:     "5433",
		Username: "postgres",
		DBName:   "smartbalance",
		Password: "secret",
		SSLMode:  "disable",
	})

	if err != nil {
		log.Printf("failed to initialize db: %s", err.Error())
	}
	defer db.Close()

	row, err := db.Query(`CREATE TABLE IF NOT EXISTS coolingsystem( id varchar(70) PRIMARY KEY, CoolingLevel varchar(70) NOT NULL, CoolingFrequency varchar(70) NOT NULL, CoolingType varchar(70) NOT NULL);`)
	if err != nil {
		log.Printf("failed to create table: %s", err.Error())
	}
	// fmt.Println(row)
	defer row.Close()

	id := handler.GenerateUUID()
	stmt, prepErr := db.Prepare("INSERT INTO coolingsystem (id, CoolingLevel, CoolingFrequency, CoolingType) VALUES ($1, $2, $3, $4)")

	if prepErr == nil {
		_, execErr := stmt.Exec(id, req.GetInfo().Coolinglevel, req.GetInfo().Coolingfrequency, req.GetInfo().Coolingtype)
		defer stmt.Close()

		if execErr != nil {
			log.Println("error while inserting values", stmt)
		}
	}

	return &api.CoolingSystemResponse{Record: id}, nil
}

// Check info from CoolingSystem
func (s *GRPCserver) CoolingSystemCheck(ctx context.Context, req *api.CoolingSystemGetRequest) (*api.CoolingSystemGetResponse, error) {

	var data string
	db, err := repository.NewPangolinDB(repository.Config{
		Host:     "172.26.0.2",
		Port:     "5433",
		Username: "postgres",
		DBName:   "smartbalance",
		Password: "secret",
		SSLMode:  "disable",
	})

	if err != nil {
		log.Printf("failed to initialize db: %s", err.Error())
	}
	defer db.Close()

	stmt, prepErr := db.Prepare("SELECT * FROM coolingsystem WHERE id = $1")

	var id, coolingLevel, coolingFrequency, coolingType string

	if prepErr == nil {

		scanErr := stmt.QueryRow(req.Record).Scan(&id, &coolingLevel, &coolingFrequency, &coolingType)
		defer stmt.Close()
		fmt.Println(scanErr)

		data = fmt.Sprintf(`{"Record" : "%s", "CoolingLevel" : "%s", "CoolingFrequency" : "%s", "CoolingType" : "%s"}`, id, coolingLevel, coolingFrequency, coolingType)

		return &api.CoolingSystemGetResponse{Value: data}, nil
		}

		return &api.CoolingSystemGetResponse{Value: "failed to get data"}, nil
}
	

// Create User
func (s *GRPCserver) CreateUser(ctx context.Context, req *api.CreateUserRequest) (*api.CreateUserResponse, error) {

	db, err := repository.NewPangolinDB(repository.Config{
		Host:     "172.26.0.2",
		Port:     "5433",
		Username: "postgres",
		DBName:   "smartbalance",
		Password: "secret",
		SSLMode:  "disable",
	})

	if err != nil {
		log.Printf("failed to initialize db: %s", err.Error())
	}
	defer db.Close()

	id := handler.GenerateUUID()
	row, err := db.Query(`CREATE TABLE IF NOT EXISTS users( id varchar(70) PRIMARY KEY, Username varchar(70) NOT NULL, Password varchar(70) NOT NULL);`)
	if err != nil {
		log.Printf("failed to create table: %s", err.Error())
	}
	defer row.Close()

	stmt, prepErr := db.Prepare("SELECT EXISTS(SELECT 1 FROM users WHERE Username = $1)")

	var usercheck string
	if prepErr == nil {
		scanErr := stmt.QueryRow(req.GetInfo().Username).Scan(&usercheck)
		defer stmt.Close()

		if scanErr == nil {

			if usercheck == "true"{
				log.Printf("trying to add existing user: %s", req.GetInfo().Username)
				return &api.CreateUserResponse{Confirm: "such a user already exists"}, err
			}
			
		}
	}


	stmt, prepErr = db.Prepare("INSERT INTO users (id, Username, Password) VALUES ($1, $2, $3)")

	if prepErr == nil {
		_, execErr := stmt.Exec(id, req.GetInfo().Username, req.GetInfo().Password)
		defer stmt.Close()

		if execErr != nil {
			log.Println("error while inserting values", stmt)
			return &api.CreateUserResponse{Confirm: "User hasn't created"}, err
		}
	}

	return &api.CreateUserResponse{Confirm: "User has successfully created"}, err
}

func (s *GRPCserver) CheckUser(ctx context.Context, req *api.CheckUserRequest) (*api.CheckUserResponse, error) {

	db, err := repository.NewPangolinDB(repository.Config{
		Host:     "172.26.0.2",
		Port:     "5433",
		Username: "postgres",
		DBName:   "smartbalance",
		Password: "secret",
		SSLMode:  "disable",
	})

	if err != nil {
		log.Printf("failed to initialize db: %s", err.Error())
	}
	defer db.Close()

	stmt, prepErr := db.Prepare("SELECT Password FROM users WHERE Username = $1")

	var passwd string
	var token string
	if prepErr == nil {

		scanErr := stmt.QueryRow(req.GetInfo().Username).Scan(&passwd)
		defer stmt.Close()

		if scanErr == nil {

			if passwd == req.GetInfo().Password {
				token = "1"
				return &api.CheckUserResponse{Token: token}, nil

			} else {

				token = "0"
				return &api.CheckUserResponse{Token: token}, nil
			}

		}

	}
	return &api.CheckUserResponse{Token: "Failed to create token"}, nil
}

func (s *GRPCserver) Dashboard(ctx context.Context, req *api.DashboardRequest) (*api.DashboardResponse, error) {

	db, err := repository.NewPangolinDB(repository.Config{
		Host:     "172.26.0.2",
		Port:     "5433",
		Username: "postgres",
		DBName:   "smartbalance",
		Password: "secret",
		SSLMode:  "disable",
	})

	if err != nil {
		log.Printf("failed to initialize db: %s", err.Error())
	}
	defer db.Close()

	rows, err := db.Query("SELECT * FROM coolingsystem")
    if err != nil {
        return nil, err
    }
    defer rows.Close()	


	// type Record struct {
	// 	// Id					string
	// 	CoolingLevel		string
	// 	CoolingFrequency 	string
	// 	CoolingType			string
	// }

	
	var data []*api.CoolingSystem

	for rows.Next() {
        var val api.CoolingSystem
		var id string 
        if err := rows.Scan(&id, &val.Coolinglevel, &val.Coolingfrequency, &val.Coolingtype); err != nil {
            return &api.DashboardResponse{Info: data}, err
        }
        data = append(data, &val)
	}

	if err = rows.Err(); err != nil {
        return &api.DashboardResponse{Info: data}, err
    }
	return &api.DashboardResponse{Info: data}, nil
}
