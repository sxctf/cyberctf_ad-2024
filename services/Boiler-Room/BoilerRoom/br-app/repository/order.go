package repository

import (
	"database/sql"

	"github.com/andreika47/BoilerRoom/model"
)

type OrderRepository struct {
	DB *sql.DB
}

type OrderRepositoryInterface interface {
	NewOrder(orderid string, post model.NewOrder, datetime string) error
	UpdateStatus(orderid string, status bool) error
	SelectById(orderid string) (model.Order, error)
	SelectAll() ([]model.Order, error)
}

func NewOrderRepository(db *sql.DB) OrderRepositoryInterface {
	return &OrderRepository{DB: db}
}

func (o *OrderRepository) NewOrder(orderid string, post model.NewOrder, datetime string) error {
	stmt, prepErr := o.DB.Prepare("INSERT INTO orders (orderid, type, username, coupon, datetime, status) VALUES ($1, $2, $3, $4, $5, $6)")

	if prepErr == nil {
		coupon := ""

		if &post.Coupon != nil {
			coupon = post.Coupon
		}
	 	_, execErr := stmt.Exec(orderid, post.Type, post.Username, coupon, datetime, false)
 		defer stmt.Close()

 		return execErr
	} else {
		return prepErr
 	}
}

func (o *OrderRepository) UpdateStatus(orderid string, status bool) error {
	stmt, prepErr := o.DB.Prepare("UPDATE orders SET status = $2 WHERE orderid = $1")

	if prepErr == nil {
		_, execErr := stmt.Exec(orderid, status)
 		defer stmt.Close()

 		return execErr
	} else {
		return prepErr
 	}
}

func (o *OrderRepository) SelectById(orderid string) (model.Order, error) {
	var order model.Order
	stmt, prepErr := o.DB.Prepare("SELECT * FROM orders WHERE orderid = $1")

	if prepErr == nil {
		queryErr := stmt.QueryRow(orderid).Scan(&order.OrderId, &order.Type, &order.Username, &order.Coupon, &order.Datetime, &order.Status)
 		defer stmt.Close()

 		return order, queryErr
	} else {
		return order, prepErr
	}
}

func (o *OrderRepository) SelectAll() ([]model.Order, error) {
	var result []model.Order
	rows, queryErr := o.DB.Query("SELECT * FROM orders")

	if queryErr == nil {
		defer rows.Close()
		for rows.Next() {
			var (
				orderid     string
		   		ordertype   string
		   		username    string
		   		coupon      string
		   		datetime    string
		   		status      bool
		  	)
			scanErr := rows.Scan(&orderid, &ordertype, &username, &coupon, &datetime, &status)

			if scanErr == nil {
				order := model.Order{OrderId: orderid, Type: ordertype, Username: username, Datetime: datetime, Coupon: coupon, Status: status}
		   		result = append(result, order)
			} else {
	       		return result, scanErr
		  	}
		}

		return result, nil
	} else if queryErr == sql.ErrNoRows {
		return result, nil
	} else {
		return result, queryErr
	}
}