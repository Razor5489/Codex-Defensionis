"""Build Codex Defensionis from the editable course in content.json."""
import json, re, math, subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=Path(__file__).parent
DATA=json.loads((ROOT/'content.json').read_text())
OUT=ROOT/'pages';OUT.mkdir(exist_ok=True)
ROMAN=['I','II','III','IV','V','VI','VII'];PAGES=[];CHAPTERS=[];SECTIONS=[]
BOOK_TITLE='CODEX DEFENSIONIS'
INK='#30363d';GOLD='#a9b3bd';MUTED='#8e8a76';PAPER='#f8f4e8';GREEN='#354451'

def text(x,y,s,size=12,fill=INK,weight='',anchor='',italic=False):
    return f'<text x="{x}" y="{y}" font-family="Georgia, Times New Roman, serif" font-size="{size}" fill="{fill}"'+(f' font-weight="{weight}"' if weight else '')+(f' text-anchor="{anchor}"' if anchor else '')+(' font-style="italic"' if italic else '')+'>'+escape(str(s))+'</text>'

def lines(s,size=12,width=479,bold=False):
    words=s.split();result=[];current=''
    for w in words:
        t=(current+' '+w).strip()
        # Slightly conservative for Georgia on browsers without the same font.
        if stringWidth(t,'Times-Bold' if bold else 'Times-Roman',size)*1.08>width and current:
            result.append(current);current=w
        else:current=t
    if current:result.append(current)
    return result

class Leaf:
    def __init__(self,section,title,subtitle='',kind='theory'):
        self.section=section;self.title=title;self.subtitle=subtitle;self.kind=kind;self.parts=[];self.plain=[section,title];self.y=109
        self.parts.append('<rect width="595" height="842" fill="'+PAPER+'"/><rect width="595" height="842" fill="url(#paper)" opacity=".17"/>')
        self.parts += [text(52,38,'CODEX DEFENSIONIS',7,MUTED),text(543,38,section.upper(),7,MUTED,anchor='end'),'<path d="M52 48H543" stroke="'+GOLD+'" stroke-width=".7"/>']
        for line in lines(title,26,480,True):self.parts.append(text(52,self.y,line,26,GREEN,'bold'));self.y+=31
        self.y+=1
        if subtitle:self.paragraph(subtitle,11,MUTED,True,16);self.y+=8
    def paragraph(self,s,size=12,fill=INK,italic=False,leading=18):
        self.plain.append(s)
        for line in lines(s,size):
            self.parts.append(text(52,self.y,line,size,fill,italic=italic));self.y+=leading
        self.y+=12
    def heading(self,s):
        self.plain.append(s);self.y+=7
        for line in lines(s,15,480,True):self.parts.append(text(52,self.y,line,15,GREEN,'bold'));self.y+=20
        self.y+=4
    def box(self,label,s):
        ls=lines(s,11,449);height=39+len(ls)*16
        self.parts.append(f'<rect x="52" y="{self.y-12}" width="491" height="{height}" fill="#eee9d8"/><path d="M52 {self.y-12}v{height}" stroke="{GOLD}" stroke-width="1.5"/>')
        self.parts.append(text(66,self.y+3,label.upper(),8,GREEN,'bold'));self.y+=24
        for line in ls:self.parts.append(text(66,self.y,line,11));self.y+=16
        self.y+=22;self.plain.extend([label,s])
    def row(self,left,right):
        self.parts.append('<!--ROW:'+str(len(self.plain))+'-->')
        for line in lines(left,11,417):self.parts.append(text(60,self.y,line,11));self.y+=16
        self.parts.append(text(536,self.y-16,right,10,MUTED,anchor='end'))
        self.parts.append(f'<path d="M60 {self.y-8}H536" stroke="#c3b89b" stroke-dasharray="1 3" stroke-width=".4"/>');self.y+=12
        self.plain.append(left+' '+str(right))
    def finish(self,folio):
        if self.y>758:raise ValueError(f'Overflow {self.title}: {self.y}')
        return svg(''.join(self.parts)+f'<path d="M52 789H543" stroke="#c3b89b" stroke-width=".45"/>'+text(52,804,'DEFENSIO · HOGWARTS · MDCCCXC',6.5,MUTED)+text(543,804,folio,8,MUTED,anchor='end'))

