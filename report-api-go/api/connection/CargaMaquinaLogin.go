package connection

import (
	"fmt"
	"log"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"github.com/PuerkitoBio/goquery"
)


func LoginOnCargaMaquina() (*http.Client, error) {
	jar, _ := cookiejar.New(nil)
	client := &http.Client{Jar: jar}

	loginURL := "https://app.cargamaquina.com.br/site/login?c=3.1%7E13%2C3%5E17%2C7"
	resp, err := client.Get(loginURL)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	loginBody, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		log.Fatal(err)
	}
	csrfToken, exists := loginBody.Find("input[name=YII_CSRF_TOKEN]").Attr("value")
	if !exists {
		log.Fatal("Não encontrou o YII_CSRF_TOKEN")
	}
	fmt.Println("CSRF Token:", csrfToken)

	loginPayload := url.Values{
		"YII_CSRF_TOKEN":        {csrfToken},
		"LoginForm[username]":   {"username"},
		"LoginForm[password]":   {"password"},
		"LoginForm[codigoConexao]": {"3.1~13,3^17,7"},
		"yt0":                   {"Entrar"},
	}

	loginResponse, err := client.PostForm(loginURL, loginPayload)
	if err != nil {
		log.Fatal(err)
	}
	defer loginResponse.Body.Close()

	fmt.Println("Resposta login:", loginResponse.StatusCode)
	fmt.Println("Resposta Cookies:", loginResponse.Cookies())

	return client, nil
}
