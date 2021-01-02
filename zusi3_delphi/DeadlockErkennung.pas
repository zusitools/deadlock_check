unit DeadlockErkennung;

interface

uses
  Contnrs;

type

{ Ein Array von Bits. F�r die bei der Deadlock-Erkennung eingesetzten Bitarrays
gilt: Die L�nge entspricht der Anzahl Z�ge in der Simulation -> jedem Zug ist
ein Bit zugeordnet.
Implementiert als ein Array von unsigned integers, die Anzahl Bits ist also
auf 32-Bit-Systemen immer ein Vielfaches von 32. }
TBitarray = array of Cardinal;

TBitarrayArray = array of TBitarray;

{ Repr�sentiert eine m�gliche n�chste Fahrstra�e f�r einen Zug
mit einem Bitarray derjenigen Z�ge, die diese Folgefahrstra�e blockieren. }
TFstrAlternative = class
public
  ZugIndex: Integer;
  WartetAufZuege: TBitarray;
end;

{ Ein Array von Zug-Indizes. }
TZugindexArray = array of Integer;

{ Ein Array von TZugindexArray. }
TZugindexArrayArray = array of TZugindexArray;

TDeadlockErkennungZustand = (dezInit, dezBerechnung, dezFertig);

{ Klasse zur Deadlock-Erkennung.

Funktionsweise:
Ein Zug gilt als blockiert, wenn er in allen Fahrstra�enalternativen auf einen
anderen Zug wartet, der ebenfalls blockiert ist.

Es werden zwei Datenstrukturen benutzt:
 - eine Menge der blockierten Z�ge,
 - f�r jede Fahrstra�enalternativen eines Zuges eine Menge von Z�gen, auf die
   er in dieser Fahrstra�enalternativen wartet.

Sobald ein Zug in mindestens einer Fahrstra�enalternative auf keinen anderen Zug
wartet oder nur auf nicht blockierte Z�ge wartet, wird er aus der Menge blockierter
Z�ge entfernt.

Am Anfang wird jeder Zug, der keine freie Folgefahrstra�e hat, als blockiert
angenommen. Nach Fixpunktiteration (mehrfaches Aufrufen der Funktion DeadlockPruefungSchritt)
enth�lt die Menge blockierter Z�ge nur solche Z�ge, die ohne Abgleisen eines Zuges
nicht weiterfahren k�nnen. Diese Menge ist mit der Funktion GetBlockierteZuege abrufbar.

Mit GetDeadlockAufloesungen wird durch simples Durchprobieren eine Liste von Zugmengen
ermittelt, deren Abgleisen den Deadlock aufl�st.

Implementierung:
 - Z�ge werden durch einen eindeutigen Index im Bereich von 0 bis MaxAnzahlZuege - 1
   identifiziert. Beispielsweise kann das ein Index in einer globalen Zugliste sein.
 - Mengen von Z�gen werden als Bitarrays dargestellt. Ein gesetztes Bit bedeutet,
   dass ein Zug in der Menge enthalten ist. Das erlaubt eine effiziente Implementierung
   von Mengenoperationen durch bitweise Operationen. }