def svg(body):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="595" height="842" viewBox="0 0 595 842"><defs><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter><pattern id="paper" width="595" height="842" patternUnits="userSpaceOnUse"><rect width="595" height="842" filter="url(#grain)" opacity=".17"/></pattern><linearGradient id="leather"><stop stop-color="#0e141a"/><stop offset=".12" stop-color="#394652"/><stop offset=".6" stop-color="#232f3b"/><stop offset="1" stop-color="#090e14"/></linearGradient></defs>'+body+'</svg>'

def add(leaf,chapter=None):
    idx=len(PAGES);folio=f'{idx+1:02}'
    if chapter:CHAPTERS.append({'title':chapter,'page':idx+1})
    artwork=leaf.finish(folio);name=f'page-{idx+1:02}.svg';(OUT/name).write_text(artwork)
    PAGES.append({'image':'pages/'+name,'text':'CODEX DEFENSIONIS\n'+'\n'.join(leaf.plain),'title':leaf.title,'folio':folio,'kind':leaf.kind})
    return idx

def cover(back=False):
    body='<rect width="595" height="842" fill="url(#leather)"/><rect width="595" height="842" fill="url(#paper)" opacity=".22"/>'
    for inset in [21,28,35]:body+=f'<rect x="{inset}" y="{inset}" width="{595-2*inset}" height="{842-2*inset}" fill="none" stroke="{GOLD}" stroke-width="{.8 if inset==21 else .4}"/>'
    for x in [35,560]:
        for y in [35,807]:body+=f'<circle cx="{x}" cy="{y}" r="2.5" fill="none" stroke="{GOLD}" stroke-width=".6"/>'
    body+=text(297.5,85,'HOGWARTS · DIFESA CONTRO LE ARTI OSCURE',9,GOLD,anchor='middle')
    body+=text(297.5,170,'CODEX',40,'#eee8dc','bold','middle')+text(297.5,216,'DEFENSIONIS',34,'#eee8dc','bold','middle')
    body+=text(297.5,258,'Conoscenza, controllo e giudizio',15,'#c9ced1',anchor='middle',italic=True)+'<path d="M205 283H390" stroke="'+GOLD+'" stroke-width=".6"/>'
    body+='<g fill="none" stroke="'+GOLD+'" stroke-width="1"><circle cx="297.5" cy="430" r="92"/><circle cx="297.5" cy="430" r="84"/><path d="M246 376q51 22 103 0v55q-2 44-51 69-50-25-52-69zM258 393q39 13 78 0v37q-1 34-38 55-38-21-40-55zM267 462l61-68M318 393l10-8 1 12 11 7-13 1-5 12-3-12-12-4z"/></g>'
    if back:
        body+=text(297.5,605,'La forza richiede controllo.',17,'#e1e2de',anchor='middle',italic=True)+text(297.5,635,'La difesa richiede giudizio.',17,'#e1e2de',anchor='middle',italic=True)+text(297.5,695,'SILAS RAVENSHAW',14,'#e1e2de',anchor='middle')
    else:
        body+=text(297.5,607,'AD USUM SCHOLASTICUM HOGVARTENSE',9,GOLD,anchor='middle')+text(297.5,675,'Professor Silas Ravenshaw',17,'#e1e2de',anchor='middle')+text(297.5,746,'RICONOSCERE · PROTEGGERE · DECIDERE',9,GOLD,anchor='middle')
    body+=text(297.5,790,'MDCCCXC',11,GOLD,anchor='middle')
    name=f'page-{len(PAGES)+1:02}.svg';(OUT/name).write_text(svg(body))
    PAGES.append(dict(image='pages/'+name,text=BOOK_TITLE+'\nSilas Ravenshaw\nHogwarts · 1890\nConoscenza, controllo e giudizio',title='Quarta di copertina' if back else 'Copertina',folio='Quarta di copertina' if back else 'Copertina',kind='cover'))

