\c db_delays;

CREATE INDEX IF NOT EXISTS idx_ac_tailno 
ON aircrafts(
    tail_no
);


CREATE INDEX IF NOT EXISTS idx_al_id
ON airlines(
    airline_id
);


CREATE INDEX IF NOT EXISTS idx_ap_iata
ON airports(
    iata
);


CREATE INDEX IF NOT EXISTS idx_fl_id
ON delays(
    delay_id
);
CREATE INDEX IF NOT EXISTS idx_fl_tailno
ON delays(
    tail_no
);
