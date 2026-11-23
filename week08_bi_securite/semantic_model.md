# Modèle sémantique (Direct Lake sur lh_gold)

## Tables
`fact_production`, `fact_consumption_weather`, `dim_date`, `dim_source`, `dim_city`.

## Relations
- `fact_production[date_key]` → `dim_date[date_key]` (n:1)
- `fact_production[source_key]` → `dim_source[source_key]` (n:1)
- `fact_consumption_weather[date_key]` → `dim_date[date_key]` (n:1)
- `fact_consumption_weather[city_key]` → `dim_city[city_key]` (n:1)

## Attention au grain
`fact_consumption_weather` est au grain **heure x ville** : la consommation nationale y est répétée pour chaque ville.
Utilise toujours **AVERAGE** pour la consommation et le CO2, jamais SUM.

## Mesures DAX
```dax
Production totale (MW) = SUM(fact_production[production_mw])

Production renouvelable (MW) =
CALCULATE([Production totale (MW)], dim_source[is_renewable] = TRUE())

Part renouvelable % = DIVIDE([Production renouvelable (MW)], [Production totale (MW)])

Consommation moyenne (MW) = AVERAGE(fact_consumption_weather[consumption_mw])

CO2 moyen (g/kWh) = AVERAGE(fact_consumption_weather[co2_g_per_kwh])

Température moyenne (°C) = AVERAGE(fact_consumption_weather[temperature_c])
```

## Bonnes pratiques
- Masquer les clés techniques, formater les mesures, renseigner les descriptions.
- Table de dates marquée comme table de dates.
- Direct Lake : après un MERGE Gold, le modèle voit les nouvelles données au prochain rafraîchissement (actualiser le cadre).
