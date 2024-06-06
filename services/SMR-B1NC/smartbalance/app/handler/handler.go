package handler

import (
	"github.com/gin-gonic/gin"
)

type Handler struct {
	// services *service.Service
}


func (h *Handler) InitRoutes() *gin.Engine {

	
	router := gin.New()
	router.Static("/assets", "/application/assets")
	router.LoadHTMLGlob("/application/templates/*.html")

	auth := router.Group("/login")
	{
		auth.GET("", h.loginpage)
		auth.POST("", h.loginpage_auth)
	}
	
	regauth := router.Group("/registration")
	{
		regauth.GET("", h.regpage)
		regauth.POST("", h.regpage_auth)
	}

	index := router.Group("/")
	{
		index.GET("", h.mainpage)
	}

	colling := router.Group("/coolingSystem")
	{
		colling.GET("/image", h.cooling)
		colling.GET("", h.collingData)
		colling.POST("", h.collingData)
	}

	dashbord := router.Group("/dashboard")
	{
		dashbord.GET("", h.dashboard)
	}

	return router
}
