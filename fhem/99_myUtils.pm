##############################################
# $Id: myUtilsTemplate.pm 7570 2015-01-14 18:31:44Z rudolfkoenig $
#
# Save this file as 99_myUtils.pm, and create your own functions in the new
# file. They are then available in every Perl expression.

package main;

use strict;
use warnings;
use POSIX;

sub
myUtils_Initialize($$)
{
  my ($hash) = @_;
}

# Enter you functions below _this_ line.
#########################################
# ReadMaxSolargesData
#########################################
sub ReadMaxSolargesData {
    my $device = 'SolargesData';
    my $filename = '/opt/fhem/max_solarges.txt';
    my $current_year = (localtime)[5] + 1900;  # Ermittelt das aktuelle Jahr
    my $current_value = '';  # Variable zum Speichern des Wertes des aktuellen Jahres
    my %yearly_max;  # Hash für den Höchstwert pro Jahr
    my %yearly_total;  # Hash für die Gesamtproduktion pro Jahr

    # Datei öffnen und lesen
    if (open(my $fh, '<', $filename)) {
        my $line_number = 0;
        while (my $line = <$fh>) {
            chomp($line);
            if ($line_number == 0) {
                # Erste Zeile (Auslesedatum)
                my ($key, $date) = split(/: /, $line);
                fhem("setreading $device Auslesedatum $date");
            } else {
                # Folgezeilen (Jahreswerte) - erwartet das Format: Jahr - Max: <Wert> W, Total: <Wert> kWh
                my ($year, $max_value, $total_value) = $line =~ /(\d{4}) - Max: ([\d.]+) W, Total: ([\d.]+) kWh/;
                
                if (defined $year && defined $max_value && defined $total_value) {
                    # Speichere den Maximalwert und die Gesamtproduktion für das Jahr
                    $yearly_max{$year} = $max_value;
                    $yearly_total{$year} = $total_value;

                    # Setze das Reading für den Maximalwert in Watt
                    fhem("setreading $device max_$year $max_value W");

                    # Setze das Reading für die Gesamtproduktion in kWh
                    fhem("setreading $device total_$year $total_value kWh");

                    # Wenn das Jahr dem aktuellen Jahr entspricht, den Wert speichern
                    if ($year == $current_year) {
                        $current_value = $max_value;
                    }
                }
            }
            $line_number++;
        }
        close($fh);

        # Den State des Geräts mit dem Maximalwert des aktuellen Jahres aktualisieren
        if ($current_value ne '') {
            fhem("setstate $device $current_value W");
        } else {
            fhem("setstate $device Kein Wert für das aktuelle Jahr");
        }

        Log 1, "ReadMaxSolargesData: Daten erfolgreich aus Datei $filename gelesen und in Readings gespeichert.";
    } else {
        Log 1, "ReadMaxSolargesData: Konnte Datei '$filename' nicht öffnen: $!";
    }
}

1;  # Behalten Sie das am Ende des Moduls

#########################################
## Wind berechnung
# AverageWindSpeed
#########################################
sub AverageWindSpeed {
  my ($device, $reading, $dummy) = @_;

  # Lese die aktuellen Windgeschwindigkeitswerte
  my @wind_speeds = split(',', ReadingsVal($device, $reading, ''));
  my $total = 0;
  my $count = 0;

  foreach my $speed (@wind_speeds) {
    $total += $speed;
    $count++;
  }

  # Berechne den Durchschnitt
  my $average = $count ? $total / $count : 0;

  # Setze den Durchschnittswert im Dummy
  fhem("setreading $dummy state $average");
  
}

1;
#########################################
# AddWindSpeedReading
#########################################
sub AddWindSpeedReading {
  my ($device, $reading, $new_value) = @_;

  # Lese die aktuellen Windgeschwindigkeitswerte
  my $values = ReadingsVal($device, $reading, '');

  # Füge den neuen Wert hinzu
  my @wind_speeds = split(',', $values);
  push(@wind_speeds, $new_value);

  # Begrenze die Anzahl der gespeicherten Werte auf 10
  shift(@wind_speeds) if scalar(@wind_speeds) > 10;

  # Setze die neuen Werte
  my $new_values = join(',', @wind_speeds);
  fhem("setreading $device $reading $new_values");
}

