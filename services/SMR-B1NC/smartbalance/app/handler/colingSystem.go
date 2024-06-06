package handler

import (
	"context"
	"encoding/base64"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"smb/pkg/api"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
)

func (h *Handler) collingData(c *gin.Context) {

	if c.Request.Method == "GET" {

		c.HTML(http.StatusOK, "coolingInsert.html", nil)

		// Insert
	} else if c.Request.Method == "POST" && c.Request.FormValue("operation") == ("Insert") {

		err := c.Request.ParseForm()
		if err != nil {
			return
		}

		conn, err := grpc.Dial("172.26.0.4:50051", grpc.WithInsecure())
		if err != nil {
			log.Println(err)
		}

		c_grpc := api.NewSmartBalanceServiceClient(conn)
		req := &api.CoolingSystemRequest{Info: &api.CoolingSystem{Coolinglevel: c.PostForm("coolLevel"), Coolingfrequency: c.PostForm("coolFreq"), Coolingtype: c.PostForm("coolType")}}
		res, err := c_grpc.CoolingSystem(context.Background(), req)

		if err != nil {
			ip := c.Request.Header.Get("Origin")
			fmt.Println(ip)
			t := time.Now().Format("2006-01-02 15:04:05")
			event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Failed to insert data cooling system", "user": "", "req": "/coolingSystem","reqdata": "%s,%s,%s"}`, t, c.PostForm("coolLevel"), c.PostForm("coolFreq"), c.PostForm("coolType"))
			agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
			fromhost := fmt.Sprintf("%s", c.ClientIP())

			log.WithFields(log.Fields{
				"event":    string(event),
				"agent":    string(agent),
				"fromhost": string(fromhost),
			}).Info("Failed to insert data")
		}

		defer conn.Close()

		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Insert data coolingSystem", "user": "", "req": "/coolingSystem","reqdata": "%s,%s,%s"}`, t, c.PostForm("coolLevel"), c.PostForm("coolFreq"), c.PostForm("coolType"))
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())

		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Sucessfully insert data to coolingSystem")

		myfile, e := os.OpenFile("./cooling_audit.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0664)
		if e != nil {
			log.Printf("Problem with creating file: %s", e)
		}

		defer myfile.Close()

		data_to_file := []byte(res.GetRecord() + ";")
		myfile.Write(data_to_file)
		//fmt.Printf("\nData %s successfully written to file\n", data_to_file)

		c.HTML(http.StatusOK, "coolingResponse.html", gin.H{
			"res": res.GetRecord(),
		})

		// Check
	} else {

		id := c.Request.Form.Get("id")

		conn, err := grpc.Dial("172.26.0.4:50051", grpc.WithInsecure())
		if err != nil {
			log.Println(err)
		}

		c_grpc := api.NewSmartBalanceServiceClient(conn)
		req := &api.CoolingSystemGetRequest{Record: id}
		res, err := c_grpc.CoolingSystemCheck(context.Background(), req)

		if err != nil {
			ip := c.Request.Header.Get("Origin")
			t := time.Now().Format("2006-01-02 15:04:05")
			event := fmt.Sprintf(`{"datetime": "%s", "level" : "ERROR", "result" : "Failed", "function" : "Check data coolingSystem", "user": "", "req": "/coolingSystem","reqdata": "%s"}`, t, c.Request.Form.Get("id"))
			agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
			fromhost := fmt.Sprintf("%s", c.ClientIP())

			log.WithFields(log.Fields{
				"event":    string(event),
				"agent":    string(agent),
				"fromhost": string(fromhost),
			}).Info("Failed to get data from coolingSystem")
		}

		defer conn.Close()

		ip := c.Request.Header.Get("Origin")
		t := time.Now().Format("2006-01-02 15:04:05")
		event := fmt.Sprintf(`{"datetime": "%s", "level" : "INFO", "result" : "Success", "function" : "Check data coolingSystem", "user": "", "req": "/coolingSystem","reqdata": "%s"}`, t, c.Request.Form.Get("id"))
		agent := fmt.Sprintf(`{"name" : "docker", "ip" : "%s", "type": "app"}`, ip)
		fromhost := fmt.Sprintf("%s", c.ClientIP())

		log.WithFields(log.Fields{
			"event":    string(event),
			"agent":    string(agent),
			"fromhost": string(fromhost),
		}).Info("Successfully get data from coolingSystem")

		val := rand.Intn(4) + 1
		data, err := os.ReadFile(fmt.Sprintf("/application/assets/img/col%s.png", strconv.Itoa(val)))

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.HTML(http.StatusOK, "coolingCheck.html", gin.H{
			"res":   res,
			"image": base64.StdEncoding.EncodeToString(data),
		})
	}
}

func (h *Handler) cooling(c *gin.Context) {

	filename := c.Query("filename")
	data, err := os.ReadFile("/application/assets/img/" + filename)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.HTML(http.StatusOK, "image.html", gin.H{"image": base64.StdEncoding.EncodeToString(data)})
}
