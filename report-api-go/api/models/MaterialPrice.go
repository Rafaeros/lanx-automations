package models

import (
	"fmt"
	"log"
	"net/url"
	"net/http"
	"github.com/PuerkitoBio/goquery"
)

type MaterialPriceHeaders struct {
	attributes map[string]string
}

type MaterialPrice struct {
	attributes map[string]string
}


func GetMaterialPriceReport(client *http.Client) ([]MaterialPrice, error) {
	var data []MaterialPrice

	materialPriceURL := "https://.cargamaquina.com.br/relatorio/catalogo/renderGridExportacaoMateriaisFornecedores"

	// Montando os parâmetros
	params := url.Values{}
	params.Add("RelatorioMateriaisFornecedores[fornecedorId][]", "7322623")
	params.Add("RelatorioMateriaisFornecedores[categoria]", "")
	params.Add("idNovoTipoMaterialtipoMaterialId", "")
	params.Add("nomeNovoTipoMaterialtipoMaterialId", "")
	params.Add("txtNomeTipoMaterialModalmodalIncluirTipoMaterialSimplificadotipoMaterialId", "")
	params.Add("RelatorioMateriaisFornecedores[tipo]", "")
	params.Add("idNovoMaterialmaterialFaltaMP", "")
	params.Add("novoMaterialmaterialFaltaMP", "")
	params.Add("txtNomeMaterialModalmodalIncluirMaterialSimplificadomaterialFaltaMP", "")
	params.Add("unidadeMedidaId", "")
	params.Add("servicoIdModalmodalIncluirMaterialSimplificadomaterialFaltaMP", "")
	params.Add("RelatorioMateriaisFornecedores[materialId]", "")
	params.Add("RelatorioMateriaisFornecedores[status]", "A")
	params.Add("RelatorioMateriaisFornecedores[kanban]", "")

	materialPriceURL = fmt.Sprintf("%s?%s", materialPriceURL, params.Encode())
	reportResponse, err := client.Get(materialPriceURL)
	if err != nil {
		log.Fatal(err)
		return data, err
	}
	defer reportResponse.Body.Close()

	reportBody, err := goquery.NewDocumentFromReader(reportResponse.Body)
	headers := reportBody.Find("thead th").Map(func(i int, s *goquery.Selection) string {
		return s.Text()
	})
	fmt.Println("HEADERS:", headers)

}




