jerkbot
=======

reddit bot for archiving K.dot comments before they're deleted

#### dependencies

most of these are in pip and you can get static PhantomJS builds on their website

- Python 3
- PRAW
- pyimgur
- Pillow
- selenium
- PhantomJS

#### how to install
you'll need to figure out your own cron job frequency and result limit so you don't go over the api limit for reddit and imgur
- download a tarball of the latest commit
- extract it anywhere
- ```$ cd <jerkbot dir>```
- ```$ cp config.py.default config.py```
- edit config.py and fill in all your own settings
- add a cron job to run jerkbot like ```./jerkbot.py``` (you can also use check.sh)

#### actual testimonials

**"i saw the code and i was like... haaaaaannh~!! nice bot ;)"** --Kanye "Weezy" West

```
:  ....,.......,..,...  ..,,,.,:::~::::::::+~=~:,,., ..,,.,.,:,,,.,,..........+Z
....... ...,,..,...........,~OOOO88N$$$ZO$$$$$$7=,...........~:,,...,.........,Z
.. .........~.........,:=$8DMNDD8DNNDNDDDNNDDNNDZI+:.......,...................,
....................,~7ODDDMD8ODNNNDDD88ND8DDNNDNNO?:,.,,,,,. ..,:... .........:
..................,=$MNDDDDDDDD8O88DND8OO88OD8DMNNNNI~,...,,,........  ..... .~?
...............,,~?NDN8DN8O$$Z77I?IIIII777$$Z8DNDDNDN7=:....,.............. ..+I
.................$DDDNDDO$$$77IIIIIIII?I??IIII7$$Z7ODN7+.................  .. .,
................?8NDNDDOZ7$777II???III?????III77$$Z$Z88I~............. ..  .....
.... ..........,DNDNDD8Z$77777III?+++???????II777$$ZOO87~....... ... ..........,
 .............,~DNNDD8OZ77$77II????=++++?++??I7777$ZZO8D~,,.,.. ....... .......:
...... ...,...:$NDDD8OO$7$7$77I??+~+====?=IIIII77$$ZOO8O+,..... ....:. .. ......
...... ...,...=ZNNNN88OZ$777$7I?I++==+++++=??+??I7$ZZOOO7...,......:............
....... ......:DNDNDD8O$$$$$$77I??+===+?+I??II?II77ZZZOO8,.. .,......... .......
.........,.. .:8NDDDDDZ$7$$$$7???+==~~~==?????+??I7$ZZOOO+...::,...............:
..... ........~7NNDD8O$$$ZZZ777O7$$$Z$7?+~~=++?+II7$$ZZOO=, ..,,,.....:... . ..?
....  .. .....~7DDDD8Z$$$Z8MNMMNNMMMNMMMMMNND8DNNMMMMMMNMN7I?...,... .~.. ....,=
..............+?ZDDD8OZ$ZNMMMMMMMMMNMMNMMMMNMMMMMMMMMMMMMNMMM~...... ,........,=
.. . .........,=ZDD8OZZ$$MNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNNMI=..,.    .  .   . .
. . . .  .....,INNDNMMNMNNMMMMMMMMMMMMMMMMD~MMNMMMMMMMMMMMDMDI.....
..   .......,=Z77ODDOO$ZZMMMMMMMMMMNMMMMNMM$?$DMMMMMMMMMMNNMN~...,.. ..  ......,
.    ........:D8$I7OOZZ$$MNMMMMMMMMMMMNMMMZ?+IOMMMMMMMMMMNMM7?.....   .  .......
..   ........+$$777ZOZZ$$MNMMMNNNNNNMNMMMN?+?I$NMMMMMMMMMNMZ?~....    ...   ....
. .  ........~I7IOZ$OZ$$$MNMNNNNNNMNNNMMM7?+??$OMMMMMMMMMMM?=... .  . ... ..  .~
.    ........~III$$7ZOZ$7$DMMNNNNNNNNNND$II???IZ8MMMMMMMMMM=.,....   ..  .... .Z
... ..... ...~?I?=7Z$OZ$$7III$ZZZOOOOODI???+~:?7Z$ODDNMMMN+.... .  .... .  . ...
....... .....~77??7$OZZZ$7III?++++++++7II7ZZ$7Z8OZOODDDND8=.... ... ...       ..
...  . .,,...:II$$Z$OZZZ$777??++==++++$8NMOOMMMMNDZ$$$ZOO?....... ..,,..     . .
. . . ........:+I7I7OZ$Z$$77I??+++????III$IZ7788OZZZ$$ZOO+..,,.. .........  ....
. ... .........,:=$8OZZ$$$777IIII?I?+??$$$I?ZZ788O$$Z$ZOOI,......  .......  . ..
... .............:~Z8Z$$$777777I7I+?O$7+I7I?77$$$88ZZOOO8=,,..,,... ...... .....
... . ......,~.....~ZOZ$$$777777$7?7Z7OOZOZZ7ZO8OOOOZOOOZ,.....,:,. ....,.....:I
..  ........,,.....,ZOZZ$7$777777778DOII?I??I??ZNN88ZOOZ?,:...,.. .....,...  .?Z
+,..........:.... .,ZZOZZ$$$$$777$ZI??I?????I?7$ZZ7$ZO$I:,.. ..,... ....,. ...$O
..... ... .........:ZZZ8OZZZ$$$$7$ZI?III77O88DD8$Z$$O$=:.,....,,=~............,7
.. ... ..... ....,::ZZZZ8OOZZZZ$OO87$7$777I787ZZOOO8O$?,,. .,O7+:,......,.....,=
... ........:...,=~NOZ$ZZ888OZOZZO8ZZZ$$$$ZOZ8O88DNDDDDO..I?77~:......,,:.... .?
..........,OI.,,:NM8OZZ$ZOONDO8OZOD$$Z7777I7ZZOO8DNNMMMND$OIO,.............. .:+
.  .... ......::NMNMOZZ$$ZO8DMD88ODOD888ZO8ZDD88NMMMMN8D++7M?~...,,,..:,......=I
.............,DDNOZM8ZZZ$$ZZODMNDO88ODODO88DDDNNMMMND8O7$NMNN:...,,...........~I
.....,......,NDNDOZ8DZ$ZZ$ZZZOOOMM8NDNN88O8DNNNNMMNO877ZOMNMNN.,..... .......,,?
~. .......,:DDDDDDD+8Z$$$ZZZZZOZZZMMMMMMMMMMNMMMM8OO8NNNNMMNMNN+~.............:+
.. ......,+DDDDNDDD88O$$$77$ZZOZOOZDMMMMMMMMMMMMOOZO8NMMMDMNNNDN7=,,..........:+
..,.. .,.ZDDDDDND88N8OZ$$77$Z$ZOOOOOONMMMMMMMMMOZZOO8NMN88MNNNNNNNN$=~:......,,=
.......:ODDDDDNODD8D8OZ$$$$$7$ZOOOO888DMMMMMMMOZOOOOD8NNIDMNDNNNNNNNZ8?:.. . ..=
..  .+O8DDNDDDO8DDD8DDZ$$$$77$$ZZOO888DDDMMMNOZZZOOOM+NMDD8NNDNNDNNDNDODD$+,....
...:7Z8DDDDDDDDDDDDO88=$$$$$7777$Z$ZO8OOOZZZZZZZZOONMDDN$$DMNDDNNNDDDDD8DDD8=,,,
?$ZO8DDDDDNDDDNDDND7$888Z$$$$$77$$$$$$$$$$777$ZZONNM$DDN$Z7MDDNNNNNN8DDDDDDD8ZII
D88DD8DDDDDNDDNDDNN8D88DD88$$$7$7$$$$$7$7777$8NNNNNZ88DM$DOMNDNNNNNNDDDDNNDDNDN8
DDDD8DDDDNNDDDN88NN8DN8:$888Z$$77777$77$8DDNNNNNNNN~DDNNDNMMNDDNNNNNDNDDDNNDDDND
DDD8NDDNDNDNDNND8DM?8D+OI~OD88D8DDNDDNNNNNNNNNNNDDZDDDNN=NDDMDNNNNNNNNDNDDNDDNDD
DDDNDNDDDNNDDDND88D788N?~D88888O8DNNDDNDDDNDDDDDDND8DD8I?DDOMNNNNNNNDNNDNDDND8DD
DDDDDDDDNDNNNDDD88D$DDDD8DD8788888DDDDDDDDDDDDDDDNDD8D:D8D?IMDDNNNNNNNDDNDDDNDDD
DNDDNDDDNDNNDDDD888=DI$DND8$ZI788888ZZDDDD8DDD8DDDD8DN8DDD8NMNNNNNNNDNNNDDNDN88D
DNNNDDDDDNNNNDDD888=D788DMNN7O888DD888Z8DDDDDDDDNDDDDD,~8DDDMMNNNNNNNNNDDDDNDZD8
DDDDDDDDDDNNDDDD8888DND+8DMNDDDDDZZ88D8888DDDDDDDDD:8D7+D8DZMMDNNNNNNNDDDDD888O$
```

