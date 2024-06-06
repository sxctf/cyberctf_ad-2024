package controller

import (
  "net/http"
  "encoding/json"
  "fmt"
  "os"
  "time"
  "io/ioutil"
  "os/exec"
  "regexp"
  "errors"

  "github.com/gorilla/websocket"
  "github.com/gorilla/mux"
 	"github.com/andreika47/BoilerRoom/model"
 	"github.com/andreika47/BoilerRoom/repository"
  "github.com/andreika47/BoilerRoom/utils"
)

var orderTypes = map[string]int{
  "Кружка чая": 15, 
  "Чашка кофе 3в1": 10, 
  "Порция пищи богов": 25, 
  "Порция бичпака": 25,
}

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}

type OrderControllerInterface interface {
  NewOrder(writer http.ResponseWriter, request *http.Request)
  CheckOrder(writer http.ResponseWriter, request *http.Request)
  GetOrder(writer http.ResponseWriter, request *http.Request)
  GetBill(writer http.ResponseWriter, request *http.Request)
  Orders(writer http.ResponseWriter, request *http.Request)
  Status(writer http.ResponseWriter, request *http.Request)
}

type OrderController struct {
 	OrderRepo       repository.OrderRepositoryInterface
}

func NewOrderController(orderRepo repository.OrderRepositoryInterface) OrderControllerInterface {
 	return &OrderController{OrderRepo: orderRepo}
}

func (o *OrderController) NewOrder(writer http.ResponseWriter, request *http.Request) {
  if request.Method == http.MethodHead {
    writer.WriteHeader(http.StatusOK)
  } else {
    timestamp := time.Now().Format(time.StampMilli)
    writer.Header().Set("Content-Type", "application/json")
    var post model.NewOrder
    jsonErr := json.NewDecoder(request.Body).Decode(&post)

    if jsonErr == nil {
      waitFor, matchType := orderTypes[post.Type]
      matchUsername, _ := regexp.MatchString(`^[a-zA-Z0-9\-_]{2,16}$`, post.Username)
      matchCoupon, _ := regexp.MatchString(`(?:^[a-zA-Z0-9=]{32}$|^$)`, post.Coupon)

      if matchType && matchUsername && matchCoupon {
        orderid := utils.GenerateUUID(timestamp)
        newErr := o.OrderRepo.NewOrder(orderid, post, timestamp)

        if newErr == nil {
          go func() {
            if len(post.Coupon) > 0 {
              waitFor -= 10
            }

            time.Sleep(time.Duration(waitFor) * time.Second)
            updateErr := o.OrderRepo.UpdateStatus(orderid, true)

            if updateErr != nil {
              utils.DefaultLog(fmt.Sprintf("UPDATEERR ON NEW ORDER: %v\nORDER: %s", orderid))
            }
          }()

          resp := model.Response{Result: "OK", Data: orderid}
          jsonErr = json.NewEncoder(writer).Encode(&resp)

          if jsonErr == nil {
            utils.DefaultLog(fmt.Sprintf("SUCCESS ON NEW ORDER\nUSER: %s", post.Username))
            utils.SecurityLog(timestamp, "INFO", "Success", "NewOrder", request)
            writer.WriteHeader(http.StatusOK)
          } else {
            utils.DefaultLog(fmt.Sprintf("RESPONSE JSON ERROR ON NEW ORDER: %v", jsonErr))
            utils.SecurityLog(timestamp, "ERROR", "Failed", "NewOrder", request)
            writer.WriteHeader(http.StatusOK)
          }
        } else {
          utils.DefaultLog(fmt.Sprintf("SQL ERROR ON NEW ORDER: %v\nUSER: %s\nORDER: %s\nCOUPON: %s", newErr, post.Username, post.Type, post.Coupon))
          utils.SecurityLog(timestamp, "ERROR", "Failed", "NewOrder", request)
          writer.WriteHeader(http.StatusOK)
        }
      } else {
        utils.DefaultLog(fmt.Sprintf("WRONG DATA ON NEW ORDER.\nUSERNAME: %s\nTYPE: %s\nCOUPON: %s", post.Username, post.Type, post.Coupon))
        utils.SecurityLog(timestamp, "ERROR", "Failed", "NewOrder", request)
        writer.WriteHeader(http.StatusBadRequest)
      }
    } else {
      utils.DefaultLog(fmt.Sprintf("REQUEST JSON ERROR ON NEW ORDER: %v", jsonErr))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "NewOrder", request)
      writer.WriteHeader(http.StatusBadRequest)
    }
  }
}

