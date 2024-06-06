package app

import (
    "net/http"
    "database/sql"
    "fmt"

    _ "github.com/lib/pq"
    "github.com/gorilla/mux"
    "github.com/andreika47/BoilerRoom/controller"
    "github.com/andreika47/BoilerRoom/utils"
    "github.com/andreika47/BoilerRoom/repository"
)

type App struct {
    DB          *sql.DB
    Router      *mux.Router
}

func (a *App) CreateConnection() error {
    connStr := fmt.Sprintf("host=%s port=%s user=%s " + "password=%s dbname=%s sslmode=disable", utils.DB_HOST, utils.DB_PORT, utils.DB_USER, utils.DB_PASS, utils.DB_NAME)
    db, openErr := sql.Open("postgres", connStr)

    if openErr == nil {
        pingErr := db.Ping()

        if pingErr == nil {
            a.DB = db
            utils.DefaultLog("DB IS OK")

            return nil
        } else {
            utils.DefaultLog(fmt.Sprintf("PINGERR: %v", pingErr))

            return pingErr
        }
    } else {
        utils.DefaultLog(fmt.Sprintf("OPENERR: %v", openErr))

        return openErr
    }
}

func (a *App) CreateRoutes() {
    router := mux.NewRouter()
    orderRepo := repository.NewOrderRepository(a.DB)
    orderController := controller.NewOrderController(orderRepo)
    utilsController := controller.NewUtilsController()

    router.HandleFunc("/api/new_order", orderController.NewOrder).Methods("POST", "HEAD")
    router.HandleFunc("/api/check_order", orderController.CheckOrder).Methods("POST", "HEAD")
    router.HandleFunc("/api/order/{orderid}", orderController.GetOrder).Methods("GET", "HEAD")
    router.HandleFunc("/api/status/{orderid}", orderController.Status).Methods("GET", "HEAD")
    router.HandleFunc("/api/bill/{orderid}", orderController.GetBill).Methods("GET", "HEAD")
    router.HandleFunc("/internal/orders", orderController.Orders).Methods("GET", "HEAD")
    router.HandleFunc("/api/healthcheck/", utilsController.HealthCheck)

    a.Router = router
}

func (a *App) Run(){
    http.ListenAndServe(fmt.Sprintf(":%d", utils.API_PORT), a.Router)
}