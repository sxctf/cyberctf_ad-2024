package model

type Order struct {
	OrderId    string `json:"orderid"`
    Type       string `json:"type"`
    Username   string `json:"username"`
    Coupon     string `json:"coupon"`
    Datetime   string `json:"datetime"`
    Status     bool   `json:"status"`
}

type NewOrder struct {
    Type       string `json:"type" binding:"required"`
    Username   string `json:"username" binding:"required"`
    Coupon     string `json:"coupon"`
}

type CheckOrder struct {
	OrderId    string `json:"orderid" binding:"required"`
}