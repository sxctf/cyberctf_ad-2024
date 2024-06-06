package controller

import (
  "net/http"
  "strings"
  "time"
  "fmt"

  "github.com/andreika47/BoilerRoom/utils"
)

type UtilsControllerInterface interface {
  HealthCheck(writer http.ResponseWriter, request *http.Request)
}

type UtilsController struct {
}

func NewUtilsController() UtilsControllerInterface {
 	return &UtilsController{}
}

func (u *UtilsController) HealthCheck(writer http.ResponseWriter, request *http.Request) {
  urlToCheck := request.URL.Query().Get("url")
  timestamp := time.Now().Format(time.StampMilli)

  if strings.Contains(urlToCheck, "http") && strings.Contains(urlToCheck, "localhost") {
    req, reqErr := http.NewRequest(http.MethodHead, urlToCheck, nil)

    if reqErr == nil {
      resp, respErr := http.DefaultClient.Do(req)

      if respErr == nil {
        writer.WriteHeader(resp.StatusCode)
        utils.DefaultLog(fmt.Sprintf("SUCCESS ON HEALTHCHECK\nURL: %s\nSTATUS CODE: %s", urlToCheck, resp.StatusCode))
        utils.SecurityLog(timestamp, "INFO", "Success", "HealthCheck", request)

      } else {
        utils.DefaultLog(fmt.Sprintf("RESPONSE ERROR ON HEALTHCHECK: %v\nURL: %s", respErr, urlToCheck))
        utils.SecurityLog(timestamp, "ERROR", "Failed", "HealthCheck", request)
      }
    } else {
      utils.DefaultLog(fmt.Sprintf("REQUEST ERROR ON HEALTHCHECK: %v\nURL: %s", reqErr, urlToCheck))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "HealthCheck", request)
    }
  } else {
    utils.DefaultLog(fmt.Sprintf("EXTERNAL URL ON HEALTHCHECK\nURL: %s", urlToCheck))
    utils.SecurityLog(timestamp, "ERROR", "Failed", "HealthCheck", request)
  }
}