package br.lanxcables.com.automation.scraping;

import java.io.IOException;
import java.net.CookieManager;
import java.net.CookiePolicy;
import java.net.HttpCookie;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import br.lanxcables.com.automation.models.MaterialReport;

public class MaterialScraper {

    private HttpClient client;
    private String loginUrl = "https://v2.cargamaquina.com.br/site/login?c=3.1~13%2C3%5E17%2C7";
    private CookieManager cookie;
    //private String materialPriceUrl = "https://v2.cargamaquina.com.br/relatorio/catalogo/renderGridExportacaoMateriaisFornecedores";

    public MaterialScraper() {
        CookieManager cookieManager = new CookieManager();
        cookieManager.setCookiePolicy(CookiePolicy.ACCEPT_ALL);
        this.cookie = cookieManager;
        this.client = HttpClient.newBuilder()
                .cookieHandler(cookieManager)
                .build();
    }

    public String fetchCSRFToken() {
        try {
            HttpRequest getLogin = HttpRequest.newBuilder()
                    .uri(URI.create(loginUrl))
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(getLogin, HttpResponse.BodyHandlers.ofString());

            System.out.println("Get CRSF Token status: " + response.statusCode());

            Document doc = Jsoup.parse(response.body());

            Element csrfInput = doc.selectFirst("input[name=YII_CSRF_TOKEN]");
            if (csrfInput != null) {
                return csrfInput.attr("value");
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            System.out.println("Erro ao buscar CSRF token");
        }
        return null;
    }

    public void login(String csrfToken, String username, String password) {
        try {
            Map<String, String> params = Map.of(
                    "YII_CSRF_TOKEN", csrfToken,
                    "LoginForm[username]", username,
                    "LoginForm[password]", password,
                    "LoginForm[codigoConexao]", "3.1~13,3^17,7",
                    "yt0", "Entrar");

            String formData = params.entrySet().stream()
                    .map(e -> URLEncoder.encode(e.getKey(), StandardCharsets.UTF_8) + "=" +
                            URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8))
                    .collect(Collectors.joining("&"));

            HttpRequest loginRequest = HttpRequest.newBuilder()
                    .uri(URI.create(loginUrl))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(formData))
                    .build();

            HttpResponse<String> response = client.send(loginRequest, HttpResponse.BodyHandlers.ofString());
            response.headers().map().forEach((k, v) -> System.out.println(k + ": " + v));
            
            if (response.statusCode() < 400 && response.statusCode() >= 200) {
                System.out.println("Login successful");
            } else {
                System.out.println("Login failed with status: " + response.statusCode());
            }


        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            System.out.println("Erro ao fazer login");
        }
    }

    public String addParamsToUrl(String baseUrl) {

        Map<String, String> params = new HashMap<>();

        params.put("RelatorioMateriaisFornecedores[fornecedorId][]", "7322623");
        params.put("RelatorioMateriaisFornecedores[categoria]", "");
        params.put("idNovoTipoMaterialtipoMaterialId", "");
        params.put("nomeNovoTipoMaterialtipoMaterialId", "");
        params.put("txtNomeTipoMaterialModalmodalIncluirTipoMaterialSimplificadotipoMaterialId", "");
        params.put("RelatorioMateriaisFornecedores[tipo]", "");
        params.put("idNovoMaterialmaterialFaltaMP", "");
        params.put("novoMaterialmaterialFaltaMP", "");
        params.put("txtNomeMaterialModalmodalIncluirMaterialSimplificadomaterialFaltaMP", "");
        params.put("unidadeMedidaId", "");
        params.put("servicoIdModalmodalIncluirMaterialSimplificadomaterialFaltaMP", "");
        params.put("RelatorioMateriaisFornecedores[materialId]", "");
        params.put("RelatorioMateriaisFornecedores[status]", "A");
        params.put("RelatorioMateriaisFornecedores[kanban]", "");

        if (params == null || params.isEmpty()) {
            return baseUrl;
        }
        String paramString = params.entrySet().stream()
                .map(e -> URLEncoder.encode(e.getKey(), StandardCharsets.UTF_8) + "=" +
                        URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8))
                .collect(Collectors.joining("&"));
        return baseUrl + "?" + paramString;
    }

    public MaterialReport fetchMaterialPrice() {
        try {
            String finalUrl = addParamsToUrl("https://v2.cargamaquina.com.br/relatorio/catalogo/renderGridExportacaoMateriaisFornecedores");

            HashMap<String, String> cookies = new HashMap<>();
            for (HttpCookie c : cookie.getCookieStore().getCookies()) {
                System.out.println("Cookie: " + c.getName() + " = " + c.getValue());
                cookies.put(c.getName(), c.getValue());
            }

            StringBuilder cookieHeader = new StringBuilder();
            for (Map.Entry<String, String> entry : cookies.entrySet()) {
                if (cookieHeader.length() > 0) {
                    cookieHeader.append("; "); // separador entre cookies
                }
                cookieHeader.append(entry.getKey()).append("=").append(entry.getValue());
            }

            HttpRequest getMaterialPrice = HttpRequest.newBuilder()
                    .uri(URI.create(finalUrl))
                    .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
                    .header("Cookie", cookieHeader.toString())
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(getMaterialPrice, HttpResponse.BodyHandlers.ofString());
            System.out.println("Material price status: " + response.statusCode());

            Document doc = Jsoup.parse(response.body());
            Element table = doc.selectFirst("table");
            if (table != null) {
                List<String> headers = table.select("thead th").stream()
                        .map(Element::text)
                        .collect(Collectors.toList());
                List<Map<String, String>> rowsAsMaps = table.select("tbody tr").stream()
                                            .map(row -> {
                                                Elements cells = row.select("td");
                                                return IntStream.range(0, cells.size())
                                                        .boxed()
                                                        .collect(Collectors.toMap(headers::get, i -> cells.get(i).text()
                                                ));
                                            })
                                            .collect(Collectors.toList());

                MaterialReport report = new MaterialReport();
                report.fromListMap(rowsAsMaps);
            }

        } catch (IOException | InterruptedException e) {
            System.out.println("Erro ao buscar preços de materiais"+ e.getMessage());
        }
        return null;
    }
}