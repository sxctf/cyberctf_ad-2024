package utils

import (
	"os"
    "strconv"
    "fmt"
    "crypto/sha256"
    "log"
    "io/ioutil"
    "net/http"

    lumberjack "gopkg.in/natefinch/lumberjack.v2"
)

var (
	DB_USER string = os.Getenv("DB_USER")
	DB_PASS string = os.Getenv("DB_PASS")
	DB_HOST string = os.Getenv("DB_HOST")
	DB_PORT string = os.Getenv("DB_PORT")
	DB_NAME string = os.Getenv("DB_NAME")
    API_PORT int = getIntEnv("API_PORT")

    DEF_LOG string = "/var/log/services/boiler_room.log"
    SEC_LOG string = "/var/log/services/boiler_room_security.log"
)

func GenerateUUID(timestamp string) string {
    hash := sha256.Sum256([]byte(timestamp))
    sHash := fmt.Sprintf("%s", fmt.Sprintf("%x", hash))
    
    return sHash
}

func Contains(s []string, e string) bool {
    for _, a := range s {
        if a == e {
            return true
        }
    }
    return false
}

func SecurityLog(datetime string, level string, res string, function string, request *http.Request) {
    log.SetOutput(&lumberjack.Logger{
        Filename:   "/var/log/services/boiler_room_security.log",
        MaxSize:    3, 
    })
    log.SetFlags(log.Flags() &^ (log.Ldate | log.Ltime))
    body, _ := ioutil.ReadAll(request.Body)
    log.Printf("{\"event\": {\"datetime\": \"%s\", \"level\": \"%s\", \"result\": \"%s\", \"function\": \"%s\", \"user\": \"\", \"req\": \"%s\", \"reqdata\": \"%s\"}, \"agent\": {\"name\": \"%s\", \"ip\": \"%s\", \"type\": \"app\"}, \"fromhost\": \"%s\"}", datetime, level, res, function, request.URL.RequestURI(), body, "BOILER_ROOM_HOSTNAME", request.Host, request.Header.Get("X-Real-Ip"))
    
    log.SetOutput(&lumberjack.Logger{
        Filename:   "/var/log/services/boiler_room.log",
        MaxSize:    3, 
    })
    log.SetFlags(log.Flags() | log.Ldate | log.Ltime)
}

func DefaultLog(l string) {
    log.SetOutput(&lumberjack.Logger{
        Filename:   "/var/log/services/boiler_room.log",
        MaxSize:    3, 
    })
    log.SetFlags(log.Flags() | log.Ldate | log.Ltime)
    log.Println(l)
}

func getIntEnv(envName string) int {
    env, convErr := strconv.Atoi(os.Getenv(envName))

    if convErr == nil {
        return env
    } else {
        panic(convErr)

        return 0
    }
}