cover();CHAPTERS.append(dict(title='Copertina',page=1))
p=Leaf('Praefatio','Il compito del difensore','Prefazione di Silas Ravenshaw')
p.paragraph('La difesa non comincia dalla formula più forte. Comincia dalla comprensione di ciò che sta accadendo: un effetto, una persona esposta, un luogo che può rendere migliore o peggiore ogni decisione.')
p.paragraph('Questo volume accompagna sette annualità, ciascuna di due settimane con due lezioni a settimana. I ventotto incontri collegano le formule del repertorio a paura, creature, oggetti sospetti e responsabilità. Ogni lezione comprende spiegazione, nozioni e confronto in aula.')
p.heading('Comprendere prima di scegliere')
p.paragraph('Una stessa manifestazione può avere conseguenze diverse in condizioni differenti. La precisione consiste nel riconoscere il bersaglio, definire un risultato necessario e controllare che l’intervento non produca un problema più grande.')
p.box('Hogwarts · 1890','Conoscenza, esecuzione e autorizzazione sono distinte. La lettura non assegna capacità avanzate e non sostituisce la valutazione del docente.')
p.paragraph('Conservate negli appunti anche i limiti delle risposte. Un giudizio affidabile non nasconde ciò che resta incerto e non scambia la prudenza per mancanza di coraggio.',11)
p.paragraph('Silas Ravenshaw',13,GREEN,True);add(p,'Prefazione')
p=Leaf('Tabula Materiarum','Indice del volume','Sette annualità · Ventotto lezioni');add(p,'Indice del volume');SECTIONS.append(['Indice',2])
p=Leaf('Cursus Septem Annorum','Il percorso delle due settimane','Quattro incontri per ciascun anno')
p.heading('Settimana I');p.paragraph('Due lezioni per riconoscere il problema, descrivere gli effetti e distinguere bersagli e condizioni.')
p.heading('Settimana II');p.paragraph('Due lezioni per approfondire il confronto, applicare il metodo e raccogliere il ripasso prima del passaggio all’annualità successiva.')
p.box('Quindici minuti','2 minuti per la domanda iniziale; 5 per spiegazione e nozioni; 5 per attività o dimostrazione; 3 per confronto e risposta ragionata.')
p.heading('Tre pagine, una lezione');p.paragraph('La spiegazione, le nozioni e la scheda per l’aula appartengono allo stesso incontro. Il repertorio finale facilita il ripasso senza aggiungere lezioni al calendario.')
p.paragraph('Recuperi, dimostrazioni e verifiche seguono le disposizioni della scuola.',11);add(p,'Il percorso delle due settimane')
p=Leaf('Methodus','Quattro domande prima di agire','Il metodo che accompagna il corso')
for h,t in [('Che cosa sta accadendo?','Descrivere l’effetto senza attribuire subito una causa o una formula. Le informazioni insufficienti restano tali.'),('Chi e che cosa è coinvolto?','Individuare bersaglio, persone vicine, appoggi, accessi e condizioni del luogo.'),('Quale risultato serve?','Definire un obiettivo circoscritto, distinguendo protezione, interruzione e assistenza.'),('Come si verificherà l’esito?','Osservare ciò che cambia, dichiarare i limiti e richiedere la competenza adatta quando il compito li supera.')]:p.heading(h);p.paragraph(t,11.5,leading=17)
p.box('La misura della preparazione','Saper scegliere comprende la capacità di sospendere un intervento o di non eseguirlo quando le condizioni non sono adeguate.');add(p,'Il metodo della difesa');SECTIONS.append(['Metodo',4])
ANNUAL=[];LESSON_POS={}
for yi,y in enumerate(DATA['years']):
    year=yi+1;annual=[l for l in DATA['lessons'] if l['year']==year]
    p=Leaf('Anno '+ROMAN[yi],y['name'],'Annus '+['Primus','Secundus','Tertius','Quartus','Quintus','Sextus','Septimus'][yi],kind='divider')
    p.y+=36;p.parts.append(text(297.5,p.y,ROMAN[yi],100,GREEN,anchor='middle'));p.y+=60
    p.paragraph(y['goal'],16,GREEN,True,24)
    p.box('L’annualità','Due settimane. Due lezioni ogni settimana. Quattro incontri, ciascuno con spiegazione, nozioni e lavoro in aula.')
    add(p,'Anno '+ROMAN[yi]+' · '+y['name']);SECTIONS.append([ROMAN[yi],len(PAGES)-1])
    ANNUAL.append((len(PAGES),year))
    add(Leaf('Anno '+ROMAN[yi],'Il programma dell’anno','Due settimane · Quattro lezioni'))
    for l in annual:
        section=f"Anno {ROMAN[yi]} · Settimana {ROMAN[l['week']-1]}"
        LESSON_POS[(year,l['meeting'])]=len(PAGES)+1
        p=Leaf(section,l['title'],l['subtitle'])
        p.parts.insert(3,text(52,72,f"LECTIO {l['meeting']} · SPIEGAZIONE",8,GOLD))
        for paragraph in l['theory']:p.paragraph(paragraph,12,leading=18)
        p.paragraph('Riferimento: '+l['source'],8.5,MUTED,False,12)
        add(p,f"{ROMAN[yi]}.{l['meeting']} · {l['title']}")
        p=Leaf(f"Anno {ROMAN[yi]} · Lectio {l['meeting']}",'Le nozioni da ricordare',l['title'])
        for label,body in l['notions']:p.heading(label);p.paragraph(body)
        p.box('Domanda da discutere',l['opening'])
        p.paragraph('Per motivare una risposta, collegare il concetto a un esempio della spiegazione. Un’opinione ragionata può essere discussa; una notizia nuova richiede una fonte.',11,MUTED)
        add(p);PAGES[-1]['title']=l['title']+' · Nozioni'
        p=Leaf(f"Anno {ROMAN[yi]} · Lectio {l['meeting']}",'Il confronto in aula',l['title']+' · Scheda della lezione')
        p.box('Apertura',l['opening'])
        for i,step in enumerate(l['steps']):p.paragraph(f'{i+1}. '+step,11.5,leading=17)
        p.heading('Domanda di ripasso');p.paragraph(l['question'],11.5,leading=17)
        p.heading('Risposta ragionata');p.paragraph(l['answer'],11,leading=16)
        if l['meeting']==4:p.paragraph('Concluso il ciclo di due settimane. '+('Si prosegue con l’anno '+ROMAN[year]+'.' if year<7 else 'Il percorso dei sette anni è concluso.'),9,GOLD)
        add(p);PAGES[-1]['title']=l['title']+' · Attività e ripasso'

