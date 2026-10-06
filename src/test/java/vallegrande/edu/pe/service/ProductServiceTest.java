package vallegrande.edu.pe.service;

import org.junit.jupiter.api.Test;
import vallegrande.edu.pe.model.Product;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ProductServiceTest {

    private final ProductService service = new ProductService();

    @Test
    void shouldReturnFiveProducts() {
        assertEquals(5, service.getProducts().size());
    }

    @Test
    void shouldProcessValidEmptyAndNullNames() {
        assertEquals("Producto procesado: Laptop", service.processProduct("Laptop"));
        assertEquals("Producto vacío", service.processProduct(""));
        assertEquals("Producto no válido", service.processProduct(null));
    }

    @Test
    void shouldValidateOnlyCompleteProductsWithPositivePrice() {
        assertTrue(service.validateProduct(new Product(1, "Laptop", 2500.0)));
        assertFalse(service.validateProduct(new Product(2, "", 80.0)));
        assertFalse(service.validateProduct(new Product(3, "Mouse", 0.0)));
        assertFalse(service.validateProduct(null));
    }
}