func (o *OrderController) CheckOrder(writer http.ResponseWriter, request *http.Request) {
  if request.Method == http.MethodHead {
    writer.WriteHeader(http.StatusOK)
  } else {
    timestamp := time.Now().Format(time.StampMilli)
    writer.Header().Set("Content-Type", "application/json")
    var post model.CheckOrder
    jsonErr := json.NewDecoder(request.Body).Decode(&post)

    if jsonErr == nil {
      requestURL := fmt.Sprintf("http://localhost:%d/internal/orders", utils.API_PORT)
      req, reqErr := http.NewRequest(http.MethodGet, requestURL, nil)

      if reqErr == nil {
        res, respErr := http.DefaultClient.Do(req)

        if respErr == nil {
          respBody, bodyErr := ioutil.ReadAll(res.Body)

          if bodyErr == nil {
            var resp model.OrdersResponse
            var orders []model.Order
            json.Unmarshal(respBody, &resp)
            orders = resp.Data
            isExist := false

            for _, order := range orders {
              if order.OrderId == post.OrderId {
                  isExist = true
                  break
              }
            }

            if isExist {
              resp := model.Response{Result: "OK", Data: isExist}
              jsonErr = json.NewEncoder(writer).Encode(&resp)

              if jsonErr == nil {
                utils.DefaultLog(fmt.Sprintf("SUCCESS ON CHECK ORDER\nORDER: %s", post.OrderId))
                utils.SecurityLog(timestamp, "INFO", "Success", "CheckOrder", request)
                writer.WriteHeader(http.StatusOK)
              } else {
                utils.DefaultLog(fmt.Sprintf("RESPONSE JSON ERROR ON CHECK ORDER: %v", jsonErr))
                utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
                writer.WriteHeader(http.StatusOK)
              }
            } else {
              resp := model.Response{Result: "NOT OK", Data: respBody}
              jsonErr = json.NewEncoder(writer).Encode(&resp)

              if jsonErr == nil {
                utils.DefaultLog(fmt.Sprintf("SUCCESS ON CHECK ORDER\nORDER: %s", post.OrderId))
                utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
                writer.WriteHeader(http.StatusNotFound)
              } else {
                utils.DefaultLog(fmt.Sprintf("RESPONSE JSON ERROR ON CHECK ORDER: %v", jsonErr))
                utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
                writer.WriteHeader(http.StatusNotFound)
              }
            }
          } else {
            utils.DefaultLog(fmt.Sprintf("PARSE BODY ERROR ON CHECK ORDER: %v", bodyErr))
            utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
            writer.WriteHeader(http.StatusOK)
          }
        } else {
          utils.DefaultLog(fmt.Sprintf("RESPONSE ERROR ON CHECK ORDER: %v", respErr))
          utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
          writer.WriteHeader(http.StatusOK)
        }
      } else {
        utils.DefaultLog(fmt.Sprintf("REQUEST ERROR ON CHECK ORDER: %v", reqErr))
        utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
        writer.WriteHeader(http.StatusOK)
      }
    } else {
      utils.DefaultLog(fmt.Sprintf("REQUEST JSON ERROR ON NEW ORDER: %v", jsonErr))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "CheckOrder", request)
      writer.WriteHeader(http.StatusBadRequest)
    }
  }
}

func (o *OrderController) GetOrder(writer http.ResponseWriter, request *http.Request) {
  if request.Method == http.MethodHead {
    writer.WriteHeader(http.StatusOK)
  } else {
    timestamp := time.Now().Format(time.StampMilli)
    writer.Header().Set("Content-Type", "application/json")
    orderid := mux.Vars(request)["orderid"]
    orderData, selectErr := o.OrderRepo.SelectById(orderid)

    if selectErr == nil {
      resp := model.Response{Result: "OK", Data: orderData}
      jsonErr := json.NewEncoder(writer).Encode(&resp)

      if jsonErr == nil {
        utils.DefaultLog(fmt.Sprintf("SUCCESS ON GET ORDER\nORDER: %s", orderid))
        utils.SecurityLog(timestamp, "INFO", "Success", "GetOrder", request)
        writer.WriteHeader(http.StatusOK)
      } else {
        utils.DefaultLog(fmt.Sprintf("RESPONSE JSON ERROR ON GET ORDER: %v", jsonErr))
        utils.SecurityLog(timestamp, "ERROR", "Failed", "GetOrder", request)
        writer.WriteHeader(http.StatusOK)
      }
    } else {
      utils.DefaultLog(fmt.Sprintf("SQL ERROR ON GET ORDER: %v\nORDER: %s", selectErr, orderid))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "GetOrder", request)
      writer.WriteHeader(http.StatusNotFound)
    }
  }
}