SECTIONS.append(['Pratica',len(PAGES)])
p=Leaf('Consilium','Scegliere una difesa','Una decisione proporzionata alla situazione')
for h,t in [('Riconoscere','Descrivere ciò che si vede prima di attribuirgli una causa. Distinguere un movimento, un effetto magico e una reazione di paura.'),('Proteggere','Individuare persone esposte e possibilità di allontanamento. Una formula difensiva richiede comunque direzione, attenzione e condizioni adatte.'),('Interrompere','Disarmare, sbilanciare e distrarre producono risultati diversi. Scegliere in rapporto al problema, senza confondere la varietà delle formule con la qualità del giudizio.'),('Verificare','Osservare ciò che è cambiato. Un effetto visibile non dimostra da solo che il pericolo sia concluso.')]:p.heading(h);p.paragraph(t,11.5,leading=17)
p.box('Caso immaginario','Un compagno perde la bacchetta mentre un altro arretra verso una scala. La classe discute prima le persone esposte e lo spazio disponibile, poi le formule eventualmente pertinenti.');add(p,'Scegliere una difesa')
p=Leaf('Relatio','Il rapporto dopo l’evento','Informazioni che altri possano verificare')
for h,t in [('Luogo e persone','Indicare quando e dove è avvenuto il fatto, chi era presente e chi ha assunto la responsabilità dell’intervento.'),('Sequenza osservata','Descrivere l’ordine degli eventi. Separare ciò che è stato visto da ciò che è stato riferito da altri.'),('Decisioni e risultati','Annotare lo scopo delle scelte, gli effetti riscontrati e le indicazioni ricevute.'),('Limiti e consegna','Registrare dubbi, condizioni non verificate e compiti affidati a un responsabile.')]:p.heading(h);p.paragraph(t,11.5,leading=17)
p.box('Esempio immaginario','Alla comparsa dell’oggetto, due studenti si allontanano. Non è osservato alcun contatto. Il docente dispone di non avvicinarsi e prende in carico la verifica. L’origine dell’oggetto resta sconosciuta.');add(p,'Il rapporto dopo l’evento')
SPELLS=json.loads((ROOT/'spell-index.json').read_text())
p=Leaf('Formulae','Le formule per anno','Quindici voci del repertorio scolastico')
for s in SPELLS:p.row(f"{ROMAN[s['year']-1]} · {s['name']}",str(LESSON_POS[(s['year'],s['meeting'])]))
p.paragraph('Il primo anno riprende le formule già svolte. Le annualità successive costituiscono una proposta didattica da coordinare con il programma della scuola.',10,MUTED)
add(p,'Le formule per anno');SECTIONS.append(['Formule',len(PAGES)-1]);SECTIONS.append(['Repertorio',len(PAGES)])
for part in range(4):
    p=Leaf('Repertorium','Effetti e nozioni','Tavola '+ROMAN[part]+' · Consultazione delle formule')
    for s in SPELLS[part*4:part*4+4]:
        p.heading(s['name']);p.paragraph(f"Anno {ROMAN[s['year']-1]} · Lezione {s['meeting']} · pagina {LESSON_POS[(s['year'],s['meeting'])]}",9,MUTED,False,13)
        p.paragraph(s['effect'],11,leading=16);p.paragraph(s['notions'],10.5,leading=15)
    add(p,'Repertorio · '+ROMAN[part])
