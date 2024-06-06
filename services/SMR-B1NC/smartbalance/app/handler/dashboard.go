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

type CoolingSystemObject struct {
	CoolingLevel,
    CoolingFrequency,
    CoolingType string 
}

func (h *Handler) dashboard(c *gin.Context){
	
	cookie, err := c.Cookie("Cookie")
	
	log.Println(cookie)

	if err != nil {
		cookie = "NotSet"
		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "WARNING", "result" : "Failed", "function" : "Get cookie", "user": "%s", "req": "/dashboard","reqdata": "%s"}`, t, c.PostForm("username"), cookie)
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())

		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Unable to get Cookie")
		c.HTML(http.StatusOK,"index.html", gin.H{
			"result": "Unable to get Cookie",
		  })
	}

	ip := c.Request.Header.Get("Origin")
	t := time.Now().Format("2006-01-02 15:04:05")
	event := fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Get cookie", "user": "%s", "req": "/dashboard","reqdata": "%s"}`, t, c.PostForm("username"), cookie)
	agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
	fromhost := fmt.Sprintf("%s", c.ClientIP())

	log.WithFields(log.Fields{
		"event":    string(event),
		"agent":    string(agent),
		"fromhost": string(fromhost),
	}).Info("Success to get Cookie")

	//Verify JWT
	verify, err := verifyJWT(cookie)
	if err != nil {
		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Verify JWT", "user": "%s", "req": "/dashboard","reqdata": "%s"}`, t, c.PostForm("username"), cookie)
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())

		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Failed to verify JWT")
	}

	ip = c.Request.Header.Get("Origin")
	t = time.Now().Format("2006-01-02 15:04:05")
	event = fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Verify JWT", "user": "%s", "req": "/dashboard","reqdata": "%s"}`, t, c.PostForm("username"), cookie)
	agent = fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
	fromhost = fmt.Sprintf("%s", c.ClientIP())

	log.WithFields(log.Fields{
		"event":    string(event),
		"agent":    string(agent),
		"fromhost": string(fromhost),
	}).Info("Success to verify JWT")

	//log.Println("TOKEN SIGN", verify)
	
	if verify == "administrator" {

		conn, err := grpc.Dial("172.26.0.4:50051", grpc.WithInsecure())
		if err != nil {
			log.Println(err)
		}

		c_grpc := api.NewSmartBalanceServiceClient(conn)
		req := &api.DashboardRequest{Flag: "all"}
		res, err := c_grpc.Dashboard(context.Background(), req)
		coolSystArray := res.GetInfo()
		// log.Println(coolSystArray)
		coolSysObject := []CoolingSystemObject{}
		for _, val := range coolSystArray {
			coolSysObject = append(coolSysObject, CoolingSystemObject{val.Coolinglevel, val.Coolingfrequency, val.Coolingtype})
		}
		c.HTML(http.StatusOK, "admin.html", gin.H{
			"Data": coolSysObject,
		  })
	}else {
		c.HTML(http.StatusOK, "index.html", gin.H{
			"result": "You don't have permission to look this page",
		  })
	}

}