TDeadlockErkennung = class
  { Erzeugt eine neue Instanz von TDeadlockErkennung, die Zug-Indizes
  von 0 bis MaxAnzahlZuege - 1 verarbeiten kann. }
  constructor Create(MaxAnzahlZuege: Integer);
  destructor Destroy; override;

  { F�gt eine neue Fahrstra�enalternative f�r den angegebenen Zug hinzu
  und gibt einen Zeiger darauf zur�ck, der als Parameter f�r WartetAuf()
  verwendet werden kann.

  Falls der Zug als n�chstes abgegleist wird oder noch keine Folgefahrstra�en bestimmt
  wurden, sollte einfach keine Fahrstra�enalternative angelegt werden. Der Zug wird dann
  als nicht blockiert markiert.

  Falls der Zug definitiv keine m�gliche Folgefahrstra�e hat (beispielsweise weil kein
  Fahrweg gefunden wurde) und auch nicht als n�chstes abgegleist wird,
  sollte eine neue Fahrstra�enalternative angelegt werden,
  in der der Zug als auf sich selbst wartend markiert wird.

  Falls der Zug noch nicht vor einem Halt zeigenden Signal steht (sich also in Bewegung
  befindet oder die M�glichkeit hat, sich nochmals in Bewegung zu setzen), ist es
  ebenfalls sinnvoll, noch keine Fahrstra�enalternative f�r diesen Zug anzulegen.
  So werden falsch positive Meldungen vermieden. }
  function NeueFstrAlternative(ZugIndex: Integer): TFstrAlternative;

  { Speichert die Information, dass der Zug in der angegebenen Fahrstra�en-Alternative
  durch einen anderen Zug blockiert ist. Beispielsweise:
   - Die Fahrstra�e kann nicht eingestellt werden, solange der andere Zug seine
     derzeit belegten Register nicht freigibt.
   - Der Zug wartet �ber eine Fahrplanabh�ngigkeit auf einen anderen Zug. }
  procedure WartetAuf(FstrAlternative: TFstrAlternative; WartetAufZugIndex: Integer);

  { F�hrt einen Schritt der Deadlock-Pr�fung durch und gibt zur�ck, ob die Berechnung
  abgeschlossen ist. }
  function DeadlockPruefungSchritt: Boolean;

  { Gibt eine Liste blockierter Zug-Indizes zur�ck, wenn die Berechnung abgeschlossen ist.
  Ansonsten wird eine Exception EInvalidOperation geworfen. }
  function GetBlockierteZuege: TZugindexArray;

  { Gibt alle m�glichen Zugindex-Arrays mit genau AnzahlZuege Z�gen zur�ck,
  durch deren Abgleisen der Deadlock aufgel�st wird. }
  function GetDeadlockAufloesungen(AnzahlZuege: Integer): TZugindexArrayArray;

private
  BlockierteZuege: TBitarray;
  FahrstrAlternativen: TObjectList;
  ZugBitarrayAnzElemente: Integer;
  Zustand: TDeadlockErkennungZustand;

  { L�scht die Bits f�r diejenigen Z�ge aus dem Bitarray "BlockierteZuege",
  die auf keinen einen anderen blockierten Zug warten. Gibt true zur�ck,
  wenn sich keine �nderung ergeben hat. }
  function AktualisiereBlockierteZuege(var BlockierteZuege: TBitarray): Boolean;

  { Gibt ein Array mit den Indizes der gesetzten Bits im Bitarray zur�ck. }
  function BitarrayZuZugindexArray(const Bitarray: TBitarray): TZugindexArray;
end;

implementation

uses Classes, SysUtils;

const
  BitarrayBitsProElement: Integer = 8 * sizeof(Cardinal);

{ Gibt zur�ck, ob das Bit mit dem angegebenen Index im Bitarray gesetzt ist. }
function BitarrayIstBitGesetzt(const Bitarray: TBitarray; BitIndex: Integer): Boolean;
begin
{$IFDEF DEBUG}
  if BitIndex div BitarrayBitsProElement >= Length(Bitarray) then
  begin
    raise EInvalidOperation.Create('BitIndex au�erhalb des g�ltigen Bereichs');
  end;
{$ENDIF}
  Result := Bitarray[BitIndex div BitarrayBitsProElement] and (1 shl (BitIndex mod BitarrayBitsProElement)) <> 0;
end;

{ L�scht das Bit mit dem angegebenen Index im Bitarray. }
procedure BitarrayLoescheBit(var Bitarray: TBitarray; BitIndex: Integer);
begin
{$IFDEF DEBUG}
  if BitIndex div BitarrayBitsProElement >= Length(Bitarray) then
  begin
    raise EInvalidOperation.Create('BitIndex au�erhalb des g�ltigen Bereichs');
  end;
{$ENDIF}
  Bitarray[BitIndex div BitarrayBitsProElement] := Bitarray[BitIndex div BitarrayBitsProElement] and not (1 shl (BitIndex mod BitarrayBitsProElement));
end;

