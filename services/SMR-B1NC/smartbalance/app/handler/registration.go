package handler

import (
	"context"
	"fmt"
	"net/http"
	"smb/pkg/api"
	"time"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
)


func (h *Handler) regpage(c *gin.Context){
	c.HTML(http.StatusOK, "register.html", nil)
}

func (h *Handler) regpage_auth(c *gin.Context){

	if c.Request.Form.Get("password") == c.Request.Form.Get("confirmpassword"){
		
		conn, err := grpc.Dial("172.26.0.4:50051", grpc.WithInsecure())
		if err != nil {
			log.Println(err)
		}	

		fmt.Println( c.Request.Form.Get("username") , c.Request.Form.Get("password"))
		c_grpc := api.NewSmartBalanceServiceClient(conn)
		req := &api.CreateUserRequest{Info: &api.User{Username: c.PostForm("username"), Password: c.PostForm("password")}}
		res, err := c_grpc.CreateUser(context.Background(), req)
		if err != nil{
			ip := c.Request.Header.Get("Origin")
			t := time.Now().Format("2006-01-02 15:04:05")
			event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Failed to create user", "user": "%s", "req": "/registration","reqdata": "%s:%s"}`, t, c.PostForm("username"), c.PostForm("username"), c.PostForm("password"))
			agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
			fromhost := fmt.Sprintf("%s", c.ClientIP())
			log.WithFields(log.Fields{
				"event":    string(event),
				"agent":    string(agent),
				"fromhost": string(fromhost),
			}).Info("Failed to create user")
		}

		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Successfully create user", "user": "%s", "req": "/registration","reqdata": "%s"}`, t, c.PostForm("username"), c.PostForm("username"))
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())
		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info(res.GetConfirm())

		c.HTML(http.StatusOK, "wellregister.html", gin.H{
			"confirm": res.GetConfirm(),
		  })

	}else {
		c.HTML(http.StatusOK, "wellregister.html", gin.H{
			"confirm": "Password doesn't match",
		  })
	}

}
