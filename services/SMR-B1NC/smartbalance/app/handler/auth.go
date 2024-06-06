package handler

import (
	"context"
	"net"
	"net/http"
	"smb/pkg/api"
	"time"
	"fmt"
	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
)

func (h *Handler) loginpage(c *gin.Context) {
	c.HTML(http.StatusOK, "login.html", nil)
}

func (h *Handler) loginpage_auth(c *gin.Context) {

	err := c.Request.ParseForm()
	if err != nil {
		return
	}

	conn, err := grpc.Dial("172.26.0.4:50051", grpc.WithInsecure())
	if err != nil {
		log.Println(err)
	}

	c_grpc := api.NewSmartBalanceServiceClient(conn)
	req := &api.CheckUserRequest{Info: &api.User{Username: c.PostForm("username"), Password: c.PostForm("password")}}
	res, err := c_grpc.CheckUser(context.Background(), req)
	if err != nil {
		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Failed to login user", "user": "%s", "req": "/login","reqdata": "%s:%s"}`, t, c.PostForm("username"), c.PostForm("username"), c.PostForm("password"))
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())

		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Failed to login user")
	}

	ip := c.Request.Header.Get("Origin")
	t := time.Now().Format("2006-01-02 15:04:05")
	event := fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Successfully login user", "user": "%s", "req": "/login","reqdata": "%s:%s"}`, t, c.PostForm("username"), c.PostForm("username"), c.PostForm("password"))
	agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
	fromhost := fmt.Sprintf("%s", c.ClientIP())

	log.WithFields(log.Fields{
		"event":    string(event),
		"agent":    string(agent),
		"fromhost": string(fromhost),
	}).Info("Success to login user")


	if res.GetToken() == "1" {
		token, err := generateJWT(c.PostForm("username"))

		if err != nil{
			ip := c.Request.Header.Get("Origin")
			t := time.Now().Format("2006-01-02 15:04:05")
			event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Generate jwt", "user": "%s", "req": "/login","reqdata": "%s"}`, t, c.PostForm("username"), c.PostForm("username"))
			agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
			fromhost := fmt.Sprintf("%s", c.ClientIP())
		
			log.WithFields(log.Fields{
				"event":    string(event),
				"agent":    string(agent),
				"fromhost": string(fromhost),
			}).Info("Failed to get JWT")
	
		}

		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Generate jwt", "user": "%s", "req": "/login","reqdata": "%s"}`, t, c.PostForm("username"), c.PostForm("username"))
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())
	
		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Success to get token")

		
		ipaddr := string(GetOutboundIP())
		c.SetCookie("Cookie", token, 3600, "/", ipaddr, false, true)
		c.HTML(http.StatusOK, "index.html", nil)
	}else {
		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Failed to login user", "user": "%s", "req": "/login","reqdata": "%s:%s"}`, t, c.PostForm("username"), c.PostForm("username"), c.PostForm("password"))
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())

		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Failed to login user")
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}

}

func GetOutboundIP() string {
    conn, err := net.Dial("udp", "8.8.8.8:80")
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()
    localAddr := conn.LocalAddr().(*net.UDPAddr)
    return localAddr.String()
}