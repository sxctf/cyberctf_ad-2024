package main

import (
	"fmt"
	"net"
	"os"
	"grpc_server/repository"
	"grpc_server/gFunctions"
	"grpc_server/pkg/api"

	_ "github.com/lib/pq"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
)


type GRPCserver struct {
	api.UnimplementedSmartBalanceServiceServer
}



func init(){
	repository.NewPangolinDB(repository.Config{
		Host: "172.26.0.2",
		Port: "5433",
		Username: "postgres",
		Password: "secret",
		DBName: "smartbalance",
		SSLMode: "disable",
	})
}

func main(){

	log.SetOutput(os.Stdout)
	fmt.Println("gRPC server running ...")

	lis, err := net.Listen("tcp", ":50051")
	if err != nil{
		fmt.Println(err)
	}

	s := grpc.NewServer()
	srv := &smartBalance.GRPCserver{}

	api.RegisterSmartBalanceServiceServer(s, srv)

	log.Printf("Server listening at %v", lis.Addr())

	if err := s.Serve(lis); err != nil {
		log.Errorf("failed to serve : %v", err)
	}

}
