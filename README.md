# Fuksi-lauta
Tämä sivusto toimii Helsingin yliopiston aineopintojen Tietokantasovelluksen harjoitustyönä.
Sivustoa pääset testaamaan osoitteesta: https://fuksi-lauta.herokuapp.com/

### Sovelluksen kuvaus:
Tämä keskustelupalvelu tarkoitettu pääsääntöisesti yliopiston ensimmäisen vuoden opiskelijoille. Täällä voit keskustella kouluun liittyvistä asioista tai myös ihan muista aiheista.

#### Sivustolla kävijä voi:
- Lukea muiden kesksteluja tai kommentteja
- Tehdä oman käyttäjätunnuksen sivulle
- Etsiä tai rajata aiheita hakusanoilla, aihealueilla tai järjestyksellä (esim. Eniten viestejä aiheella)

#### Kirjautunut käyttäjä voi:
- Aloittaa uuden keskusteluaiheen tai kommentoida muita aloituksia
- Vaihtaa profiilikuvan haluamakseen
- Vaihtaa salasanan uuteen
- Poistaa oman aloituksen tai kommentin
- Tykätä tai ei tykätä aloituksista tai kommenteista

#### Ylläpitäjä voi:
- Poistaa minkä tahansa aloituksen tai kommentin
- Lisätä oletusprofiilikuvia tietokantaan, jolloin jokainen käyttäjä saa sen profiilikuvaluetteloonsa

#### Sovelluksen rajoitukset:
- Salasanan pitää sisältää 8 merkkiä, mikä koostuu kirjaimista **ja** numeroista
- Aloituksen pitää sisältää otsikko (kuva tai aloitusviesti eivät ole pakollisia)
- Kuvatiedosto voi olla joko .png, .jpeg tai .jpg

#### Muuta:
- Sivuston alareunassa näkyy milloin viimeksi kävit sivustolla, kirjautuneiden käyttäjien sekä käviöiden määrä
- Sivusto toimii osittain JavaScriptillä, joten on suotavaa sen olla päällä selaimen asetuksissa. (Sivusto kuitenkin toimii moitteetta ilmankin, mutta virheviestit eivät saata olla niin kattavia silloin käyttäjälle.)
- Jokaisella käyttäjällä on aluksi oletusprofiilikuva
- Kun käyttäjä vaihtaa profiilikuvan, vanha profiilikuva jää talteen käyttäjän profiiliin, jolloin hän voi vaihtaa sen helposti aijempaan. Muut käyttäjät eivät kuitenkaan pääse käsiksi niihin.

#### Uuden aloituksen lisäys:
- Aloituksella pitää olla otsikko (maksimi 60 merkkiä pitkä)
- Aloitusviesti voidaan lisätä, mikä näkyy etusivulla esikatselussa (maksimi 4000 merkkiä pitkä)
- Aloitukseen voidaan lisätä kuva, mikä myös näkyy etusivulla
- Aloitukselle pitää valita aihealue, joita ovat:
  - Satunnainen
  - Autot
  - Harrastukset
  - Musiikki
  - Opiskelu
  - Pelit
  - Ruoka
  - Tietokoneet
  - Tietotekniikka
  - Urheilu
  - testing

#### Hakutoiminto:
- Voit etsiä tai rajata aiheita hakusanoilla. Ensins sivusto näyttää ne, jos otsikossa ollut sama sana, sen jälkeen jos aloitusviestissä ollut kyseinen sana
- Voit rajata aihealueen perusteella esim. vain Urheiluun liittyvät aiheet
- Voit järjestää aiheet sivustolla neljällä tavalla:
  - uusin ensin (oletus)
  - vanhin ensin
  - eniten viestejä
  - eniten tykkäyksiä
- Voit myös määrätä aiheiden määrän per sivu (5, 10, 15, 20 tai 25), jonka jälkeen pystyt navigoimaan sivujen välillä sivuston alapuolella olevien sivut-nappien avulla.


Osoite sivustolle: https://fuksi-lauta.herokuapp.com/
