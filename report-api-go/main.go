package main

import (
	"fmt"
	"log"

	"br.lanxcables.com/api/connection"
	"br.lanxcables.com/api/models"
)

func main() {
	
	client, err := connection.LoginOnCargaMaquina()
	if err != nil {
		log.Fatal(err)
	}

	materialPrice, err := models.GetMaterialPriceReport(client)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(materialPrice)
}
