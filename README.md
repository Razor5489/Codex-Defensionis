# Codex Defensionis

Libro scolastico di Silas Ravenshaw, autore fittizio, per Hogwarts nel 1890.

[Apri il libro](https://razor5489.github.io/Codex-Defensionis/)

120 pagine, sette anni, 28 incontri. Due lezioni a settimana per due settimane per ogni annualità. L’ordinamento concordato del 22 novembre 2026 prevale sulle precedenti collocazioni delle formule modificate. Più schede di formula possono appartenere a un solo incontro.

| Anno | Settimana I · Due incontri | Settimana II · Due incontri |
|---|---|---|
| 1 | Fattura, maleficio e maledizione; Rictusempra | Flipendo; Protego |
| 2 | Il Molliccio e il potere della paura; Riddikulus e Coloshoo | Tarantallegra; Vermilius |
| 3 | Fireball; Confundo | Expelliarmus; Evertestatum |
| 4 | I licantropi; Le Acromantule | Confringo; Petrificus |
| 5 | Gli Auror; Diffindo | Incendio; Incarcerous |
| 6 | I Dissennatori; Gli Inferi | Bombarda; Confringo · Approfondimento |
| 7 | Gli Obscuriali; Il giudizio del difensore | Expulso; Expecto Patronum |

## Collocazioni e limiti

Incantesimi: al secondo anno Accio, Levioso, Alohomora e Colloportus nella prima settimana; Depulso e Puncheck nella seconda. Al terzo anno Descendo, Arresto Momentum e Ventus, seguiti da ripasso.

D.C.A.O.: Tarantallegra e Vermilius nella seconda settimana del secondo anno; Fireball e Confundo al terzo; Confringo al quarto. La ripresa di Confringo al sesto è un approfondimento, non una nuova introduzione. Verdimilius resta distinto da Vermilius e conserva il primo anno di Incantesimi.

Puncheck simula un pugno magico, secondo la descrizione fornita dall’utente. I volumi pubblicati mantengono una voce interamente in roleplay; i dettagli tecnici e i riferimenti esterni restano in questa documentazione. Diffindo, Incendio e Incarcerous nel programma DCAO della fonte sono applicazioni difensive di formule condivise con altre materie. Gli anni non ridefiniti mantengono il percorso precedente e i richiami vengono coordinati.

## Fonti e generazione

Base: [Libro DCAO di Francis Lake](https://francislake.altervista.org/Libro%20DCAO.php) e DCAO.pdf fornito dall’utente, rielaborati secondo gli aggiornamenti concordati. Modificare `content.json`, `spell-index.json` e `supplementary-topics.json`, quindi eseguire `python build-book.py` con Python/ReportLab. Il tema dei troll è conservato come lettura complementare senza aggiungere incontri.

Il generatore sincronizza pagine SVG, indice, numerazione e dati incorporati. Lettore con ricerca, segnalibri e modalità a una o due pagine. Pubblicazione GitHub Pages da main, radice. Esclusioni richieste rispettate.