{ Setzt das Bit mit dem angegebenen Index im Bitarray. }
procedure BitarraySetzeBit(var Bitarray: TBitarray; BitIndex: Integer);
begin
{$IFDEF DEBUG}
  if BitIndex div BitarrayBitsProElement >= Length(Bitarray) then
  begin
    raise EInvalidOperation.Create('BitIndex au�erhalb des g�ltigen Bereichs');
  end;
{$ENDIF}
  Bitarray[BitIndex div BitarrayBitsProElement] := Bitarray[BitIndex div BitarrayBitsProElement] or (1 shl (BitIndex mod BitarrayBitsProElement));
end;

{ Gibt true zuruck gdw. alle Bits im Bitarray 0 sind. "AnzahlElemente" ist die Anzahl
Elemente (nicht Bits!) im Bitarray und wird ben�tigt, um einen Aufruf von Length()
zu sparen. }
function BitarrayIst0(const Bitarray: TBitarray; const AnzahlElemente: Integer): Boolean;
var
  i: Integer;
begin
{$IFDEF DEBUG}
  if Length(Bitarray) <> AnzahlElemente then
  begin
    raise EInvalidOperation.Create('AnzahlElemente falsch');
  end;
{$ENDIF}
  Result := true;
  for i := 0 to AnzahlElemente - 1 do
  begin
    if Bitarray[i] <> 0 then
    begin
      Result := false;
      Break;
    end;
  end;
end;



constructor TDeadlockErkennung.Create(MaxAnzahlZuege: Integer);
begin
  inherited Create;
  Self.Zustand := dezInit;
  Self.ZugBitarrayAnzElemente := (MaxAnzahlZuege + BitarrayBitsProElement - 1) div BitarrayBitsProElement;

  SetLength(Self.BlockierteZuege, ZugBitarrayAnzElemente); { wird mit 0 initialisiert }
  Self.FahrstrAlternativen := TObjectList.Create;
end;

destructor TDeadlockErkennung.Destroy;
begin
  Self.FahrstrAlternativen.Free;
  inherited Destroy;
end;

function TDeadlockErkennung.NeueFstrAlternative(ZugIndex: Integer): TFstrAlternative;
begin
  if Zustand <> dezInit then
  begin
    raise EInvalidOperation.Create('Berechnung wurde bereits gestartet.');
  end;
  Result := TFstrAlternative.Create;
  Result.ZugIndex := ZugIndex;
  SetLength(Result.WartetAufZuege, Self.ZugBitarrayAnzElemente) { wird mit 0 initialisiert };
  Self.FahrstrAlternativen.Add(Result);
  { Bis zum Aufruf von WartetAuf() ist der Zug in dieser Fstr-Alternative
  durch keinen anderen Zug blockiert. }
  BitarrayLoescheBit(Self.BlockierteZuege, ZugIndex);
end;

procedure TDeadlockErkennung.WartetAuf(FstrAlternative: TFstrAlternative; WartetAufZugIndex: Integer);
begin
  BitarraySetzeBit(FstrAlternative.WartetAufZuege, WartetAufZugIndex);
  BitarraySetzeBit(Self.BlockierteZuege, FstrAlternative.ZugIndex);
end;

function TDeadlockErkennung.DeadlockPruefungSchritt: Boolean;
begin
  if Zustand = dezInit then
  begin
    Zustand := dezBerechnung;
  end;
  Result := AktualisiereBlockierteZuege(Self.BlockierteZuege);
  if Result then
  begin
    Zustand := dezFertig;
  end;
end;

function TDeadlockErkennung.GetBlockierteZuege: TZugindexArray;
begin
  if Zustand <> dezFertig then
  begin
    raise EInvalidOperation.Create('Berechnung ist noch nicht abgeschlossen');
  end;
  Result := BitarrayZuZugindexArray(Self.BlockierteZuege);
end;

function TDeadlockErkennung.BitarrayZuZugindexArray(const Bitarray: TBitarray): TZugindexArray;
var
  i, j: Integer;
begin
  SetLength(Result, 0);
  for i := 0 to Self.ZugBitarrayAnzElemente - 1 do
  begin
    for j := 0 to BitarrayBitsProElement - 1 do
    begin
      if Bitarray[i] and (1 shl j) <> 0 then
      begin
        SetLength(Result, Length(Result) + 1);
        Result[Length(Result) - 1] := i * BitarrayBitsProElement + j;
      end;
    end;
  end;
end;

