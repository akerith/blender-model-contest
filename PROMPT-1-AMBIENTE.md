Prompt da incollare in ogni programma (Claude Code, Codex, Antigravity, Qwen Code).
Prima di incollarlo: apri il programma nella cartella C:\Users\USER\gara-modelli, scegli il modello,
e sostituisci NOME con il nome del concorrente:

claude-opus, claude-fable, gpt-astra, gpt-sol, gemini-argon, gemini-hydrogen, qwen-max

Un concorrente alla volta: chiudi Blender prima di passare al successivo.

---------------------------------------------------------------------------------

Partecipi a una gara tra modelli di intelligenza artificiale che creano grafica 3D in Blender. Il tuo nome nella gara è NOME. Lavora nella cartella C:\Users\USER\gara-modelli.

Adesso prepara solo l'ambiente, senza cominciare nessun progetto:

1. Leggi tutto il file REGOLE.md e il file kit/gara.py.
2. Controlla che Python funzioni (`python --version`) e che esista Blender in C:\Program Files\Blender Foundation\Blender 5.2\blender.exe.
3. Avvia Blender con `python -I kit/gara.py avvia NOME` (se dice che Blender è già aperto, fermati e dimmelo).
4. Scrivi un file di prova in concorrenti/NOME/lavoro/prova.py che svuota la scena, crea un cubo con sopra una sfera e una luce del sole, scrive nel log i nomi degli oggetti e chiama render_viste("prova", viste=["fronte", "tre_quarti"]). Eseguilo con `python -I kit/gara.py passo NOME concorrenti/NOME/lavoro/prova.py`.
5. Apri e guarda l'immagine concorrenti/NOME/outbox/prova_tre_quarti.png e dimmi cosa vedi.
6. Apri e guarda le tre immagini nella cartella riferimenti e descrivimi in poche righe ciascuna, così so che le leggi bene.

Non cambiare niente nella cartella kit, non installare niente, non scaricare niente da internet. Alla fine rispondimi in italiano semplice: tutto pronto oppure cosa non funziona. Poi aspetta: il primo progetto te lo do io in un messaggio successivo.
