program DeadlockErkennungTest;

{$APPTYPE CONSOLE}

uses
  Classes,
  SysUtils,
  DeadlockErkennung in 'DeadlockErkennung.pas';

type
  TTestFunktion = function: Boolean;

function TestKeineZuege: Boolean;
var
  de: TDeadlockErkennung;
  fertig: Boolean;
begin
  de := TDeadlockErkennung.Create(10);
  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;
  Result := (Length(de.GetBlockierteZuege) = 0);
end;

function TestKeinDeadlock: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  fertig: Boolean;
begin
  de := TDeadlockErkennung.Create(4);

  { <0---<1---<2---<3 }
  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  fsa := de.NeueFstrAlternative(1);
  de.WartetAuf(fsa, 2);

  fsa := de.NeueFstrAlternative(2);
  de.WartetAuf(fsa, 3);

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  Result := (Length(de.GetBlockierteZuege) = 0);
end;

function TestSimpel: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  aufloesungen: TZugindexArrayArray;
  fertig: Boolean;
begin
  { 0>---<1 }
  de := TDeadlockErkennung.Create(2);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  fsa := de.NeueFstrAlternative(1);
  de.WartetAuf(fsa, 0);

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  aufloesungen := de.GetDeadlockAufloesungen(1);

  Result := (Length(de.GetBlockierteZuege) = 2)
    and (Length(aufloesungen) = 2)
    and (aufloesungen[0][0] = 0)
    and (aufloesungen[1][0] = 1);
end;

function TestMehrereDeadlocks: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  aufloesungen: TZugindexArrayArray;
  fertig: Boolean;
begin
  { 0>---<1
    2>---<3 }
  de := TDeadlockErkennung.Create(4);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  fsa := de.NeueFstrAlternative(1);
  de.WartetAuf(fsa, 0);

  fsa := de.NeueFstrAlternative(2);
  de.WartetAuf(fsa, 3);

  fsa := de.NeueFstrAlternative(3);
  de.WartetAuf(fsa, 2);

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  aufloesungen := de.GetDeadlockAufloesungen(2);

  Result := (Length(de.GetBlockierteZuege) = 4)
    and (Length(de.GetDeadlockAufloesungen(1)) = 0 { es gen¸gt nicht, einen Zug abzugleisen })
    and (Length(aufloesungen) = 4)
    and (aufloesungen[0][0] = 0) and (aufloesungen[0][1] = 2)
    and (aufloesungen[1][0] = 0) and (aufloesungen[1][1] = 3)
    and (aufloesungen[2][0] = 1) and (aufloesungen[2][1] = 2)
    and (aufloesungen[3][0] = 1) and (aufloesungen[3][1] = 3);
end;

function TestMehrereFstrAlternativen: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  aufloesungen: TZugindexArrayArray;
  fertig: Boolean;
begin
  { 0>---<1
       \-<2 }
  de := TDeadlockErkennung.Create(3);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 2);

  fsa := de.NeueFstrAlternative(1);
  de.WartetAuf(fsa, 0);

  fsa := de.NeueFstrAlternative(2);
  de.WartetAuf(fsa, 0);

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  aufloesungen := de.GetDeadlockAufloesungen(1);

  Result := (Length(de.GetBlockierteZuege) = 3)
    and (Length(aufloesungen) = 3)
    and (aufloesungen[0][0] = 0)
    and (aufloesungen[1][0] = 1)
    and (aufloesungen[2][0] = 2)
    and (Length(de.GetDeadlockAufloesungen(2)) = 0 { es gen¸gt immer, einen Zug abzugleisen });
end;

function TestZyklusAberKeinDeadlock: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  fertig: Boolean;
begin
  {  0>----<1
    <3--\--<2

    Zyklische Abh‰ngigkeit 0 -> 1 -> 2, aber Zug 2 hat noch eine andere Fahrmˆglichkeit. }
  de := TDeadlockErkennung.Create(4);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 2);

  fsa := de.NeueFstrAlternative(1);
  de.WartetAuf(fsa, 0);

  fsa := de.NeueFstrAlternative(2);
  de.WartetAuf(fsa, 0);

  fsa := de.NeueFstrAlternative(2);
  de.WartetAuf(fsa, 3);

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  Result := (Length(de.GetBlockierteZuege) = 0)
    { kein Deadlock -> keine Auflˆsungen }
    and (Length(de.GetDeadlockAufloesungen(1)) = 0)
    and (Length(de.GetDeadlockAufloesungen(2)) = 0)
    and (Length(de.GetDeadlockAufloesungen(3)) = 0);
end;

function TestZugBlockiertSichSelbst: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  aufloesungen: TZugindexArrayArray;
  fertig: Boolean;
begin
  { 0>---1>, Zug 1 hat keine Folgefahrstraﬂe }
  de := TDeadlockErkennung.Create(2);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  fsa := de.NeueFstrAlternative(1);
  de.WartetAuf(fsa, 1);

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  aufloesungen := de.GetDeadlockAufloesungen(1);

  Result := (Length(de.GetBlockierteZuege) = 2)
    and (Length(aufloesungen) = 1)
    and (aufloesungen[0][0] = 1);
end;

function TestZugWirdAbgegleist: Boolean;
var
  de: TDeadlockErkennung;
  fsa: TFstrAlternative;
  fertig: Boolean;
begin
  { 0>---1>, Zug 1 wird als n‰chstes abgegleist }
  de := TDeadlockErkennung.Create(2);

  fsa := de.NeueFstrAlternative(0);
  de.WartetAuf(fsa, 1);

  { Zug 1 hat keine Fahrstraﬂenalternativen. }

  fertig := false;
  while not fertig do
  begin
    fertig := de.DeadlockPruefungSchritt;
  end;

  Result := (Length(de.GetBlockierteZuege) = 0);
end;

var
  TestFunktionen: TList;
  i: Integer;

begin
  ExitCode := 0;

  TestFunktionen := TList.Create;
  TestFunktionen.Add(@TestKeineZuege);
  TestFunktionen.Add(@TestKeinDeadlock);
  TestFunktionen.Add(@TestSimpel);
  TestFunktionen.Add(@TestMehrereDeadlocks);
  TestFunktionen.Add(@TestZugBlockiertSichSelbst);
  TestFunktionen.Add(@TestZugWirdAbgegleist);
  TestFunktionen.Add(@TestMehrereFstrAlternativen);
  TestFunktionen.Add(@TestZyklusAberKeinDeadlock);

  for i := 0 to TestFunktionen.Count - 1 do
  begin
    if TTestFunktion(TestFunktionen.Items[i]) then
    begin
      WriteLn(i, ' OK');
    end
    else
    begin
      WriteLn(i, ' FEHLER');
      ExitCode := 1;
    end;
  end;
end.