function TDeadlockErkennung.GetDeadlockAufloesungen(AnzahlZuege: Integer): TZugindexArrayArray;

  procedure GetDeadlockAufloesungenRek(
    const StartIndex: Integer; { Index des ersten m�glichen abzugleisenden Zuges. }
    const AnzahlAbzugleisendeZuege: Integer;
    const BlockierteZuege: TBitarray;
    var EntfernteZuege: TBitarray);
  var
    bitIndex: Integer;
    fertig: Boolean;
    blockierteZuegeNeu: TBitarray;
  begin
    SetLength(blockierteZuegeNeu, Self.ZugBitarrayAnzElemente);
    for bitIndex := StartIndex to (Self.ZugBitarrayAnzElemente * BitarrayBitsProElement) - 1 do
    begin
      { Suche den n�chsten blockierten Zug und probiere, was passieren w�rde,
      wenn man ihn entfernte. }
      if not BitarrayIstBitGesetzt(BlockierteZuege, bitIndex)
        or BitarrayIstBitGesetzt(EntfernteZuege, bitIndex) then
      begin
        Continue;
      end;

      BitarraySetzeBit(EntfernteZuege, bitIndex);

      Move(BlockierteZuege[0], blockierteZuegeNeu[0], Self.ZugBitarrayAnzElemente * sizeof(Cardinal));
      BitarrayLoescheBit(blockierteZuegeNeu, bitIndex);

      fertig := False;
      while not fertig do
      begin
        fertig := AktualisiereBlockierteZuege(blockierteZuegeNeu);
      end;

      if BitarrayIst0(blockierteZuegeNeu, Self.ZugBitarrayAnzElemente) then
      begin
        if AnzahlAbzugleisendeZuege = 1 then
        begin
          SetLength(Result, Length(Result) + 1);
          Result[Length(Result) - 1] := BitarrayZuZugindexArray(EntfernteZuege);
        end;
      end
      else
      begin
        if AnzahlAbzugleisendeZuege > 1 then
        begin
          GetDeadlockAufloesungenRek(
            bitIndex + 1,
            AnzahlAbzugleisendeZuege - 1,
            blockierteZuegeNeu,
            EntfernteZuege);
        end;
      end;

      BitarrayLoescheBit(EntfernteZuege, bitIndex);
    end;
  end;

var
  entfernteZuege: TBitarray;
begin
  if Zustand <> dezFertig then
  begin
    raise EInvalidOperation.Create('Berechnung ist noch nicht abgeschlossen');
  end;

  SetLength(Result, 0);
  SetLength(entfernteZuege, Self.ZugBitarrayAnzElemente);
  GetDeadlockAufloesungenRek(0, AnzahlZuege, Self.BlockierteZuege, entfernteZuege);
end;

function TDeadlockErkennung.AktualisiereBlockierteZuege(var BlockierteZuege: TBitarray): Boolean;
var
  i, j: Integer;
  zugIstBlockiert: Boolean;
  fstrAlternative: TFstrAlternative;
begin
  Result := true;
  for i := 0 to Self.FahrstrAlternativen.Count - 1 do
  begin
    fstrAlternative := TFstrAlternative(Self.FahrstrAlternativen.Items[i]);

    { Wenn der Zug nicht blockiert ist, ist nichts mehr zu tun. }
    if not BitarrayIstBitGesetzt(BlockierteZuege, fstrAlternative.ZugIndex) then
    begin
      Continue;
    end;

    { Ansonsten pr�fe, ob er mittlerweile nicht mehr blockiert ist. }
    zugIstBlockiert := false;
    for j := 0 to Self.ZugBitarrayAnzElemente - 1 do
    begin
      if (fstrAlternative.WartetAufZuege[j] and BlockierteZuege[j]) <> 0 then
      begin
        zugIstBlockiert := true;
        Break;
      end;
    end;

    { Falls ja, aktualisiere die Bitmaske mit blockierten Z�gen entsprechend
    und setze Result := false, da ein weiterer Berechnungsschritt notwendig ist. }
    if not zugIstBlockiert then
    begin
      BitarrayLoescheBit(BlockierteZuege, fstrAlternative.ZugIndex);
      Result := false;
    end;
  end;
end;

end.
