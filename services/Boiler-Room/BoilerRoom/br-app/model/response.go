package model

type Response struct {
	Result    string `json:"result"`
    Data      any    `json:"data"`
}

type OrdersResponse struct {
	Result    string  `json:"result"`
    Data      []Order `json:"data"`
}