1; # Wichtig für Perl Module
#########################################
## Helligkeitsberechnung
# AverageIllumination
#########################################
sub AverageIllumination {
  my ($device, $dummy) = @_;

  # Lese die aktuellen Helligkeitswerte aus dem Reading '1.ILLUMINATION'
  my @illumination_values = split(',', ReadingsVal($device, '1.ILLUMINATION', ''));
  my $total = 0;
  my $count = 0;

  foreach my $illumination (@illumination_values) {
    $total += $illumination;
    $count++;
  }

  # Berechne den Durchschnitt
  my $average = $count ? $total / $count : 0;

  # Setze den Durchschnittswert im Dummy
  fhem("setreading $dummy state $average");
}

1;
#########################################
# AddIlluminationReading
#########################################
sub AddIlluminationReading {
  my ($device, $new_value) = @_;

  # Lese die aktuellen Helligkeitswerte aus dem Reading '1.ILLUMINATION'
  my $values = ReadingsVal($device, '1.ILLUMINATION', '');

  # Füge den neuen Wert hinzu
  my @illumination_values = split(',', $values);
  push(@illumination_values, $new_value);

  # Begrenze die Anzahl der gespeicherten Werte auf 3
  shift(@illumination_values) if scalar(@illumination_values) > 10;

  # Setze die neuen Werte
  my $new_values = join(',', @illumination_values);
  fhem("setreading $device 1.ILLUMINATION $new_values");
}

1; # Wichtig für Perl Module

#########################################
# DebianMail  Mail auf dem RPi versenden 
#########################################
sub 
DebianMail 
{ 
 my $rcpt = shift;
 my $subject = shift; 
 my $text = "..";
 my $attach = "attach"; 
 my $ret = "";
 my $sender = "holger.mangold\@netcologne.de"; 
 my $konto = "holger.mangold\@netcologne.de";
 my $passwrd = "32Ma56Ho!";
 my $provider = "smtp.netcologne.de:587";
 Log 1, "sendEmail RCP: $rcpt";
 Log 1, "sendEmail Subject: $subject";
 Log 1, "sendEmail Text: $text";
 Log 1, "sendEmail Anhang: $attach";
 
 $ret .= qx(sendEmail -f $sender -t $rcpt -u $subject -m $text -s $provider -xu $konto -xp $passwrd -o tls=yes );
 $ret =~ s,[\r\n]*,,g;    # remove CR from return-string 
 Log 1, "sendEmail returned: $ret"; 
}

1;
#########################################
# IncrementalSwitch
#########################################
sub IncrementalSwitch {
  my ($device, $reading) = @_;

  # Lese den aktuellen Wert des Zählers
  my $count = ReadingsVal($device, $reading, 0);

  # Erhöhe den Zähler um 1
  $count++;

  # Setze den neuen Wert des Zählers
  fhem ( "setreading $device $reading $count" );

  # Gib den neuen Wert in den Log aus (optional)
  Log 3, "IncrementalSwitch: Neuer Wert für $device - $reading ist $count";
}

1; # Wichtig für Perl ModuleInternals:

###########################
# DOIF für Rolladen Position
###########################
sub SetRolladenByRoomPct {
  my $input = ReadingsVal("GptVoiceCommand", "state", "");
  Log 1, "SetRolladenByRoomPct: Eingabe = '$input'";

  if ($input =~ m/\b(K(ü|ue)che|Wohnzimmer|Esszimmer|Schlafzimmer|Bad|Diele|Terrassent(ü|ue)r|Markise)\b.*?Rollade.*?(\d{1,3})/i) {
    my $room = lc($1);
    my $pct = $2;
    Log 1, "SetRolladenByRoomPct: Raum='$room', Prozent='$pct'";

    my %room_to_device = (
      'küche'         => ['Roll_Kueche'],
      'kueche'        => ['Roll_Kueche'],
      'wohnzimmer'    => ['Roll_Wohnz'],
      'esszimmer'     => ['Roll_Ess'],
      'schlafzimmer'  => ['Roll_Schlaf1', 'Roll_Schlaf2'],
      'bad'           => ['Roll_Bad'],
      'diele'         => ['Roll_Diele'],
      'terrassentür'  => ['HM_731E63'],
      'terrassentuer' => ['HM_731E63'],
      'markise'       => ['Roll_Markise'],
    );

    my $devices = $room_to_device{$room};

    if (defined $devices && $pct >= 0 && $pct <= 100) {
      foreach my $device (@$devices) {
        Log 1, "SetRolladenByRoomPct: set $device pct $pct";
        fhem("set $device pct $pct");
      }
    } else {
      Log 1, "SetRolladenByRoomPct: Raum oder Prozent ungültig!";
    }
  } else {
    Log 1, "SetRolladenByRoomPct: Keine Übereinstimmung mit Regex!";
  }
}

1; 
