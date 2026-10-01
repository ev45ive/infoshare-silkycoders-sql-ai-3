# Handoff: konwencje projektowania hurtowni danych 2026

## Kontekst
- Użytkownik pisze po polsku; odpowiadaj po polsku, zwięźle.
- Data: 2026-10-01. Wiedza modelu kończy się w kwietniu 2024, więc fakty z 2026 weryfikuj przez web (`fetch_webpage`).
- Workspace: infoshare-silkycoders-sql-ai-3 (README.md, docs/ai-sessions/, zgloszenia/E00/eksperymenty-ask.md). Nie analizowano go, brak zmian w plikach projektu.
- Pytanie: "najnowsze konwencje projektowania hurtowni danych", potem "czy aktualne na 2026" i "wprawdź w web".

## Zweryfikowane trendy (źródła: bigdataboutique, algoscale, synxdata, hevodata - blogi vendorów)
- Architektura medallion (bronze/silver/gold).
- ELT zamiast ETL.
- Star schema nadal standardem warstwy analitycznej.
- dbt do transformacji i testów.
- Hybryda Data Vault 2.0 + Kimball (DV w warstwie integracji, star schema w prezentacji). Poprawna nazwa: Data Vault 2.0.
- Otwarte formaty tabel (Iceberg, Delta, Hudi).
- Rozdzielenie storage i compute.
- Jakość danych, lineage, RBAC.
- CDC do ładowania przyrostowego.

## Dodatki z 2026
- Klasyczny model trójwarstwowy jest przestarzały.
- Iceberg REST catalog.
- Streaming jako pełnoprawne źródło.
- Projektowanie pod AI/ML.
- Wektory i dane multimodalne.
- FinOps (kontrola kosztów).
- Przenośność, unikanie vendor lock-in.
- Iteracyjne dostarczanie.

## Zastrzeżenia
- Źródła to blogi vendorów, nie neutralne badania.
- Lakehouse ma wysoki koszt operacyjny.
- Data contracts i Data Mesh potwierdzone tylko w snippetach wyszukiwarki, nie w pełnych artykułach.

## Błędy do uniknięcia
- Pierwsza odpowiedź była z pamięci i błędnie podała "Vault 2.0". Weryfikuj twierdzenia zależne od czasu.

## Możliwe kolejne kroki
- Pogłębić temat: utrzymanie Iceberg, Data Vault vs Kimball, praktyki dbt, data contracts.
- Przeanalizować workspace (README.md, pliki SQL) i zastosować konwencje. Najpierw zapytać użytkownika.
