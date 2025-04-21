###########################
# DOIF für Rolladen Position
###########################
sub SetRolladenByRoomPct {
  my $input = ReadingsVal("GptVoiceCommand", "state", "");
  Log 1, "SetRolladenByRoomPct: Eingabe = '$input'";

  if ($input =~ m/^(K(ü|ue)che|Wohnzimmer|Esszimmer|Schlafzimmer|Bad|Diele|Terrassent(ü|ue)r|Markise).*Rollade.*?(\d{1,3})\s*%?/i) {
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
        fhem("sleep 1; set $device pct $pct");
      }
    } else {
      Log 1, "SetRolladenByRoomPct: Raum oder Prozent ungültig!";
    }
  } else {
    Log 1, "SetRolladenByRoomPct: Keine Übereinstimmung mit Regex!";
  }
}


1; 