**"it was the greatest bot i ever saw"** --Tupac "2-Pac" Shakur
```
................................................................................
...............................,,....,..........................................
..........................=$$II?7??$7$ZOI~?I=,+:I+ON?$7,........................
........................~?I$7II?I77I7$ZOOO8ZZD8+8Z$$N~:$7=,.....................
...................,.,:7$I+7$7=?ZZ$Z?I~~D7ZNNNZO$ZZIOD=88O$I?...................
.................~78I7++:IIIII7$?$7:O?:$ONNND8DOZOOZON$DMN=:++..................
...............~77~Z=$Z$:+?$DI~+IZ:7$8NN7ONNMMNNNMNNMM?.8DMND~$:................
..............~=~~I=$~?DNONOZI~O:7IDZ7ONNMNZ8NDD888NDZZ:.~N$ONM=Z+..............
............~~=+O8=~~DDNZ78+?O=IN7==ZNDNN8OZD8ZZ$7II++?+.,.,OON8N$7,............
...........,+=IZ+I+OINN~8Z7877D8O78ONNNNN8ZZZ$$77I?++++?7..,,NOO?ZD==,..........
..........:=?OZ$I$NNZI?ZI8$7DNZ$I$ZNZO8DD8DD8O7II?+++==+I~...DDD8DNN+~..........
........,=+$$D$7ND8IOD7ZN?Z8DIII$8N8ZDNNNNNNDDO$7I?+??II??,...DODD8DNO..........
.......+=77D?+D$D??I$ODZI$OZII7$ONNDNNDNND8DOZZ$$77II7ZODOZZ=..8$D88DDZ.........
......++788$I7DOI?8$ON877ZZI7I$7NDDDDD8OOZZZZ$7$777I77Z8DN88$=.,7?8?OND7........
....=+I8DZ$D?$878OZDDD77$$7I77$DNND8OZ$$$$$ZOOZ$$77II7ZZZOZ7Z$~..O?8?ODD7.......
...~IIDDODO$7II?ZODDDIZ77$$7I8DDN88ZZ$7III77ZZ8OZ7I??7$7IIII77?...7+$+7D8?......
...?7$DD$OZI7=OZ8DDDZ7Z$ZZ77$DDD8OZ$7???????I$8OZ7?++77II7+=+I+....I=I7O88I.....
..~$ZDD7O$?77ZO8DDD?7$$Z77$$O$DD8OZ$7I?I77?IIIZZ$I?+=77Z7I++=?:......O$7O88+....
..?O8DZ$7O?=O78DDDO7D7$$Z$$$OZDDD8OZ$NN8ZI$DD7I7$7I?+=$NDDDDND~,......:O7Z88,...
..7$D7?$O$7?ZZDDD$ODDZ$$Z$$Z$8DDDDNNDDDDI=I$$$77$7II?==ZDNI,=D$=........:7IO7...
..~$8I?OO7O87DND$NND$Z$OZZZ$$DDD8DNDDD8D8ZZO777777II??+~+OZZ$I.............$Z7..
...$7+=87O8Z$DOZDNN87O8OZZ$Z$OZZ$$ZO88D8O$7I7I?IIIIII?+=~~III?:..............::.
...:IIZ7ZDD+DZDDNN8Z78Z$ZZ$$7$$$$77777IIIIIIIIII7777I?+++=~:=~~,................
..,,?7D$OOIDODNNNN8ZIDZOZ$$I77$777IIIII??????III777II?++++=~:+=~................
..,,:?OOODN$NNNND8OZ78OOZZI7777777IIIIII?????II77$I??7$$$7??===~~...............
..,,:+$DD$7NNNNDOOO7ZZZZZ7777$$$7$7$77IIIIIIIII7Z$$ODNMND8$7I$===...............
..,,::$ZD$NNND8OOZ$I8ZZZ$7$$ZZZZZ$$$77777IIIII7788DNMMMMMD8$MI===...............
..,,::7?I78DZOOOZZ$$O$O$$$ZZOZOOOZOOOZ$$$$77III78NN888OOOZ?7+====...............
...,,,ZNNNDDO8D8Z$$$DDZOZZOOOO88888888OOZZ$77IIII7$$Z888O7ZZZ?=~=,..............
...,,:NNNNNDDDDOZ$778DZOOOO88888D88D88OOOZZ777III77$8888$7$ZO$Z~=...............
...,::DNN8ZONNDI777I7DOZO8O888DD888D88OOOZZ$7777I7OOOOZ$7II?===7=...............
...,,,$DNO8DNDD$$7I7$ZZZOO888DDDDDD888OOOZZ$777$Z8D8Z7OO$$ZI?++IZ...............
....,,,ONZDNOO8DZ$777$$OZOO888DDDDD88888OOZZZ$ZDDNO$8O$Z$ZZ7II?+?...............
....,,,:O8O87Z$78Z777ZOZZ$ZOOO8888888888OOZZZODND8DNND8DOZ7ZOZO$I...............
....,,,,,$77Z888IO7$$OOZZZO8OOO8888888888OOZ8NNNDNNNNNNO7???=~~I7...............
.....,,,,,IOO77ZD8Z$ZOOZOO8OOOOOOOOOOOO8OOOZDDNND8Z$$$77I??+++==?...............
............7ZDOO$ZZZOOOZO8ZOOOOOOOOOOOOOOO8D8DDD88OZZOO8Z$II??I=...............
..............?77ZZZZZZZOOOOOOOOOOOOOOOO8O88D8OOO8DNNNNNDDNDDOZI+...............
...............:7$7ZZZOZOOOO8D8888888888D888DNDDDDDDDDDD888OZ$7I~...............
................I77ZZZOOO8888DDDDDDDDDDDD8DDDNDDDDDDD88OOZZ$$77I................
................?I$ZOOOOOODDDDDDDDDDDDDDDD88DD8DD8888OOZ$$7III??................
................?7$ZOO88888DDDDDDDDDDDDDD8DDDDDD8OOOOOZ$Z$7II???................
................?7$ZOO88DDDDDDDDDDDDDDDDDDDDDNDD8888888O8ZZZ$77?................
................?IZZZO88DDDDDDDDDDDDDDDDDDDDNNNDDDDDDDDD8OO88Z8+................
................=I$$ZZO8DDDDDDDDDDDDDDDDDDDDNNNNNDDNNNNDDD8DD8Z.................
................=I7$ZO88DDDDDDDDDDDDDDDNNDDDDDNNNNNNNNNDDDNDO,..................
................=I7$ZO8D8D8DDDDDDNDNDDDDNDDDDDDDDDNNN87=:,......................
................=I7$ZZO8888DDDDDDNNDDNDNNDDDDDD88O$77I?,........................
............::~=+I7$ZOO88888DDDDDDDDDDDDDDDDD8OZ$777III~........................
...........,Z$$Z?I7$ZO8888888DDDDD88888DDDD88OZ$7I777II=,.......................
..........,,?$$$?77$ZOOO8O8888888888DDDDDD8OOZZ$II777I?++:......................
............~$$III$$$ZOOOOO8888888DDDDDDD88OOZZ$7777II??Z+:.....................
............,~.II77$ZZOOOOO88888DDDDDDDDDD8OOZZ$777IIIII$O=:....................
...........,.:7$77$$ZZOOO8OOO888DDDDDDDDD88OOOZ$77777II7NZ?:,,..................
.............,+8O$$ZOOOO888O88888DDDDDDDD8OZOZ$$$$77777Z7DZ+,...................
~===~,,....,..,IDOZZOOOOOO88888DDDDDDDDD88OZZZZ$Z$$$7$ZD?D8$~,..................
==~..:,......,,,88OOOOO888888888D8DDDDDD8OOOOZZOZZZZZOODIO8Z~,...,,,............
.,,,,,,,,...,,...ID8OOO8888D888DD8DDDDDDD8OZOOOOOOOOO8DN?7OO~:..,..,:...,,,,....
:,,::,,,,..,,..,,.~D888888DDDDDDDDDDDDDD888D8888888DDDNNI?ZO:,,....:~~:....:~::~
,:,,:.,,,......,,..,D8888D8DDDDDDDDDDDDDDD8D8DDDDDDDDNND??$?,......,=~~:,....~++
,:::=:,,,,..........,$DDDDDDDDDDDDDDDDDDDDDDNNDDNNNNNN+?+?$=,,,.....~+=:,..,...,
,~==?I,,,............,,,=8DDDNDNNNDDDDDDDNNNNNNNDND8::=7+?=,O~,......:=+~,.:,..,
:~==+?,,,,,.........,.,,,...~ODDDDDNNDDNNNNNNNNND+,,:~7I,:~:8NM+.....,~+=:.,~:..
```
