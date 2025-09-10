package br.lanxcables.com.automation.models;

import java.util.Date;
import java.util.Map;
import java.util.List;

abstract class AbstractMaterialPrice {
    private String code;
    private float price;
    private short icms;
    private float ipi;
    private float pis;
    private float cofins;


    AbstractMaterialPrice(String code, float price, short icms, float ipi, float pis, float cofins) {
        this.code = code;
        this.price = price;
        this.icms = icms;
        this.ipi = ipi;
        this.pis = pis;
        this.cofins = cofins;
    }


    public String getCode() {
        return code;
    }


    public float getPrice() {
        return price;
    }


    public short getIcms() {
        return icms;
    }


    public float getPis() {
        return pis;
    }


    public float getCofins() {
        return cofins;
    }


    public void setCode(String code) {
        this.code = code;
    }


    public void setPrice(float price) {
        this.price = price;
    }


    public void setIcms(short icms) {
        this.icms = icms;
    }


    public void setPis(float pis) {
        this.pis = pis;
    }


    public void setCofins(float cofins) {
        this.cofins = cofins;
    }


    public float getIpi() {
        return ipi;
    }


    public void setIpi(float ipi) {
        this.ipi = ipi;
    }
}

class MaterialPrice extends AbstractMaterialPrice {
    private String description;
    private String category;
    private String origin;
    private String currencyType;
    private boolean principal;
    private float liquidCost;
    private float structureLiquidCost;
    private int ncm;
    private Date updatedAt;
    private boolean kanban;


    MaterialPrice(String code, String description, String category, String origin, String currencyType, boolean principal, float price, short icms, float ipi, float liquidCost, float structureLiquidCost, int ncm, boolean kanban, Date updatedAt, float pis, float cofins) {
        super(code, price, icms, ipi, pis, cofins);
        this.description = description;
        this.category = category;
        this.origin = origin;
        this.currencyType = currencyType;
        this.principal = principal;
        this.liquidCost = liquidCost;
        this.structureLiquidCost = structureLiquidCost;
        this.ncm = ncm;
        this.updatedAt = updatedAt;
        this.kanban = kanban;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getOrigin() {
        return origin;
    }

    public void setOrigin(String origin) {
        this.origin = origin;
    }

    public String getCurrencyType() {
        return currencyType;
    }

    public void setCurrencyType(String currencyType) {
        this.currencyType = currencyType;
    }

    public boolean isPrincipal() {
        return principal;
    }

    public void setPrincipal(boolean principal) {
        this.principal = principal;
    }

    public float getLiquidCost() {
        return liquidCost;
    }

    public void setLiquidCost(float liquidCost) {
        this.liquidCost = liquidCost;
    }

    public float getStructureLiquidCost() {
        return structureLiquidCost;
    }

    public void setStructureLiquidCost(float structureLiquidCost) {
        this.structureLiquidCost = structureLiquidCost;
    }

    public int getNcm() {
        return ncm;
    }

    public void setNcm(int ncm) {
        this.ncm = ncm;
    }

    public Date getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Date updatedAt) {
        this.updatedAt = updatedAt;
    }

    public boolean isKanban() {
        return kanban;
    }

    public void setKanban(boolean kanban) {
        this.kanban = kanban;
    }
}

class SupplierMaterialPrice extends AbstractMaterialPrice {
    private int leadTime;
    private float moq;
    private float multipleLot;

    SupplierMaterialPrice(String code, float price, short icms, float ipi, float pis, float cofins, int leadTime, float moq, float multipleLot) {
        super(code, price, icms, ipi, pis, cofins);
        this.leadTime = leadTime;
        this.moq = moq;
        this.multipleLot = multipleLot;
    }

    public int getLeadTime() {
        return leadTime;
    }

    public void setLeadTime(int leadTime) {
        this.leadTime = leadTime;
    }

    public float getMoq() {
        return moq;
    }

    public void setMoq(float moq) {
        this.moq = moq;
    }

    public float getMultipleLot() {
        return multipleLot;
    }

    public void setMultipleLot(float multipleLot) {
        this.multipleLot = multipleLot;
    }
}

public class MaterialReport {
    private MaterialPrice lanxMaterial;
    private SupplierMaterialPrice supplierMaterial;

    public MaterialPrice getLanxMaterial() {
        return lanxMaterial;
    }

    public void setLanxMaterial(MaterialPrice lanxMaterial) {
        this.lanxMaterial = lanxMaterial;
    }

    public SupplierMaterialPrice getSupplierMaterial() {
        return supplierMaterial;
    }

    public void setSupplierMaterial(SupplierMaterialPrice supplierMaterial) {
        this.supplierMaterial = supplierMaterial;
    }

    public void fromListMap(List<Map<String, String>> materialDataMap) {
    }

}