package br.lanxcables.com.automation;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import br.lanxcables.com.automation.scraping.MaterialScraper;

@SpringBootApplication
public class AutomationApplication {

	public static void main(String[] args) {
		SpringApplication.run(AutomationApplication.class, args);

		MaterialScraper scraper = new MaterialScraper();

		String csrfToken = scraper.fetchCSRFToken();
		System.out.println("CSRF Token: " + csrfToken);

		// 2. Login
		scraper.login(csrfToken, "user", "password");

		// 3. Fetch Material Prices
		scraper.fetchMaterialPrice();

	}

}