p=Leaf('Disciplinae','Confini e responsabilità','La materia nel programma della scuola')
for h,t in [('D.C.A.O.','Studia riconoscimento delle minacce, difesa, contrasto e giudizio. La formula viene letta insieme alle sue conseguenze e ai suoi limiti.'),('Le altre materie','Il catalogo segue la ripartizione scolastica: Incendio, Diffindo e Verdimillius restano in Incantesimi; Incarcerous resta in Trasfigurazione. Un collegamento teorico non trasferisce la formula di materia.'),('Studio e pratica','Mollicci, creature pericolose e magie sulla memoria non sono pretesti per prove improvvisate. Il docente distingue dimostrazione, discussione e lavoro consentito.'),('Le informazioni mancanti','Per Fireball il nome suggerisce il tema del fuoco, ma il comportamento specifico in gioco richiede conferma. Il corso non inventa gittata, danno o comandi.')]:p.heading(h);p.paragraph(t,11,leading=16)
add(p,'Confini e responsabilità')
p=Leaf('Lexicon','Le parole della difesa','Un lessico da usare con precisione')
for h,t in [('Minaccia','Una condizione capace di produrre un danno, da valutare nel suo contesto.'),('Bersaglio','Persona, oggetto o effetto a cui è diretto l’intervento.'),('Protezione','Azione volta a ridurre l’esposizione; non coincide con invulnerabilità.'),('Disarmo','Perdita della presa sulla bacchetta o sull’oggetto interessato.'),('Sbilanciamento','Alterazione dell’equilibrio, distinta dall’immobilizzazione.'),('Controllo','Capacità di mantenere lo scopo e verificare le conseguenze dell’azione.'),('Proporzione','Rapporto ragionato fra problema, risultato necessario e conseguenze previste.')]:p.heading(h);p.paragraph(t,11,leading=16)
add(p,'Lessico essenziale');SECTIONS.append(['Lessico',len(PAGES)-1])
p=Leaf('Nota dell’edizione','I materiali del volume','Una rielaborazione per l’insegnamento')
p.heading('Le fonti di partenza');p.paragraph('Il libro D.C.A.O. disponibile sul sito di Francis Lake e il documento DCAO fornito per questa edizione hanno ispirato la progressione fra formule, creature e temi difensivi. Testi, casi e schede di lezione sono rielaborati per questo corso.',11)
p.paragraph('Riferimento web: francislake.altervista.org · Libro DCAO.php',9,MUTED)
p.heading('La ripartizione scolastica');p.paragraph('La selezione considera il repertorio in gioco e la divisione delle altre materie. Protego, Flipendo e Rictusempra riprendono il primo anno già svolto; la collocazione successiva è una proposta didattica, non un requisito tecnico verificato del gioco.',11)
p.heading('L’orizzonte del volume');p.paragraph('L’ambientazione è Hogwarts nel 1890. Non si utilizzano avvenimenti successivi o rimedi futuri come conoscenze disponibili. Le informazioni incomplete sono dichiarate senza attribuire proprietà aggiuntive alle formule.',11)
p.heading('L’edizione');p.paragraph('Silas Ravenshaw è un autore fittizio. I casi immaginari servono alla discussione in aula e non introducono regole nuove nel repertorio della scuola.',11)
add(p,'I materiali del volume');SECTIONS.append(['Fonti',len(PAGES)-1])
p=Leaf('Finis','Conoscere la minaccia.','Scegliere con giudizio.')
p.y=370;p.paragraph('Sette annualità. Quattordici settimane. Ventotto lezioni per riconoscere, proteggere e comprendere le conseguenze delle proprie decisioni.',19,GREEN,True,29)
p.y+=42;p.paragraph('Silas Ravenshaw',15,GREEN);p.paragraph('Hogwarts · MDCCCXC',10,GOLD);add(p,'Finis')
name=f'page-{len(PAGES)+1:02}.svg';body='<rect width="595" height="842" fill="#202c37"/>'
for i in range(38):
    yy=i*24;body+=f'<path d="M-40 {yy} Q130 {yy-80} 298 {yy+9}T650 {yy-5}" fill="none" stroke="{["#a9b3bd","#647787","#394652"][i%3]}" stroke-width="{1+i%4}" opacity=".5"/>'