func (o *OrderController) GetBill(writer http.ResponseWriter, request *http.Request) {
  if request.Method == http.MethodHead {
    writer.WriteHeader(http.StatusOK)
  } else {
    timestamp := time.Now().Format(time.StampMilli)
    orderid := mux.Vars(request)["orderid"]
    filename := fmt.Sprintf("%s_for_%s.data", orderid, request.Header["True-Real-Ip"][len(request.Header["True-Real-Ip"]) - 1])
    filepath := fmt.Sprintf("/tmp/%s", filename)

    if _, err := os.Stat(filepath); errors.Is(err, os.ErrNotExist) {
      orderData, selectErr := o.OrderRepo.SelectById(orderid)

      if selectErr == nil {
        fileCmd := exec.Command("/bin/sh", "-c", fmt.Sprintf("touch %s", filepath))
        _, cmdErr := fileCmd.Output()

        if cmdErr == nil {
          file, fileErr := os.OpenFile(filepath, os.O_APPEND|os.O_WRONLY, os.ModeAppend)

          if fileErr == nil {
            billText := fmt.Sprintf("ID: %s\n====================\nКлиент: %s\n====================\n%s\n====================\nПромокод: %s\n====================\nДата и время: %s\n", orderData.OrderId, orderData.Username, orderData.Type, orderData.Coupon, orderData.Datetime)
            _, writeErr := file.WriteString(billText)

            if writeErr == nil {
              utils.SecurityLog(timestamp, "INFO", "Success", "GetBill", request)
            } else {
              utils.DefaultLog(fmt.Sprintf("WRITE TO FILE ERROR ON GET BILL: %v\nFILENAME: %s", writeErr, filename))
              utils.SecurityLog(timestamp, "ERROR", "Failed", "GetBill", request)
              writer.WriteHeader(http.StatusOK)
            }
            defer file.Close()
          } else {
            utils.DefaultLog(fmt.Sprintf("OPEN FILE ERROR ON GET BILL: %v\nFILENAME: %s", fileErr, filename))
            utils.SecurityLog(timestamp, "ERROR", "Failed", "GetBill", request)
            writer.WriteHeader(http.StatusOK)
          }
        } else {
          utils.DefaultLog(fmt.Sprintf("CREATE FILE ERROR ON GET BILL: %v\nFILENAME: %s", cmdErr, filename))
          utils.SecurityLog(timestamp, "ERROR", "Failed", "GetBill", request)
          writer.WriteHeader(http.StatusOK)
        }
      } else {
        utils.DefaultLog(fmt.Sprintf("SQL ERROR ON GET ORDER: %v\nORDER: %s", selectErr, orderid))
        utils.SecurityLog(timestamp, "ERROR", "Failed", "GetBill", request)
        writer.WriteHeader(http.StatusNotFound)
      }
    }

    writer.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", filename))
    file, fileErr := os.Open(filepath)

    if fileErr == nil {
      http.ServeContent(writer, request, filename, time.Now(), file)
      defer file.Close()
    } else {
      utils.DefaultLog(fmt.Sprintf("READ FILE BYTES ERROR ON GET BILL: %v\nFILENAME: %s", fileErr, filename))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "GetBill", request)
      writer.WriteHeader(http.StatusOK)
    }
  }
}

func (o *OrderController) Orders(writer http.ResponseWriter, request *http.Request) {
  if request.Method == http.MethodHead {
    writer.WriteHeader(http.StatusOK)
  } else {
    timestamp := time.Now().Format(time.StampMilli)
    writer.Header().Set("Content-Type", "application/json")
    ordersData, selectErr := o.OrderRepo.SelectAll()

    if selectErr == nil {
      resp := model.Response{Result: "OK", Data: ordersData}
      jsonErr := json.NewEncoder(writer).Encode(&resp)

      if jsonErr == nil {
        utils.DefaultLog(fmt.Sprintf("SUCCESS ON ORDERS"))
        utils.SecurityLog(timestamp, "INFO", "Success", "Orders", request)
        writer.WriteHeader(http.StatusOK)
      } else {
        utils.DefaultLog(fmt.Sprintf("RESPONSE JSON ERROR ON ORDERS: %v", jsonErr))
        utils.SecurityLog(timestamp, "ERROR", "Failed", "Orders", request)
        writer.WriteHeader(http.StatusOK)
      }
    } else {
      utils.DefaultLog(fmt.Sprintf("SQL ERROR ON ORDERS: %v\n", selectErr))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "Orders", request)
      writer.WriteHeader(http.StatusOK)
    }
  }
}

func (o *OrderController) Status(writer http.ResponseWriter, request *http.Request) {
  if request.Method == http.MethodHead {
    writer.WriteHeader(http.StatusOK)
  } else {
    timestamp := time.Now().Format(time.StampMilli)
    orderid := mux.Vars(request)["orderid"]
    conn, socketErr := upgrader.Upgrade(writer, request, nil)
    defer conn.Close()

    if socketErr == nil {
      utils.SecurityLog(timestamp, "INFO", "Success", "Status", request)
      go func() {
        for {
          orderData, selectErr := o.OrderRepo.SelectById(orderid)

          if selectErr == nil {
            writeErr := conn.WriteMessage(websocket.TextMessage, []byte(fmt.Sprintf("%t", orderData.Status)))

            if writeErr == nil {
              time.Sleep(1 * time.Second)
            } else {
              utils.DefaultLog(fmt.Sprintf("WRITE TO SOCKET ERROR ON CHECK ORDER: %v", writeErr))
              break
            }
          } else {
            utils.DefaultLog(fmt.Sprintf("SQL ERROR ON CHECK ORDER: %v", selectErr))
            break
          }
        }
        defer conn.Close()
      }()

      select {}
    } else {
      utils.DefaultLog(fmt.Sprintf("SOCKET ERROR ON CHECK ORDER: %v", socketErr))
      utils.SecurityLog(timestamp, "ERROR", "Failed", "Status", request)
      writer.WriteHeader(http.StatusOK)
    }
  }
}