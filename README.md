# MOVfuscator - WORK IN PROGRESS!

Ivan Miruna Maria - Grupa 141
Parapeanu Maria - Grupa 131
Popa David-Gabriel - Grupa 134
Teodorescu Luca Nicolae - Grupa 151

🞺Obiectiv:
Traducerea a cat mai multor instructiunilor dintr-un program Assembly in instructiuni de tip “mov”.

🞺Functionalitate:
Programul citeste un fisier assembly de intrare, identifica main-ul, iar apoi in functie de instructiune, realizeaza transformari specifice pentru a o rescrie.


★Instructiunea add:
Este simulata prin operatii pe bytes si tabele de look-up si foloseste strict mutari de date(mov).

Operanzii sunt impartiti in 4 bytes. Adunarea se realizeaza byte cu byte. Stocam registrii intr-o zona de memorie special alocata pentru a putea extrage byte cu byte. Pentru fiecare pereche de bytes, se utilizeaza un tabel de suma(look-up table) pe 256x256 (cu indecsi de la 0 la 255). Conceptul acestui tabel are la baza inlocuirea timpului de procesare cu spatiu de memorie. Practic vom avea precalculate toate combinatiile de sume posibile(mod 256), astfel incat la intersectia rand(%ah) coloana(%al) se va afla rezultatul sumei celor 2 bytes. Indexul il avem in %esi. Punand byte-ul primului operand in %ah si pe celalalt in %al, vom avea in %ax pozitia corecta: (rand*256)+coloana. Este necesar  si un tabel de carry care care indica, (tot conform conceptului prezentat la sum_table), prezenta carry-ului. De exemplu: daca avem in %ah 255 si in %al 1, la intersectia celor 2 vom gasi valoarea 256. Dar aceasta valoare produce un transport, asa ca verificam in tabelul de carry, unde vom gasi valoarea 1. Carry-ul este transportat intre bytes.. Rezultatul presupune reconstruirea de bytes calculati. 
 
★Instructiunea sub:
Este in esenta logica add-ului, dar in complement fata de 2.
Se inverseaza bitii, se adauga 1, pentru a obtine -(operand). Se apeleaza add cu noul operand.

★Instructiunea inc:
Este un add cu operand $1.

★Instructiunea dec:
Este un sub cu operand $1.

★Instructiunea mul:
Implementarea acestei functii se foloseste de functia de comparare a celor doua valori. Alegem valoarea mai mica, dupa care iteram prin bitii de la 0 la 31 si verificam daca respectivul bit se afla in valoarea mai mica. In caz pozitiv, la suma totala se adauga valoarea mai mare dintre cele doua. Indiferent de rezultat, pentru fiecare iteratie prin biti tinem intr-o valoare auxiliara dublul valorii curente utilizate pentru adaugarea in suma.

★Instructiunea shift left:
Este un mul repetat cu operand 2. Instructiunea se realizeaza repetat pe baza marimii operandului.

★Instructiunile and, or, xor:
Implementarea acestor instructiuni se bazeaza tot pe conceptul de look-up table. Fiind operatii pe biti, aici este mai simplu pentru ca nu trebuie sa tinem cont de carry(ca la add). Stocam operanzii in memorie pentru a ii putea accesa pe bytes. Punem primul operand in %ah, al doilea operand in %al; acum avem indexul: %ax = (%ah*256) + %al. Accesam tabelul precalculat and si construim rezultatul pe bytes.


★Instructiunile jump si cmp:
Implicit, in Assembly, in instructiunea cmp realizeaza op2-op1, iar aceasta valoare se compara cu 0. Am implementat aceasta logica si in programul nostru, compararea realizandu-se de la MSB la LSB. Operanzii sunt mutati in memorie pentru a fi impartiti in bytes, iar dupa aceasta folosim doua tabele: cmp_byte_table, ce compara doi bytes si returneaza 0 daca sunt egali, 1 daca primul este mai mare sau 2 daca al doilea este mai mare, si transition_table, care implementeaza urmatoarea logica: dacă starea anterioară era 0, noua stare este dată de comparația byte-ului curent. Dacă starea anterioară era deja decisă (1 sau 2), aceasta se propagă neschimbată, indiferent de bytes-ii următori.
Deoarece modificarea directă a registrului %eip prin mov este imposibilă, controlul fluxului de execuție este simulat prin manipularea stivei și a instrucțiunii ret.
In cazul jump-ului neconditionat, se muta adresa etichetei destinatie in varful stivei, urmata de instructiunea ret, pentru a sari direct la acea eticheta.
Jump-urile conditionate se bazeaza pe rezultatul calculat anterior de cmp (op2-op1) si se aplica o masca specifica pentru a determina o valoare booleana care ne informeaza daca trebuie sa efectuam saltul sau nu. Folosid un choosing_tabel care contine adresa instrucțiunii următoare și adresa etichetei destinație si in functie de aceasta valoare booleana punem adresa corecta pe stiva si apelam ret.

★Instructiunea loop:
Loopul implementeaza o decrementare a registrului ecx, o comparare a valorii din ecx cu 0 si in cazul in care ecx!=0, jump la label. Pentru a implementa loop-ul am folosit functiile create anterior pentru a decrementa si a face cmp, jne.

★Instructiunea lea:
In cazul nostru, o putem substitui cu mov $operand1, operand2, din moment ce este folosita doar pentru accesarea adresei inceputului unui array. 

★Instructiunea push:
Este in sine o pseudoinstructiune pentru sub $4, %esp, respectiv mov operand, 0(%esp). Poate fi tratata prin apel catre functia de sub, iar mov-ul nu se schimba, categoric.

★Instructiunea pop:
Acelasi rationament pentru push.Cu toate acestea, in cazul nostru, a fost folosita doar pentru a curata stiva, nu si pentru a stoca valori. Am substituit-o cu add $4, %esp.


🞺Limitari:
Instructiunea de div pare foarte dificil de implementat folosind doar tabele si mutari byte cu byte. Din acelasi motiv, atat ea, cat si shift right vor fi ignorate si pastrate asa cum sunt.
Syscall-urile si apelurile de biblioteca (printf, fflush) sunt aproape imposibil de implementat. Au fost ignorate.