(OUT/name).write_text(svg(body));PAGES.append(dict(image='pages/'+name,text='Controguardia posteriore marmorizzata.',title='Controguardia posteriore',folio='Controguardia',kind='endpaper'))
cover(True)

def replace_leaf(index,p):
    (OUT/f'page-{index+1:02}.svg').write_text(p.finish(f'{index+1:02}'))
    PAGES[index]['text']=BOOK_TITLE+'\n'+'\n'.join(p.plain)
for index,year in ANNUAL:
    p=Leaf('Anno '+ROMAN[year-1],'Il programma dell’anno','Due settimane · Quattro lezioni')
    for l in [l for l in DATA['lessons'] if l['year']==year]:
        if l['meeting'] in [1,3]:p.heading('Settimana '+ROMAN[l['week']-1])
        p.row(f"Lezione {l['meeting']} · {l['title']}",str(LESSON_POS[(year,l['meeting'])]))
        p.paragraph(l['subtitle'],10,MUTED,True,15)
    p.box('Traguardo',DATA['years'][year-1]['goal']);p.paragraph('Le tre pagine di ogni lezione uniscono spiegazione, nozioni e confronto. Dopo il quarto incontro si passa all’annualità successiva.',11)
    replace_leaf(index,p)
chapter_pages={c['title']:c['page'] for c in CHAPTERS}
p=Leaf('Tabula Materiarum','Indice del volume','Sette annualità · Ventotto lezioni')
for title in ['Prefazione','Il percorso delle due settimane','Il metodo della difesa']+['Anno '+ROMAN[i]+' · '+y['name'] for i,y in enumerate(DATA['years'])]+['Scegliere una difesa','Il rapporto dopo l’evento','Le formule per anno','Repertorio · I','Lessico essenziale','I materiali del volume','Finis']:p.row(title,str(chapter_pages[title]))
p.paragraph('Il repertorio contiene quattro tavole. La ricerca permette di trovare formule, argomenti e singole lezioni.',10,MUTED);replace_leaf(2,p)
assert len(PAGES)==116,len(PAGES)
assert len(DATA['lessons'])==28
for item in PAGES:item['image']+='?v=20261121-defence1'
packed={'pages':PAGES,'chapters':CHAPTERS,'sections':SECTIONS}
(ROOT/'book-data.json').write_text(json.dumps(packed,ensure_ascii=False,indent=2)+'\n')
index=ROOT/'index.html';embedded=json.dumps(packed,ensure_ascii=False).replace('</','<\\/')
index.write_text(re.sub(r'(<script id="book-data" type="application/json">).*?(</script>)',lambda m:m[1]+embedded+m[2],index.read_text(),flags=re.S))
print(f'{len(PAGES)} pagine, {len(DATA["lessons"])} lezioni, {len(SPELLS)} formule. Margini rispettati.')
